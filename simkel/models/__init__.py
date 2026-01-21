from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Text, desc, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from zope.sqlalchemy import register
from opensipkd.base.models.meta import NAMING_CONVENTION
from opensipkd.base import models
from opensipkd.base.models import Departemen


metadata = MetaData(naming_convention=NAMING_CONVENTION)
SimkelBase = declarative_base(metadata=metadata)
session_factory = sessionmaker()
SimkelDBSession = scoped_session(session_factory)
register(SimkelDBSession)   

class StandarModel(models.StandarModel):
    db_session = SimkelDBSession

class PermohonantTypeModel(StandarModel, SimkelBase):
    __tablename__ = 'permohonan_type'
    name = Column(String(255))
    level=Column(Integer)  # e.g., 1 for high, 2 for medium, etc.
    def __repr__(self):
        return f"<PermohonantTypeModel(name={self.name}, description={self.description})>"
    
class PermohonanModel(StandarModel, SimkelBase):
    __tablename__ = 'permohonan'
    id = Column(Integer, primary_key=True)
    nomor = Column(String(50))
    jenis_id = Column(Integer, ForeignKey('permohonan_type.id'))
    jenis = relationship("PermohonantTypeModel")
    pemohon_nama = Column(String(255))
    pemohon_alamat = Column(Text)
    status = Column(String(50))  # e.g., 'pending', 'approved', 'rejected'

    def __repr__(self):
        return f"<PermohonanModel(nomor={self.nomor}, pemohon_nama={self.pemohon_nama}, status={self.status})>"