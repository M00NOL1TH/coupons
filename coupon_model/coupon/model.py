from datetime import datetime
from pydantic import BaseModel
from sqlmodel import Column, DateTime, Field, SQLModel
from enum import Enum


class DiscountType(str, Enum):
    """
    Discount types enum.
    """

    fixed = "fixed"
    percentage = "percentage"


class CouponBase(SQLModel):
    """
    Coupon
    Base model shared some common attributes.
    """

    code: str = Field(index=True, regex=r"^[A-Z0-9]{8}$", unique=True)
    description: str
    discount: int
    discount_type: DiscountType
    is_active: bool
    valid_from: datetime
    valid_until: datetime


class CouponTable(CouponBase, table=True):
    """
    Coupon
    The database model.

    The db table name should be simple: "coupons", but this model is a bit different from the API model.
    """

    __tablename__ = "coupons"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class Coupon(CouponBase):
    """
    Coupon
    API model.
    """

    id: int
    created_at: datetime


class CouponCreate(CouponBase):
    """
    Coupon creation model.

    Arguments:
    - code
    - description
    - discount
    - discount_type
    """

    pass


class CouponUpdate(SQLModel):
    """
    Coupon update model.

    Arguments:
    - description
    - discount
    """

    description: str | None
    discount: int | None
    valid_from: datetime | None
    valid_until: datetime | None


class CouponStatus(BaseModel):
    """
    Coupon status response model.
    """

    is_active: bool
    is_valid: bool


class CouponApplied(BaseModel):
    """
    A discount earned by a used coupon.
    """

    discount: int
    discount_type: DiscountType
