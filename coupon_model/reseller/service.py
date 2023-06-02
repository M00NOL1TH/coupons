from sqlmodel import select, Session

from coupon_utils.service import CommitFailed, NotFound

from .model import ResellerCreate, ResellerTable, ResellerUpdate


class ResellerService:
    """
    Reseller-related services.
    """

    __slots__ = "_session"

    def __init__(self, session: Session) -> None:
        """
        Initialization.

        Arguments:
            session: The session instance.
        """
        self._session = session

    def create(self, data: ResellerCreate) -> ResellerTable:
        """
        Creates a new reseller.

        Arguments:
            data: Creation data.

        Raises:
            CommitFailed: If the service fails to commit the new reseller.
        """
        session = self._session

        db_item = ResellerTable.from_orm(data)
        session.add(db_item)
        try:
            session.commit()
        except Exception:
            raise CommitFailed("Failed to create the reseller.")
        session.refresh(db_item)
        return db_item

    def delete_by_id(self, id: int) -> None:
        """
        Deletes the reseller by ID.

        Arguments:
            id: Reseller database ID.

        Raises:
            CommitFailed: If the service fails to delete the reseller.
            NotFound: If the reseller with the given id does not exist.
        """
        session = self._session

        item = self.get_by_id(id)
        if item is None:
            raise NotFound("Reseller not found.")

        session.delete(item)
        try:
            session.commit()
        except Exception:
            raise CommitFailed("Failed to delete the reseller.")

    def get_all(self, offset: int, limit: int) -> list[ResellerTable]:
        """
        Returns all resellers from the database with pagination.
        """
        return self._session.exec(select(ResellerTable).offset(offset).limit(limit)).all()

    def get_by_id(self, id: int) -> ResellerTable | None:
        """
        Returns the reseller with the given ID if it exists.

        Arguments:
            id: Reseller database ID.
        """
        return self._session.get(ResellerTable, id)

    def update(self, id: int, data: ResellerUpdate) -> ResellerTable:
        """
        Update a reseller with the given ID.

        Arguments:
            id: Reseller database ID.
            data: Update data.

        Raises:
            CommitFailed: If the service fails to update the reseller.
            NotFound: If the reseller with the given id does not exist.
        """
        session = self._session

        db_item = self.get_by_id(id)
        if db_item is None:
            raise NotFound("Reseller not found.")

        changes = data.dict(exclude_unset=True)
        for key, value in changes.items():
            setattr(db_item, key, value)

        session.add(db_item)
        try:
            session.commit()
        except Exception:
            raise CommitFailed("Failed to update the reseller.")

        session.refresh(db_item)
        return db_item
