from . import SimkelBase, StandarModel
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class LogApprovalModel(StandarModel, SimkelBase):
    __tablename__ = 'simkel_log_approval'

    id = Column(Integer, primary_key=True)

    create_uid = Column(Integer)

    created = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    id_permohonan = Column(
        Integer,
        ForeignKey('permohonan.id'),
        nullable=False
    )

    status = Column(Integer)

    # optional relationship (kalau PermohonanModel ada)
    permohonan = relationship('PermohonanModel')

    def __repr__(self):
        return (
            f"<LogApprovalModel("
            f"id_permohonan={self.id_permohonan}, "
            f"status={self.status})>"
        )
