import transaction
from datetime import datetime, time
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import desc, asc, or_, cast, Date
from ..models import SimkelDBSession, SimkelPermohonanField, SimkelLogApproval
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
        params = self.request.params
        search = params.get('search')
        status_filter = params.get('status')
        sort_option = params.get('sort')
        limit = int(params.get('limit', 25))
        
        query = self.session.query(SimkelPermohonanField)

        if status_filter and status_filter.strip() != "":
            query = query.filter(SimkelPermohonanField.status == int(status_filter))
        else:
            query = query.filter(SimkelPermohonanField.status.in_([1, 3]))

        if search:
            query = query.filter(
                or_(
                    SimkelPermohonanField.nama.ilike(f'%{search}%'),
                    SimkelPermohonanField.kode.ilike(f'%{search}%')
                )
            )

        if sort_option == 'id_asc':
            query = query.order_by(asc(SimkelPermohonanField.created))
        elif sort_option == 'nama_asc':
            query = query.order_by(asc(SimkelPermohonanField.nama))
        elif sort_option == 'nama_desc':
            query = query.order_by(desc(SimkelPermohonanField.nama))
        else:
            query = query.order_by(desc(SimkelPermohonanField.created))

        rows = query.limit(limit).all()
        
        return dict(
            title=f"Daftar {self.title}", 
            rows=rows,
            params=params
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
            try:
                item.status = 3 
                item.updated = datetime.now()
                self.session.add(item)

                log = SimkelLogApproval()
                log.id_permohonan = item.id
                log.status = 3
                log.create_uid = request.user.id if hasattr(request, 'user') and request.user else None
                self.session.add(log)
                
                self.session.flush()
                transaction.commit()
                
                request.session.flash(f"ID {item.id}: Permohonan Berhasil DISETUJUI.")
            except Exception as e:
                transaction.abort()
                request.session.flash(f"Gagal Approve: {str(e)}", 'error')
        
        return HTTPFound(location=request.route_url('simkel-approval'))

    def view_reject(self):
        request = self.request
        item = self.get_row(request.matchdict.get('id'))

        if item and item.status == 1:
            try:
                item.status = 2
                item.updated = datetime.now()
                self.session.add(item)

                log = SimkelLogApproval()
                log.id_permohonan = item.id
                log.status = 2
                log.create_uid = request.user.id if hasattr(request, 'user') and request.user else None
                self.session.add(log)
                
                self.session.flush()
                transaction.commit()
                
                request.session.flash(f"ID {item.id}: Permohonan DITOLAK.")
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
            
        if item.status not in [1, 3]:
            request.session.flash("Cetak hanya tersedia untuk permohonan aktif.", 'warning')
            return HTTPFound(location=request.route_url('simkel-approval'))

        return dict(title="Cetak Arsip Approval", row=item)