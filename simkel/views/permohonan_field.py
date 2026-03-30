import colander
import transaction
from datetime import datetime
from deform import widget, Form, ValidationFailure
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import desc
from ..models import SimkelDBSession, SimkelPermohonan, SimkelPermohonanField
from opensipkd.base.views import BaseView 

class FieldSchema(colander.Schema):
    permohonan_id = colander.SchemaNode(
        colander.Integer(), 
        title="ID Permohonan",
        widget=widget.SelectWidget())
    nama = colander.SchemaNode(
        colander.String(), 
        title="Nama Field")
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
        query = self.session.query(SimkelPermohonanField).order_by(desc(SimkelPermohonanField.id))
        rows = query.all()
        return dict(
            title="Daftar Permohonan Field", 
            rows=rows, 
            form=None
        )

    def view_form(self):
        request = self.request
        row_id = request.matchdict.get('id')
        item = self.get_row(row_id) if row_id else None
        
        if item and hasattr(item, 'status') and str(item.status) not in ['0', '2']:
            request.session.flash("Data sudah dikunci!", 'error')
            return HTTPFound(location=request.route_url('simkel-permohonan-field'))
        
        p_query = self.session.query(SimkelPermohonan).all()
        choices = [('', '-- Pilih Permohonan --')] + [(p.id, f"{p.nomor or p.id}") for p in p_query]
        schema = FieldSchema().bind()
        schema['permohonan_id'].widget.values = choices
        form = Form(schema, buttons=('simpan', 'kirim', 'batal'))
        
        if request.POST:
            if 'batal' in request.POST:
                return HTTPFound(location=request.route_url('simkel-permohonan-field'))
            try:
                controls = request.POST.items()
                appstruct = form.validate(controls)
                
                if not item: 
                    item = SimkelPermohonanField()
                item.permohonan_id = appstruct['permohonan_id']
                item.nama = appstruct['nama']
                item.value = appstruct['value']
                
                self.session.add(item)
                self.session.flush()
                transaction.commit() 
                
                request.session.flash(f"Data berhasil disimpan.")
                return HTTPFound(location=request.route_url('simkel-permohonan-field'))
            except ValidationFailure as e:
                return dict(title=f"Form {self.title}", form=e.render())

        appstruct = {}
        if item:
            appstruct = {
                'permohonan_id': getattr(item, 'permohonan_id', None),
                'nama': item.nama,
                'value': item.value
            }
        
        return dict(title=f"Form {self.title}", form=form.render(appstruct))


    def view_delete(self):
        request = self.request
        row_id = request.matchdict.get('id')
        item = self.get_row(row_id)
        
        if not item:
            request.session.flash("Data tidak ditemukan.", 'error')
            return HTTPFound(location=request.route_url('simkel-permohonan-field'))

        if hasattr(item, 'status') and str(item.status) in ['0', '2']:
            try:
                self.session.delete(item)
                self.session.flush()
                transaction.commit()
                request.session.flash(f"Data ID {row_id} berhasil dihapus.")
            except Exception as e:
                transaction.abort()
                request.session.flash(f"Gagal menghapus: {str(e)}", 'error')
        else:
            request.session.flash("Data tidak bisa dihapus karena sedang diproses atau sudah selesai.", 'error')
            
        return HTTPFound(location=request.route_url('simkel-permohonan-field'))

    def view_unlocked(self):
        request = self.request
        row_id = request.matchdict.get('id')
        item = self.get_row(row_id)
        
        if item and hasattr(item, 'status') and str(item.status) == '1':
            try:
                item.status = '0'
                self.session.add(item)
                self.session.flush()
                transaction.commit()
                request.session.flash("Data berhasil dibuka kembali (menjadi Draft).")
            except Exception as e:
                transaction.abort()
                request.session.flash(f"Gagal membuka kunci: {str(e)}", 'error')
        else:
            request.session.flash("Data tidak dalam status terkunci.", 'warning')
            
        return HTTPFound(location=request.route_url('simkel-permohonan-field'))