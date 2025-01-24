"""Reward migration.

Revision ID: 3679d9d1bfd5
Revises: b007ae530844
Create Date: 2024-07-24 16:14:49.335640

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3679d9d1bfd5'
down_revision = 'b007ae530844'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('referral', 'code',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.Integer(),
               existing_nullable=True,
               postgresql_using='code::integer')
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('referral', 'code',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(length=50),
               existing_nullable=True)
    # ### end Alembic commands ###


    # ### end Alembic commands ###
