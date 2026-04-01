import json
import logging
import colander
import transaction
from datetime import datetime, date
from sqlalchemy import desc, or_
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
        missing=None,
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
        
        self.allow_print = False 

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
        query = self.session.query(SimkelPermohonan)
        
        if hasattr(user, 'partner_id') and user.partner_id:
            query = query.filter(SimkelPermohonan.partner_id == user.partner_id)

        jenis_id = params.get('jenis_id')
        if jenis_id and jenis_id.isdigit():
            query = query.filter(SimkelPermohonan.jenis_id == int(jenis_id))

        search = params.get('term') or params.get('search')
        if search:
            query = query.filter(or_(
                SimkelPermohonan.keterangan.ilike(f'%{search}%'),
                SimkelPermohonan.nomor_permohonan.ilike(f'%{search}%')
            ))

        rows = query.order_by(desc(SimkelPermohonan.id)).all()
        jpel_list = [(p.id, p.nama) for p in self.session.query(SimkelJenisPermohonan).all()]

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
        
        res = super().view_view()
        if isinstance(res, dict):
            res.update(dict(
                title=f"Detail {self.title}",
                row=row,
                fields=fields,
                data=row.additional_data or {}
            ))
        return res

    def view_add(self):
        return self.view_form()

    def view_edit(self):
        return self.view_form()

    def view_form(self):
        request = self.request
        row_id = request.matchdict.get('id')
        item = self.query_id().first() if row_id else SimkelPermohonan()
        jenis_id = request.params.get('jenis_id') or (item.jenis_id if row_id else None)
        
        if row_id and item.status not in [0, 2]:
            request.session.flash("Data sudah dikunci.", 'warning')
            return HTTPFound(location=request.route_url(self.route))

        schema = FieldSchema()
        
        if jenis_id:
            fields = self.session.query(SimkelPermohonanField).filter_by(
                jpel_id=int(jenis_id)
            ).order_by(SimkelPermohonanField.id).all()
            
            for f in fields:
                node_type = colander.String()
                if f.tipe == 'number': node_type = colander.Integer()
                elif f.tipe == 'date': node_type = colander.Date()

                schema.add(colander.SchemaNode(
                    node_type,
                    name=str(f.kode),
                    title=str(f.nama),
                    missing=colander.drop if not f.is_required else None,
                    widget=widget.TextAreaWidget() if f.tipe == 'textarea' else widget.TextInputWidget()
                ))

        schema = schema.bind()
        form = Form(schema, buttons=('simpan', 'kirim', 'batal'))
        p_query = self.session.query(SimkelJenisPermohonan.id, SimkelJenisPermohonan.nama).all()
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

        appstruct = {}
        if row_id:
            appstruct = {
                'jenis_id': item.jenis_id,
                'tgl_permohonan': item.tgl_permohonan.date() if item.tgl_permohonan else None,
                'keterangan': item.keterangan,
            }
            if item.additional_data:
                appstruct.update(item.additional_data)

        return dict(title=f"Form {self.title}", form=form.render(appstruct), row=item)

    def view_act(self, item, appstruct):
        request = self.request
        try:
            item.jenis_id = appstruct['jenis_id']
            item.keterangan = appstruct['keterangan']

            if not item.id:
                item.partner_id = getattr(request.user, 'partner_id', 1) or 1
                item.tgl_permohonan = datetime.now()
            
            exclude = ['jenis_id', 'tgl_permohonan', 'keterangan']
            additional_data = {}
            for k, v in appstruct.items():
                if k not in exclude:
                    if isinstance(v, (datetime, date)):
                        additional_data[k] = v.strftime('%Y-%m-%d')
                    else:
                        additional_data[k] = v
            item.additional_data = additional_data
            
            if 'kirim' in request.POST:
                item.status = 1
                self.session.add(item)
                self.session.flush()

                log_entry = SimkelLogApproval()
                log_entry.id_permohonan = item.id
                log_entry.status = 1
                log_entry.keterangan = "Permohonan dikirim oleh warga"
                log_entry.created = datetime.now()
                self.session.add(log_entry)
            else:
                item.status = 0
                self.session.add(item)

            transaction.commit()
            request.session.flash("Data berhasil disimpan.")
            return HTTPFound(location=request.route_url(self.route))

        except Exception as e:
            transaction.abort()
            request.session.flash(f"Gagal: {str(e)}", 'error')
            return HTTPFound(location=request.environ.get('HTTP_REFERER', '/'))

    def view_delete(self):
        row = self.query_id().first()
        if row and row.status == 0:
            try:
                self.session.delete(row)
                transaction.commit()
                request.session.flash("Data berhasil dihapus.")
            except Exception as e:
                transaction.abort()
                request.session.flash(f"Gagal: {str(e)}", 'error')
        else:
            request.session.flash("Data tidak bisa dihapus.", 'warning')
        return HTTPFound(location=self.request.route_url(self.route))