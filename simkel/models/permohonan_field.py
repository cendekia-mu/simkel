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

    @property
    def kode(self):
        """Menghasilkan key slug untuk JSON additional_data"""
        if not self.nama:
            return f"field_{self.id}"
        return self.nama.lower().strip().replace(' ', '_').replace('-', '_')

    @property
    def tipe(self):
        if not self.nama:
            return 'string'
        n = self.nama.lower()
        if any(x in n for x in ['tgl', 'tanggal', 'lahir']):
            return 'date'
        if any(x in n for x in ['jumlah', 'nik', 'nomor', 'rt', 'rw', 'harga', 'kode_pos']):
            return 'number'
        if any(x in n for x in ['alamat', 'keterangan', 'catatan', 'uraian']):
            return 'textarea'
        return 'string'

    @property
    def is_required(self):
        if not self.nama:
            return True
        n = self.nama.lower()
        if any(x in n for x in ['opsional', 'bila ada', 'tidak wajib', '(kalo ada)']):
            return False
        return True

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, jpel_id={self.jpel_id}, nama='{self.nama}')>"