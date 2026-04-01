import os
from sqlalchemy import Column, ForeignKey, Integer, String
from . import SimkelBase, SimkelDBSession

class SimkelPartnerDocs(SimkelBase):
    __tablename__ = 'partner_docs'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    
    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer, ForeignKey('partner.id'), nullable=False)
    jdoc_id = Column(Integer, ForeignKey('simkel_jdoc.id'), nullable=False)
    doc_name = Column(String(128))
    status = Column(Integer, nullable=False, default=0) 

    @property
    def status_label(self):
        labels = {
            0: 'Draft/Pending',
            1: 'Terverifikasi',
            2: 'Ditolak/Perlu Unggah Ulang',
            -1: 'Kadaluwarsa'
        }
        return labels.get(self.status, 'Unknown')

    @property
    def file_extension(self):
        if self.doc_name:
            return os.path.splitext(self.doc_name)[1].lower()
        return ""

    @property
    def is_image(self):
        return self.file_extension in ['.jpg', '.jpeg', '.png', '.gif']

    def __repr__(self):
        return f"<SimkelPartnerDocs(id={self.id}, partner_id={self.partner_id}, doc_name='{self.doc_name}')>"