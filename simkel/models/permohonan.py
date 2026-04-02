import json
from sqlalchemy import Column, Integer, String, DateTime, Text
from . import SimkelBase, SimkelDBSession

class SimkelPermohonan(SimkelBase):
    __tablename__ = 'simkel_permohonan'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    
    id = Column(Integer, primary_key=True)
    
    partner_id = Column(Integer, nullable=False)
    jenis_id = Column(Integer, nullable=False)   
    
    tgl_permohonan = Column(DateTime, nullable=False)
    status = Column(Integer, nullable=False, default=0)
    additional = Column(Text)   
    reason = Column(String(128))

    @property
    def additional_data(self):
        if self.additional:
            try:
                return json.loads(self.additional)
            except:
                return {}
        return {}

    @additional_data.setter
    def additional_data(self, value):
        self.additional = json.dumps(value)

    @property
    def created(self):
        return self.tgl_permohonan

    @property
    def pemohon_nm(self):
        """Tarik nama partner secara manual"""
        if not self.partner_id:
            return '-'
        from . import PartnerModel
        row = self.db_session().query(PartnerModel).filter_by(id=self.partner_id).first()
        return row.nama if row else '-'

    @property
    def jenis_nm(self):
        """Tarik nama layanan secara manual"""
        if not self.jenis_id:
            return 'Surat'
        from .jenispermohonan import SimkelJenisPermohonan
        row = self.db_session().query(SimkelJenisPermohonan).filter_by(id=self.jenis_id).first()
        return row.nama if row else 'Surat'