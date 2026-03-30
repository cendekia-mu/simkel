from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from . import SimkelBase, NamaModel, SimkelDBSession

class SimkelJenisPermohonan(NamaModel, SimkelBase):
    __tablename__ = 'simkel_jpel'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    id = Column(Integer, primary_key=True)
    file_nm = Column(String(128))

class SimkelPermohonanField(NamaModel, SimkelBase):
    __tablename__ = 'simkel_jpel_field'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    id = Column(Integer, primary_key=True)
    jpel_id = Column(Integer, ForeignKey('simkel_jpel.id'), nullable=False)
    value = Column(Integer, nullable=False)

    jenis_permohonan = relationship("SimkelJenisPermohonan", backref="fields")