from pydantic import BaseModel, ConfigDict

from app.schemas.entity_count import EntityCountResponse
from app.schemas.financial import FinancialResponse
from app.schemas.lease import OccupiedRoomLeasesResponse
from app.schemas.room import RoomGridSummary


class LandlordDashboardStats(BaseModel):
    financials : FinancialResponse
    entity_counts: EntityCountResponse
    occupied_rooms_lease: OccupiedRoomLeasesResponse
    vacant_rooms: list[RoomGridSummary]
    maintenance_rooms: list[RoomGridSummary]

    model_config = ConfigDict(from_attributes=True)