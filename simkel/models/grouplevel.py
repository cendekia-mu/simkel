from sqlalchemy import Column, Integer, ForeignKey
from . import SimkelBase, SimkelDBSession

class SimkelGroupLevel(SimkelBase):
    __tablename__ = 'simkel_group_level'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    
    id = Column(Integer, ForeignKey('groups.id'), primary_key=True)
    level_id = Column(Integer, nullable=False)    
    input_level = Column(Integer, nullable=False) 

    def __repr__(self):
        return f"<SimkelGroupLevel(id={self.id}, level_id={self.level_id})>"