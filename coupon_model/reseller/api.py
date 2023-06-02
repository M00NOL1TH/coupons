from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlmodel import Session
from typing_extensions import Annotated

from coupon_app.typings import SessionContextProvider
from coupon_utils.service import CommitFailed, NotFound

from .model import Reseller, ResellerCreate, ResellerUpdate
from .service import ResellerService


def make_routes(*, session_provider: SessionContextProvider) -> APIRouter:
    """
    Reseller `APIRouter` factory.

    Arguments:
        session_provider: Session context provider dependency.
    """

    router = APIRouter(
        prefix="/resellers",
        tags=["resellers"],
    )

    def service_provider(session: Annotated[Session, Depends(session_provider)]) -> ResellerService:
        """
        FastAPI dependency that creates a coupon service instance for the API.
        """
        return ResellerService(session)

    ServiceProvider = Annotated[ResellerService, Depends(service_provider)]

    @router.get("/", response_model=list[Reseller])
    def get_all(*, service: ServiceProvider, offset: int = 0, limit: int = Query(default=20, lte=50)):
        """
        Return all the resellers.
        """
        return service.get_all(offset, limit)

    @router.get("/{id}", response_model=Reseller)
    def get_by_id(*, service: ServiceProvider, id: int):
        """
        Return a reseller by ID.
        """
        reseller = service.get_by_id(id)
        if reseller is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reseller not found.")
        return reseller

    @router.post(
        "/",
        response_model=Reseller,
        response_description="The newly created reseller",
        status_code=status.HTTP_201_CREATED,
    )
    def create_reseller(*, service: ServiceProvider, data: ResellerCreate):
        """
        Create a reseller with all the information:

        Arguments:
        - **name**: Display name
        """
        try:
            return service.create(data)
        except CommitFailed as exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=exception.args,
            )

    @router.delete("/{id}")
    def delete_by_id(*, service: ServiceProvider, id: int):
        """
        Delete a reseller by ID.
        """
        try:
            service.delete_by_id(id)
        except NotFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reseller not found: {id}.")
        except CommitFailed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to delete reseller: {id}.")

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.patch(
        "/{id}",
        response_model=Reseller,
        response_description="The updated reseller.",
    )
    def update_by_id(*, service: ServiceProvider, id: int, data: ResellerUpdate):
        """
        Update a reseller's name.

        Arguments:

        - **name**: Display name
        """
        try:
            return service.update(id, data)
        except NotFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reseller not found: {id}.")
        except CommitFailed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to update reseller: {id}.")

    return router
