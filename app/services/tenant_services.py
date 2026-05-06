from sqlalchemy.orm import Session

from app.crud.lodge import crud_lodge
from app.crud.user import crud_user
from app.crud.tenantprofile import crud_tenant
from app.core.enums import UserRole
from app.core.exceptions import UserAlreadyExistError, LodgeNotFoundError
from app.core.security import  get_password_hash
from app.models.user import User
from app.schemas.tenantprofile import TenantProfileCreate
from app.schemas.user import UserInternal
from app.services import lodge_service


def sign_up_tenant(
        lodge_id: int,
        db: Session,
        tenant_in: TenantProfileCreate,
):
    if not crud_lodge.get(db, item_id=lodge_id):
        raise LodgeNotFoundError()

    if crud_user.get_user_by_email(db, email=tenant_in.user_info.email):
        raise UserAlreadyExistError(email=tenant_in.user_info.email)

    hashed = get_password_hash(tenant_in.user_info.password)

    base_user_data = UserInternal(
        first_name=tenant_in.user_info.first_name,
        last_name=tenant_in.user_info.last_name,
        phone_no=tenant_in.user_info.phone_no,
        email=tenant_in.user_info.email,
        hashed_password=hashed,
        role=UserRole.TENANT
    )

    return crud_tenant.create_tenant(db, tenant_in=tenant_in, internal_user=base_user_data, lodge_id = lodge_id)



def fetch_lodge_tenants(
        db: Session,
        lodge_id: int,
        landlord_user: User ,
        skip: int,
        limit: int
):

    lodge = lodge_service.verify_lodge_ownership(db, lodge_id=lodge_id, landlord_id=landlord_user.id)
    if not lodge:
        raise LodgeNotFoundError()

    tenants =  crud_tenant.get_tenants(db, lodge_id=lodge_id, skip=skip, max_limit=limit)
    return tenants


