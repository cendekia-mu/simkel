import colander
import transaction
import json
from datetime import datetime
from deform import widget, Form, ValidationFailure
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import desc, or_
from ..models import SimkelDBSession, SimkelJenisPermohonan, SimkelPermohonan, SimkelPermohonanField
from opensipkd.base.views import BaseView 

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

    def get_row(self, row_id):
        return self.session.query(SimkelPermohonan).filter_by(id=row_id).first()

    def view_list(self):
        jenis_id = self.request.params.get('jenis_id')
        search = self.request.params.get('term') or self.request.params.get('search')
        user_id = self.request.user.id 
        query = self.session.query(SimkelPermohonan).filter(
            SimkelPermohonan.partner_id == user_id
        )
        if jenis_id and jenis_id.isdigit():
            query = query.filter(SimkelPermohonan.jpel_id == int(jenis_id))

        if search:
            query = query.filter(
                or_(
                    SimkelPermohonan.kode.ilike(f'%{search}%'),
                    SimkelPermohonan.keterangan.ilike(f'%{search}%')
                )
            )
        rows = query.order_by(desc(SimkelPermohonan.id)).all()
        
        p_query = self.session.query(SimkelJenisPermohonan).all()
        jpel_list = [(p.id, p.nama) for p in p_query]
        return dict(
            title=f"Daftar {self.title}",
            rows=rows,
            jpel_list=jpel_list,
            params=self.request.params
        )

    def view_add(self):
        request = self.request
        jenis_id = request.params.get('jenis_id')
        schema = FieldSchema().bind()
        
        if jenis_id:
            fields = self.session.query(SimkelPermohonanField).filter_by(
                jpel_id=jenis_id, status=3
            ).order_by(SimkelPermohonanField.id).all()
            
            for f in fields:

                if f.tipe == 'number':
                    node_type = colander.Integer()
                elif f.tipe == 'date':
                    node_type = colander.Date()
                else:
                    node_type = colander.String()

                schema.add(colander.SchemaNode(
                    node_type,
                    name=f.kode,
                    title=f.nama,
                    missing=None if f.is_required else colander.drop,
                    widget=widget.TextAreaWidget() if f.tipe == 'textarea' else widget.TextInputWidget()
                ))
        form = Form(schema, buttons=('simpan', 'kirim', 'batal'))
        p_query = self.session.query(SimkelJenisPermohonan).all()
        schema['jenis_id'].widget.values = [(p.id, p.nama) for p in p_query]

        return dict(
            title=f"Tambah {self.title}",
            form=form.render(),
            jenis_id=jenis_id,
            row = None
        )
    
    def view_edit(self):
        request = self.request
        row_id = request.matchdict.get('id')
        item = self.get_row(row_id)

        if not item or item.partner_id != request.user.id:
            request.session.flash("Data tidak ditemukan atau bukan milik Anda.", 'error')
            return HTTPFound(location=request.route_url('simkel-permohonan'))
        
        if item.status not in [0, 2]:
            request.session.flash("Data sudah dikunci, tidak bisa diubah.", 'warning')
            return HTTPFound(location=request.route_url('simkel-permohonan'))
        
        schema = FieldSchema().bind()

        fields = self.session.query(SimkelPermohonanField).filter_by(
            jpel_id=item.jpel_id, status=3
        ).order_by(SimkelPermohonanField.id).all()

        for f in fields:
            if f.tipe == 'number':
                node_type = colander.Integer()
            elif f.tipe == 'date':
                node_type = colander.Date()
            else:
                node_type = colander.String()

            schema.add(colander.SchemaNode(
                node_type,
                name=f.kode,
                title=f.nama,
                missing=None if f.is_required else colander.drop,
                widget=widget.TextAreaWidget() if f.tipe == 'textarea' else widget.TextInputWidget()
            ))

        appstruct = {
            'jenis_id': item.jpel_id,
            'tgl_permohonan': item.tgl_permohonan,
            'keterangan': item.keterangan,
        }

        if item.additional_data:
            try:
                data_tambahan = json.loads(item.additional_data)
                appstruct.update(data_tambahan)
            except:
                pass

        form = Form(schema, buttons=('simpan', 'batal'))
        
        p_query = self.session.query(SimkelJenisPermohonan).all()
        schema['jenis_id'].widget.values = [(p.id, p.nama) for p in p_query]

        return dict(
            title=f"Edit {self.title}",
            form=form.render(appstruct), 
            row=item
        )
    
    def view_act(self):
        request = self.request
        row_id = request.matchdict.get('id')
        item = self.get_row(row_id) if row_id else SimkelPermohonan()

        if row_id and item.status not in [0, 2]:
            request.session.flash("Data sudah dikunci, tidak bisa diubah.", 'error')
            return HTTPFound(location=request.route_url('simkel-permohonan'))
        
        if request.POST:
            if 'batal' in request.POST:
                return HTTPFound(location=request.route_url('simkel-permohonan'))
            
            try:
                item.jpel_id = request.POST.get('jenis_id')
                item.keterangan = request.POST.get('keterangan')

                if not row_id:
                    item.partner_id = request.user.id
                    item.tgl_permohonan = datetime.now()
                
                item.updated = datetime.now()

                main_fields = ['jenis_id', 'tgl_permohonan', 'keterangan', 'csrf_token', 'id']
                additional_data = {}

                for key in request.POST:
                    if key not in main_fields and not key.startswith('__'):
                        additional_data[key] = request.POST.get(key)
                
                item.additional_data = json.dumps(additional_data)

                if 'kirim' in request.POST:
                    item.status = 1 
                    msg = "Permohonan berhasil dikirim ke petugas."
                else:
                    item.status = 0
                    msg = "Permohonan berhasil disimpan sebagai Draft."

                self.session.add(item)
                self.session.flush()
                transaction.commit()
                
                request.session.flash(msg)
                return HTTPFound(location=request.route_url('simkel-permohonan'))

            except Exception as e:
                transaction.abort()
                request.session.flash(f"Gagal Simpan: {str(e)}", 'error')
                return HTTPFound(location=request.environ.get('HTTP_REFERER', '/'))
                
                request.session.flash(msg)
                return HTTPFound(location=request.route_url('simkel-permohonan'))
            
    def view_delete(self):
        request = self.request
        row_id = request.matchdict.get('id')
        item = self.get_row(row_id)
        
        if not item or item.owner_id != request.user.id:
            request.session.flash("Data tidak ditemukan.", 'error')
            return HTTPFound(location=request.route_url('simkel-permohonan'))
        
        if item.status != 0:
            request.session.flash("Data yang sudah diproses tidak bisa dihapus.", 'warning')
            return HTTPFound(location=request.route_url('simkel-permohonan'))
        
        try:
            self.session.delete(item)
            self.session.flush()
            transaction.commit()
            request.session.flash("Data berhasil dihapus.")
        except Exception as e:
            transaction.abort()
            request.session.flash(f"Gagal Hapus: {str(e)}", 'error')

        return HTTPFound(location=request.route_url('simkel-permohonan'))
    
    