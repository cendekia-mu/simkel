from pyramid.renderers import get_renderer
from sqlalchemy import func
from ..models import SimkelDBSession, SimkelPermohonan

class Views:
    def __init__(self, request):
        self.request = request
        self.session = SimkelDBSession()

    def view_list(self):
        # =====================
        # 🔹 1. IDENTIFIKASI USER & ROLE
        # =====================
        user = getattr(self.request, 'user', None)
        dashboard_type = 'warga'
        user_groups = []

        if user:
            try:
                user_groups = [g.group_name for g in user.groups]
            except:
                user_groups = list(getattr(user, 'groups', []))

            if 'Admin' in user_groups:
                dashboard_type = 'admin'
            elif 'Pejabat' in user_groups:
                dashboard_type = 'pejabat'
            elif 'Petugas' in user_groups:
                dashboard_type = 'petugas'
            else:
                dashboard_type = 'warga'

        # =====================
        # 🔹 2. LOGIKA DATA & ACTION PER ROLE
        # =====================
        query = self.session.query(SimkelPermohonan)
        actions = [] # List untuk menampung tombol aksi di dashboard

        if dashboard_type == 'warga' and user:
            query = query.filter(SimkelPermohonan.partner_id == user.id)
            actions.append({
                'label': 'Ajukan Permohonan Layanan',
                'route': 'simkel-permohonan-add', # Sesuaikan dengan route name Anda
                'class': 'btn-primary'
            })
            
        elif dashboard_type == 'petugas':
            query = query.filter(SimkelPermohonan.status == 1)
            actions.append({
                'label': 'Verifikasi Berkas',
                'route': 'simkel-verifikasi',
                'class': 'btn-warning'
            })

        elif dashboard_type == 'pejabat':
            query = query.filter(SimkelPermohonan.status == 2)
            actions.append({
                'label': 'Approval & TTE',
                'route': 'simkel-approval',
                'class': 'btn-success'
            })

        items = query.order_by(SimkelPermohonan.id.desc()).limit(10).all()

        # =====================
        # 🔹 3. STATISTIK & RENDER
        # =====================
        summary = {'draft': 0, 'proses': 0, 'selesai': 0, 'ditolak': 0}
        if dashboard_type in ['admin', 'pejabat', 'petugas']:
            stats = self.session.query(
                SimkelPermohonan.status,
                func.count(SimkelPermohonan.id).label('total')
            ).group_by(SimkelPermohonan.status).all()

            for s in stats:
                if s.status == 0: summary['draft'] = s.total [cite: 9]
                elif s.status == 1: summary['proses'] = s.total [cite: 9]
                elif s.status == 3: summary['selesai'] = s.total
                elif s.status == 4: summary['ditolak'] = s.total

        renderer = get_renderer('simkel:views/templates/base.pt')
        
        return {
            'base_template': renderer.implementation(),
            'summary': summary,
            'items': items,
            'dashboard_type': dashboard_type,
            'actions': actions, # Kirim list aksi ke template
        }