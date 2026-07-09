from fastapi import APIRouter

from app.models.finance import FinanceSummary

router = APIRouter()


@router.get("/finance/summary", response_model=FinanceSummary)
def get_finance_summary() -> FinanceSummary:
    return FinanceSummary(
        net_worth=0,
        cash=0,
        investments=0,
        total_debt=0,
        monthly_income=0,
        monthly_expenses=0,
        projected_debt_free_date=None,
    )
