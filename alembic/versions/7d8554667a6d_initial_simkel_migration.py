"""Initial Simkel Migration

Revision ID: 7d8554667a6d
Revises: 
Create Date: 2026-03-30 16:39:19.360517

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7d8554667a6d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # ---------------------------------------------------------
    # PARTNER DOCS
    # ---------------------------------------------------------
    op.add_column('partner_docs', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('partner_docs', sa.Column('desa_id', sa.Integer(), nullable=True))
    
    # ---------------------------------------------------------
    # SIMKEL FLOW
    # ---------------------------------------------------------
    op.add_column('simkel_flow', sa.Column('resource_id', sa.Integer(), autoincrement=True, nullable=False, server_default='0'))
    op.add_column('simkel_flow', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.add_column('simkel_flow', sa.Column('ordering', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('simkel_flow', sa.Column('resource_name', sa.Unicode(length=100), nullable=False, server_default='0'))
    op.add_column('simkel_flow', sa.Column('resource_type', sa.Unicode(length=30), nullable=False, server_default='0'))
    op.add_column('simkel_flow', sa.Column('owner_group_id', sa.Integer(), nullable=True))
    op.add_column('simkel_flow', sa.Column('owner_user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(op.f('fk_simkel_flow_departemen_id_departemen'), 'simkel_flow', 'departemen', ['departemen_id'], ['id'])
    op.create_foreign_key(op.f('fk_simkel_flow_jenis_id_simkel_jpel'), 'simkel_flow', 'simkel_jpel', ['jenis_id'], ['id'])
    
    # ---------------------------------------------------------
    # SIMKEL GROUP LAYANAN
    # ---------------------------------------------------------
    op.add_column('simkel_group_layanan', sa.Column('jenis_id', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('simkel_group_layanan', sa.Column('departemen_id', sa.Integer(), nullable=True))
    op.add_column('simkel_group_layanan', sa.Column('no_urut', sa.Integer(), nullable=True))
    op.add_column('simkel_group_layanan', sa.Column('status', sa.SmallInteger(), nullable=False, server_default='0'))
    op.add_column('simkel_group_layanan', sa.Column('created', sa.DateTime(), nullable=True))
    op.add_column('simkel_group_layanan', sa.Column('updated', sa.DateTime(), nullable=True))
    op.add_column('simkel_group_layanan', sa.Column('create_uid', sa.Integer(), nullable=True))
    op.add_column('simkel_group_layanan', sa.Column('update_uid', sa.Integer(), nullable=True))
    op.create_foreign_key(op.f('fk_simkel_group_layanan_jpel_id_simkel_jpel'), 'simkel_group_layanan', 'simkel_jpel', ['jpel_id'], ['id'])
    op.create_foreign_key(op.f('fk_simkel_group_layanan_group_id_groups'), 'simkel_group_layanan', 'groups', ['group_id'], ['id'])
    
    # ---------------------------------------------------------
    # SIMKEL GROUP LEVEL
    # ---------------------------------------------------------
    op.add_column('simkel_group_level', sa.Column('group_id', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('simkel_group_level', sa.Column('jpel_id', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('simkel_group_level', sa.Column('status', sa.SmallInteger(), nullable=False, server_default='0'))
    op.add_column('simkel_group_level', sa.Column('created', sa.DateTime(), nullable=True))
    op.add_column('simkel_group_level', sa.Column('updated', sa.DateTime(), nullable=True))
    op.add_column('simkel_group_level', sa.Column('create_uid', sa.Integer(), nullable=True))
    op.add_column('simkel_group_level', sa.Column('update_uid', sa.Integer(), nullable=True))
    
    # ---------------------------------------------------------
    # SIMKEL JDOC
    # ---------------------------------------------------------
    op.add_column('simkel_jdoc', sa.Column('path', sa.String(length=256), nullable=False, server_default='-'))
    op.add_column('simkel_jdoc', sa.Column('status', sa.Integer(), server_default='1', nullable=False))
    op.add_column('simkel_jdoc', sa.Column('type', sa.SmallInteger(), server_default='0', nullable=False))
    op.add_column('simkel_jdoc', sa.Column('app_id', sa.SmallInteger(), server_default='0', nullable=False))
    op.add_column('simkel_jdoc', sa.Column('module', sa.String(length=256), nullable=True))
    op.add_column('simkel_jdoc', sa.Column('is_menu', sa.SmallInteger(), nullable=True))
    op.add_column('simkel_jdoc', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.add_column('simkel_jdoc', sa.Column('order_id', sa.Integer(), nullable=True))
    op.add_column('simkel_jdoc', sa.Column('permission', sa.String(length=256), nullable=True))
    op.add_column('simkel_jdoc', sa.Column('class_view', sa.String(length=256), nullable=True))
    op.add_column('simkel_jdoc', sa.Column('def_func', sa.String(length=256), nullable=True))
    op.add_column('simkel_jdoc', sa.Column('template', sa.String(length=256), nullable=True))
    op.add_column('simkel_jdoc', sa.Column('icon', sa.String(length=256), nullable=True))
    op.add_column('simkel_jdoc', sa.Column('created', sa.DateTime(), nullable=True))
    op.add_column('simkel_jdoc', sa.Column('updated', sa.DateTime(), nullable=True))
    op.add_column('simkel_jdoc', sa.Column('create_uid', sa.Integer(), nullable=True))
    op.add_column('simkel_jdoc', sa.Column('update_uid', sa.Integer(), nullable=True))
    op.alter_column('simkel_jdoc', 'kode', existing_type=sa.VARCHAR(length=50), type_=sa.String(length=128), existing_nullable=True)
    # Jika nama kosong, beri nilai sementara "0"
    op.alter_column('simkel_jdoc', 'nama', existing_type=sa.VARCHAR(length=128), nullable=False, server_default='0')
    op.create_unique_constraint(op.f('uq_simkel_jdoc_kode'), 'simkel_jdoc', ['kode'])

    # ---------------------------------------------------------
    # SIMKEL JPEL & JPEL FIELD
    # ---------------------------------------------------------
    op.alter_column('simkel_jpel', 'kode', existing_type=sa.VARCHAR(length=64), type_=sa.String(length=50), existing_nullable=True)
    op.alter_column('simkel_jpel', 'status', existing_type=sa.SMALLINT(), nullable=False, existing_server_default=sa.text('0'))
    
    # PERBAIKAN UTAMA DI SINI (Menambahkan server_default='0')
    op.add_column('simkel_jpel_field', sa.Column('level_id', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('simkel_jpel_field', sa.Column('input_level', sa.Integer(), nullable=False, server_default='0'))
    
    op.alter_column('simkel_jpel_field', 'status', existing_type=sa.INTEGER(), type_=sa.SmallInteger(), nullable=False, existing_server_default=sa.text('0'))
    op.create_foreign_key(op.f('fk_simkel_group_level_id_groups'), 'simkel_group_level', 'groups', ['id'], ['id'])

    # ---------------------------------------------------------
    # SIMKEL LOG APPROVAL
    # ---------------------------------------------------------
    op.add_column('simkel_log_approval', sa.Column('partner_id', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('simkel_log_approval', sa.Column('jenis_id', sa.Integer(), nullable=False, server_default='0'))
    # Tanggal diisi dengan hari ini secara default jika kosong
    op.add_column('simkel_log_approval', sa.Column('tgl_permohonan', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')))
    op.add_column('simkel_log_approval', sa.Column('additional', sa.Text(), nullable=True))
    op.add_column('simkel_log_approval', sa.Column('reason', sa.Text(), nullable=True))
    op.add_column('simkel_log_approval', sa.Column('update_uid', sa.Integer(), nullable=True))
    op.add_column('simkel_log_approval', sa.Column('updated', sa.DateTime(), nullable=True))
    op.add_column('simkel_log_approval', sa.Column('nomor', sa.String(length=50), nullable=True))
    op.add_column('simkel_log_approval', sa.Column('pemohon_nama', sa.String(length=255), nullable=True))
    op.add_column('simkel_log_approval', sa.Column('pemohon_alamat', sa.Text(), nullable=True))
    op.alter_column('simkel_log_approval', 'status', existing_type=sa.INTEGER(), nullable=False, server_default='0')
    op.alter_column('simkel_log_approval', 'created', existing_type=postgresql.TIMESTAMP(), nullable=True, existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.create_foreign_key(op.f('fk_simkel_log_approval_id_permohonan_simkel_permohonan'), 'simkel_log_approval', 'simkel_permohonan', ['id_permohonan'], ['id'])

    # ---------------------------------------------------------
    # SIMKEL PERMOHONAN
    # ---------------------------------------------------------
    op.add_column('simkel_permohonan', sa.Column('departemen_id', sa.Integer(), nullable=True))
    op.add_column('simkel_permohonan', sa.Column('jabatan_id', sa.SmallInteger(), nullable=True))
    op.add_column('simkel_permohonan', sa.Column('mulai', sa.DateTime(), nullable=True))
    op.add_column('simkel_permohonan', sa.Column('selesai', sa.DateTime(), nullable=True))
    op.create_foreign_key(op.f('fk_simkel_permohonan_jenis_id_simkel_jpel'), 'simkel_permohonan', 'simkel_jpel', ['jenis_id'], ['id'])
    op.create_foreign_key(op.f('fk_simkel_permohonan_partner_id_partner'), 'simkel_permohonan', 'partner', ['partner_id'], ['id'])
    
    # ---------------------------------------------------------
    # SIMKEL SK
    # ---------------------------------------------------------
    op.add_column('simkel_sk', sa.Column('create_uid', sa.Integer(), nullable=True))
    op.add_column('simkel_sk', sa.Column('created', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('simkel_sk', sa.Column('id_permohonan', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('simkel_sk', sa.Column('status', sa.Integer(), nullable=True))
    op.add_column('simkel_sk', sa.Column('updated', sa.DateTime(), nullable=True))
    op.add_column('simkel_sk', sa.Column('update_uid', sa.Integer(), nullable=True))

def downgrade() -> None:
    """Downgrade schema."""
    pass