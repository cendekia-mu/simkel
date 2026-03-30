from sqlalchemy import Column, Integer, String, DateTime, SmallInteger
from datetime import datetime
from . import SimkelBase, NamaModel, SimkelDBSession

class SimkelJenisPermohonan(NamaModel, SimkelBase):
    __tablename__ = 'simkel_jpel'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    
    id = Column(Integer, primary_key=True)
    file_nm = Column(String(128))
    status = Column(SmallInteger, default=0)
    
    create_uid = Column(Integer)
    update_uid = Column(Integer)
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<SimkelJenisPermohonan(id={self.id}, kode='{self.kode}', nama='{self.nama}')>"