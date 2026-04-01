from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from . import SimkelBase, SimkelDBSession

class SimkelPermohonan(SimkelBase):
    __tablename__ = 'simkel_permohonan'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    
    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, ForeignKey('partner.id'), nullable=False)
    jenis_id = Column(Integer, ForeignKey('simkel_jpel.id'), nullable=False)   
    tgl_permohonan = Column(DateTime, nullable=False)
    status = Column(Integer, nullable=False, default=0)
    additional = Column(Text)   
    reason = Column(String(128))

    def __repr__(self):
        return f"<SimkelPermohonan(id={self.id}, status={self.status})>"