"""peneyesuaian models

Revision ID: b36a33765b7e
Revises: 7d8554667a6d
Create Date: 2026-04-01 12:43:46.573920

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b36a33765b7e'
down_revision = '7d8554667a6d'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # --- 1. MEMBERSIHKAN TABEL UTAMA DARI KOLOM AUDIT (LEMAK) ---
    tables = [
        'simkel_permohonan', 'simkel_sk', 'simkel_jpel', 
        'simkel_jpel_field', 'simkel_jdoc', 'simkel_flow', 
        'simkel_group_layanan', 'simkel_group_level', 'simkel_log_approval'
    ]
    
    for table in tables:
        op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS created")
        op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS updated")
        op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS create_uid")
        op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS update_uid")

    # --- 2. MEMBERSIHKAN CONSTRAINT GANDA (PENYEBAB ERROR) ---
    op.execute("ALTER TABLE user_area DROP CONSTRAINT IF EXISTS fk_user_area_desa_id_res_desa")
    op.execute("ALTER TABLE simkel_group_layanan DROP CONSTRAINT IF EXISTS fk_simkel_group_layanan_group_id_groups")
    op.execute("ALTER TABLE simkel_group_level DROP CONSTRAINT IF EXISTS fk_simkel_group_level_id_groups")

    # --- 3. FIX TIPE DATA (SAKLEK MODE) ---
    op.execute("ALTER TABLE simkel_permohonan ALTER COLUMN additional TYPE TEXT")
    op.execute("ALTER TABLE simkel_permohonan ALTER COLUMN reason TYPE TEXT")

def downgrade() -> None:
    pass