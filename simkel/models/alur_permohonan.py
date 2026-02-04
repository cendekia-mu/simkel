from . import SimkelBase, StandarModel
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship


class AlurPermohonanModel(StandarModel, SimkelBase):
    __tablename__ = 'alur_permohonan'

    id = Column(Integer, primary_key=True)

    # FK ke JenisPermohonan
    jenis_id = Column(
        Integer,
        ForeignKey('jenis_permohonan.id'),
        nullable=False
    )

    jenis = relationship("JenisPermohonanModel")

    # urutan proses untuk setiap jenis pelayanan
    no_urut = Column(Integer)

    # FK ke Departemen (organisasi aktif)
    departemen_id = Column(
        Integer,
        ForeignKey('departemen.id')
    )

    departemen = relationship("DepartemenModel")

    def __repr__(self):
        return (
            f"<AlurPermohonanModel("
            f"jenis_id={self.jenis_id}, "
            f"no_urut={self.no_urut}, "
            f"departemen_id={self.departemen_id}"
            f")>"
        )
