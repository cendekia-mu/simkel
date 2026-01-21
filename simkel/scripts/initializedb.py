from lkpj.models import LkpjDBSession
from opensipkd.models import Group, Permission, GroupPermission, User, UserGroup
from opensipkd.base.scripts.initializedb import append_csv, reset_sequences, \
    alembic_run, create_schema
from opensipkd.base.models import DBSession
from opensipkd.base import Base
from sqlalchemy import (
    engine_from_config,
)
from pyramid.paster import (
    get_appsettings,
    setup_logging,
)
import transaction
import sys
import os
from ..models import *
def get_file(filename):
    base_dir = os.path.split(__file__)[0]
    fullpath = os.path.join(base_dir, 'data', filename)
    return open(fullpath)


def usage(argv):
    pass


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    # Base.metadata.create_all(bind=engine)
    
    LkpjDBSession.configure(bind=engine)
    LkpjBase.metadata.bind = engine

    reset_sequences()

    print('>>Append Table')
    append_csv(Group, 'groups.csv', ['group_name'],
               get_file_func=get_file, update_exist=True)
    append_csv(Permission, 'permissions.csv', [
               'perm_name'], get_file_func=get_file, update_exist=True)
    append_csv(User, "users.csv", ["user_name"], get_file_func=get_file)
    transaction.commit()

    append_csv(GroupPermission, 'group_permissions.csv', [
               'group_id', 'perm_name'], get_file_func=get_file, update_exist=True)
    append_csv(UserGroup, "users_groups.csv", [
               "user_id", "group_id"], get_file_func=get_file)
    transaction.commit()
    print('****PBB ETA CREATED****')
