"""Transaction table update migration.

Revision ID: 743fb2ca89cb
Revises: 52dd8b80fa1b
Create Date: 2024-07-21 17:58:02.326680

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '743fb2ca89cb'
down_revision = '52dd8b80fa1b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('type', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.drop_column('type')

    # ### end Alembic commands ###