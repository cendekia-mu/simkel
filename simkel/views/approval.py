import os
import logging
import transaction
import colander
from sqlalchemy import desc, insert
from pyramid.httpexceptions import HTTPFound
from pyramid.response import FileResponse
from deform import widget, Form, ValidationFailure

from opensipkd.base.views import BaseView
from ..models import SimkelDBSession
from ..models.permohonan import SimkelPermohonan
from ..models.jenispermohonan import SimkelJenisPermohonan
from ..models import SimkelLogApproval

log = logging.getLogger(__name__)

# Status permohonan (sesuai SimkelLogApproval.status_text):
# 0  = Draft
# 1  = Dikirim / Menunggu Verifikasi Petugas
# 2  = Perbaikan / Dikembalikan
# 3  = Disetujui Petugas / Proses SK (menunggu pejabat)
# 4  = Selesai / SK Terbit
# -1 = Dibatalkan / Ditolak


class ApprovalSchema(colander.Schema):
    nama = colander.SchemaNode(
        colander.String(),
        title="Jenis Permohonan",
        missing=colander.drop,
        widget=widget.TextInputWidget(readonly=True))

    catatan = colander.SchemaNode(
        colander.String(),
        title="Catatan / Alasan Penolakan",
        missing=colander.drop,
        widget=widget.TextAreaWidget(rows=3))


class Views(BaseView):
    def __init__(self, request):
        super().__init__(request)
        self.request = request
        self.session = SimkelDBSession()
        self.request.title = "Verifikasi & Approval"
        self.title = self.request.title
        self.list_route = 'simkel-approval'
        self.route = 'simkel-approval'
        self.table = SimkelPermohonan
        self.list_schema = ApprovalSchema
        self.edit_schema = ApprovalSchema
        self.add_schema  = ApprovalSchema

        user = self.request.user
        group_names = [g.group_name for g in user.groups] if user else []

        if 'admin' in group_names:
            self.allow_add = True
            self.allow_edit = True
            self.allow_delete = True
        else:
            self.allow_add = False
            self.allow_edit = True
            self.allow_delete = False

    def query_id(self):
        row_id = self.request.matchdict.get('id')
        return self.session.query(SimkelPermohonan).filter_by(id=row_id)

    def view_list(self):
        res = super().view_list()
        user = self.request.user
        group_names = [g.group_name for g in user.groups]
        query = self.session.query(SimkelPermohonan)

        if 'admin' in group_names:
            pass
        elif 'pejabat' in group_names:
            query = query.filter(SimkelPermohonan.status == 3)
        elif 'petugas' in group_names:
            query = query.filter(SimkelPermohonan.status == 1)
        else:
            return HTTPFound(location=self.request.route_url('home'))

        rows = query.order_by(desc(SimkelPermohonan.id)).all()
        jpel_dict = {p.id: p.nama for p in self.session.query(SimkelJenisPermohonan).all()}

        for r in rows:
            r.nama = jpel_dict.get(r.jenis_id, '-')
            r.status_edit = self.allow_edit
            r.status_delete = self.allow_delete

        res.update(dict(rows=rows, title=self.title))
        return res

    def view_view(self):
        return self.view_form()

    def view_form(self):
        row = self.query_id().first()
        if not row:
            return HTTPFound(location=self.request.route_url(self.list_route))

        user = self.request.user
        group_names = [g.group_name for g in user.groups] if user else []

        if 'petugas' in group_names and row.status == 1:
            buttons = ('approve', 'reject', 'batal')
        elif 'pejabat' in group_names and row.status == 3:
            buttons = ('approve', 'reject', 'batal')
        elif 'admin' in group_names:
            buttons = ('approve', 'reject', 'batal')
        else:
            buttons = ('batal',)

        schema = ApprovalSchema()
        form = Form(schema, buttons=buttons)

        if self.request.POST:
            if 'batal' in self.request.POST:
                return HTTPFound(location=self.request.route_url(self.list_route))
            try:
                controls = self.request.POST.items()
                appstruct = form.validate(controls)
                return self.view_act(row, appstruct)
            except ValidationFailure as e:
                return dict(form=e.render(), row=row, title=self.title)

        jpel = self.session.query(SimkelJenisPermohonan).filter_by(id=row.jenis_id).first()
        appstruct = {
            'nama': str(jpel.nama) if jpel else '-',
            'catatan': str(row.reason) if row.reason else ''
        }

        return dict(form=form.render(appstruct), row=row, title=self.title)

    def returned_form(self, form, **kwargs):
        kwargs.setdefault("title", self.title)
        kwargs.setdefault("row", self.query_id().first())
        return super().returned_form(form, **kwargs)

    def view_act(self, row, appstruct):
        user = self.request.user
        if not user:
            self.request.session.flash("Sesi tidak valid, silakan login kembali.", 'error')
            return HTTPFound(location=self.request.route_url('home'))

        group_names = [g.group_name for g in user.groups]
        catatan = appstruct.get('catatan', '')

        try:
            if 'approve' in self.request.POST:
                if 'petugas' in group_names:
                    row.status = 3
                    pesan = "Petugas: Verifikasi disetujui, diteruskan ke pejabat."
                elif 'pejabat' in group_names:
                    tte_sukses = self.trigger_tte(row)
                    if not tte_sukses:
                        raise Exception("Proses TTE gagal, approval dibatalkan.")
                    row.status = 4
                    pesan = "Pejabat: Approval final & TTE sukses."
                elif 'admin' in group_names:
                    if row.status == 1:
                        row.status = 3
                    elif row.status == 3:
                        row.status = 4
                    pesan = f"Admin: Status diperbarui ke {row.status}"
                else:
                    raise Exception("Grup user tidak memiliki izin untuk approve.")

            elif 'reject' in self.request.POST:
                row.status = -1
                row.reason = catatan
                pesan = f"Ditolak oleh {user.user_name}: {catatan}"

            else:
                return HTTPFound(location=self.request.route_url(self.list_route))

            self.session.add(row)
            self.session.flush()

            self.session.execute(insert(SimkelLogApproval).values(
                id_permohonan=row.id,
                status=row.status
            ))

            transaction.commit()
            log.info(pesan)
            self.request.session.flash(pesan)
            return HTTPFound(location=self.request.route_url(self.list_route))

        except Exception as e:
            transaction.abort()
            log.error(f"Approval error: {str(e)}")
            self.request.session.flash(f"Error: {str(e)}", 'error')
            return HTTPFound(location=self.request.route_url(self.list_route))

    def trigger_tte(self, row):
        # TODO: Implementasi integrasi TTE di sini
        # Return True jika sukses, False jika gagal
        return True

    def view_preview(self):
        row = self.query_id().first()
        if row and row.file_path:
            if not row.file_path.lower().endswith('.pdf'):
                self.request.session.flash("File bukan PDF.", 'error')
                return HTTPFound(location=self.request.route_url(self.list_route))
            if os.path.exists(row.file_path):
                return FileResponse(row.file_path, request=self.request, content_type='application/pdf')
        return HTTPFound(location=self.request.route_url(self.list_route))