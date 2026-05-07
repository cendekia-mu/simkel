import json
import logging
import colander
import transaction
from datetime import datetime, date
from sqlalchemy import desc, insert
from pyramid.httpexceptions import HTTPFound
from deform import widget, Form, ValidationFailure

from opensipkd.base.views import BaseView
from ..models import (
    SimkelDBSession,
    SimkelPermohonan,
    SimkelJenisPermohonan,
    SimkelLogApproval,
    SimkelPermohonanField
)

log = logging.getLogger(__name__)


class FieldSchema(colander.Schema):
    jenis_id = colander.SchemaNode(
        colander.Integer(),
        title="Jenis Pelayanan",
        widget=widget.SelectWidget())

    tgl_permohonan = colander.SchemaNode(
        colander.Date(),
        title="Tanggal",
        default=datetime.now().date(),
        widget=widget.DateInputWidget())

    keterangan = colander.SchemaNode(
        colander.String(),
        title="Keterangan Tambahan",
        missing=colander.drop,
        widget=widget.TextAreaWidget(rows=3))


class Views(BaseView):
    def __init__(self, request):
        super().__init__(request)
        self.request = request
        self.session = SimkelDBSession()
        self.title = "Permohonan"
        self.route = 'simkel-permohonan'
        self.list_route = 'simkel-permohonan'
        self.table = SimkelPermohonan
        self.list_schema = FieldSchema
        self.edit_schema = FieldSchema
        self.add_schema = FieldSchema
        self.allow_print = False

    def query_id(self):
        row_id = self.request.matchdict.get('id')
        q = self.session.query(SimkelPermohonan).filter_by(id=row_id)
        pid = getattr(self.request.user, 'partner_id', None)
        if pid:
            q = q.filter_by(partner_id=pid)
        return q

    def get_values(self, row):
        return {c.name: getattr(row, c.name) for c in row.__table__.columns}

    def get_item_table(self, **kwargs):
        return None

    def view_list(self):
        user = self.request.user
        params = self.request.params
        query = self.session.query(SimkelPermohonan)

        if hasattr(user, 'partner_id') and user.partner_id:
            query = query.filter(SimkelPermohonan.partner_id == user.partner_id)

        jenis_id = params.get('jenis_id')
        if jenis_id and jenis_id.isdigit():
            query = query.filter(SimkelPermohonan.jenis_id == int(jenis_id))

        search = params.get('term') or params.get('search')
        if search:
            query = query.filter(SimkelPermohonan.reason.ilike(f'%{search}%'))

        rows = query.order_by(desc(SimkelPermohonan.id)).all()
        jpel_query = self.session.query(SimkelJenisPermohonan).all()
        jpel_dict = {p.id: p.nama for p in jpel_query}

        for r in rows:
            r.nama = jpel_dict.get(r.jenis_id, '-')
            r.deskripsi = r.reason if r.reason else '-'

        return dict(
            title=f"Daftar {self.title}",
            rows=rows,
            jpel_list=[(p.id, p.nama) for p in jpel_query],
            params=params
        )

    def view_view(self):
        row = self.query_id().first()
        if not row:
            return HTTPFound(location=self.request.route_url(self.route))

        fields = self.session.query(SimkelPermohonanField).filter_by(
            jpel_id=row.jenis_id
        ).order_by(SimkelPermohonanField.id).all()

        additional = {}
        if row.additional:
            try:
                additional = json.loads(row.additional) if isinstance(row.additional, str) else row.additional
            except Exception:
                additional = {}

        jpel = self.session.query(SimkelJenisPermohonan).filter_by(id=row.jenis_id).first()

        status_map = {
            0:  ('default', 'Draft'),
            1:  ('warning', 'Menunggu Verifikasi'),
            2:  ('danger',  'Perbaikan / Dikembalikan'),
            3:  ('info',    'Disetujui Petugas / Proses SK'),
            4:  ('success', 'Selesai / SK Terbit'),
            -1: ('danger',  'Ditolak'),
        }
        status_class, status_label = status_map.get(row.status, ('default', str(row.status)))
        tgl = row.tgl_permohonan
        tgl_str = tgl.strftime('%d/%m/%Y') if tgl else '-'

        return dict(
            title=f"Detail {self.title}",
            row=row,
            nama_jenis=jpel.nama if jpel else '-',
            tgl_str=tgl_str,
            status_class=status_class,
            status_label=status_label,
            additional_display=[
                {'label': f.nama, 'value': additional.get(f.nama, '-')}
                for f in fields
            ],
        )

    def view_add(self):
        return self.view_form()

    def view_edit(self):
        return self.view_form()

    def view_form(self):
        request = self.request
        row_id = request.matchdict.get('id')
        item = self.query_id().first() if row_id else SimkelPermohonan()

        if row_id and item and item.status not in [0, 2]:
            request.session.flash("Data sudah dikunci atau sedang diproses.", 'warning')
            return HTTPFound(location=request.route_url(self.route))

        jenis_id = request.params.get('jenis_id') or (item.jenis_id if row_id and item else None)

        schema = FieldSchema()
        if jenis_id:
            fields = self.session.query(SimkelPermohonanField).filter_by(
                jpel_id=int(jenis_id)
            ).order_by(SimkelPermohonanField.id).all()
            for f in fields:
                schema.add(colander.SchemaNode(
                    colander.String(),
                    name=str(f.nama),
                    title=str(f.nama),
                    missing=colander.drop,
                    default=str(f.value) if f.value else '',
                    widget=widget.TextInputWidget()
                ))

        schema = schema.bind()
        form = Form(schema, buttons=('simpan', 'kirim', 'batal'))
        schema['jenis_id'].widget.values = [(p.id, p.nama) for p in self.session.query(SimkelJenisPermohonan).all()]

        if request.POST:
            if 'batal' in request.POST:
                return HTTPFound(location=request.route_url(self.route))
            try:
                appstruct = form.validate(request.POST.items())
                return self.view_act(item, appstruct)
            except ValidationFailure as e:
                return dict(title=f"Form {self.title}", form=e.render(), row=item)

        appstruct = {}
        if row_id and item:
            tgl = item.tgl_permohonan
            appstruct = {
                'jenis_id': item.jenis_id,
                'tgl_permohonan': tgl.date() if hasattr(tgl, 'date') else tgl,
                'keterangan': item.reason or '',
            }
            if item.additional:
                try:
                    add_data = json.loads(item.additional) if isinstance(item.additional, str) else item.additional
                    appstruct.update(add_data)
                except Exception:
                    pass

        return dict(title=f"Form {self.title}", form=form.render(appstruct), row=item)

    def view_act(self, item, appstruct):
        request = self.request
        try:
            if item.id and item.status not in [0, 2]:
                request.session.flash("Data ini sudah diproses dan tidak dapat diubah.", 'warning')
                return HTTPFound(location=request.route_url(self.route))

            item.jenis_id = appstruct['jenis_id']
            item.tgl_permohonan = appstruct.get('tgl_permohonan') or datetime.now().date()
            item.reason = appstruct.get('keterangan') or ''

            if not item.id:
                item.partner_id = getattr(request.user, 'partner_id', None) or 1

            exclude = {'jenis_id', 'tgl_permohonan', 'keterangan'}
            additional_data = {}
            for k, v in appstruct.items():
                if k not in exclude:
                    if isinstance(v, (datetime, date)):
                        additional_data[k] = v.strftime('%Y-%m-%d')
                    elif v is not None:
                        additional_data[k] = v

            item.additional = json.dumps(additional_data) if additional_data else None

            if 'kirim' in request.POST:
                item.status = 1
                pesan = "Permohonan berhasil dikirim ke petugas."
            else:
                item.status = 0
                pesan = "Draft permohonan berhasil disimpan."

            self.session.add(item)
            self.session.flush()
            self.session.execute(insert(SimkelLogApproval).values(
                id_permohonan=item.id,
                status=item.status
            ))
            transaction.commit()
            request.session.flash(pesan)
            return HTTPFound(location=request.route_url(self.route))

        except Exception as e:
            transaction.abort()
            log.error("Permohonan error: %s", e, exc_info=True)
            request.session.flash(f"Error: {str(e)}", 'error')  # sementara untuk debug
            return HTTPFound(location=request.route_url(self.route))

    def view_delete(self):
        request = self.request
        row = self.query_id().first()

        if not row:
            request.session.flash("Data tidak ditemukan.", 'warning')
            return HTTPFound(location=request.route_url(self.route))

        if row.status == 0:
            try:
                self.session.delete(row)
                transaction.commit()
                request.session.flash("Data berhasil dihapus.")
            except Exception as e:
                transaction.abort()
                log.error("Delete error: %s", e, exc_info=True)
                request.session.flash("Gagal menghapus data.", 'error')
        else:
            request.session.flash("Data tidak bisa dihapus karena sudah diproses.", 'warning')

        return HTTPFound(location=request.route_url(self.route))