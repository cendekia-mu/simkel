import transaction
from datetime import datetime
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import desc
from ..models import SimkelDBSession, PermohonanFieldsModel
from opensipkd.base.views import BaseView

class ApprovalView(BaseView):
    def __init__(self, request):
        super().__init__(request)
        self.request = request
        self.session = SimkelDBSession

    def get_row(self, row_id):
        return self.session.query(PermohonanFieldsModel).filter_by(id=row_id).first()

    def view_list(self):
        # Filter: Ambil status '1' (Proses) DAN '3' (Selesai/Approve)
        # Agar data yang sudah di-approve tidak hilang dari tabel ini
        query = self.session.query(PermohonanFieldsModel).filter(
            PermohonanFieldsModel.status.in_(['1', 1, '3', 3])
        ).order_by(desc(PermohonanFieldsModel.id))
        
        rows = query.all()
        
        # Log untuk cek di terminal
        print(f"DEBUG: Menampilkan {len(rows)} data (Proses & Selesai)")
        
        return dict(
            title="DAFTAR APPROVAL & RIWAYAT",
            rows=rows
        )

    def view_approve(self):
        request = self.request
        row_id = request.matchdict.get('id')
        item = self.get_row(row_id)

        # Pastikan statusnya '1' sebelum di-approve
        if item and str(item.status) == '1':
            try:
                item.status = '3'  # Ubah ke Selesai
                self.session.add(item)
                self.session.flush()
                transaction.commit()
                request.session.flash(f"Data ID {row_id} Berhasil Disetujui.")
            except Exception as e:
                transaction.abort()
                request.session.flash(f"Error: {str(e)}", 'error')
        
        return HTTPFound(location=request.route_url('simkel-approval'))

    def view_reject(self):
        request = self.request
        row_id = request.matchdict.get('id')
        item = self.get_row(row_id)

        # Pastikan statusnya '1' sebelum di-reject
        if item and str(item.status) == '1':
            try:
                item.status = '2'  # Ubah ke Ditolak
                self.session.add(item)
                self.session.flush()
                transaction.commit()
                request.session.flash(f"Data ID {row_id} Telah Ditolak.")
            except Exception as e:
                transaction.abort()
                request.session.flash(f"Error: {str(e)}", 'error')
            
        return HTTPFound(location=request.route_url('simkel-approval'))