from datetime import datetime, timedelta
import random
import string

from sqlmodel import select, Session, SQLModel
from typer import Typer

from coupon_app.main import get_db_engine
from coupon_app.settings import get_settings
from coupon_model import init_models  # noqa
from coupon_model.coupon.model import CouponTable, CouponCreate, DiscountType
from coupon_model.customer.model import CustomerTable, CustomerCreate
from coupon_model.coupon_customer_link.model import CouponCustomerLinkTable


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

    now = datetime.utcnow()

    with Session(engine) as session:
        print("Clear database")

        for table in (CouponTable, CustomerTable):
            session.query(table).delete()
            session.commit()

        print("Create customers")

        session.add_all(
            [
                CustomerTable.from_orm(
                    CustomerCreate(
                        name=f"Customer {i}",
                        username=f"customer{i}",
                    )
                )
                for i in range(10)
            ]
        )
        session.commit()

        print("Create coupons")

        session.add_all(
            [
                CouponTable.from_orm(
                    CouponCreate(
                        code="".join(random.choice(string.ascii_uppercase) for i in range(8)),
                        description="The greatest discount",
                        discount=42,
                        discount_type=DiscountType.fixed if i % 3 == 1 else DiscountType.percentage,
                        is_active=True if i % 2 == 1 else False,
                        valid_from=now + timedelta(days=random.randrange(-7, 7)),
                        valid_until=now + timedelta(days=random.randrange(14, 28)),
                    )
                )
                for i in range(20)
            ]
        )

        session.commit()

        print("Create coupon-customer links")

        all_coupons = session.exec(select(CouponTable)).all()

        def get_random_coupons() -> list[CouponTable]:
            return random.sample(all_coupons, 3)

        for customer in session.exec(select(CustomerTable)).all():
            session.add_all(
                [
                    CouponCustomerLinkTable(
                        coupon_id=coupon.id,
                        customer_id=customer.id,
                    )
                    for coupon in get_random_coupons()
                ]
            )

        session.commit()


if __name__ == "__main__":
    app()
