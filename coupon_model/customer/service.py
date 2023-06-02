from sqlmodel import select, Session

from coupon_utils.service import CommitFailed, NotFound

from .model import CustomerCreate, CustomerTable, CustomerUpdate


class CustomerService:
    """
    Customer-related services.
    """

    __slots__ = "_session"

    def __init__(self, session: Session) -> None:
        """
        Initialization.

        Arguments:
            session: The session instance.
        """
        self._session = session

    def create(self, data: CustomerCreate) -> CustomerTable:
        """
        Creates a new customer.

        Arguments:
            data: Creation data.

        Raises:
            CommitFailed: If the service fails to commit the new customer.
        """
        session = self._session

        db_item = CustomerTable.from_orm(data)
        session.add(db_item)
        try:
            session.commit()
        except Exception:
            raise CommitFailed("Failed to create the customer.")
        session.refresh(db_item)
        return db_item

    def delete_by_id(self, id: int) -> None:
        """
        Deletes the customer by ID.

        Arguments:
            id: Customer database ID.

        Raises:
            CommitFailed: If the service fails to delete the customer.
            NotFound: If the customer with the given id does not exist.
        """
        session = self._session

        item = self.get_by_id(id)
        if item is None:
            raise NotFound("Customer not found.")

        session.delete(item)
        try:
            session.commit()
        except Exception:
            raise CommitFailed("Failed to delete the customer.")

    def get_all(self, offset: int, limit: int) -> list[CustomerTable]:
        """
        Returns all customers from the database with pagination.
        """
        return self._session.exec(select(CustomerTable).offset(offset).limit(limit)).all()

    def get_by_id(self, id: int) -> CustomerTable | None:
        """
        Returns the customer with the given ID if it exists.

        Arguments:
            id: Customer database ID.
        """
        return self._session.get(CustomerTable, id)

    def update(self, id: int, data: CustomerUpdate) -> CustomerTable:
        """
        Update a customer with the given ID.

        Arguments:
            id: Customer database ID.
            data: Update data.

        Raises:
            CommitFailed: If the service fails to update the customer.
            NotFound: If the customer with the given id does not exist.
        """
        session = self._session

        db_item = self.get_by_id(id)
        if db_item is None:
            raise NotFound("Coupon not found.")

        changes = data.dict(exclude_unset=True)
        for key, value in changes.items():
            setattr(db_item, key, value)

        session.add(db_item)
        try:
            session.commit()
        except Exception:
            raise CommitFailed("Failed to update the customer.")

        session.refresh(db_item)
        return db_item
