from . import SimkelBase, StandarModel
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

class GroupLevelModel(StandarModel, SimkelBase):
    __tablename__ = 'simkel_group_level'

    id = Column(Integer, ForeignKey('groups.id'), primary_key=True)

    level_id = Column(Integer, nullable=False)
    input_level = Column(Integer, nullable=False)

    group = relationship('Group')

    def __repr__(self):
        return (
            f"<GroupLevelModel(group_id={self.id}, "
            f"level_id={self.level_id}, input_level={self.input_level})>"
        )
