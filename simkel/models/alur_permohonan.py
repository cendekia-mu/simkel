from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from opensipkd.base.models import Departemen
from . import SimkelBase, StandarModel, SimkelDBSession

class SimkelAlurPermohonan(StandarModel, SimkelBase):
    __tablename__ = 'simkel_flow'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    
    id = Column(Integer, primary_key=True)
    
    jenis_id = Column(
        Integer,
        ForeignKey('simkel_jpel.id'),
        nullable=False
    )

    departemen_id = Column(
        Integer, 
        ForeignKey('departemen.id')
    )
    
    no_urut = Column(Integer)

    jenis = relationship("SimkelJenisPermohonan", backref="flows")
    
    departemen = relationship(
        Departemen,
        primaryjoin=lambda: SimkelAlurPermohonan.departemen_id == Departemen.id,
        foreign_keys=lambda: [SimkelAlurPermohonan.departemen_id]
    )

    def __repr__(self):
        return (
            f"<SimkelAlurPermohonan("
            f"id={self.id}, "
            f"jenis_id={self.jenis_id}, "
            f"no_urut={self.no_urut}"
            f")>"
        )