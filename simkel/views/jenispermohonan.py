import colander
import transaction
from deform import widget, Form, ValidationFailure
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import desc, or_
from sqlalchemy.exc import IntegrityError

from opensipkd.base.views import BaseView
from ..models import SimkelDBSession, SimkelJenisPermohonan


class JenisPermohonanSchema(colander.Schema):
    kode = colander.SchemaNode(
        colander.String(),
        title="Kode Layanan",
        validator=colander.Length(max=32),
        widget=widget.TextInputWidget(),
    )
    nama = colander.SchemaNode(
        colander.String(),
        title="Nama Layanan",
        validator=colander.Length(max=128),
        widget=widget.TextInputWidget(),
    )


class Views(BaseView):

    def __init__(self, request):
        super().__init__(request)
        self.request = request
        self.session = SimkelDBSession
        self.title = "Jenis Permohonan"
        self.route = "simkel-jper"
        self.edit_schema = JenisPermohonanSchema
        self.add_schema = JenisPermohonanSchema

    def _redirect(self):
        return HTTPFound(location=self.request.route_url(self.route))

    def _form_ctx(self, form, row, readonly=False):
        return dict(
            title=f"{'Detail' if readonly else 'Form'} {self.title}",
            form=form,
            row=row,
            readonly=readonly,
            table=None,
            scripts="",
            css=[],
            js=[],
        )

    def query_id(self):
        row_id = self.request.matchdict.get("id")
        return self.session.query(SimkelJenisPermohonan).filter_by(id=row_id)

    def view_list(self):
        params = self.request.params
        search = params.get("term") or params.get("search")
        query = self.session.query(SimkelJenisPermohonan)
        if search:
            query = query.filter(
                or_(
                    SimkelJenisPermohonan.kode.ilike(f"%{search}%"),
                    SimkelJenisPermohonan.nama.ilike(f"%{search}%"),
                )
            )
        rows = query.order_by(desc(SimkelJenisPermohonan.id)).all()
        return dict(title=f"Daftar {self.title}", rows=rows, params=params)

    def view_view(self):
        row = self.query_id().first()
        if not row:
            self.request.session.flash("Data tidak ditemukan.", "error")
            return self._redirect()

        form = Form(JenisPermohonanSchema().bind(), buttons=())
        rendered = form.render({"kode": row.kode, "nama": row.nama}, readonly=True)
        return self._form_ctx(rendered, row, readonly=True)

    def view_add(self):
        return self.view_form()

    def view_edit(self):
        return self.view_form()

    def view_form(self):
        request = self.request
        row_id = request.matchdict.get("id")
        item = self.query_id().first() if row_id else SimkelJenisPermohonan()

        if row_id and not item:
            request.session.flash("Data tidak ditemukan.", "error")
            return self._redirect()

        schema = JenisPermohonanSchema().bind()
        form = Form(schema, buttons=("simpan", "batal"))

        if request.POST:
            if "batal" in request.POST:
                return self._redirect()
            try:
                appstruct = form.validate(request.POST.items())
                return self.view_act(item, appstruct)
            except ValidationFailure as e:
                return self._form_ctx(e.render(), item)

        appstruct = {"kode": item.kode or "", "nama": item.nama or ""} if row_id else {}
        return self._form_ctx(form.render(appstruct), item)

    def view_act(self, item, appstruct):
        request = self.request
        is_new = not bool(item.id)

        try:
            kode_upper = appstruct["kode"].strip().upper()
            nama_bersih = appstruct["nama"].strip()

            if not kode_upper or not nama_bersih:
                request.session.flash("Kode dan Nama tidak boleh kosong.", "error")
                form = Form(JenisPermohonanSchema().bind(), buttons=("simpan", "batal"))
                return self._form_ctx(form.render(appstruct), item)

            existing = (
                self.session.query(SimkelJenisPermohonan)
                .filter(
                    SimkelJenisPermohonan.kode == kode_upper,
                    SimkelJenisPermohonan.id != item.id,
                )
                .first()
            )

            if existing:
                request.session.flash("Kode sudah digunakan!", "error")
                form = Form(JenisPermohonanSchema().bind(), buttons=("simpan", "batal"))
                return self._form_ctx(form.render(appstruct), item)

            item.kode = kode_upper
            item.nama = nama_bersih
            self.session.add(item)

            pesan = (
                "Data berhasil ditambahkan." if is_new else "Data berhasil diperbarui."
            )
            request.session.flash(pesan)
            return self._redirect()

        except IntegrityError:
            transaction.abort()
            request.session.flash("Kode sudah ada!", "error")
            return self._redirect()

        except Exception as e:
            transaction.abort()
            request.session.flash(f"Gagal: {str(e)}", "error")
            return self._redirect()

    def view_delete(self):
        request = self.request
        row = self.query_id().first()

        if not row:
            request.session.flash("Data tidak ditemukan.", "warning")
            return self._redirect()

        try:
            nama = row.nama
            self.session.delete(row)
            request.session.flash(f"{nama} berhasil dihapus.")
        except Exception as e:
            transaction.abort()
            request.session.flash(f"Gagal menghapus: {str(e)}", "error")

        return self._redirect()
