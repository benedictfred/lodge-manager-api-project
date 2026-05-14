from sqlalchemy.orm import Session
from app.core.enums import UserRole
from app.models.room import Room
from app.schemas.lodge import LodgeCreate, LodgeUpdate
from app.core.exceptions import LodgeAlreadyExistError, LodgeNotFoundError
from app.crud.lodge import crud_lodge


def get_landlord_dashboard(
        lodge_id: int,
        landlord_id: int
):
    # check if the lodge exist and is owned by the landlord
    #TODO: SUM ALL financial for the landlords revenue(expected, collected & outstanding)
    #find all rooms and sum their agreed_rent_amt columns , don't forget to account for None
    #rules for expected -> only the most recent lease are allowed
    #-if active-lease/pending termination, use the agreed amt from the lease contract and store in the current expected revenue
    #-if lease is vacant/maintenance, store the base_rent_price from the room in the total potential revenue
    #-if lease is expired/terminated, they don't contribute to the current expected revenue


    #find all rooms with the most recent lease(active, pending, expired, terminated) and sum all their payments within the time frame
    #rules , rooms with no leases(vacant and maintenance) don't contribute to this

    #only the most recent leases contribute to this
    #each lease have payments so they also shd have balance(agreed_rent_amt for that lease - total payments made for that lease)
    #only add the balance to outstanding if it's > 0 for that lease(have unpaid rent)


    #Todo: count all the entities tied to the landlord's lodge( rooms, tenant, room statuses)
    #Todo: group rooms into occupied(safe, expiring & overdue) , vacant & maintenance

    pass
