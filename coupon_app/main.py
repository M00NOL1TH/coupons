from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.future import Engine
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator

from .settings import get_settings, Settings


def get_db_engine(settings: Settings = Depends(get_settings)) -> "Engine":
    """
    Create the SQLAlchemy Engine instance.
    """
    return create_engine(settings.database_url, echo=settings.database_echo)


def get_db_session(engine: "Engine" = Depends(get_db_engine)) -> Generator[Session, None, None]:
    """
    Session provider
    """
    with Session(engine) as session:
        yield session


def register_routes(app: FastAPI, *, api_prefix="/api/v1") -> None:
    """
    Registers all the routes of the application.

    Arguments:
        app: The FastAPI application where the routes should be registered.
        api_prefix: API prefix for the included routes.
    """
    from coupon_model.coupon.api import make_routes as make_coupon_routes
    from coupon_model.customer.api import make_routes as make_customer_routes
    from coupon_model.reseller.api import make_routes as make_reseller_routes
    from coupon_model.coupon_customer_link.api import make_routes as make_coupon_customer_link_routes

    app.include_router(make_coupon_routes(session_provider=get_db_session), prefix=api_prefix)
    app.include_router(make_customer_routes(session_provider=get_db_session), prefix=api_prefix)
    app.include_router(make_reseller_routes(session_provider=get_db_session), prefix=api_prefix)
    app.include_router(make_coupon_customer_link_routes(session_provider=get_db_session), prefix=api_prefix)


def create_app() -> FastAPI:
    """
    Creates a new application instance.
    """
    from coupon_model.coupon.metadata import metadata as coupons_metadata
    from coupon_model.customer.metadata import metadata as customers_metadata
    from coupon_model.reseller.metadata import metadata as reseller_metadata
    from coupon_model.coupon_customer_link.metadata import metadata as coupon_customer_link_metadata

    tags_metadata = [coupons_metadata, customers_metadata, reseller_metadata, coupon_customer_link_metadata]

    app = FastAPI(
        title="CouponAPI",
        description="Simple coupon app with FastAPI, SQLModel and PostgresSQL",
        version="0.0.1",
        openapi_tags=tags_metadata,
    )
    settings = get_settings()

    # Init DB and create tables at startup

    @app.on_event("startup")
    def on_startup() -> None:
        """
        Initialize DB at startup
        """
        # Register all the models.
        from coupon_model import init_models  # noqa

        # Create DB engine.
        engine = get_db_engine(settings)

        # Initialize the database from SQLModel's metadata.
        SQLModel.metadata.create_all(engine)

    # Routing

    register_routes(app, api_prefix=settings.api_prefix)

    @app.get("/", response_class=RedirectResponse)
    def redirect_docs():
        return "/docs"

    return app
