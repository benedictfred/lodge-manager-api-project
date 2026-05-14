from pydantic import BaseModel, ConfigDict


class FinancialResponse(BaseModel):
    expected_revenue: int
    collected_revenue: int
    outstanding_revenue: int

    model_config = ConfigDict(from_attributes=True)