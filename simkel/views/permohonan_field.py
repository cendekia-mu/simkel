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
        title="Nama Field")
    
    kode = colander.SchemaNode(
        colander.String(),
        title="Kode",
        missing=None) 
        
    value = colander.SchemaNode(
        colander.String(), 
        title="Nilai")

class Views(BaseView):
    def __init__(self, request):
        super().__init__(request)
        self.request = request
        self.session = SimkelDBSession
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
        return dict(title=f"Detail {self.title}", row=item)

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
                return dict(title=f"Form {self.title}", form=e.render())
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
                'value': item.value
            }
        
        return dict(title=f"Form {self.title}", form=form.render(appstruct))

    def view_send(self):
        request = self.request
        item = self.get_row(request.matchdict.get('id'))
        if item and item.status in [0, 2, None]:
            try:
                item.status = 1
                item.updated = datetime.now()
                self.session.add(item)
                transaction.commit()
                request.session.flash(f"Data ID {item.id} berhasil dikirim.")
            except Exception as e:
                transaction.abort()
                request.session.flash(f"Gagal mengirim: {str(e)}", 'error')
        return HTTPFound(location=request.route_url('simkel-permohonan-field'))

    def view_delete(self):
        request = self.request
        item = self.get_row(request.matchdict.get('id'))
        if item and item.status in [0, 2, None]:
            try:
                self.session.delete(item)
                transaction.commit()
                request.session.flash("Data berhasil dihapus.")
            except Exception as e:
                transaction.abort()
                request.session.flash(f"Gagal hapus: {str(e)}", 'error')
        return HTTPFound(location=request.route_url('simkel-permohonan-field'))