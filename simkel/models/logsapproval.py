from sqlalchemy import Column, Integer, DateTime, ForeignKey
from . import SimkelBase,SimkelDBSession

class SimkelLogApproval(SimkelBase):
    __tablename__ = 'simkel_log_approval'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession 
    
    id = Column(Integer, primary_key=True)
    create_uid = Column(Integer) 
    created = Column(DateTime)    
    id_permohonan = Column(Integer, nullable=False) 
    status = Column(Integer)  

    def __repr__(self):
        return f"<SimkelLogApproval(id={self.id}, id_permohonan={self.id_permohonan}, status={self.status})>"