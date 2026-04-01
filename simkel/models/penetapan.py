from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from . import SimkelBase, SimkelDBSession

class SimkelPenetapan(SimkelBase):
    __tablename__ = 'simkel_sk'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    
    id = Column(Integer, primary_key=True)
    kode = Column(String(64))
    permohonan_id = Column(
        Integer, 
        ForeignKey('simkel_permohonan.id'), 
        nullable=False, 
        unique=True
    )
    tgl_ttd = Column(DateTime, nullable=False)
    ttd_id = Column(Integer, ForeignKey('partner.id'), nullable=False)
    ttd_id2 = Column(Integer, ForeignKey('partner.id'))
    kelurahan = Column(String(64))
    kecamatan = Column(String(64))
    kota = Column(String(64))
    jabatan = Column(String(64))
    jabatan_2 = Column(String(64))

    @property
    def tgl_cetak_str(self):
        if self.tgl_ttd:
            return self.tgl_ttd.strftime('%d-%m-%Y')
        return "-"

    @property
    def info_wilayah(self):
        return f"Kel. {self.kelurahan}, Kec. {self.kecamatan}"

    def __repr__(self):
        return f"<SimkelPenetapan(id={self.id}, kode='{self.kode}')>"