from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, agents
from app.api.v1 import investigations

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(investigations.router, prefix="/investigations", tags=["Investigations"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])


