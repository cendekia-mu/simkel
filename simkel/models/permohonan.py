from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from opensipkd.base.models import Partner 
from . import SimkelBase, StandarModel, SimkelDBSession

class SimkelPermohonan(StandarModel, SimkelBase):
    __tablename__ = 'simkel_permohonan'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, ForeignKey('penduduk.id'), nullable=False)
    partner = relationship(
        Partner, 
        primaryjoin=lambda: SimkelPermohonan.partner_id == Partner.id,
        foreign_keys=lambda: [SimkelPermohonan.partner_id]
    )
    jenis_id = Column(Integer, ForeignKey('simkel_jpel.id'), nullable=False)
    jenis = relationship("SimkelJenisPermohonan")
    tgl_permohonan = Column(DateTime, nullable=False, default=datetime.now)
    status = Column(Integer, nullable=False, default=0)
    additional = Column(JSON)
    reason = Column(String(128))
    create_uid = Column(Integer)
    update_uid = Column(Integer)
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, onupdate=datetime.now)
    nomor = Column(String(50))
    pemohon_nama = Column(String(255))
    pemohon_alamat = Column(Text)

    def __repr__(self):
        return f"<SimkelPermohonan(id={self.id}, status={self.status})>"