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
    partner_id = Column(Integer, ForeignKey('partner.id'), nullable=False)
    jdoc_id = Column(Integer, ForeignKey('simkel_jdoc.id'), nullable=False)
    doc_name = Column(String(128))
    status = Column(Integer, nullable=False, default=0)
    
    partner = relationship(
        Partner,
        primaryjoin=lambda: SimkelPartnerDocs.partner_id == Partner.id,
        foreign_keys=lambda: [SimkelPartnerDocs.partner_id]
    )
    
    jenis_dokumen = relationship("SimkelJenisDokumen", backref="partner_docs")

    def __repr__(self):
        return f"<SimkelPartnerDocs(id={self.id}, partner_id={self.partner_id}, doc_name='{self.doc_name}')>"