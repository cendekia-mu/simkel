from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from . import SimkelBase, StandarModel, SimkelDBSession

class SimkelPermohonanField(StandarModel, SimkelBase):
    __tablename__ = 'simkel_jpel_field'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    id = Column(Integer, primary_key=True)
    jpel_id = Column(Integer, ForeignKey('simkel_jpel.id'), nullable=False)
    nama = Column(String(255))
    value = Column(Integer, nullable=False)
    jenis_permohonan = relationship("SimkelJenisPermohonan")

    def __repr__(self):
        return f"<SimkelPermohonanField(id={self.id}, jpel_id={self.jpel_id})>"