from sqlalchemy import Column, Integer, ForeignKey
from . import SimkelBase, SimkelDBSession

class SimkelGroupLevel(SimkelBase):
    __tablename__ = 'simkel_group_level'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    
    id = Column(Integer, ForeignKey('groups.id'), primary_key=True)
    level_id = Column(Integer, nullable=False) 
    input_level = Column(Integer, nullable=False) 

    @property
    def level_name(self):
        levels = {
            1: 'Staff/Operator',
            2: 'Kasi/Kasubag',
            3: 'Sekretaris',
            4: 'Lurah/Kepala',
            99: 'Administrator'
        }
        return levels.get(self.level_id, f'Level {self.level_id}')

    @property
    def can_approve(self):
        return self.level_id >= 2

    @property
    def is_warga(self):
        return self.level_id == 0

    def __repr__(self):
        return f"<SimkelGroupLevel(id={self.id}, level_id={self.level_id})>"