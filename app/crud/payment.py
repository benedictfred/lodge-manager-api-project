from sqlalchemy.orm import Session
from app.models.payment import  Payment
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.crud.base_crud import  CRUDBase
from sqlalchemy import func, select


class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentResponse]):
    def get_payments_aggregate_by_lease_id(self, db: Session, lease_id: int):
        return db.query(func.sum(self.model.amount_paid)).filter(Payment.lease_id == lease_id).scalar()

    def get_lease_payments(self, db: Session, lease_id: int, skip: int = 0, limit: int = 50) -> list[type[Payment]]:
        return db.query(self.model).filter(self.model.lease_id == lease_id).offset(skip).limit(limit).all()

crud_payment = CRUDPayment(Payment)

