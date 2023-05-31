from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select
from typing_extensions import Annotated

from coupon_app.typings import SessionContextProvider

from .model import Coupon, CouponCreate, CouponTable


def make_routes(*, session_provider: SessionContextProvider) -> APIRouter:
    """
    Coupon `APIRouter` factory.

    Arguments:
        session_provider: Session context provider dependency.
    """

    router = APIRouter(
        prefix="/coupons",
        tags=["coupons"],
    )

    @router.get("/", response_model=list[Coupon])
    def get_all(session: Annotated[Session, Depends(session_provider)]):
        """
        Return all the coupons
        """
        return session.exec(select(CouponTable)).all()

    @router.post(
        "/",
        response_model=Coupon,
        response_description="The newly created coupon",
        status_code=status.HTTP_201_CREATED,
    )
    def create_coupon(coupon: CouponCreate, session: Session = Depends(session_provider)):
        """
        Create a coupon with all the information:

        Arguments:
        - **code**: Each coupon must have a uniqe coupon code
        - **description**: Description of the coupon
        - **discount**: The amount of discount
        - **discount_type**: The type of discount (_fixed_ or _percentage_)
        """
        add_coupon = CouponTable.from_orm(coupon)
        session.add(add_coupon)
        session.commit()
        session.refresh(add_coupon)

        return add_coupon

    return router
