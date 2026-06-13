from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas import user as schema_user
from app.schemas import tenantprofile as schema_tenant

from app.services import user_service
from app.services.tenant_services import sign_up_tenant
from app.core.exceptions import UserAlreadyExistError
