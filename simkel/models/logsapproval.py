from sqlalchemy import Column, Integer, DateTime, ForeignKey
from . import SimkelBase, SimkelDBSession

class SimkelLogApproval(SimkelBase):
    __tablename__ = 'simkel_log_approval'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession 
    
    id = Column(Integer, primary_key=True)
    create_uid = Column(Integer)
    created = Column(DateTime)   
    id_permohonan = Column(Integer, nullable=False) 
    status = Column(Integer)  

    @property
    def status_text(self):
        status_map = {
            0: 'Draft',
            1: 'Dikirim/Menunggu Verifikasi',
            2: 'Perbaikan (Dikembalikan)',
            3: 'Disetujui/Proses SK',
            4: 'Selesai/SK Terbit',
            -1: 'Dibatalkan/Ditolak'
        }
        return status_map.get(self.status, f'Status {self.status}')

    @property
    def created_str(self):
        if self.created:
            return self.created.strftime('%d/%m/%Y %H:%M')
        return "-"

    def __repr__(self):
        return f"<SimkelLogApproval(id={self.id}, id_permohonan={self.id_permohonan}, status={self.status})>"