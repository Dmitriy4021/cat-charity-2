from fastapi import APIRouter

from app.api.endpoints import (
    charity_project_router,
    donation_router,
)
from app.core.user import auth_backend, fastapi_users
from app.schemas.user import UserCreate, UserRead, UserUpdate

main_router = APIRouter()

main_router.include_router(
    charity_project_router,
    prefix='/charity_project',
    tags=['Charity Project'],
)
main_router.include_router(
    donation_router,
    prefix='/donation',
    tags=['Donation'],
)
main_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=['auth'],
)
main_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)

users_router = fastapi_users.get_users_router(UserRead, UserUpdate)
users_router.routes = [
    route for route in users_router.routes if route.name != 'users:delete_user'
]
main_router.include_router(
    users_router,
    prefix='/users',
    tags=['users'],
)
