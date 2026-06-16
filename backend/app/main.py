from fastapi import FastAPI
from app.core.config import settings
from app.db import base
from app.api.v1.user import router as user_router
from app.api.v1.lodges import router as lodge_router
from app.api.v1.rooms import router as room_router
from app.api.v1.tenants import router as tenant_router
from app.api.v1.leases import router as lease_router
from app.api.v1.payments import router as payment_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.handlers import lodge_ops_handlers
from app.api.v1.dashboards.landlord_dashboard import router as landlord_dashboard_router
app = FastAPI(title=settings.PROJECT_NAME, exception_handlers=lodge_ops_handlers)

# Explicitly list the allowed origins instead of using '*'
origins = [
    "http://localhost:5173", # Default for Vite React apps
    "http://localhost:3000", # Default for Create React App
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(user_router, prefix='/api/v1/auth', tags=['Authentication'])

app.include_router(lodge_router, prefix='/api/v1/lodges', tags=['Lodges'])

app.include_router(room_router, prefix='/api/v1/rooms', tags=['Rooms'])

app.include_router(tenant_router, prefix='/api/v1/tenants', tags=['Tenants'])

app.include_router(lease_router, prefix='/api/v1/leases', tags=['Leases'])


app.include_router(payment_router, prefix='/api/v1/payments', tags=['Payments'])


app.include_router(landlord_dashboard_router, prefix='/api/v1/dashboard-landlord', tags=['Dashboards'])

@app.get("/healthy")
def health_status():
    return {"message": f"Your {settings.PROJECT_NAME} is working well"}


