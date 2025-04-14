"""create transactions table

Revision ID: 1a1c23d45e67
Revises: 
Create Date: 2024-04-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1a1c23d45e67'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transaction_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('prediction', sa.String(), nullable=False),
        sa.Column('probability', sa.Float(), nullable=False),
        sa.Column('is_fraud', sa.Boolean(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('v1', sa.Float(), nullable=False),
        sa.Column('v2', sa.Float(), nullable=False),
        sa.Column('v3', sa.Float(), nullable=False),
        sa.Column('v4', sa.Float(), nullable=False),
        sa.Column('v5', sa.Float(), nullable=False),
        sa.Column('v6', sa.Float(), nullable=False),
        sa.Column('v7', sa.Float(), nullable=False),
        sa.Column('v8', sa.Float(), nullable=False),
        sa.Column('v9', sa.Float(), nullable=False),
        sa.Column('v10', sa.Float(), nullable=False),
        sa.Column('v11', sa.Float(), nullable=False),
        sa.Column('v12', sa.Float(), nullable=False),
        sa.Column('v13', sa.Float(), nullable=False),
        sa.Column('v14', sa.Float(), nullable=False),
        sa.Column('v15', sa.Float(), nullable=False),
        sa.Column('v16', sa.Float(), nullable=False),
        sa.Column('v17', sa.Float(), nullable=False),
        sa.Column('v18', sa.Float(), nullable=False),
        sa.Column('v19', sa.Float(), nullable=False),
        sa.Column('v20', sa.Float(), nullable=False),
        sa.Column('v21', sa.Float(), nullable=False),
        sa.Column('v22', sa.Float(), nullable=False),
        sa.Column('v23', sa.Float(), nullable=False),
        sa.Column('v24', sa.Float(), nullable=False),
        sa.Column('v25', sa.Float(), nullable=False),
        sa.Column('v26', sa.Float(), nullable=False),
        sa.Column('v27', sa.Float(), nullable=False),
        sa.Column('v28', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transaction_id')
    )

def downgrade():
    op.drop_table('transactions') 