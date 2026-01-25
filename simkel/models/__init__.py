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

class StandarModel(models.StandarModel):
    db_session = SimkelDBSession

class User(models.User, SimkelBase):
    db_session = SimkelDBSession

