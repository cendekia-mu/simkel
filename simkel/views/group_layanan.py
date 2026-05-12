import colander
import transaction
from deform import Form, widget, ValidationFailure
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import desc, or_

from opensipkd.base.views import BaseView
from opensipkd.models import DBSession, Group
from ..models import SimkelDBSession, SimkelGroupLayanan, SimkelJenisPermohonan


@colander.deferred
def jpel_widget(node, kw):
    jpels = kw.get("jpels", [])
    choices = [("", "-- Pilih Jenis Permohonan --")] + [
        (str(j.id), f"{j.kode} - {j.nama}") for j in jpels
    ]
    return widget.SelectWidget(values=choices)


class GroupLayananSchema(colander.Schema):

    group_id = colander.SchemaNode(
        colander.Integer(), title="Group ID", widget=widget.TextInputWidget()
    )

    jpel_id = colander.SchemaNode(
        colander.Integer(), title="Jenis Permohonan", widget=jpel_widget
    )


class Views(BaseView):

    def __init__(self, request):
        super().__init__(request)
        self.request = request
        self.session = SimkelDBSession
        self.title = "Group Layanan"
        self.route = "simkel-group-layanan"

    def _redirect(self):
        return HTTPFound(location=self.request.route_url(self.route))

    def _get_group(self, group_id):
        return DBSession.query(Group).filter_by(id=group_id).first()

    def _get_jpel(self, jpel_id):
        return self.session.query(SimkelJenisPermohonan).filter_by(id=jpel_id).first()

    def _get_jpels(self):
        return (
            self.session.query(SimkelJenisPermohonan)
            .order_by(SimkelJenisPermohonan.kode)
            .all()
        )

    def _schema_bind(self):
        return GroupLayananSchema().bind(jpels=self._get_jpels())

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
        return self.session.query(SimkelGroupLayanan).filter_by(id=row_id)

    def view_list(self):
        search = self.request.params.get("term") or self.request.params.get("search")

        query = self.session.query(SimkelGroupLayanan)

        if search:
            try:
                search_int = int(search)
                query = query.filter(
                    or_(
                        SimkelGroupLayanan.group_id == search_int,
                        SimkelGroupLayanan.jpel_id == search_int,
                    )
                )
            except ValueError:
                pass

        rows = query.order_by(desc(SimkelGroupLayanan.id)).all()

        for row in rows:
            group = self._get_group(row.group_id)
            jpel = self._get_jpel(row.jpel_id)
            row.nama = f"{group.description if group else row.group_id} → {jpel.nama if jpel else row.jpel_id}"
            row.kode = f"G:{row.group_id} / J:{row.jpel_id}"
            row.status = 0

        return dict(title=f"Daftar {self.title}", rows=rows, params=self.request.params)

    def view_view(self):
        row = self.query_id().first()

        if not row:
            return self._redirect()

        group = self._get_group(row.group_id)
        jpel = self._get_jpel(row.jpel_id)

        form = Form(self._schema_bind(), buttons=())
        rendered = form.render(
            {
                "group_id": row.group_id,
                "jpel_id": row.jpel_id,
            },
            readonly=True,
        )

        return dict(
            **self._form_ctx(rendered, row, readonly=True),
            group_name=group.description if group else "-",
            jpel_nama=jpel.nama if jpel else "-",
        )

    def view_add(self):
        return self.view_form()

    def view_edit(self):
        return self.view_form()

    def view_form(self):
        request = self.request
        row_id = request.matchdict.get("id")
        item = self.query_id().first() if row_id else SimkelGroupLayanan()

        if row_id and not item:
            return self._redirect()

        schema = self._schema_bind()
        form = Form(schema, buttons=("simpan", "batal"))

        if request.POST:
            if "batal" in request.POST:
                return self._redirect()

            try:
                appstruct = form.validate(request.POST.items())
                return self.view_act(item, appstruct)

            except ValidationFailure as e:
                return self._form_ctx(e.render(), item)

        appstruct = (
            {"group_id": item.group_id or "", "jpel_id": item.jpel_id or ""}
            if row_id
            else {}
        )

        return self._form_ctx(form.render(appstruct), item)

    def view_act(self, item, appstruct):
        try:
            # Validasi Group
            group = self._get_group(appstruct["group_id"])
            if not group:
                form = Form(self._schema_bind(), buttons=("simpan", "batal"))
                return self._form_ctx(form.render(appstruct), item)

            # Validasi Jenis Permohonan
            jpel = self._get_jpel(appstruct["jpel_id"])
            if not jpel:
                form = Form(self._schema_bind(), buttons=("simpan", "batal"))
                return self._form_ctx(form.render(appstruct), item)

            # Cek duplikasi
            duplikat = (
                self.session.query(SimkelGroupLayanan)
                .filter(
                    SimkelGroupLayanan.group_id == appstruct["group_id"],
                    SimkelGroupLayanan.jpel_id == appstruct["jpel_id"],
                    SimkelGroupLayanan.id != item.id,
                )
                .first()
            )

            if duplikat:
                form = Form(self._schema_bind(), buttons=("simpan", "batal"))
                return self._form_ctx(form.render(appstruct), item)

            item.group_id = appstruct["group_id"]
            item.jpel_id = appstruct["jpel_id"]

            self.session.add(item)
            return self._redirect()

        except Exception:
            transaction.abort()
            return self._redirect()

    def view_delete(self):
        row = self.query_id().first()

        if not row:
            return self._redirect()

        try:
            self.session.delete(row)
        except Exception:
            transaction.abort()

        return self._redirect()
