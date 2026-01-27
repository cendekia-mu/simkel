
from . import SimkelBase, StandarModel, NamaModel
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

class PermohonantTypeModel(NamaModel, SimkelBase):
    __tablename__ = 'permohonan_type'
    nama = Column(String(255))
    level = Column(Integer)  # e.g., 1 for high, 2 for medium, etc.

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
