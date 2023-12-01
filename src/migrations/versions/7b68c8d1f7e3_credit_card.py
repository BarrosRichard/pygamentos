"""credit_card

Revision ID: 7b68c8d1f7e3
Revises: e33e334787ab
Create Date: 2023-12-01 11:02:00.373757

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b68c8d1f7e3'
down_revision = 'e33e334787ab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('credit_card',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('number', sa.String(length=16), nullable=False),
    sa.Column('validate', sa.String(length=7), nullable=False),
    sa.Column('cvv', sa.String(length=3), nullable=False),
    sa.Column('description', sa.String(length=60), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('credit_card')
    # ### end Alembic commands ###
