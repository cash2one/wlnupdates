"""empty message

Revision ID: 99efc33eaaa0
Revises: 10dd5ff41d2b
Create Date: 2016-08-12 22:40:43.545881

"""

# revision identifiers, used by Alembic.
revision = '99efc33eaaa0'
down_revision = '10dd5ff41d2b'

from alembic import op
import sqlalchemy as sa
import citext
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('series', sa.Column('sort_mode', postgresql.ENUM('parsed_title_order', 'chronological_order', name='series_sort_mode_enum'), server_default='parsed_title_order', nullable=True))
    op.add_column('serieschanges', sa.Column('sort_mode', postgresql.ENUM('parsed_title_order', 'chronological_order', name='series_sort_mode_enum'), server_default='parsed_title_order', nullable=True))
    op.add_column('watches', sa.Column('watch_as_name', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():

    op.drop_column('watches', 'watch_as_name')
    op.drop_column('serieschanges', 'sort_mode')
    op.drop_column('series', 'sort_mode')
    ### end Alembic commands ###
