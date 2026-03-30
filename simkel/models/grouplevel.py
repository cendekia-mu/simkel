from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from opensipkd.base.models import Group 
from . import SimkelBase, StandarModel, SimkelDBSession

class SimkelGroupLevel(StandarModel, SimkelBase):
    __tablename__ = 'simkel_group_level'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    
    id = Column(Integer, ForeignKey('groups.id'), primary_key=True)
    level_id = Column(Integer, nullable=False)
    input_level = Column(Integer, nullable=False)
    
    group = relationship(
        Group,
        primaryjoin=lambda: SimkelGroupLevel.id == Group.id,
        foreign_keys=lambda: [SimkelGroupLevel.id]
    )

    def __repr__(self):
        return f"<SimkelGroupLevel(id={self.id}, level_id={self.level_id}, input_level={self.input_level})>"