import colander
import transaction
from datetime import datetime
from deform import widget, Form, ValidationFailure
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import desc
from ..models import SimkelDBSession, PermohonanModel, PermohonanFieldsModel
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
        return self.session.query(PermohonanFieldsModel).filter_by(id=row_id).first()

    def view_list(self):
        query = self.session.query(PermohonanFieldsModel).filter(
            PermohonanFieldsModel.status.in_(['0', '2'])
        ).order_by(desc(PermohonanFieldsModel.id))
        
        rows = query.all()
        return dict(title="Daftar Permohonan Field", rows=rows)

    def view_form(self):
        request = self.request
        row_id = request.matchdict.get('id')
        item = self.get_row(row_id) if row_id else None

        # Data hanya bisa diedit jika status Draft (0) atau Ditolak (2)
        if item and str(item.status) not in ['0', '2']:
            request.session.flash("Data sudah dikunci (Proses/Selesai)!", 'error')
            return HTTPFound(location=request.route_url('simkel-permohonan-field'))

        p_query = self.session.query(PermohonanModel).all()
        choices = [('', '-- Pilih Permohonan --')] + [(p.id, f"{p.nomor or p.id}") for p in p_query]
        
        schema = FieldSchema().bind()
        schema['permohonan_id'].widget.values = choices
        form = Form(schema, buttons=('simpan', 'kirim', 'batal'))
        
        if request.POST:
            if 'batal' in request.POST:
                return HTTPFound(location=request.route_url('simkel-permohonan-field'))
            try:
                appstruct = form.validate(request.POST.items())
                if not item: 
                    item = PermohonanFieldsModel()
                
                item.jpel_id = appstruct['permohonan_id']
                item.nama = appstruct['nama']
                item.value = appstruct['value']
                # Status '1' jika klik kirim, '0' jika klik simpan biasa
                item.status = '1' if 'kirim' in request.POST else '0'
                
                self.session.add(item)
                self.session.flush()
                transaction.commit() 
                
                request.session.flash(f"Data berhasil disimpan.")
                return HTTPFound(location=request.route_url('simkel-permohonan-field'))
            except ValidationFailure as e:
                return dict(title=f"Form {self.title}", form=e.render())
        
        appstruct = {'permohonan_id': item.jpel_id, 'nama': item.nama, 'value': item.value} if item else {}
        return dict(title=f"Form {self.title}", form=form.render(appstruct))

    def view_delete(self):
        """ Fungsi untuk menghapus data """
        request = self.request
        row_id = request.matchdict.get('id')
        item = self.get_row(row_id)
        
        if not item:
            request.session.flash("Data tidak ditemukan.", 'error')
            return HTTPFound(location=request.route_url('simkel-permohonan-field'))

        # Syarat hapus: Status harus Draft ('0') atau Ditolak ('2')
        if str(item.status) in ['0', '2']:
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
        if item and str(item.status) == '1':
            item.status = '0'
            self.session.add(item)
            self.session.flush()
            transaction.commit()
            request.session.flash("Data dikembalikan ke Draft.")
        return HTTPFound(location=request.route_url('simkel-permohonan-field'))