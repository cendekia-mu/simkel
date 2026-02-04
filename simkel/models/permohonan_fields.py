from . import SimkelBase, StandarModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class PermohonanFieldsModel(StandarModel, SimkelBase):
    __tablename__ = 'permohonan_fields'

    id = Column(Integer, primary_key=True)

    # FK ke JenisPermohonan
    jpel_id = Column(
        Integer,
        ForeignKey('jenis_permohonan.id'),
        nullable=False
    )

    jenis_permohonan = relationship("JenisPermohonanModel")

    # nama field (dari NamaModel)
    nama = Column(String(255))

    # tipe/value field (1 = Integer, 2 = String)
    value = Column(
        String(50),
        nullable=False
    )

    def __repr__(self):
        return (
            f"<PermohonanFieldsModel("
            f"jpel_id={self.jpel_id}, "
            f"nama={self.nama}, "
            f"value={self.value}"
            f")>"
        )
