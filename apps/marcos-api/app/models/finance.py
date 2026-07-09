from pydantic import BaseModel


class FinanceSummary(BaseModel):
    net_worth: float
    cash: float
    investments: float
    total_debt: float
    monthly_income: float
    monthly_expenses: float
    projected_debt_free_date: str | None
