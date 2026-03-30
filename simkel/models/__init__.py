from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from zope.sqlalchemy import register
from opensipkd.base.models.meta import NAMING_CONVENTION
from opensipkd.base import models

metadata = MetaData(naming_convention=NAMING_CONVENTION)
SimkelBase = declarative_base(metadata=metadata)
session_factory = sessionmaker()
SimkelDBSession = scoped_session(session_factory)
register(SimkelDBSession)

class SimkelUser(models.User, SimkelBase):
    db_session = SimkelDBSession

class StandarModel(models.StandarModel):
    db_session = SimkelDBSession

class NamaModel(models.NamaModel):
    db_session = SimkelDBSession

class KodeModel(models.KodeModel):
    db_session = SimkelDBSession

class ProvinsiModel(models.ResProvinsi, SimkelBase):
    db_session = SimkelDBSession

class Dati2Model(models.ResDati2, SimkelBase):
    db_session = SimkelDBSession

class KecamatanModel(models.ResKecamatan, SimkelBase):
    db_session = SimkelDBSession

class KelurahanModel(models.ResDesa, SimkelBase):
    db_session = SimkelDBSession

class PartnerModel(models.Partner, SimkelBase):
    db_session = SimkelDBSession


from .jenispermohonan import SimkelJenisPermohonan
from .permohonan import SimkelPermohonan 
from .permohonan_field import SimkelPermohonanField
from .penetapan import SimkelPenetapan
from .partner_docs import SimkelPartnerDocs
from .logsapproval import SimkelLogApproval 
from .jenisdokumen import SimkelJenisDokumen
from .grouplevel import SimkelGroupLevel
from .grouplayanan import SimkelGroupLayanan
from .alur_permohonan import SimkelAlurPermohonan