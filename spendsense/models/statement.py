"""Statement model - represents an uploaded bank statement."""
from datetime import datetime, UTC
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from spendsense.models.base import Base

if TYPE_CHECKING:
    from spendsense.models.transaction import Transaction


class Statement(Base):
    """
    Represents an uploaded bank/credit card statement (PDF).
    
    Used to:
    - Track which file transactions came from
    - Prevent duplicate uploads (via file_hash)
    - Enable rollback/reprocessing of a statement
    """
    __tablename__ = "statements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC)
    )
    transaction_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationship
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="statement",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Statement(id={self.id}, filename={self.filename})>"
