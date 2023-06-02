from sqlmodel import select, Session

from coupon_utils.service import CommitFailed, NotFound

from .model import CouponCustomerLinkCreate, CouponCustomerLinkTable


class CouponCustomerLinkService:
    """
    Coupon-customer-link-related services.
    """

    __slots__ = "_session"

    def __init__(self, session: Session) -> None:
        """
        Initialization.

        Arguments:
            session: The session instance.
        """
        self._session = session

    def create(self, data: CouponCustomerLinkCreate) -> CouponCustomerLinkTable:
        """
        Creates a new coupon-customer-link.

        Arguments:
            data: Creation data.

        Raises:
            CommitFailed: If the service fails to commit the new link.
        """
        session = self._session

        db_item = CouponCustomerLinkTable.from_orm(data)
        session.add(db_item)
        try:
            session.commit()
        except Exception:
            raise CommitFailed("Failed to create the link.")
        session.refresh(db_item)
        return db_item

    def delete_by_ids(self, coupon_id: int, customer_id: int) -> None:
        """
        Deletes the coupon-customer link by IDs.

        Arguments:
            coupon_id: Coupon database ID.
            customer_id: Customer database ID.
        Raises:
            CommitFailed: If the service fails to delete the link.
            NotFound: If the link with the given ids does not exist.
        """
        session = self._session

        item = self.get_by_ids(coupon_id=coupon_id, customer_id=customer_id)
        if item is None:
            raise NotFound("Link not found.")

        session.delete(item)
        try:
            session.commit()
        except Exception:
            raise CommitFailed("Failed to delete the link.")

    def get_all(self, offset: int, limit: int) -> list[CouponCustomerLinkTable]:
        """
        Returns all customers from the database with pagination.
        """
        return self._session.exec(select(CouponCustomerLinkTable).offset(offset).limit(limit)).all()

    def get_by_ids(self, coupon_id: int, customer_id: int) -> CouponCustomerLinkTable | None:
        """
        Returns the coupon-customer link with the given IDs if it exists.

        Arguments:
            coupon_id: Coupon database ID.
            customer_id: Customer database ID.
        """
        return self._session.get(CouponCustomerLinkTable, {"coupon_id": coupon_id, "customer_id": customer_id})
