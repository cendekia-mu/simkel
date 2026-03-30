from sqlalchemy import Column, Integer, String
from . import SimkelBase, NamaModel, SimkelDBSession

class SimkelJenisDokumen(NamaModel, SimkelBase):
    __tablename__ = "simkel_jdoc"
    __table_args__ = {'extend_existing': True}
    DBSession = SimkelDBSession
    id = Column(Integer, primary_key=True)
    kode = Column(String(50), unique=True)
    nama = Column(String(128))

    def __repr__(self):
        return f"<SimkelJenisDokumen(id={self.id}, kode={self.kode}, nama={self.nama})>"