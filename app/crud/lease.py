# from sqlalchemy.orm import Session
# from app.models.lease import Lease
# from app.models.room import RoomStatus, Room
# from app.schemas.lease import LeaseCreate, LeaseUpdate
# from app.models.tenant import Tenant
# from datetime import datetime
#
#
# def get_leases(db: Session, skip: int = 0, max_limit: int = 50):
#     return db.query(Lease).offset(skip).limit(max_limit).all()
#
#
# def get_lease(db: Session, lease_id: int):
#     return db.query(Lease).filter(Lease.id == lease_id).first()
#
# def get_active_lease_by_room(db: Session, room_id: int):
#     return db.query(Lease).filter(Lease.room_id == room_id, Lease.is_active == True).first()
#
# def create_lease(db: Session, lease_data: LeaseCreate, room: Room):
#     db_lease = Lease(**lease_data.model_dump())
#
#     room.status = RoomStatus.OCCUPIED
#
#     db.add(db_lease)
#     db.commit()
#     db.refresh(db_lease)
#     return db_lease
#
#
# def update_lease(db: Session, lease_data: LeaseUpdate, db_lease: Lease):
#     update_data = lease_data.model_dump(exclude_unset=True)
#
#     for k, v in update_data.items():
#         setattr(db_lease, k, v)
#
#     db.add(db_lease)
#     db.commit()
#     db.refresh(db_lease)
#     return db_lease
#
#
# def terminate_lease(db: Session, db_lease: Lease):
#     db_lease.is_active = False
#     db_lease.room.status = RoomStatus.VACANT
#     db_lease.end_date = datetime.now()
#
#     db.commit()
#     db.refresh(db_lease)
#     return db_lease
#
#
# def get_active_lease_by_tenant(db: Session, tenant: Tenant):
#     return db.query(Lease).filter(Lease.tenant_id == tenant.id, Lease.is_active == True).first()
