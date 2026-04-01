from sqlalchemy import Column, Integer, ForeignKey
from . import SimkelBase,SimkelDBSession

class SimkelGroupLayanan(SimkelBase):
    __tablename__ = 'simkel_group_layanan'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    jpel_id = Column(Integer, ForeignKey('simkel_jpel.id'), nullable=False)

    def __repr__(self):
        return f"<SimkelGroupLayanan(id={self.id}, group_id={self.group_id}, jpel_id={self.jpel_id})>"