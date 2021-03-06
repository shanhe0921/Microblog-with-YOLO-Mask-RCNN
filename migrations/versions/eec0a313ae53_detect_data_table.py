"""detect data table

Revision ID: eec0a313ae53
Revises: 944feb55819d
Create Date: 2020-07-02 14:57:04.954265

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eec0a313ae53'
down_revision = '944feb55819d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('detect_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('class_index', sa.Integer(), nullable=True),
    sa.Column('predicted_class', sa.String(length=120), nullable=True),
    sa.Column('obj_score', sa.Float(), nullable=True),
    sa.Column('left', sa.Integer(), nullable=True),
    sa.Column('top', sa.Integer(), nullable=True),
    sa.Column('right', sa.Integer(), nullable=True),
    sa.Column('bottom', sa.Integer(), nullable=True),
    sa.Column('all_score', sa.PickleType(), nullable=True),
    sa.Column('multiple_obj', sa.PickleType(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('detect_data')
    # ### end Alembic commands ###
