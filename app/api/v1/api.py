from fastapi import APIRouter
from app.api.v1.endpoints import auth, family, milestone, todo

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(family.router, prefix="/family", tags=["family"])
api_router.include_router(milestone.router, prefix="/milestone", tags=["milestone"])
api_router.include_router(todo.router, prefix="/todo", tags=["todo"])
