from . import SimkelBase, StandarModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .jenispermohonan import JenisPermohonan


class PermohonanField(StandarModel, SimkelBase):
    __tablename__ = "simkel_jpel_field"

    id = Column(Integer, primary_key=True)
    jpel_id = Column(
        Integer, ForeignKey("simkel_jpel.id"), nullable=False
    )  # FK ke JenisPermohonan
    nama = Column(String)  # Nama field tambahan
    value = Column(String, nullable=False)  # 1=Integer, 2=String

    # Relationship biar bisa akses data JenisPermohonan langsung
    jenis_permohonan = relationship("JenisPermohonan", backref="fields")

    def __repr__(self):
        return f"<PermohonanField(id={self.id}, jpel_id={self.jpel_id}, nama={self.nama}, value={self.value})>"
