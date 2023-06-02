from typing import TYPE_CHECKING

from datetime import datetime
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel

from coupon_model.coupon_customer_link.model import CouponCustomerLinkTable

if TYPE_CHECKING:
    from coupon_model.coupon.model import Coupon, CouponTable


class CustomerBase(SQLModel):
    """
    Customer
    Base model shared some common attributes.
    """

    username: str = Field(index=True, unique=True, regex=r"^[a-z0-9][a-z0-9-_.]{3,21}[a-z0-9]$")
    name: str


class CustomerTable(CustomerBase, table=True):
    """
    Customer
    The database model.

    The db table name should be simple: "customers", but this model is a bit different from the API model.
    """

    __tablename__ = "customers"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    coupons: list["CouponTable"] = Relationship(back_populates="customers", link_model=CouponCustomerLinkTable)


class Customer(CustomerBase):
    """
    Customer
    API model.
    """

    id: int
    created_at: datetime


class CustomerCreate(CustomerBase):
    """
    Customer creation model.

    Arguments:
    - username
    - name
    """

    pass


class CustomerUpdate(SQLModel):
    """
    Customer update model.

    Arguments:
    - name
    """

    name: str | None
