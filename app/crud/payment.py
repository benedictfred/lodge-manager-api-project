# from sqlalchemy.orm import Session
# from app.models.payment import  Payment
# from app.schemas.payment import PaymentCreate, PaymentUpdate
#
#
#
# def get_payments(db:Session, skip:int = 0, limit: int=20):
#     return db.query(Payment).offset(skip).limit(limit).all()
#
#
# def get_payment_by_id(db: Session, pay_id: int):
#     return db.query(Payment).filter(Payment.id == pay_id).first()
#
#
# def create_payment(db:Session, pay_data: PaymentCreate):
#     db_payment = Payment(**pay_data.model_dump())
#
#     db.add(db_payment)
#     db.commit()
#     db.refresh(db_payment)
#     return db_payment
#
# def update_payment(db: Session, pay_data: PaymentUpdate, db_payment: Payment):
#     update_data = pay_data.model_dump(exclude_unset=True)
#
#     for key, value in update_data.items():
#         setattr(db_payment, key, value)
#
#     db.add(db_payment)
#     db.commit()
#     db.refresh(db_payment)
#     return db_payment
#
# def get_payments_by_lease_id(db: Session , lease_id: int):
#     return db.query(Payment).filter(Payment.lease_id == lease_id).all()
#
# def get_payment_by_lease_id(db: Session, lease_id: int):
#     return db.query(Payment).filter(Payment.lease_id == lease_id).first()
#
