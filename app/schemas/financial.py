"""
Pydantic schemas for financial summaries.

This module contains the schema used to represent financial statistics
for the landlord's dashboard.
"""
from pydantic import BaseModel, ConfigDict


class FinancialResponse(BaseModel):
    """
    Schema representing the financial summary for a landlord.

    Attributes:
        potential_revenue (int): The maximum possible revenue.
        expected_revenue (int): The revenue expected based on current leases.
        collected_revenue (int): The actual revenue collected.
        unpaid_rent (int): The amount of rent that is unpaid.
    """
    potential_revenue: int
    expected_revenue: int
    collected_revenue: int
    unpaid_rent: int

    model_config = ConfigDict(from_attributes=True)