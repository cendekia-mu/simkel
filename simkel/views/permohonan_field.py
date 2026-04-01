import colander
import transaction
from datetime import datetime
from deform import widget, Form, ValidationFailure
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import desc, or_
from ..models import SimkelDBSession, SimkelJenisPermohonan, SimkelPermohonanField
from opensipkd.base.views import BaseView 

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
        title="ID HTML (Tanpa Spasi)")
    
    tipe = colander.SchemaNode(
        colander.String(),
        title="Tipe Input",
        widget=widget.SelectWidget(values=[
            ('text', 'Teks'),
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
    
    value = colander.SchemaNode(
        colander.String(), 
        title="Nilai Default / Opsi",
        missing=None)

class Views(BaseView):
    def __init__(self, request):
        super().__init__(request)
        self.request = request
        self.session = SimkelDBSession()
        self.title = "Permohonan Field"

    def get_row(self, row_id):
        return self.session.query(SimkelPermohonanField).filter_by(id=row_id).first()

    def view_list(self):
        jpel_id = self.request.params.get('jpel_id')
        search = self.request.params.get('term') or self.request.params.get('search')
        query = self.session.query(SimkelPermohonanField).filter(
            or_(
                SimkelPermohonanField.status == 0, 
                SimkelPermohonanField.status == 2,
                SimkelPermohonanField.status == None
            )
        )
        if jpel_id and jpel_id.isdigit():
            query = query.filter(SimkelPermohonanField.jpel_id == int(jpel_id))
        if search:
            query = query.filter(SimkelPermohonanField.nama.ilike(f'%{search}%'))
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
        item = self.get_row(self.request.matchdict.get('id'))
        if not item:
            self.request.session.flash("Data tidak ditemukan.", 'error')
            return HTTPFound(location=self.request.route_url('simkel-permohonan-field'))
        return dict(
            title=f"Detail {self.title}", 
            row=item,
            form=None
        )

    def view_form(self):
        request = self.request
        row_id = request.matchdict.get('id')
        item = self.get_row(row_id) if row_id else SimkelPermohonanField()
        if row_id and item.status in [1, 3]:
            request.session.flash("Data sudah dikunci atau disetujui.", 'warning')
            return HTTPFound(location=request.route_url('simkel-permohonan-field'))
        p_query = self.session.query(SimkelJenisPermohonan).all()
        choices = [('', '-- Pilih Jenis Pelayanan --')] + [
            (p.id, f"{p.kode} - {p.nama}") for p in p_query
        ]
        schema = FieldSchema().bind()
        schema['jpel_id'].widget.values = choices
        form = Form(schema, buttons=('simpan', 'kirim', 'batal'))
        if request.POST:
            if 'batal' in request.POST:
                return HTTPFound(location=request.route_url('simkel-permohonan-field'))
            try:
                controls = request.POST.items()
                appstruct = form.validate(controls)
                item.jpel_id = appstruct['jpel_id']
                item.nama = appstruct['nama']
                item.kode = appstruct['kode']
                item.tipe = appstruct['tipe']
                item.is_required = appstruct['is_required']
                item.value = appstruct['value']
                item.updated = datetime.now()
                if 'kirim' in request.POST:
                    item.status = 1
                    msg = "Berhasil dikirim ke Approval."
                else:
                    item.status = 0
                    msg = "Berhasil disimpan sebagai Draft."
                self.session.add(item)
                self.session.flush()
                transaction.commit() 
                request.session.flash(msg)
                return HTTPFound(location=request.route_url('simkel-permohonan-field'))
            except ValidationFailure as e:
                return dict(title=f"Form {self.title}", form=e.render(), row=item)
            except Exception as e:
                transaction.abort()
                request.session.flash(f"Gagal Simpan: {str(e)}", 'error')
                return HTTPFound(location=request.environ.get('HTTP_REFERER', '/'))
        appstruct = {}
        if row_id and item:
            appstruct = {
                'jpel_id': item.jpel_id, 
                'nama': item.nama, 
                'kode': item.kode,
                'tipe': getattr(item, 'tipe', 'text'),
                'is_required': getattr(item, 'is_required', False),
                'value': item.value
            }
        return dict(title=f"Form {self.title}", form=form.render(appstruct), row=item)