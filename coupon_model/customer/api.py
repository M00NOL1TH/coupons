from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select
from typing_extensions import Annotated

from coupon_app.typings import SessionContextProvider

from .model import Customer, CustomerCreate, CustomerTable


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

    @router.get("/", response_model=list[Customer])
    def get_all(session: Annotated[Session, Depends(session_provider)]):
        """
        Return all the customers
        """
        return session.exec(select(CustomerTable)).all()

    @router.post(
        "/",
        response_model=Customer,
        response_description="The newly created customer",
        status_code=status.HTTP_201_CREATED,
    )
    def create_customer(customer: CustomerCreate, session: Session = Depends(session_provider)):
        """
        Create a customer with all the information:

        Arguments:
        - **username**: Each customer must have a uniqe username
        - **name**: Display name
        """
        add_customer = CustomerTable.from_orm(customer)
        session.add(add_customer)
        session.commit()
        session.refresh(add_customer)

        return add_customer

    return router
