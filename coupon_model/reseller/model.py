from datetime import datetime
from sqlmodel import Column, DateTime, Field, SQLModel


class ResellerBase(SQLModel):
    """
    Reseller
    Base model shared some common attributes.
    """

    name: str


class ResellerTable(ResellerBase, table=True):
    """
    Reseller
    The database model.

    The db table name should be simple: "resellers", but this model is a bit different from the API model.
    """

    __tablename__ = "resellers"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class Reseller(ResellerBase):
    """
    Reseller
    API model.
    """

    id: int
    created_at: datetime


class ResellerCreate(ResellerBase):
    """
    Reseller creation model.

    Arguments:
    - name
    """

    pass


class ResellerUpdate(SQLModel):
    """
    Reseller update model.

    Arguments:
    - name
    """

    name: str | None
