import fastapi
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


def create_app(project_name: str) -> fastapi.FastAPI:
    global ROOT_PATH
    ROOT_PATH = ""

    app = FastAPI(
        root_path=ROOT_PATH,
        name=project_name,
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    @limiter.limit("10/minute")
    async def root(request: Request):
        return RedirectResponse(url=f"{ROOT_PATH}/docs")

    Instrumentator().instrument(app).expose(app)

    return app