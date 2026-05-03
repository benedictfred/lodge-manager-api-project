from app.core.enums import TenantType, StudentLevel
from app.db.session import  Base
from sqlalchemy import Column, String, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship


class TenantProfile(Base):
    __tablename__ = 'tenant_profiles'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    tenant_type = Column(Enum(TenantType), nullable=False, default=TenantType.STUDENT)
    emergency_contact_name = Column(String(20), nullable=False,  index=True)
    emergency_contact_phone_no = Column(String, nullable=False)
    level = Column(Enum(StudentLevel), nullable=True)
    department = Column(String, nullable=True)
    reg_no = Column(String, nullable=True)
    user = relationship('User', back_populates='tenant_profile')
    # leases = relationship('Lease', back_populates='tenant')

