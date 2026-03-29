from . import SimkelBase, StandarModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class PermohonanFieldsModel(StandarModel, SimkelBase):
    __tablename__ = 'simkel_jpel_field'

    id = Column(Integer, primary_key=True)

    jpel_id = Column(
        Integer,
        ForeignKey('simkel_jpel.id'),
        nullable=False
    )

    jenis_permohonan = relationship("JenisPermohonan")

    nama = Column(String(255))

    value = Column(
        String(50),
        nullable=False
    )

    def __repr__(self):
        return (
            f"<PermohonanFieldsModel("
            f"id={self.id}, "
            f"jpel_id={self.jpel_id}, "
            f"nama={self.nama})"
            f">"
        )