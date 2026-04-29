# from app.models.tenant import Tenant
# from app.schemas.tenant import TenantCreate, TenantUpdate
# from sqlalchemy.orm import Session
#
#
#
# def get_tenants(db: Session, skip: int = 0, max_limit= 50):
#     return db.query(Tenant).offset(skip).limit(max_limit).all()
#
#
# def get_tenant(db: Session , tenant_id):
#     return db.query(Tenant).filter(Tenant.id == tenant_id).first()
#
# def get_tenant_by_email(db: Session, email: str):
#     return db.query(Tenant).filter(Tenant.email == email).first()
#
# def create_tenant(db:Session, tenant_data: TenantCreate):
#     db_tenant = Tenant(**tenant_data.model_dump())
#     db.add(db_tenant)
#     db.commit()
#     db.refresh(db_tenant)
#     return db_tenant
#
# def update_tenant(db: Session, db_tenant: Tenant, tenant_data: TenantUpdate):
#
#
#     # Only extract fields that were actually provided in the update request
#     update_data = tenant_data.model_dump(exclude_unset=True)
#
#     # Update the model attributes dynamically
#     for key, value in update_data.items():
#         setattr(db_tenant, key, value)
#
#     db.add(db_tenant)
#     db.commit()
#     db.refresh(db_tenant)
#     return db_tenant
#
# def delete_tenant(db: Session, db_tenant: Tenant):
#     db.delete(db_tenant)
#     db.commit()
#     db.close()
