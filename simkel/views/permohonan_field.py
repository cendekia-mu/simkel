import re
import json
import logging
import colander
import transaction
from sqlalchemy import desc, or_
from pyramid.httpexceptions import HTTPFound
from deform import widget, Form, ValidationFailure

from opensipkd.base.views import BaseView 
from ..models import SimkelDBSession
from ..models.permohonan_field import SimkelPermohonanField
from ..models.jenispermohonan import SimkelJenisPermohonan

log = logging.getLogger(__name__)

# --- PENGAMAN 1: Validasi agar Kode tidak pakai spasi ---
def validate_kode(node, value):
    if not re.match(r"^[a-zA-Z0-9_]+$", value):
        raise colander.Invalid(node, "Kode hanya boleh huruf, angka, dan underscore (_). Tidak boleh ada spasi!")

class FieldSchema(colander.Schema):
    jpel_id = colander.SchemaNode(
        colander.Integer(), 
        title="Pilih Jenis Layanan",
        widget=widget.SelectWidget())
    
    nama = colander.SchemaNode(
        colander.String(), 
        title="Pertanyaan di Form Warga (Label)",
        description="Contoh: Nama Ibu Kandung, Luas Tanah, dll")

    kode = colander.SchemaNode(
        colander.String(),
        title="Kode Field / Variabel Database",
        description="Contoh: nama_ibu, luas_tanah (Tanpa spasi)",
        validator=validate_kode)

    tipe = colander.SchemaNode(
        colander.String(),
        title="Tipe Isian",
        widget=widget.SelectWidget(values=[
            ('text', 'Teks Singkat (Satu Baris)'),
            ('number', 'Angka / Nominal'),
            ('date', 'Pilih Tanggal'),
            ('textarea', 'Paragraf (Alamat/Keterangan Panjang)')
        ]),
        default='text')

    is_required = colander.SchemaNode(
        colander.Boolean(),
        title="Wajib Diisi oleh Warga?",
        widget=widget.CheckboxWidget(),
        missing=False)

    is_printed = colander.SchemaNode(
        colander.Boolean(),
        title="Cetak di PDF Surat?",
        widget=widget.CheckboxWidget(),
        missing=True)
    
    value = colander.SchemaNode(
        colander.String(), 
        title="Opsi Tambahan (Biar dikosongkan jika tidak paham)",
        missing=None,
        widget=widget.TextAreaWidget(rows=2))

class Views(BaseView):
    def __init__(self, request):
        super().__init__(request)
        self.request = request
        self.session = SimkelDBSession()
        self.title = "Master Desain Form Layanan" # Nama disesuaikan fungsinya
        self.route = 'simkel-permohonan-field'
        self.list_route = 'simkel-permohonan-field'
        
        self.table = SimkelPermohonanField
        self.list_schema = FieldSchema
        self.edit_schema = FieldSchema

    def query_id(self):
        row_id = self.request.matchdict.get('id')
        return self.session.query(SimkelPermohonanField).filter_by(id=row_id)

    def get_values(self, row):
        return {c.name: getattr(row, c.name) for c in row.__table__.columns}

    def get_item_table(self, parent):
        return None

    def view_list(self):
        jpel_id = self.request.params.get('jpel_id')
        search = self.request.params.get('term') or self.request.params.get('search')
        
        query = self.session.query(SimkelPermohonanField)
        
        if jpel_id and jpel_id.isdigit():
            query = query.filter(SimkelPermohonanField.jpel_id == int(jpel_id))
        
        if search:
            query = query.filter(
                or_(
                    SimkelPermohonanField.nama.ilike(f'%{search}%'),
                    SimkelPermohonanField.kode.ilike(f'%{search}%')
                )
            )
            
        rows = query.order_by(desc(SimkelPermohonanField.id)).all()
        
        # Mapping nama layanan agar gampang dibaca di template UI
        p_query = self.session.query(SimkelJenisPermohonan).all()
        jpel_dict = {p.id: p.nama for p in p_query}
        
        # Tambahkan atribut virtual untuk dibaca template
        for r in rows:
            r.nama_layanan = jpel_dict.get(r.jpel_id, 'Tidak Diketahui')
        
        return dict(
            title=f"Daftar {self.title}", 
            rows=rows,
            jpel_list=[(p.id, p.nama) for p in p_query], 
            params=self.request.params
        )

    def view_view(self):
        row = self.query_id().first()
        if not row:
            self.request.session.flash("Data tidak ditemukan.", 'error')
            return HTTPFound(location=self.request.route_url(self.route))
            
        if not hasattr(row, 'status'):
            row.status = None

        res = super().view_view()
        if isinstance(res, dict):
            res['title'] = f"Detail {self.title}"
            res['row'] = row
        return res

    def view_add(self):
        return self.view_form()

    def view_edit(self):
        return self.view_form()

    def view_form(self):
        request = self.request
        row_id = request.matchdict.get('id')
        item = self.query_id().first() if row_id else SimkelPermohonanField()
        
        p_query = self.session.query(SimkelJenisPermohonan).all()
        choices = [(p.id, p.nama) for p in p_query]
        
        schema = FieldSchema().bind()
        schema['jpel_id'].widget.values = choices
        
        form = Form(schema, buttons=('simpan', 'batal'))

        if request.POST:
            if 'batal' in request.POST:
                return HTTPFound(location=request.route_url(self.route))
            return self.view_act(item, form)

        appstruct = {}
        if row_id and item:
            appstruct = self.get_values(item)
            if not hasattr(item, 'status'):
                item.status = None
            
        return dict(
            title=f"Form {self.title}", 
            form=form.render(appstruct), 
            row=item
        )

    def view_act(self, item, form):
        request = self.request
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
            
            # --- PENGAMAN 2: Cek Duplikat Kode ---
            cek_duplikat = self.session.query(SimkelPermohonanField).filter(
                SimkelPermohonanField.jpel_id == appstruct['jpel_id'],
                SimkelPermohonanField.kode == appstruct['kode'],
                SimkelPermohonanField.id != item.id # Abaikan ID sendiri jika sedang edit
            ).first()
            
            if cek_duplikat:
                request.session.flash(f"Gagal! Kode '{appstruct['kode']}' sudah dipakai di layanan ini.", 'error')
                return dict(title=f"Form {self.title}", form=form.render(appstruct), row=item)
            # -------------------------------------

            for field in appstruct:
                setattr(item, field, appstruct[field])
            
            self.session.add(item)
            self.session.flush()
            transaction.commit()
            
            request.session.flash(f"{self.title} berhasil disimpan.")
            return HTTPFound(location=request.route_url(self.route))
            
        except ValidationFailure as e:
            return dict(title=f"Form {self.title}", form=e.render(), row=item)
        except Exception as e:
            transaction.abort()
            request.session.flash(f"Gagal Simpan: {str(e)}", 'error')
            return HTTPFound(location=request.environ.get('HTTP_REFERER', '/'))

    def view_delete(self):
        request = self.request
        item = self.query_id().first()
        
        if not item:
            request.session.flash("Data tidak ditemukan.", 'error')
            return HTTPFound(location=request.route_url(self.route))
        
        try:
            self.session.delete(item)
            transaction.commit()
            request.session.flash(f"{self.title} berhasil dihapus.")
        except Exception as e:
            transaction.abort()
            request.session.flash(f"Gagal hapus: {str(e)}", 'error')
            
        return HTTPFound(location=request.route_url(self.route))