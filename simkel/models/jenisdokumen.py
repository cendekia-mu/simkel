from sqlalchemy import Column, Integer, String
from . import SimkelBase, SimkelDBSession

class SimkelJenisDokumen(SimkelBase):
    __tablename__ = "simkel_jdoc"
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    
    id = Column(Integer, primary_key=True)
    kode = Column(String(32)) 
    nama = Column(String(128)) 

    @property
    def slug(self):
        if not self.kode:
            return f"doc_{self.id}"
        return self.kode.lower().strip().replace(' ', '_')

    @property
    def display_name(self):
        if not self.nama:
            return "Dokumen Pendukung"
        return self.nama.title()

    @property
    def is_mandatory_global(self):
        n = (self.nama or '').lower()
        return any(x in n for x in ['ktp', 'kartu keluarga', 'kk'])

    def __repr__(self):
        return f"<SimkelJenisDokumen(id={self.id}, kode='{self.kode}', nama='{self.nama}')>"