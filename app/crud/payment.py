from sqlalchemy.orm import Session
from app.models.payment import  Payment
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.crud.base_crud import  CRUDBase
from sqlalchemy import func


class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentResponse]):
    def get_payments_aggregate_by_lease_id(self, db: Session, lease_id: int):
        return db.query(func.sum(self.model.amount_paid)).filter(Payment.lease_id == lease_id).scalar()



crud_payment = CRUDPayment(Payment)

