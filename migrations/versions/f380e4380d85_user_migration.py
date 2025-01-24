"""User migration.

Revision ID: f380e4380d85
Revises: 3679d9d1bfd5
Create Date: 2024-07-24 16:36:14.064008

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f380e4380d85'
down_revision = '3679d9d1bfd5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('already_invited_someone', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('already_invited_someone')

    # ### end Alembic commands ###
