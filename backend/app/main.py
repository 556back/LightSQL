import mimetypes
from pathlib import Path

import sentry_sdk
from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.api.deps import SessionDep
from app.api.main import api_router
from app.api.routes.integration import router as integration_router
from app.core.config import settings

FRONTEND_DIR = Path(__file__).parent / "frontend"
# Windows registry MIME mappings may label .js as text/plain, which browsers
# reject for ES modules. Keep frontend delivery consistent across platforms.
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/javascript", ".mjs")


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.FASTAPI_ENV != "development":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)


@app.exception_handler(RequestValidationError)
async def validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    if request.url.path.startswith(
        ("/api/integration/", f"{settings.API_V1_STR}/integrations")
    ):
        return JSONResponse(
            status_code=422,
            content={
                "code": "INVALID_INPUT",
                "message": "请求参数不符合接口约定",
                "request_id": getattr(request.state, "request_id", ""),
                "retryable": False,
            },
        )
    if request.url.path.startswith(
        (
            f"{settings.API_V1_STR}/datasources",
            f"{settings.API_V1_STR}/queries",
            f"{settings.API_V1_STR}/assistant",
            f"{settings.API_V1_STR}/quality",
        )
    ):
        # Never echo a submitted database password in a validation error.
        return JSONResponse(
            status_code=422,
            content={
                "detail": [
                    {"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]}
                    for e in exc.errors()
                ]
            },
        )
    return await request_validation_exception_handler(request, exc)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_HOST],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(integration_router)


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    if request.url.path.startswith("/api/integration/"):
        codes = {
            401: "UNAUTHENTICATED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            410: "EXPIRED",
            422: "INVALID_INPUT",
            429: "RATE_LIMITED",
            503: "UNAVAILABLE",
        }
        return JSONResponse(
            status_code=exc.status_code,
            headers=exc.headers,
            content={
                "code": codes.get(exc.status_code, "REQUEST_FAILED"),
                "message": str(exc.detail),
                "request_id": getattr(request.state, "request_id", ""),
                "retryable": exc.status_code in (429, 503),
            },
        )
    from fastapi.exception_handlers import http_exception_handler

    return await http_exception_handler(request, exc)


@app.middleware("http")
async def integration_headers(request: Request, call_next):
    import uuid

    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    if request.url.path.startswith(
        ("/api/integration/", "/api/v1/integrations", "/embed/")
    ):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "no-referrer"
    if request.url.path != "/embed/ask":
        response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/embed/ask", include_in_schema=False, tags=["embed"])
def embed_page(client_id: str, session: SessionDep):
    import uuid

    from fastapi.responses import FileResponse

    from app.modules.integration.models import IntegrationClient

    try:
        client = session.get(IntegrationClient, uuid.UUID(client_id))
    except ValueError:
        raise HTTPException(404, "嵌入应用不存在") from None
    if not client or not client.enabled or "embed" not in client.config["scopes"]:
        raise HTTPException(404, "嵌入应用不可用")
    origins = " ".join(client.config["origins"])
    if not origins:
        raise HTTPException(403, "尚未登记嵌入来源")
    return FileResponse(
        FRONTEND_DIR / "index.html",
        headers={"Content-Security-Policy": f"frame-ancestors {origins}"},
    )


app.frontend("/", directory=FRONTEND_DIR)
