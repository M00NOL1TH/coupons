from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlmodel import Session
from typing_extensions import Annotated

from coupon_app.typings import SessionContextProvider
from coupon_utils.service import CommitFailed, NotFound

from .model import CouponCustomerLink, CouponCustomerLinkCreate
from .service import CouponCustomerLinkService


def make_routes(*, session_provider: SessionContextProvider) -> APIRouter:
    """
    Customer `APIRouter` factory.

    Arguments:
        session_provider: Session context provider dependency.
    """

    router = APIRouter(
        prefix="/coupon-customer-link",
        tags=["coupon-customer-link"],
    )

    def service_provider(session: Annotated[Session, Depends(session_provider)]) -> CouponCustomerLinkService:
        """
        FastAPI dependency that creates a coupon service instance for the API.
        """
        return CouponCustomerLinkService(session)

    ServiceProvider = Annotated[CouponCustomerLinkService, Depends(service_provider)]

    @router.get("/", response_model=list[CouponCustomerLink])
    def get_all(*, service: ServiceProvider, offset: int = 0, limit: int = Query(default=20, lte=50)):
        """
        Return all the customers.
        """
        return service.get_all(offset, limit)

    @router.get("/{coupon_id}/{customer_id}", response_model=CouponCustomerLink)
    def get_by_ids(*, service: ServiceProvider, coupon_id: int, customer_id: int):
        """
        Return a coupon-customer-link by IDs.
        """
        link = service.get_by_ids(coupon_id=coupon_id, customer_id=customer_id)
        if link is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon-customer-link not found.")
        return link

    @router.post(
        "/",
        response_model=CouponCustomerLink,
        response_description="The newly created link",
        status_code=status.HTTP_201_CREATED,
    )
    def create_link(*, service: ServiceProvider, data: CouponCustomerLinkCreate):
        """
        Create a coupon-customer-link.
        """
        try:
            return service.create(data)
        except CommitFailed as exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=exception.args,
            )

    @router.delete("/{coupon_id}/{customer_id}")
    def delete_by_ids(*, service: ServiceProvider, coupon_id: int, customer_id: int):
        """
        Delete a coupon-customer-link by IDs.
        """
        try:
            service.delete_by_ids(coupon_id=coupon_id, customer_id=customer_id)
        except NotFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Link not found: {coupon_id}-{customer_id}."
            )
        except CommitFailed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to delete link: {coupon_id}-{customer_id}."
            )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router
