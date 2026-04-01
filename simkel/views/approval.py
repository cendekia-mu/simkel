import logging
import transaction
import colander
from datetime import datetime
from sqlalchemy import desc, or_
from pyramid.httpexceptions import HTTPFound
from deform import widget, Form, ValidationFailure

from opensipkd.base.views import BaseView 
from ..models import SimkelDBSession
from ..models.permohonan import SimkelPermohonan
from ..models.jenispermohonan import SimkelJenisPermohonan

log = logging.getLogger(__name__)

class ApprovalSchema(colander.Schema):
    nama = colander.SchemaNode(
        colander.String(), 
        title="Nama Pemohon", 
        missing=None,
        widget=widget.TextInputWidget(readonly=True))
    
    nomor_permohonan = colander.SchemaNode(
        colander.String(), 
        title="Nomor Permohonan", 
        missing=None,
        widget=widget.TextInputWidget(readonly=True))
    
    catatan = colander.SchemaNode(
        colander.String(), 
        title="Catatan Verifikasi/Revisi",
        missing=None,
        widget=widget.TextAreaWidget(rows=3))

class Views(BaseView):
    def __init__(self, request):
        super().__init__(request)
        self.request = request
        self.session = SimkelDBSession()
        self.title = "Verifikasi & Approval"
        self.list_route = 'simkel-approval'
        self.route = 'simkel-approval'
        self.table = SimkelPermohonan 
        self.list_schema = ApprovalSchema 
        self.edit_schema = ApprovalSchema
        self.allow_add = False
        self.allow_edit = True
        self.allow_delete = False

    def query_id(self):
        row_id = self.request.matchdict.get('id')
        return self.session.query(SimkelPermohonan).filter_by(id=row_id)

    def get_values(self, row):
        return {c.name: getattr(row, c.name) for c in row.__table__.columns}

    def get_item_table(self, parent):
        return None

    def view_list(self):
        user = self.request.user
        params = self.request.params
        query = self.session.query(SimkelPermohonan).filter(SimkelPermohonan.status == 1)
        
        if hasattr(user, 'kelurahan_id') and user.kelurahan_id:
            query = query.filter(SimkelPermohonan.kelurahan_id == user.kelurahan_id)
        
        jpel_id = params.get('jpel_id')
        if jpel_id and jpel_id.isdigit():
            query = query.filter(SimkelPermohonan.jpel_id == int(jpel_id))
            
        search = params.get('term') or params.get('search')
        if search:
            query = query.filter(or_(
                SimkelPermohonan.nama.ilike(f'%{search}%'),
                SimkelPermohonan.nomor_permohonan.ilike(f'%{search}%')
            ))
            
        rows = query.order_by(desc(SimkelPermohonan.id)).all()
        jpel_list = [(p.id, p.nama) for p in self.session.query(SimkelJenisPermohonan).all()]
        
        return dict(
            title=self.title,
            rows=rows,
            jpel_list=jpel_list,
            params=params
        )

    def view_view(self):
        row = self.query_id().first()
        res = super().view_view()
        if isinstance(res, dict):
            res['title'] = self.title
            res['row'] = row
        return res

    def next_view(self, form=None, row=None):
        if not self.request.POST:
            return None
            
        btn_approve = 'approve' in self.request.POST
        btn_reject = 'reject' in self.request.POST
        catatan = self.request.params.get('catatan', '')

        try:
            if btn_approve:
                is_tahap_akhir = False 
                if is_tahap_akhir:
                    row.status = 3
                    self.request.session.flash("Berkas disetujui dan TTE berhasil.")
                else:
                    row.status = 1 
                    self.request.session.flash("Verifikasi berhasil, diteruskan ke tahap selanjutnya.")
            
            elif btn_reject:
                if not catatan:
                    self.request.session.flash("Catatan wajib diisi untuk penolakan.", 'error')
                    return None
                row.status = 4 
                self.request.session.flash("Berkas telah ditolak.")

            self.session.flush()
            transaction.commit()
            return HTTPFound(location=self.request.route_url(self.list_route))
            
        except Exception as e:
            transaction.abort()
            self.request.session.flash(f"Error: {str(e)}", 'error')
            return None