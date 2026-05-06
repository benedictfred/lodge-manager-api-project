from typing import Dict, Any

from app.core.enums import UserRole
from app.core.security import get_password_hash
from app.crud.user import crud_user
from app.models.tenantprofile import TenantProfile
from app.models.user import User
from app.schemas.tenantprofile import TenantProfileCreate, TenantProfileUpdate
from sqlalchemy.orm import Session, joinedload
from app.crud.base_crud import CRUDBase
from app.schemas.user import UserCreate, UserInternal


class CRUDTenantProfile(CRUDBase[TenantProfile, TenantProfileCreate, TenantProfileUpdate]):
    def create_tenant(self, db: Session, tenant_in: TenantProfileCreate, internal_user: UserInternal, lodge_id: int):
        try:
            db_user = User(**internal_user.model_dump())
            db.add(db_user)
            db.flush()

            tenant_profile = tenant_in.model_dump(exclude={'user_info'})
            tenant_profile['tenant_info']['user_id'] = db_user.id
            tenant_profile['tenant_info']['lodge_id'] = lodge_id

            db_tenant = TenantProfile(**tenant_profile.get('tenant_info'))
            db.add(db_tenant)
            db.commit()
            db.refresh(db_tenant)

            return db_tenant
        except Exception as e:
            db.rollback()
            raise e

    def get_tenants(self, db: Session, lodge_id: int, skip: int = 0, max_limit=50):
        return db.query(self.model).filter(self.model.lodge_id == lodge_id).offset(skip).limit(max_limit).all()



def get_tenant(db: Session , tenant_id):
    return db.query(TenantProfile).filter(TenantProfile.id == tenant_id).first()

def get_tenant_by_email(db: Session, email: str):
    return db.query(TenantProfile).filter(TenantProfile.email == email).first()


crud_tenant = CRUDTenantProfile(TenantProfile)

def update_tenant(db: Session, db_tenant: TenantProfile, tenant_data: TenantProfileUpdate):


    # Only extract fields that were actually provided in the update request
    update_data = tenant_data.model_dump(exclude_unset=True)

    # Update the model attributes dynamically
    for key, value in update_data.items():
        setattr(db_tenant, key, value)

    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant

def delete_tenant(db: Session, db_tenant: TenantProfile):
    db.delete(db_tenant)
    db.commit()

