"""empty message

Revision ID: 49e40f474845
Revises: 82309c589333
Create Date: 2022-06-12 23:05:29.753597

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49e40f474845'
down_revision = '82309c589333'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show', sa.Column('id', sa.Integer(), nullable=False))
    op.alter_column('show', 'venue_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('show', 'artist_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    sa.PrimaryKeyConstraint('id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('show', 'id')
    # ### end Alembic commands ###
