import transaction
from datetime import datetime
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import desc, or_
from ..models import SimkelDBSession, SimkelPermohonanField 
from opensipkd.base.views import BaseView

class ApprovalView(BaseView):
    def __init__(self, request):
        super().__init__(request)
        self.request = request
        self.session = SimkelDBSession
        self.title = "Verifikasi & Approval"

    def get_row(self, row_id):
        return self.session.query(SimkelPermohonanField).filter_by(id=row_id).first()

    def view_list(self):
        query = self.session.query(SimkelPermohonanField).filter(
            or_(
                SimkelPermohonanField.status == 1,
                SimkelPermohonanField.status == 3
            )
        ).order_by(desc(SimkelPermohonanField.id))
        
        return dict(
            title=f"Daftar {self.title}", 
            rows=query.all()
        )
    
    def view_view(self):
        item = self.get_row(self.request.matchdict.get('id'))
        if not item:
            self.request.session.flash("Data tidak ditemukan.", 'error')
            return HTTPFound(location=self.request.route_url('simkel-approval'))
        
        return dict(
            title="Review Detail Permohonan",
            row=item,
            form='', 
            readonly=True
        )
    
    def view_approve(self):
        request = self.request
        item = self.get_row(request.matchdict.get('id'))

        if item and item.status == 1:
            item_id = item.id 
            try:
                item.status = 3 
                item.updated = datetime.now()
                
                self.session.add(item)
                self.session.flush()
                transaction.commit()
                
                request.session.flash(f"ID {item_id}: Permohonan Berhasil DISETUJUI.")
            except Exception as e:
                transaction.abort()
                request.session.flash(f"Gagal Approve: {str(e)}", 'error')
        
        return HTTPFound(location=request.route_url('simkel-approval'))

    def view_reject(self):
        request = self.request
        item = self.get_row(request.matchdict.get('id'))

        if item and item.status == 1:
            item_id = item.id
            try:
                item.status = 2
                item.updated = datetime.now()
                
                self.session.add(item)
                self.session.flush()
                transaction.commit()
                
                request.session.flash(f"ID {item_id}: Permohonan DITOLAK & Dikembalikan ke Pemohon.")
            except Exception as e:
                transaction.abort()
                request.session.flash(f"Gagal Reject: {str(e)}", 'error')
            
        return HTTPFound(location=request.route_url('simkel-approval'))

    def view_print(self):
        request = self.request
        item = self.get_row(request.matchdict.get('id'))
        
        if not item:
            request.session.flash("Data tidak ditemukan.", 'error')
            return HTTPFound(location=request.route_url('simkel-approval'))
            
        if item.status != 3:
            request.session.flash("Cetak hanya tersedia untuk permohonan yang sudah disetujui.", 'warning')
            return HTTPFound(location=request.route_url('simkel-approval'))

        return dict(title="Cetak Arsip Approval", row=item)