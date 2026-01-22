"""Repository pattern for database operations."""
from datetime import date

from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from spendsense.models import Transaction, Statement


class StatementRepository:
    """Database operations for Statement model."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, filename: str, file_hash: str) -> Statement:
        """Create a new statement record."""
        stmt = Statement(filename=filename, file_hash=file_hash)
        self.session.add(stmt)
        self.session.flush()
        return stmt
    
    def get_by_hash(self, file_hash: str) -> Statement | None:
        """Find statement by file hash."""
        return self.session.query(Statement).filter(
            Statement.file_hash == file_hash
        ).first()
    
    def update_count(self, statement_id: int, count: int) -> None:
        """Update transaction count for a statement."""
        stmt = self.session.query(Statement).get(statement_id)
        if stmt:
            stmt.transaction_count = count
    
    def get_all(self) -> list[Statement]:
        """Get all statements."""
        return self.session.query(Statement).order_by(Statement.uploaded_at.desc()).all()


class TransactionRepository:
    """Database operations for Transaction model."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(
        self,
        posted_date: date,
        amount: float,
        description: str,
        dedupe_hash: str,
        merchant_clean: str | None = None,
        category: str | None = None,
        statement_id: int | None = None,
    ) -> Transaction | None:
        """
        Create a transaction if it doesn't exist.
        Returns None if duplicate (by dedupe_hash).
        """
        existing = self.session.query(Transaction).filter(
            Transaction.dedupe_hash == dedupe_hash
        ).first()
        
        if existing:
            return None
        
        txn = Transaction(
            posted_date=posted_date,
            amount=abs(amount),
            description=description,
            merchant_clean=merchant_clean,
            category=category,
            statement_id=statement_id,
            dedupe_hash=dedupe_hash,
        )
        self.session.add(txn)
        return txn
    
    def get_by_id(self, txn_id: int) -> Transaction | None:
        """Get transaction by ID."""
        return self.session.query(Transaction).get(txn_id)
    
    def update_category(self, txn_id: int, category: str) -> None:
        """Update category of a transaction."""
        txn = self.session.query(Transaction).get(txn_id)
        if txn:
            txn.category = category
    
    # =========================================================================
    # Analytics Queries
    # =========================================================================
    
    def get_available_months(self) -> list[str]:
        """Get list of months with transactions (YYYY-MM format)."""
        results = self.session.query(
            func.strftime('%Y-%m', Transaction.posted_date).label('month')
        ).distinct().order_by('month').all()
        return [r.month for r in results]
    
    def get_for_month(self, year: int, month: int) -> list[Transaction]:
        """Get all transactions for a given month."""
        return self.session.query(Transaction).filter(
            extract('year', Transaction.posted_date) == year,
            extract('month', Transaction.posted_date) == month
        ).order_by(Transaction.posted_date).all()
    
    def get_category_totals(self, year: int, month: int) -> list[tuple[str, float]]:
        """Get category totals for a given month."""
        results = self.session.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total')
        ).filter(
            extract('year', Transaction.posted_date) == year,
            extract('month', Transaction.posted_date) == month
        ).group_by(Transaction.category).order_by(
            func.sum(Transaction.amount).desc()
        ).all()
        return [(r.category or "Uncategorized", r.total) for r in results]
    
    def get_merchant_totals(self, year: int, month: int) -> list[tuple[str, float]]:
        """Get merchant totals for a given month."""
        results = self.session.query(
            Transaction.merchant_clean,
            func.sum(Transaction.amount).label('total')
        ).filter(
            extract('year', Transaction.posted_date) == year,
            extract('month', Transaction.posted_date) == month
        ).group_by(Transaction.merchant_clean).order_by(
            func.sum(Transaction.amount).desc()
        ).all()
        return [(r.merchant_clean or "Unknown", r.total) for r in results]
    
    def get_top_transactions(self, year: int, month: int, limit: int = 5) -> list[Transaction]:
        """Get top N transactions by amount for a given month."""
        return self.session.query(Transaction).filter(
            extract('year', Transaction.posted_date) == year,
            extract('month', Transaction.posted_date) == month
        ).order_by(Transaction.amount.desc()).limit(limit).all()
    
    def get_monthly_total(self, year: int, month: int) -> float:
        """Get total spending for a given month."""
        result = self.session.query(func.sum(Transaction.amount)).filter(
            extract('year', Transaction.posted_date) == year,
            extract('month', Transaction.posted_date) == month
        ).scalar()
        return result or 0.0
    
    def get_count(self, year: int, month: int) -> int:
        """Get transaction count for a given month."""
        return self.session.query(Transaction).filter(
            extract('year', Transaction.posted_date) == year,
            extract('month', Transaction.posted_date) == month
        ).count()
