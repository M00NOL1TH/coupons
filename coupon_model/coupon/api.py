from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlmodel import Session
from typing_extensions import Annotated

from coupon_app.typings import SessionContextProvider
from coupon_utils.service import CommitFailed, NotFound, ValidationFailed

from .model import Coupon, CouponCreate, CouponStatus, CouponUpdate
from .service import CouponService


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

    def service_provider(session: Annotated[Session, Depends(session_provider)]) -> CouponService:
        """
        FastAPI dependency that creates a coupon service instance for the API.
        """
        return CouponService(session)

    ServiceProvider = Annotated[CouponService, Depends(service_provider)]

    @router.get("/", response_model=list[Coupon])
    def get_all(*, service: ServiceProvider, offset: int = 0, limit: int = Query(default=20, lte=50)):
        """
        Return all the coupons.
        """
        return service.get_all(offset, limit)

    @router.get("/{id}", response_model=Coupon)
    def get_by_id(*, service: ServiceProvider, id: int):
        """
        Return a coupons by ID.
        """
        coupon = service.get_by_id(id)
        if coupon is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found.")
        return coupon

    @router.post("/", status_code=status.HTTP_201_CREATED)
    def create_coupons(*, service: ServiceProvider, data: list[CouponCreate]):
        """
        Create many coupons with all the information:

        Arguments:
        - **code**: Each coupon must have a uniqe coupon code
        - **description**: Description of the coupon
        - **discount**: The amount of discount
        - **discount_type**: The type of discount (_fixed_ or _percentage_)
        - **is_active**: Whether the coupon is currently active
        - **valid_from**: The coupon is valid from this time
        - **valid_until**: The coupon is valid until this time
        """
        try:
            return service.create_many(data)
        except CommitFailed as exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=exception.args,
            )

    @router.delete("/{id}")
    def delete_by_id(*, service: ServiceProvider, id: int):
        """
        Delete a coupons by ID.
        """
        try:
            service.delete_by_id(id)
        except NotFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Coupon not found: {id}.")
        except CommitFailed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to delete coupon: {id}.")

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.patch(
        "/{id}",
        response_model=Coupon,
        response_description="The updated coupon.",
    )
    def update_by_id(*, service: ServiceProvider, id: int, data: CouponUpdate):
        """
        Update a coupon with some of the relevant information:

        Arguments:

        - **description**: Description of the coupon
        - **discount**: The amount of discount
        """
        try:
            return service.update(id, data)
        except NotFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Coupon not found: {id}.")
        except CommitFailed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to update coupon: {id}.")

    @router.get("/{id}/status", response_model=CouponStatus)
    def coupon_status(*, service: ServiceProvider, id: int):
        """
        Returns the status of the coupon with the given ID.
        """
        try:
            return service.status_by_id(id)
        except NotFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Coupon not found: {id}.")

    @router.patch("/apply/{code}")
    def apply_by_code(*, service: ServiceProvider, code: str):
        """
        Apply a coupon.
        """
        try:
            service.apply_by_code(code)
        except ValidationFailed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Coupon not available: {code}.")
        except NotFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Coupon not found: {code}.")
        except CommitFailed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to apply coupon: {code}.")

    return router
