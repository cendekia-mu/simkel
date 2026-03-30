import colander
import transaction
from datetime import datetime
from deform import widget, Form, ValidationFailure
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import desc, or_
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
        query = self.session.query(SimkelPermohonanField).filter(
            or_(
                SimkelPermohonanField.status == 0, 
                SimkelPermohonanField.status == 2,
                SimkelPermohonanField.status == None
            )
        ).order_by(desc(SimkelPermohonanField.id))
        
        return dict(title="Daftar Permohonan Saya", rows=query.all())

    def view_view(self):
        item = self.get_row(self.request.matchdict.get('id'))
        if not item:
            self.request.session.flash("Data tidak ditemukan.", 'error')
            return HTTPFound(location=self.request.route_url('simkel-permohonan-field'))
        return dict(title="Detail Permohonan Field", row=item)

    def view_form(self):
        request = self.request
        row_id = request.matchdict.get('id')
        item = self.get_row(row_id) if row_id else SimkelPermohonanField()

        if row_id and item.status in [1, 3]:
            request.session.flash("Data sudah dikunci atau disetujui, tidak dapat diubah.", 'warning')
            return HTTPFound(location=request.route_url('simkel-permohonan-field'))

        p_query = self.session.query(SimkelPermohonan).all()
        choices = [('', '-- Pilih --')] + [(p.id, f"{p.nomor or p.id}") for p in p_query]
        
        schema = FieldSchema().bind()
        schema['permohonan_id'].widget.values = choices
        form = Form(schema, buttons=('simpan', 'kirim', 'batal'))
        
        if request.POST:
            if 'batal' in request.POST:
                return HTTPFound(location=request.route_url('simkel-permohonan-field'))
            
            try:
                controls = request.POST.items()
                appstruct = form.validate(controls)
                
                item.permohonan_id = appstruct['permohonan_id']
                item.nama = appstruct['nama']
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
            appstruct = {'permohonan_id': item.permohonan_id, 'nama': item.nama, 'value': item.value}
        
        return dict(title=f"Form {self.title}", form=form.render(appstruct))

    def view_send(self):
        request = self.request
        item = self.get_row(request.matchdict.get('id'))
        if item and item.status in [0, 2, None]:
            try:
                item_id = item.id 
                item.status = 1
                item.updated = datetime.now()
                self.session.add(item)
                self.session.flush()
                transaction.commit()
                request.session.flash(f"Data ID {item_id} berhasil dikirim.")
            except Exception as e:
                transaction.abort()
                request.session.flash(f"Gagal mengirim: {str(e)}", 'error')
        return HTTPFound(location=request.route_url('simkel-permohonan-field'))

    def view_print(self):
        request = self.request
        item = self.get_row(request.matchdict.get('id'))
        
        if not item:
            request.session.flash("Data tidak ditemukan.", 'error')
            return HTTPFound(location=request.route_url('simkel-permohonan-field'))
            
        if item.status != 3:
            request.session.flash("Cetak hanya tersedia untuk permohonan yang sudah disetujui.", 'warning')
            return HTTPFound(location=request.route_url('simkel-permohonan-field'))

        return dict(title="Cetak Permohonan", row=item)

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