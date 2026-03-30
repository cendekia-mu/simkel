from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from opensipkd.base.models import Partner 
from . import SimkelBase, StandarModel, SimkelDBSession

class SimkelPartnerDocs(StandarModel, SimkelBase):
    __tablename__ = 'partner_docs'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, ForeignKey('penduduk.id'), nullable=False)
    partner = relationship(
        Partner,
        primaryjoin=lambda: SimkelPartnerDocs.partner_id == Partner.id,
        foreign_keys=lambda: [SimkelPartnerDocs.partner_id]
    )
    file_nm = Column(String(255))
    keterangan = Column(String(255))
    create_uid = Column(Integer)
    update_uid = Column(Integer)
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, onupdate=datetime.now)

    def __repr__(self):
        return f"<SimkelPartnerDocs(id={self.id}, partner_id={self.partner_id})>"