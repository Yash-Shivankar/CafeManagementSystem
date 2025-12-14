from sqlalchemy import Column, Integer, Date, Numeric, UniqueConstraint
from app.models.Common import Common


class ProfitLoss(Common):
    __tablename__ = "profit_loss"
    __table_args__ = (UniqueConstraint("date", name="uq_profit_loss_date"),)

    id = Column(Integer, primary_key=True, index=True)

    date = Column(Date, nullable=False)

    revenue = Column(Numeric(12, 2), nullable=False)
    expenses = Column(Numeric(12, 2), nullable=False)
    profit = Column(Numeric(12, 2), nullable=False)

    def __repr__(self):
        return f"<ProfitLoss {self.date} profit={self.profit}>"
