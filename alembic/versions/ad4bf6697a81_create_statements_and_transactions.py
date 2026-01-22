"""create_statements_and_transactions

Revision ID: ad4bf6697a81
Revises: 
Create Date: 2026-01-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad4bf6697a81'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create statements and transactions tables."""
    
    # 1. Create statements table first (parent)
    op.create_table(
        'statements',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('file_hash', sa.String(64), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('transaction_count', sa.Integer(), default=0),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('file_hash', name='uq_statements_file_hash')
    )
    
    # 2. Create transactions table (child)
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('posted_date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('merchant_clean', sa.String(255), nullable=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('statement_id', sa.Integer(), nullable=True),
        sa.Column('dedupe_hash', sa.String(64), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['statement_id'], ['statements.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('dedupe_hash', name='uq_transactions_dedupe_hash')
    )
    
    # 3. Create indexes for common queries
    op.create_index('idx_transactions_posted_date', 'transactions', ['posted_date'])
    op.create_index('idx_transactions_category', 'transactions', ['category'])
    op.create_index('idx_transactions_merchant', 'transactions', ['merchant_clean'])
    op.create_index('idx_transactions_statement', 'transactions', ['statement_id'])


def downgrade() -> None:
    """Drop transactions and statements tables."""
    
    # Drop indexes first
    op.drop_index('idx_transactions_statement', table_name='transactions')
    op.drop_index('idx_transactions_merchant', table_name='transactions')
    op.drop_index('idx_transactions_category', table_name='transactions')
    op.drop_index('idx_transactions_posted_date', table_name='transactions')
    
    # Drop tables (child first, then parent)
    op.drop_table('transactions')
    op.drop_table('statements')
