from sqlalchemy import Column, ForeignKey, Integer
from . import SimkelBase, SimkelDBSession

class SimkelAlurPermohonan(SimkelBase):
    __tablename__ = 'simkel_flow'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    
    id = Column(Integer, primary_key=True)
    jenis_id = Column(
        Integer,
        ForeignKey('simkel_jpel.id'),
        nullable=False
    )
    no_urut = Column(Integer, nullable=False)
    departemen_id = Column(
        Integer, 
        ForeignKey('departemen.id'),
        nullable=False
    )

    @property
    def is_first_step(self):
        return self.no_urut == 1

    @property
    def next_step_no(self):
        return self.no_urut + 1

    @property
    def step_label(self):
        labels = {
            1: 'Verifikasi Berkas (Staff)',
            2: 'Validasi Subseksi (Kasi)',
            3: 'Persetujuan Akhir (Lurah)',
        }
        return labels.get(self.no_urut, f'Tahap ke-{self.no_urut}')

    def __repr__(self):
        return f"<SimkelAlurPermohonan(id={self.id}, jenis={self.jenis_id}, urut={self.no_urut})>"