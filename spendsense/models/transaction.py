"""Transaction model - represents a single financial transaction."""
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import String, Float, Date, Text, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from spendsense.models.base import Base

if TYPE_CHECKING:
    from spendsense.models.statement import Statement


class Transaction(Base):
    """
    Represents a single financial transaction.
    
    Fields:
    - posted_date: For month filtering, trends, comparisons
    - amount: Stored positive for totals, top spends
    - description: Raw statement text for search/debugging
    - merchant: Cleaned merchant name for grouping
    - category: Assigned category for analytics
    - statement_id: Links to source upload
    - dedupe_hash: Prevents duplicate imports
    """
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    posted_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    merchant: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    statement_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("statements.id", ondelete="CASCADE"),
        nullable=True
    )
    dedupe_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    
    # Relationship
    statement: Mapped["Statement | None"] = relationship(back_populates="transactions")

    # Indexes for common queries
    __table_args__ = (
        Index("idx_transactions_posted_date", "posted_date"),
        Index("idx_transactions_category", "category"),
        Index("idx_transactions_merchant", "merchant"),
        Index("idx_transactions_statement", "statement_id"),
    )

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, date={self.posted_date}, amount={self.amount})>"
