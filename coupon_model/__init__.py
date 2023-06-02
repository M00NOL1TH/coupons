def init_models() -> None:
    """
    Register models to SQLModel's metadata
    """
    from .coupon.model import CouponTable  # noqa
    from .customer.model import CustomerTable  # noqa
    from .reseller.model import ResellerTable  # noqa
    from .coupon_customer_link.model import CouponCustomerLinkTable  # noqa
