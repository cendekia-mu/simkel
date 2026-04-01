from pyramid.renderers import get_renderer
from sqlalchemy import func
from ..models import SimkelDBSession, SimkelPermohonan 

class Views:
    def __init__(self, request):
        self.request = request
        self.session = SimkelDBSession

    def view_list(self):
        # Statistik
        stats = self.session.query(
            SimkelPermohonan.status, 
            func.count(SimkelPermohonan.id).label('total')
        ).group_by(SimkelPermohonan.status).all()

        summary = {'draft': 0, 'proses': 0, 'selesai': 0, 'ditolak': 0}
        for s in stats:
            if s.status == 0: summary['draft'] = s.total
            elif s.status == 1: summary['proses'] = s.total
            elif s.status == 3: summary['selesai'] = s.total
            elif s.status == 4: summary['ditolak'] = s.total

        items = self.session.query(SimkelPermohonan).order_by(SimkelPermohonan.id.desc()).limit(10).all()

        # Load base template lokal simkel
        renderer = get_renderer('simkel:views/templates/base.pt')
        base_template = renderer.implementation()

        return {
            'base_template': base_template, # Ini kunci agar NameError hilang
            'summary': summary,
            'items': items,
            'dashboard_type': 'petugas',
        }