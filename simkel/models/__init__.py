from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Text, desc, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from zope.sqlalchemy import register
from opensipkd.base.models.meta import NAMING_CONVENTION
from opensipkd.base import models
from opensipkd.base.models import Departemen


metadata = MetaData(naming_convention=NAMING_CONVENTION)
SimkelBase = declarative_base(metadata=metadata)
session_factory = sessionmaker()
SimkelDBSession = scoped_session(session_factory)
register(SimkelDBSession)   


class User(models.User):
    db_session = SimkelDBSession

class StandarModel(models.StandarModel):
    db_session = SimkelDBSession

class NamaModel(models.NamaModel):
    db_session = SimkelDBSession
class ProvinsiModel(models.ResProvinsi):
    db_session = SimkelDBSession
class Dati2Model(models.ResDati2):
    db_session = SimkelDBSession
class KecamatanModel(models.ResKecamatan):
    db_session = SimkelDBSession
class KelurahanModel(models.ResDesa):
    db_session = SimkelDBSession

class PartnerModel(models.Partner):
    db_session = SimkelDBSession

    


