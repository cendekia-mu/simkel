import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy import Table, Column, Integer # <--- TAMBAHAN PENTING

from alembic import context

# ---------------------------------------------------------------------
# SETUP PATH
# ---------------------------------------------------------------------
parent_dir = os.path.abspath(os.path.join(os.getcwd(), "."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# ---------------------------------------------------------------------
# IMPORT MODELS
# ---------------------------------------------------------------------
from opensipkd.base.models import Base as BaseUtama
from simkel.models import SimkelBase

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------
# MERGE METADATA DENGAN DUMMY INJECTION (ANTI GAGAL)
# ---------------------------------------------------------------------
def get_merged_metadata():
    m = BaseUtama.metadata
    
    # 1. INJEKSI TABEL BAYANGAN UNTUK REFERENSI BASE
    # Kita buatkan tabel dummy di memori agar SQLAlchemy tidak komplain.
    missing_base_tables = ['departemen', 'partner', 'users', 'groups']
    for tname in missing_base_tables:
        if tname not in m.tables:
            # Buat tabel dummy yang hanya berisi kolom 'id'
            Table(tname, m, Column('id', Integer, primary_key=True))
            
    # 2. MASUKKAN TABEL SIMKEL
    for table in SimkelBase.metadata.tables.values():
        if table.name not in m.tables:
            table.tometadata(m)
            
    return m

target_metadata = get_merged_metadata()

# ---------------------------------------------------------------------
# FILTER OBJEK
# ---------------------------------------------------------------------
def include_object(obj, name, type_, reflected, compare_to):
    if type_ == "table":
        # Alembic hanya akan membuat file migrasi untuk tabel ini,
        # jadi tabel "bayangan" di atas tidak akan ikut ter-create.
        return name.startswith('simkel_') or name == 'partner_docs'
    return True

# ---------------------------------------------------------------------
# MIGRATION FUNCTIONS
# ---------------------------------------------------------------------
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table='alembic_simkel',
        include_object=include_object
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            version_table='alembic_simkel',
            include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()