from sqlalchemy import Column, ForeignKey, Integer, String
from . import SimkelBase, SimkelDBSession

class SimkelPartnerDocs(SimkelBase):
    __tablename__ = 'partner_docs'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    
    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, ForeignKey('partner.id'), nullable=False)
    jdoc_id = Column(Integer, ForeignKey('simkel_jdoc.id'), nullable=False)
    doc_name = Column(String(128))
    status = Column(Integer, nullable=False, default=0) 

    def __repr__(self):
        return f"<SimkelPartnerDocs(id={self.id}, partner_id={self.partner_id}, doc_name='{self.doc_name}')>"