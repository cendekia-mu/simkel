import os
import json
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
from ..models.permohonan_field import SimkelPermohonanField
from ..models import SimkelLogApproval

log = logging.getLogger(__name__)


def is_admin(group_names):
    return 'admin' in group_names or 'Superuser' in group_names


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

        if is_admin(group_names):
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

    def get_list_jenis(self):
        return self.session.query(SimkelJenisPermohonan).all()

    def _get_additional(self, row):
        """Ambil data additional yang diisi warga."""
        if not row.additional:
            return {}
        try:
            return json.loads(row.additional) if isinstance(row.additional, str) else row.additional
        except Exception:
            return {}

    def _get_fields(self, jenis_id):
        """Ambil field dinamis sesuai jenis permohonan."""
        if not jenis_id:
            return []
        return self.session.query(SimkelPermohonanField).filter_by(
            jpel_id=jenis_id
        ).order_by(SimkelPermohonanField.id).all()

    def view_list(self):
        res = super().view_list()
        user = self.request.user
        group_names = [g.group_name for g in user.groups]
        query = self.session.query(SimkelPermohonan)

        if is_admin(group_names):
            pass
        elif 'pejabat' in group_names:
            query = query.filter(SimkelPermohonan.status == 3)
        elif 'petugas' in group_names:
            query = query.filter(SimkelPermohonan.status == 1)
        else:
            return HTTPFound(location=self.request.route_url('simkel-home'))

        rows = query.order_by(desc(SimkelPermohonan.id)).all()
        list_jenis = self.get_list_jenis()
        jpel_dict = {p.id: p.nama for p in list_jenis}

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

        list_jenis = self.get_list_jenis()
        user = self.request.user

        if not user:
            return HTTPFound(location=self.request.route_url('simkel-home'))

        group_names = [g.group_name for g in user.groups]

        if ('petugas' in group_names and row.status == 1) or \
           ('pejabat' in group_names and row.status == 3) or \
           is_admin(group_names):
            buttons = ('approve', 'reject', 'batal')
        else:
            buttons = ('batal',)

        schema = ApprovalSchema()
        form = Form(schema, buttons=buttons)

        additional_fields = self._get_fields(row.jenis_id)
        additional_data   = self._get_additional(row)

        if self.request.POST:
            if 'batal' in self.request.POST:
                return HTTPFound(location=self.request.route_url(self.list_route))
            try:
                controls = self.request.POST.items()
                appstruct = form.validate(controls)
                return self.view_act(row, appstruct)
            except ValidationFailure as e:
                return dict(
                    form=e.render(),
                    row=row,
                    title=self.title,
                    list_jenis=list_jenis,
                    additional_fields=additional_fields,
                    additional_data=additional_data,
                )

        jpel = self.session.query(SimkelJenisPermohonan).filter_by(id=row.jenis_id).first()
        appstruct = {
            'nama'   : str(jpel.nama) if jpel else '-',
            'catatan': str(row.reason) if row.reason else '',
        }

        return dict(
            form=form.render(appstruct),
            row=row,
            title=self.title,
            list_jenis=list_jenis,
            additional_fields=additional_fields,
            additional_data=additional_data,
        )

    def returned_form(self, form, **kwargs):
        kwargs.setdefault("title", self.title)
        kwargs.setdefault("row", self.query_id().first())
        kwargs.setdefault("list_jenis", self.get_list_jenis())
        kwargs.setdefault("additional_fields", [])
        kwargs.setdefault("additional_data", {})
        return super().returned_form(form, **kwargs)

    def view_act(self, row, appstruct):
        user = self.request.user
        if not user:
            self.request.session.flash("Sesi tidak valid, silakan login kembali.", 'error')
            return HTTPFound(location=self.request.route_url('simkel-home'))

        group_names = [g.group_name for g in user.groups]
        catatan = appstruct.get('catatan', '').strip()

        try:
            if 'approve' in self.request.POST:
                if 'petugas' in group_names:
                    if row.status != 1:
                        raise Exception("Status tidak valid untuk diverifikasi petugas.")
                    row.status = 3
                    pesan = "Petugas: Verifikasi disetujui, diteruskan ke pejabat."

                elif 'pejabat' in group_names:
                    if row.status != 3:
                        raise Exception("Status tidak valid untuk disetujui pejabat.")
                    if not self.trigger_tte(row):
                        raise Exception("Proses TTE gagal, approval dibatalkan.")
                    row.status = 4
                    pesan = "Pejabat: Approval final & TTE sukses."

                elif is_admin(group_names):
                    if row.status == 1:
                        row.status = 3
                    elif row.status == 3:
                        row.status = 4
                    else:
                        raise Exception(f"Status {row.status} tidak bisa di-approve.")
                    pesan = f"Admin: Status diperbarui ke {row.status}."

                else:
                    raise Exception("Akun Anda tidak memiliki izin untuk melakukan approval.")

            elif 'reject' in self.request.POST:
                if not catatan:
                    raise Exception("Catatan/alasan penolakan wajib diisi.")
                row.status = -1
                row.reason = catatan
                pesan = f"Ditolak oleh {user.user_name}: {catatan}"

            else:
                return HTTPFound(location=self.request.route_url(self.list_route))

            self.session.add(row)
            self.session.flush()

            self.session.execute(insert(SimkelLogApproval).values(
                id_permohonan=row.id,
                status=row.status,
            ))

            transaction.commit()
            log.info(pesan)
            self.request.session.flash(pesan, 'success')
            return HTTPFound(location=self.request.route_url(self.list_route))

        except Exception as e:
            transaction.abort()
            log.error(f"Approval error: {str(e)}")
            self.request.session.flash(f"Error: {str(e)}", 'error')
            return HTTPFound(location=self.request.route_url(self.list_route))

    def trigger_tte(self, row):
        return True

    def view_preview(self):
        row = self.query_id().first()
        if not row:
            self.request.session.flash("Data tidak ditemukan.", 'error')
            return HTTPFound(location=self.request.route_url(self.list_route))

        file_path = getattr(row, 'file_path', None)
        if not file_path:
            self.request.session.flash("File tidak tersedia.", 'error')
            return HTTPFound(location=self.request.route_url(self.list_route))

        if not file_path.lower().endswith('.pdf'):
            self.request.session.flash("File bukan PDF.", 'error')
            return HTTPFound(location=self.request.route_url(self.list_route))

        if not os.path.exists(file_path):
            self.request.session.flash("File tidak ditemukan di server.", 'error')
            return HTTPFound(location=self.request.route_url(self.list_route))

        return FileResponse(file_path, request=self.request, content_type='application/pdf')