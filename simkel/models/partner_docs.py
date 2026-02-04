from . import SimkelBase, StandarModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class PartnerDocsModel(StandarModel, SimkelBase):
    __tablename__ = 'partner_docs'

    id = Column(Integer, primary_key=True)

    # FK ke Penduduk (partner)
    partner_id = Column(
        Integer,
        ForeignKey('penduduk.id'),
        nullable=False
    )

    partner = relationship("PendudukModel")

    # FK ke Jenis Dokumen
    jdoc_id = Column(
        Integer,
        ForeignKey('jenis_dokumen.id'),
        nullable=False
    )

    jenis_dokumen = relationship("JenisDokumenModel")

    # nama dokumen
    doc_name = Column(String(128))

    # status dokumen (default: 0)
    status = Column(
        Integer,
        nullable=False,
        default=0
    )

    def __repr__(self):
        return (
            f"<PartnerDocsModel("
            f"partner_id={self.partner_id}, "
            f"jdoc_id={self.jdoc_id}, "
            f"status={self.status}"
            f")>"
        )
