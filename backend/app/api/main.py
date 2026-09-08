from fastapi import APIRouter

from app.api.routes import assistant, catalog, datasources, items, login, private, quality, queries, topics, users, utils
from app.core.config import settings
from app.api.routes.integration import admin_router as integrations_admin

api_router = APIRouter()
api_router.include_router(integrations_admin)
api_router.include_router(quality.router)
api_router.include_router(assistant.router)
api_router.include_router(queries.router)
api_router.include_router(topics.router)
api_router.include_router(catalog.router)
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(datasources.router)


if settings.FASTAPI_ENV == "development":
    api_router.include_router(private.router)
