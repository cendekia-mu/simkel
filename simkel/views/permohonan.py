import json
import logging
import colander
import transaction
from datetime import datetime, date
from sqlalchemy import desc, or_, insert
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
        return self.session.query(SimkelPermohonan).filter_by(id=row_id)

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
            query = query.filter(
                SimkelPermohonan.reason.ilike(f'%{search}%')
            )

        rows = query.order_by(desc(SimkelPermohonan.id)).all()

        jpel_query = self.session.query(SimkelJenisPermohonan).all()
        jpel_dict = {p.id: p.nama for p in jpel_query}

        for r in rows:
            r.nama = jpel_dict.get(r.jenis_id, '-')
            r.deskripsi = r.reason if r.reason else '-'

        jpel_list = [(p.id, p.nama) for p in jpel_query]

        return dict(
            title=f"Daftar {self.title}",
            rows=rows,
            jpel_list=jpel_list,
            params=params
        )

    def view_view(self):
        row = self.query_id().first()
        if not row:
            return HTTPFound(location=self.request.route_url(self.route))

        fields = self.session.query(SimkelPermohonanField).filter_by(
            jpel_id=row.jenis_id
        ).order_by(SimkelPermohonanField.id).all()

        # Ambil data additional (JSON) dari kolom 'additional'
        additional = {}
        if row.additional:
            try:
                additional = json.loads(row.additional) if isinstance(row.additional, str) else row.additional
            except Exception:
                additional = {}

        jpel = self.session.query(SimkelJenisPermohonan).filter_by(id=row.jenis_id).first()

        # Status label sesuai status_text di model
        status_map = {
            0:  ('<span class="label label-default">Draft</span>'),
            1:  ('<span class="label label-warning">Menunggu Verifikasi</span>'),
            2:  ('<span class="label label-danger">Perbaikan / Dikembalikan</span>'),
            3:  ('<span class="label label-info">Disetujui Petugas / Proses SK</span>'),
            4:  ('<span class="label label-success">Selesai / SK Terbit</span>'),
            -1: ('<span class="label label-danger">Ditolak</span>'),
        }
        status_html = status_map.get(row.status, f'<span class="label label-default">{row.status}</span>')

        nama_jenis = jpel.nama if jpel else '-'
        tgl = row.tgl_permohonan
        tgl_str = tgl.strftime('%d/%m/%Y') if tgl else '-'

        # Bangun HTML detail
        html = f'''
        <div class="form-horizontal">
            <div class="form-group">
                <label class="col-md-3 control-label">Jenis Pelayanan</label>
                <div class="col-md-9"><p class="form-control-static">{nama_jenis}</p></div>
            </div>
            <div class="form-group">
                <label class="col-md-3 control-label">Tanggal Permohonan</label>
                <div class="col-md-9"><p class="form-control-static">{tgl_str}</p></div>
            </div>
            <div class="form-group">
                <label class="col-md-3 control-label">Status</label>
                <div class="col-md-9"><p class="form-control-static">{status_html}</p></div>
            </div>
            <div class="form-group">
                <label class="col-md-3 control-label">Keterangan</label>
                <div class="col-md-9"><p class="form-control-static">{row.reason or '-'}</p></div>
            </div>
        '''

        # Tampilkan alasan penolakan kalau ditolak
        if row.status == -1 and row.reason:
            html += f'''
            <div class="form-group">
                <label class="col-md-3 control-label text-danger">Alasan Penolakan</label>
                <div class="col-md-9">
                    <p class="form-control-static text-danger"><strong>{row.reason}</strong></p>
                </div>
            </div>
            '''

        # Tampilkan field dinamis dari additional
        if additional and fields:
            html += '<hr><h4>Data Tambahan</h4>'
            for f in fields:
                val = additional.get(f.nama, '-')
                html += f'''
                <div class="form-group">
                    <label class="col-md-3 control-label">{f.nama}</label>
                    <div class="col-md-9"><p class="form-control-static">{val}</p></div>
                </div>
                '''

        html += '</div>'

        return dict(
            title=f"Detail {self.title}",
            row=row,
            form=html
        )

    def view_add(self):
        return self.view_form()

    def view_edit(self):
        return self.view_form()

    def view_form(self):
        request = self.request
        row_id = request.matchdict.get('id')
        item = self.query_id().first() if row_id else SimkelPermohonan()

        # Cek apakah data boleh diedit (hanya status 0=Draft atau 2=Perbaikan)
        if row_id and item and item.status not in [0, 2]:
            request.session.flash("Data sudah dikunci atau sedang diproses.", 'warning')
            return HTTPFound(location=request.route_url(self.route))

        jenis_id = request.params.get('jenis_id') or (item.jenis_id if row_id and item else None)

        schema = FieldSchema()

        # Tambahkan field dinamis sesuai jenis pelayanan
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

        # Isi pilihan jenis pelayanan
        p_query = self.session.query(SimkelJenisPermohonan).all()
        schema['jenis_id'].widget.values = [(p.id, p.nama) for p in p_query]

        if request.POST:
            if 'batal' in request.POST:
                return HTTPFound(location=request.route_url(self.route))
            controls = request.POST.items()
            try:
                appstruct = form.validate(controls)
                return self.view_act(item, appstruct)
            except ValidationFailure as e:
                return dict(title=f"Form {self.title}", form=e.render(), row=item)

        # Isi appstruct untuk form edit
        appstruct = {}
        if row_id and item:
            tgl = item.tgl_permohonan
            appstruct = {
                'jenis_id': item.jenis_id,
                'tgl_permohonan': tgl.date() if hasattr(tgl, 'date') else tgl,
                'keterangan': item.reason or '',
            }
            # Tambahkan data additional ke appstruct
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

            # Simpan field dinamis ke kolom 'additional' (JSON)
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
            log.error(f"Permohonan error: {str(e)}")
            request.session.flash(f"Gagal: {str(e)}", 'error')
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
                log.error(f"Delete error: {str(e)}")
                request.session.flash(f"Gagal menghapus: {str(e)}", 'error')
        else:
            request.session.flash("Data tidak bisa dihapus karena sudah diproses.", 'warning')

        return HTTPFound(location=request.route_url(self.route))