from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from opensipkd.base.models import Partner 
from . import SimkelBase, StandarModel, SimkelDBSession

class SimkelPenetapan(StandarModel, SimkelBase):
    __tablename__ = 'simkel_sk'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    id = Column(Integer, primary_key=True)
    kode = Column(String(50))
    permohonan_id = Column(Integer, ForeignKey('simkel_permohonan.id'), nullable=False, unique=True)
    permohonan = relationship("SimkelPermohonan")
    ttd_id = Column(Integer, ForeignKey('penduduk.id'), nullable=False)
    ttd = relationship(
        Partner, 
        primaryjoin=lambda: SimkelPenetapan.ttd_id == Partner.id,
        foreign_keys=lambda: [SimkelPenetapan.ttd_id]
    )
    ttd_id2 = Column(Integer, ForeignKey('penduduk.id'))
    ttd2 = relationship(
        Partner,
        primaryjoin=lambda: SimkelPenetapan.ttd_id2 == Partner.id,
        foreign_keys=lambda: [SimkelPenetapan.ttd_id2]
    )
    tgl_ttd = Column(DateTime, nullable=False, default=datetime.now)
    kelurahan = Column(String(64))
    kecamatan = Column(String(64))
    kota = Column(String(64))
    jabatan = Column(String(64))
    jabatan_2 = Column(String(64))

    def __repr__(self):
        return f"<SimkelPenetapan(id={self.id}, kode={self.kode})>"