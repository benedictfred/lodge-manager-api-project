from pydantic import BaseModel, ConfigDict


class FinancialResponse(BaseModel):
    potential_revenue: int
    expected_revenue: int
    collected_revenue: int
    unpaid_rent: int

    model_config = ConfigDict(from_attributes=True)