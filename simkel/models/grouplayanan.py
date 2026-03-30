from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from opensipkd.base.models import Group 
from . import SimkelBase, StandarModel, SimkelDBSession

class SimkelGroupLayanan(StandarModel, SimkelBase):
    __tablename__ = 'simkel_group_layanan'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)    
    jenis_id = Column(Integer, ForeignKey('simkel_jpel.id'), nullable=False)
    group = relationship(
        Group,
        primaryjoin=lambda: SimkelGroupLayanan.group_id == Group.id,
        foreign_keys=lambda: [SimkelGroupLayanan.group_id]
    )
    jenis = relationship("SimkelJenisPermohonan")

    def __repr__(self):
        return f"<SimkelGroupLayanan(id={self.id}, group_id={self.group_id}, jenis_id={self.jenis_id})>"