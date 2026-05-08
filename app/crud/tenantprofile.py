from typing import Dict, Any, Optional

from app.core.enums import UserRole
from app.core.security import get_password_hash
from app.crud.user import crud_user
from app.models.tenantprofile import TenantProfile
from app.models.user import User
from app.schemas.tenantprofile import TenantProfileCreate, TenantProfileUpdate
from sqlalchemy.orm import Session, joinedload
from app.crud.base_crud import CRUDBase, UpdateSchemaType, ModelType
from app.schemas.user import UserCreate, UserInternal


class CRUDTenantProfile(CRUDBase[TenantProfile, TenantProfileCreate, TenantProfileUpdate]):
    def create_tenant(self, db: Session, tenant_in: TenantProfileCreate, internal_user: UserInternal):
        try:
            db_user = User(**internal_user.model_dump())
            db.add(db_user)
            db.flush()

            tenant_profile = tenant_in.model_dump(exclude={'user_info'})
            tenant_profile['tenant_info']['user_id'] = db_user.id

            db_tenant = TenantProfile(**tenant_profile.get('tenant_info'))
            db.add(db_tenant)
            db.commit()
            db.refresh(db_tenant)

            return db_tenant
        except Exception as e:
            db.rollback()
            raise e

    def get_tenants(self, db: Session, lodge_id: int, skip: int = 0, max_limit=50) -> list[type[TenantProfile]]:
        return db.query(self.model).filter(self.model.lodge_id == lodge_id).offset(skip).limit(max_limit).all()


    def update_tenant(self, db: Session, update_data: UpdateSchemaType, base_user: User,
                      tenant_user: TenantProfile) -> ModelType:

        tenant_profile_dict: dict = update_data.model_dump(exclude_unset=True, exclude={'user_info'}).get('tenant_info',
                                                                                                          None)

        user_data_dict: dict = update_data.model_dump(exclude_unset=True, exclude={'tenant_info'}).get('user_info',
                                                                                                       None)

        try:

            for k, v in user_data_dict.items():
                setattr(base_user, k, v)

            db.add(base_user)

            for k, v in tenant_profile_dict.items():
                setattr(tenant_user, k, v)

            db.add(tenant_user)
            db.commit()
            db.refresh(tenant_user)
            return tenant_user

        except Exception as e:
            db.rollback()
            raise e





crud_tenant = CRUDTenantProfile(TenantProfile)
