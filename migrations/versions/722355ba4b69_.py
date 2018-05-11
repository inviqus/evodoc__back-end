"""empty message

Revision ID: 722355ba4b69
Revises: e31a098f469a
Create Date: 2018-05-11 16:52:41.342584

"""
from alembic import op
import sqlalchemy_utils.types 
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '722355ba4b69'
down_revision = 'e31a098f469a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('search_vector', sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True))

    with op.batch_alter_table('user_token', schema=None) as batch_op:
        batch_op.add_column(sa.Column('search_vector', sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_token', schema=None) as batch_op:
        batch_op.drop_column('search_vector')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('search_vector')

    # ### end Alembic commands ###
