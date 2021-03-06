"""images table

Revision ID: 944feb55819d
Revises: 30abf1816e15
Create Date: 2020-05-06 13:18:28.719605

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '944feb55819d'
down_revision = '30abf1816e15'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('address', sa.String(length=120), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_image_address'), 'image', ['address'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_image_address'), table_name='image')
    op.drop_table('image')
    # ### end Alembic commands ###
