from . import SimkelBase, StandarModel
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship


class GroupLayananModel(StandarModel, SimkelBase):
    __tablename__ = 'simkel_group_layanan'

    id = Column(Integer, primary_key=True)

    group_id = Column(
        Integer,
        ForeignKey('group.id'),
        nullable=False
    )

    jpel_id = Column(
        Integer,
        ForeignKey('jenis_permohonan.id'),
        nullable=False
    )

    
    group = relationship('Group')
    jenis_permohonan = relationship('JenisPermohonan')

    def __repr__(self):
        return (
            f"<GroupLayananModel("
            f"group_id={self.group_id}, "
            f"jpel_id={self.jpel_id})>"
        )
