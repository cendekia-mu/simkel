from . import SimkelBase, StandarModel
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime


class PenetapanModel(StandarModel, SimkelBase):
    __tablename__ = 'penetapan'

    id = Column(Integer, primary_key=True)

    # dari KodeModel
    kode = Column(String(50))

    # FK ke permohonan (NOT NULL, UNIQUE)
    permohonan_id = Column(
        Integer,
        ForeignKey('permohonan.id'),
        nullable=False,
        unique=True
    )

    permohonan = relationship("PermohonanModel")

    # tanggal tanda tangan
    tgl_ttd = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # penandatangan utama
    ttd_id = Column(
        Integer,
        ForeignKey('penduduk.id'),
        nullable=False
    )

    ttd = relationship(
        "PendudukModel",
        foreign_keys=[ttd_id]
    )

    # penandatangan kedua (opsional)
    ttd_id2 = Column(
        Integer,
        ForeignKey('penduduk.id')
    )

    ttd2 = relationship(
        "PendudukModel",
        foreign_keys=[ttd_id2]
    )

    # wilayah administratif
    kelurahan = Column(String(64))
    kecamatan = Column(String(64))
    kota = Column(String(64))

    # jabatan penandatangan
    jabatan = Column(String(64))
    jabatan_2 = Column(String(64))

    def __repr__(self):
        return (
            f"<PenetapanModel("
            f"kode={self.kode}, "
            f"permohonan_id={self.permohonan_id}, "
            f"tgl_ttd={self.tgl_ttd}"
            f")>"
        )
