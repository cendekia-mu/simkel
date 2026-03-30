from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import SimkelBase, StandarModel, SimkelDBSession

class SimkelLogApproval(StandarModel, SimkelBase):
    __tablename__ = 'simkel_log_approval'
    __table_args__ = {'extend_existing': True}
    DBSession = SimkelDBSession
    id = Column(Integer, primary_key=True)
    create_uid = Column(Integer)
    created = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    id_permohonan = Column(
        Integer,
        ForeignKey('simkel_permohonan.id'),
        nullable=False
    )
    status = Column(Integer)
    permohonan = relationship('SimkelPermohonan')

    def __repr__(self):
        return (
            f"<SimkelLogApproval("
            f"id={self.id}, "
            f"id_permohonan={self.id_permohonan}, "
            f"status={self.status})>"
        )