from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from . import SimkelBase, NamaModel, SimkelDBSession

class SimkelPermohonanField(NamaModel, SimkelBase):
    __tablename__ = 'simkel_jpel_field'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    
    id = Column(Integer, primary_key=True)
    jpel_id = Column(Integer, ForeignKey('simkel_jpel.id'), nullable=False)
    kode = Column(String(50))
    value = Column(Text)
    status = Column(Integer, default=0)
    
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    create_uid = Column(Integer)
    update_uid = Column(Integer)
    
    jenis_permohonan = relationship("SimkelJenisPermohonan", backref="permohonan_fields")

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, jpel_id={self.jpel_id}, nama='{self.nama}')>"