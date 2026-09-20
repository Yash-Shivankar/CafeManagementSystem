from sqlalchemy import Column, Date, ForeignKey, Index, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.Common import Common


class ProfitLoss(Common):
    __tablename__ = "profit_loss"
    __table_args__ = (
        UniqueConstraint("outlet_id", "date", name="uq_profit_loss_outlet_date"),
        Index("ix_profit_loss_outlet_deleted", "outlet_id", "is_deleted"),
    )

    id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(
        Integer,
        ForeignKey("outlets.id"),
        nullable=False,
        index=True,
    )

    date = Column(Date, nullable=False)

    revenue = Column(Numeric(12, 2), nullable=False)
    expenses = Column(Numeric(12, 2), nullable=False)
    profit = Column(Numeric(12, 2), nullable=False)

    outlet = relationship("Outlet", foreign_keys=[outlet_id])

    def __repr__(self):
        return f"<ProfitLoss {self.date} profit={self.profit}>"
