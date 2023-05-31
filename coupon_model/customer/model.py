from datetime import datetime
from sqlmodel import Column, DateTime, Field, SQLModel


class BaseCustomer(SQLModel):
    """
    Customer
    Base model shared some common attributes.
    """

    username: str = Field(index=True, unique=True, regex=r"^[a-z0-9][a-z0-9-_.]{3,21}[a-z0-9]$")
    name: str


class CustomerTable(BaseCustomer, table=True):
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


class Customer(BaseCustomer):
    """
    Customer
    API model.
    """

    id: int
    created_at: datetime


class CustomerCreate(BaseCustomer):
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