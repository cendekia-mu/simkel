from . import SimkelBase, StandarModel
from sqlalchemy import Column, Integer, String


class JenisDokumen(StandarModel, SimkelBase):
    __tablename__ = "simkel_jdoc"

    id = Column(Integer, primary_key=True)
    kode = Column(String)
    nama = Column(String)

    def __repr__(self):
        return f"<JenisDokumen(id={self.id}, kode={self.kode}, nama={self.nama})>"
