"""Add document pricing

Revision ID: ca45ca3a0823
Revises: 06c1c7363fb6
Create Date: 2023-10-29 01:00:43.759225

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca45ca3a0823'
down_revision = '06c1c7363fb6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('document_model', schema=None) as batch_op:
        batch_op.add_column(sa.Column('price', sa.Float(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('document_model', schema=None) as batch_op:
        batch_op.drop_column('price')

    # ### end Alembic commands ###