from typing import Optional

from sqlalchemy.orm import Session
from app.core.enums import UserRole, BadgeTexts
from app.models.room import Room
from app.schemas.lease import OccupiedRoomLeasesResponse
from app.schemas.lodge import LodgeCreate, LodgeUpdate
from app.core.exceptions import LodgeAlreadyExistError, LodgeNotFoundError
from app.crud.lodge import crud_lodge
from app.crud.room import crud_room
from app.schemas.room import RoomGridSummary
from app.services import lodge_service
from typing import Union
from app.core.enums import RoomStatus


def get_landlord_dashboard(
        db: Session,
        lodge_id: int,
        landlord_id: int,
        filter_by: Union[BadgeTexts, RoomStatus],
        skip: Optional[int] = None,
        limit: Optional[int] = None
):
    # check if the lodge exist and is owned by the landlord
    #TODO: SUM ALL financial for the landlords revenue(expected, collected & outstanding)
    lodge = lodge_service.verify_lodge_ownership(lodge_id=lodge_id, landlord_id=landlord_id)

    financials = crud_room.get_financials_related_to_active_lease(lodge_id=lodge.id)

    # Todo: count all the entities tied to the landlord's lodge( rooms, tenant, room statuses)


    #Todo: group rooms into occupied(safe, expiring & overdue) , vacant & maintenance
    raw_dashboard_rooms = crud_room.get_dashboard_rooms(db, filter_by=filter_by, lodge_id=lodge_id, skip=skip,limit=limit)
    occupied_rooms_lease = OccupiedRoomLeasesResponse(
        safe= [RoomGridSummary(**r) for r in raw_dashboard_rooms if r.badge_text == BadgeTexts.SAFE],
        expiring= [RoomGridSummary(**r) for  r in raw_dashboard_rooms if r.badge_text == BadgeTexts.EXPIRING],
        overdue= [RoomGridSummary(**r) for  r in raw_dashboard_rooms if r.badge_text == BadgeTexts.OVERDUE],
        owing= [RoomGridSummary(**r) for  r in raw_dashboard_rooms if r.badge_text == BadgeTexts.OWING]
    )
    pass
