from sqlmodel import Session, SQLModel
from typer import Typer

from coupon_app.main import get_db_engine
from coupon_app.settings import get_settings
from coupon_model import init_models  # noqa
from coupon_model.coupon.model import CouponTable
from coupon_model.customer.model import CustomerTable


app = Typer()


@app.command()
def clear_db():
    """
    Clear connected db.
    """

    # Create DB engine.
    engine = get_db_engine(get_settings())

    # Drop all known tables from the database by SQLModel's metadata.
    SQLModel.metadata.drop_all(engine)


@app.command()
def demo_fixture():
    """
    Executes the demo fixture.
    """
    print("Build a demo database...")

    # Create DB engine.
    engine = get_db_engine(get_settings())

    # Initialize the database from SQLModel's metadata.
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        print("Clear database")
        for table in (CouponTable, CustomerTable):
            session.query(table).delete()
            session.commit()


if __name__ == "__main__":
    app()
