from sqlalchemy import Column, Integer, String
from . import SimkelBase, SimkelDBSession

class SimkelJenisDokumen(SimkelBase):
    __tablename__ = "simkel_jdoc"
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    
    id = Column(Integer, primary_key=True)
    kode = Column(String(32)) 
    nama = Column(String(128)) 

    def __repr__(self):
        return f"<SimkelJenisDokumen(id={self.id}, kode='{self.kode}', nama='{self.nama}')>"