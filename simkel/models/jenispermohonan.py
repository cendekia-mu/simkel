import os
from sqlalchemy import Column, Integer, String
from . import SimkelBase, SimkelDBSession

class SimkelJenisPermohonan(SimkelBase):
    __tablename__ = 'simkel_jpel'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    
    id = Column(Integer, primary_key=True)
    kode = Column(String(32), nullable=False, unique=True)
    nama = Column(String(128), nullable=False)
    file_nm = Column(String(128))

    @property
    def template_path(self):
        if self.file_nm:
            return self.file_nm
        return f"{self.kode.lower()}.pt"

    @property
    def display_title(self):
        return self.nama.upper()

    @property
    def slug(self):
        return self.nama.lower().replace(' ', '-')

    def __repr__(self):
        return f"<SimkelJenisPermohonan(id={self.id}, kode='{self.kode}', nama='{self.nama}')>"