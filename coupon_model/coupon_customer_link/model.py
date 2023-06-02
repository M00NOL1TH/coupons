from sqlmodel import Field, SQLModel


class BaseCouponCustomerLink(SQLModel):
    """
    Base coupon-customer link model with shared attributes.
    """

    coupon_id: int = Field(foreign_key="coupons.id", primary_key=True)
    customer_id: int = Field(foreign_key="customers.id", primary_key=True)


class CouponCustomerLinkTable(BaseCouponCustomerLink, table=True):
    """
    Coupon-customer link DB table.
    """

    __tablename__ = "coupon_customer_link"


class CouponCustomerLink(BaseCouponCustomerLink):
    """
    Coupon-customer link.
    """

    pass


class CouponCustomerLinkCreate(BaseCouponCustomerLink):
    """
    Coupon-customer link creation model.
    """

    pass
