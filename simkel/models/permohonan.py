from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Date, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from opensipkd.base.models import Partner 
from . import SimkelBase, StandarModel, SimkelDBSession

class SimkelPermohonan(StandarModel, SimkelBase):
    __tablename__ = 'simkel_permohonan'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, ForeignKey('partner.id'), nullable=False)
    jenis_id = Column(Integer, ForeignKey('simkel_jpel.id'), nullable=False)   
    tgl_permohonan = Column(Date, nullable=False, default=datetime.now().date)
    status = Column(Integer, nullable=False, default=0)
    additional = Column(Text)
    reason = Column(Text)   
    create_uid = Column(Integer)
    update_uid = Column(Integer)
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, onupdate=datetime.now)
    nomor = Column(String(50))
    pemohon_nama = Column(String(255))
    pemohon_alamat = Column(Text)
    partner = relationship(
        Partner, 
        primaryjoin=partner_id == Partner.id,
        foreign_keys=[partner_id]
    )
    
    jenis = relationship("SimkelJenisPermohonan", backref="permohonan_list")

    def __repr__(self):
        return f"<SimkelPermohonan(id={self.id}, nomor='{self.nomor}')>"