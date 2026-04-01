import logging
import transaction
import colander
from sqlalchemy import desc, or_
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from deform import widget, Form, ValidationFailure

from opensipkd.base.views import BaseView 
from ..models import SimkelDBSession
from ..models.permohonan_field import SimkelPermohonanField
from ..models.jenispermohonan import SimkelJenisPermohonan

log = logging.getLogger(__name__)

class FieldSchema(colander.Schema):
    jpel_id = colander.SchemaNode(
        colander.Integer(), 
        title="Jenis Pelayanan",
        widget=widget.SelectWidget())
    
    nama = colander.SchemaNode(
        colander.String(), 
        title="Label di Form Warga")

    kode = colander.SchemaNode(
        colander.String(),
        title="ID/Kode Field (Tanpa Spasi)",
        missing=None)

    tipe = colander.SchemaNode(
        colander.String(),
        title="Tipe Input",
        widget=widget.SelectWidget(values=[
            ('text', 'Teks Singkat'),
            ('number', 'Angka'),
            ('date', 'Tanggal'),
            ('file', 'Upload Berkas'),
            ('textarea', 'Alamat/Paragraf')
        ]),
        default='text')

    is_required = colander.SchemaNode(
        colander.Boolean(),
        title="Wajib Diisi?",
        widget=widget.CheckboxWidget(),
        missing=False)

    is_printed = colander.SchemaNode(
        colander.Boolean(),
        title="Tampilkan di PDF/TTE?",
        widget=widget.CheckboxWidget(),
        missing=True)
    
    value = colander.SchemaNode(
        colander.String(), 
        title="Opsi Tambahan (JSON)",
        missing=None,
        widget=widget.TextAreaWidget(rows=3))

class Views(BaseView):
    def __init__(self, request):
        super().__init__(request)
        self.request = request
        self.session = SimkelDBSession()
        self.title = "Master Field Permohonan"
        self.route = 'simkel-permohonan-field'
        self.list_route = 'simkel-permohonan-field'
        
        # Penyesuaian BaseView
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
                    SimkelPermohonanField.value.ilike(f'%{search}%')
                )
            )
            
        rows = query.order_by(desc(SimkelPermohonanField.id)).all()
        p_query = self.session.query(SimkelJenisPermohonan).all()
        jpel_list = [(p.id, p.nama) for p in p_query]
        
        return dict(
            title=f"Daftar {self.title}", 
            rows=rows,
            jpel_list=jpel_list, 
            params=self.request.params
        )

    def view_view(self):
        row = self.query_id().first()
        if not row:
            self.request.session.flash("Data tidak ditemukan.", 'error')
            return HTTPFound(location=self.request.route_url(self.route))
            
        # FIX: Tambahkan atribut status dummy karena template base5.pt mengekspektasikannya
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
        choices = [(p.id, f"{p.id} - {p.nama}") for p in p_query]
        
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
            # Pastikan row tersedia untuk template base.pt
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
        row_id = request.matchdict.get('id')
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