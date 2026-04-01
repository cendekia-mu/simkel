from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from . import SimkelBase, SimkelDBSession

class SimkelPermohonanField(SimkelBase):
    __tablename__ = 'simkel_jpel_field'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    
    id = Column(Integer, primary_key=True)
    jpel_id = Column(Integer, ForeignKey('simkel_jpel.id'), nullable=False)
    nama = Column(String(255))
    value = Column(Text)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, jpel_id={self.jpel_id}, nama='{self.nama}')>"