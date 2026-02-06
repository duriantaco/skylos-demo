from fastapi import FastAPI
from app.logging import configure_logging
from app.api.routers import api_router
from app.db.session import init_db
from app.integrations.bootstrap import init_integrations  # NEW

# UNUSED: not used anywhere in runtime
APP_DISPLAY_NAME = "Skylos Demo API"  # UNUSED

def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="Skylos Demo API",
        version="0.1.0",
    )

    app.include_router(api_router)

    init_integrations(app)

    @app.on_event("startup")
    def _startup() -> None:
        init_db()

    return app


app = create_app()
