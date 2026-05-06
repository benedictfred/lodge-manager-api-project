from sqlalchemy.orm import Session

from app.crud.lodge import crud_lodge
from app.crud.user import crud_user
from app.crud.tenantprofile import crud_tenant
from app.core.enums import UserRole
from app.core.exceptions import UserAlreadyExistError, LodgeNotFoundError, UserNotFoundError
from app.core.security import get_password_hash
from app.models.tenantprofile import TenantProfile
from app.models.user import User
from app.schemas.tenantprofile import TenantProfileCreate, TenantProfileUpdate
from app.schemas.user import UserInternal
from app.services import lodge_service
from app.services.lodge_service import is_landlord, is_tenant


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

    return crud_tenant.create_tenant(db, tenant_in=tenant_in, internal_user=base_user_data, lodge_id=lodge_id)


def fetch_lodge_tenants(
        db: Session,
        lodge_id: int,
        landlord_user: User,
        skip: int,
        limit: int
):
    lodge = lodge_service.verify_lodge_ownership(db, lodge_id=lodge_id, landlord_id=landlord_user.id)
    if not lodge:
        raise LodgeNotFoundError()

    tenants = crud_tenant.get_tenants(db, lodge_id=lodge_id, skip=skip, max_limit=limit)
    return tenants


def update_tenant_profile(
        db: Session,
        base_user: User,
        update_data: TenantProfileUpdate
):

    tenant_user = base_user.tenantprofile
    return crud_tenant.update_tenant(db, update_data=update_data, tenant_user=tenant_user, base_user=base_user)


def fetch_tenant(
        db: Session,
        tenant_id: int,
        current_user: User
):
    # check the role of the user
    #if landlord -> fetch the tenant by the id -> error
    #check if the lodge the tenant belongs to has a landlord id that is same as the current landlord user -> error
    #if true -> return the found tenant
    # if tenant -> use the user_realtionship to get the tenant associated with the logged in user

    if is_landlord(current_user.role):
        tenant = crud_tenant.get(db, item_id=tenant_id)

        if not tenant:
            raise UserNotFoundError()

        if tenant.lodge.landlord_id != current_user.id:
            raise UserNotFoundError()

        return tenant

    tenant = current_user.tenantprofile
    return tenant


