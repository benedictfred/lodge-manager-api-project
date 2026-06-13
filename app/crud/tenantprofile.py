from typing import Dict, Any, Optional

from app.core.enums import UserRole
from app.core.security import get_password_hash
from app.crud.user import crud_user
from app.models.tenantprofile import TenantProfile
from app.models.user import User
from app.schemas.tenantprofile import TenantProfileCreate, TenantProfileUpdate, TenantInfoUpdate
from sqlalchemy.orm import Session, joinedload
from app.crud.base_crud import CRUDBase, UpdateSchemaType, ModelType
from app.schemas.user import UserCreate, UserInternal, UserUpdate


class CRUDTenantProfile(CRUDBase[TenantProfile, TenantProfileCreate, TenantProfileUpdate]):
    _USER_UPDATE_FIELDS = {'first_name', 'last_name', 'phone_no', 'email'} # email update will be by a security feature
    _TENANT_UPDATE_FIELDS = {'emergency_contact_name', 'emergency_contact_phone_no', 'level', 'reg_no', 'department'
                             'tenant_type'} #other specific fields for specific tenants will also be a security feature

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


    def update_tenant(self, db: Session, update_data: TenantProfileUpdate, base_user: User,
                      tenant_user: TenantProfile) -> ModelType:

        user_data_dict = update_data.user_info.model_dump(exclude_unset=True) if isinstance(update_data.user_info, UserUpdate) else {}
        tenant_profile_dict = update_data.tenant_info.model_dump(exclude_unset=True) if isinstance(update_data.tenant_info, TenantInfoUpdate) else {}

        try:

            for field in self._USER_UPDATE_FIELDS:
                if field in user_data_dict:
                    setattr(base_user, field, user_data_dict[field])

            db.add(base_user)

            for field in self._TENANT_UPDATE_FIELDS:
                if field in tenant_profile_dict:
                    setattr(tenant_user, field, tenant_profile_dict[field])

            db.add(tenant_user)

            db.commit()
            db.refresh(tenant_user)
            return tenant_user

        except Exception as e:
            db.rollback()
            raise e





crud_tenant = CRUDTenantProfile(TenantProfile)
