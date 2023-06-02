from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlmodel import Session
from typing_extensions import Annotated

from coupon_app.typings import SessionContextProvider
from coupon_utils.service import CommitFailed, NotFound

from .model import Customer, CustomerCreate, CustomerUpdate
from .service import CustomerService


def make_routes(*, session_provider: SessionContextProvider) -> APIRouter:
    """
    Customer `APIRouter` factory.

    Arguments:
        session_provider: Session context provider dependency.
    """

    router = APIRouter(
        prefix="/customers",
        tags=["customers"],
    )

    def service_provider(session: Annotated[Session, Depends(session_provider)]) -> CustomerService:
        """
        FastAPI dependency that creates a coupon service instance for the API.
        """
        return CustomerService(session)

    ServiceProvider = Annotated[CustomerService, Depends(service_provider)]

    @router.get("/", response_model=list[Customer])
    def get_all(*, service: ServiceProvider, offset: int = 0, limit: int = Query(default=20, lte=50)):
        """
        Return all the customers.
        """
        return service.get_all(offset, limit)

    @router.get("/{id}", response_model=Customer)
    def get_by_id(*, service: ServiceProvider, id: int):
        """
        Return a customer by ID.
        """
        customer = service.get_by_id(id)
        if customer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
        return customer

    @router.post(
        "/",
        response_model=Customer,
        response_description="The newly created customer",
        status_code=status.HTTP_201_CREATED,
    )
    def create_customer(*, service: ServiceProvider, data: CustomerCreate):
        """
        Create a customer with all the information:

        Arguments:
        - **username**: Each customer must have a uniqe username
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
        Delete a customer by ID.
        """
        try:
            service.delete_by_id(id)
        except NotFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer not found: {id}.")
        except CommitFailed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to delete customer: {id}.")

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.patch(
        "/{id}",
        response_model=Customer,
        response_description="The updated customer.",
    )
    def update_by_id(*, service: ServiceProvider, id: int, data: CustomerUpdate):
        """
        Update a customer's name.

        Arguments:

        - **name**: Display name
        """
        try:
            return service.update(id, data)
        except NotFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer not found: {id}.")
        except CommitFailed:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to update customer: {id}.")

    return router
