import colander
import transaction
from deform import Form, widget, ValidationFailure
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from sqlalchemy import desc, or_, cast, String
import csv
import io

from opensipkd.base.views import BaseView
from ..models import SimkelDBSession, SimkelGroupLevel

LEVEL_CHOICES = [
    ("", "-- Pilih Level --"),
    ("0", "Super User/Admin"),
    ("1", "Guest/Warga"),
    ("2", "Petugas"),
    ("3", "Pejabat"),
]


class GroupLevelSchema(colander.Schema):

    level_id = colander.SchemaNode(
        colander.Integer(),
        title="Level Jabatan",
        missing=colander.null,
        widget=widget.SelectWidget(values=LEVEL_CHOICES),
    )

    input_level = colander.SchemaNode(
        colander.Integer(),
        title="Level Minimal Input",
        missing=colander.null,
        validator=colander.Range(min=0, max=3),
        widget=widget.TextInputWidget(
            attributes={"type": "number", "min": "0", "max": "3"}
        ),
    )


class Views(BaseView):

    def __init__(self, request):
        super().__init__(request)
        self.request = request
        self.session = SimkelDBSession
        self.title = "Group Level"
        self.route = "simkel-group-level"

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
        return self.session.query(SimkelGroupLevel).filter_by(id=row_id)

    def view_list(self):
        search = self.request.params.get("term") or self.request.params.get("search")

        query = self.session.query(SimkelGroupLevel)

        if search:
            query = query.filter(
                or_(
                    cast(SimkelGroupLevel.level_id, String).ilike(f"%{search}%"),
                    cast(SimkelGroupLevel.input_level, String).ilike(f"%{search}%"),
                )
            )

        rows = query.order_by(desc(SimkelGroupLevel.id)).all()

        for row in rows:
            row.nama = row.level_name
            row.kode = f"Input Level: {row.input_level}"
            row.status = 0

        return dict(title=f"Daftar {self.title}", rows=rows, params=self.request.params)

    def view_view(self):
        row = self.query_id().first()

        if not row:
            return self._redirect()

        form = Form(GroupLevelSchema().bind(), buttons=())
        rendered = form.render(
            {
                "level_id": row.level_id if row.level_id is not None else colander.null,
                "input_level": (
                    row.input_level if row.input_level is not None else colander.null
                ),
            },
            readonly=True,
        )

        return self._form_ctx(rendered, row, readonly=True)

    def view_add(self):
        return self.view_form()

    def view_edit(self):
        return self.view_form()

    def view_form(self):
        request = self.request
        row_id = request.matchdict.get("id")
        item = self.query_id().first() if row_id else SimkelGroupLevel()

        if row_id and not item:
            return self._redirect()

        schema = GroupLevelSchema().bind()
        form = Form(schema, buttons=("simpan", "batal"))

        if request.POST:
            if "batal" in request.POST:
                return self._redirect()

            try:
                appstruct = form.validate(request.POST.items())
                return self.view_act(item, appstruct)

            except ValidationFailure as e:
                return self._form_ctx(e.render(), item)

        if row_id:
            appstruct = {
                "level_id": (
                    item.level_id if item.level_id is not None else colander.null
                ),
                "input_level": (
                    item.input_level if item.input_level is not None else colander.null
                ),
            }
        else:
            appstruct = {}

        return self._form_ctx(form.render(appstruct), item)

    def view_act(self, item, appstruct):
        try:
            item.level_id = appstruct["level_id"]
            item.input_level = appstruct["input_level"]

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

    def view_csv(self):
        rows = (
            self.session.query(SimkelGroupLevel)
            .order_by(desc(SimkelGroupLevel.id))
            .all()
        )

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["Level ID", "Nama Level", "Input Level"])

        for row in rows:
            writer.writerow([row.level_id, row.level_name, row.input_level])

        response = Response(content_type="text/csv")
        response.text = output.getvalue()
        response.headers["Content-Disposition"] = "attachment; filename=group_level.csv"

        return response
