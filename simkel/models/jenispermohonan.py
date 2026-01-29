from . import SimkelBase, StandarModel
from sqlalchemy import Column, Integer, String


class JenisPermohonan(StandarModel, SimkelBase):
    __tablename__ = "simkel_jpel"

    id = Column(Integer, primary_key=True)
    kode = Column(String)  # dari NamaModel, dipakai untuk kode SK/surat
    nama = Column(String)  # dari NamaModel
    file_nm = Column(String(128))  # Report/Format Output

    def __repr__(self):
        return f"<JenisPermohonan(id={self.id}, kode={self.kode}, nama={self.nama}, file_nm={self.file_nm})>"
