from datetime import datetime

from sqlmodel import select, Session

from coupon_utils.service import CommitFailed, NotFound, ValidationFailed

from .model import CouponCreate, CouponStatus, CouponTable, CouponUpdate


class CouponService:
    """
    Coupon-related services.
    """

    __slots__ = "_session"

    def __init__(self, session: Session) -> None:
        """
        Initialization.

        Arguments:
            session: The session instance.
        """
        self._session = session

    def create_many(self, data: list[CouponCreate]) -> None:
        """
        Creates many new coupon.

        Arguments:
            data: Creation data.

        Raises:
            CommitFailed: If the service fails to commit the new coupons.
        """
        session = self._session

        session.add_all([CouponTable.from_orm(coupon) for coupon in data])
        try:
            session.commit()
        except Exception:
            raise CommitFailed("Failed to create the coupons.")

    def delete_by_id(self, id: int) -> None:
        """
        Deletes the coupon by ID.

        Arguments:
            id: Coupon database ID.

        Raises:
            CommitFailed: If the service fails to delete the coupon.
            NotFound: If the coupon with the given id does not exist.
        """
        session = self._session

        item = self.get_by_id(id)
        if item is None:
            raise NotFound("Coupon not found.")

        session.delete(item)
        try:
            session.commit()
        except Exception:
            raise CommitFailed("Failed to delete the coupon.")

    def get_all(self, offset: int, limit: int) -> list[CouponTable]:
        """
        Returns all coupons from the database with pagination.
        """
        return self._session.exec(select(CouponTable).offset(offset).limit(limit)).all()

    def get_by_id(self, id: int) -> CouponTable | None:
        """
        Returns the coupon with the given ID if it exists.

        Arguments:
            id: Coupon database ID.
        """
        return self._session.get(CouponTable, id)

    def get_by_code(self, code: str) -> CouponTable | None:
        """
        Returns the coupon with the given coupon code if it exists.

        Arguments:
            code: Coupon code.
        """
        return self._session.exec(select(CouponTable).where(CouponTable.code == code)).first()

    def update(self, id: int, data: CouponUpdate) -> CouponTable:
        """
        Update a coupon with the given id.

        Arguments:
            id: Coupon database ID.
            data: Update data.

        Raises:
            CommitFailed: If the service fails to update the coupon.
            NotFound: If the coupon with the given id does not exist.
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
            raise CommitFailed("Failed to update the coupon.")

        session.refresh(db_item)
        return db_item

    def status_by_id(self, id: int) -> CouponStatus:
        """
        Returns the current status of the coupon with the given ID.

        Arguments:
            id: Coupon database ID.

        Raises:
            NotFound: If the coupon with the given id does not exist.
        """
        coupon = self.get_by_id(id)
        if coupon is None:
            raise NotFound(f"Coupon: {id}")
        is_valid = True if coupon.valid_from <= datetime.utcnow() < coupon.valid_until else False
        return CouponStatus(is_active=coupon.is_active, is_valid=is_valid)

    def apply_by_code(self, code: str) -> None:
        """
        Apply a coupon.
        """
        session = self._session

        db_item = self.get_by_code(code)
        is_valid = True if db_item.valid_from <= datetime.utcnow() < db_item.valid_until else False
        if db_item is None:
            raise NotFound(f"Coupon: {id}")
        elif db_item.is_active and is_valid:
            setattr(db_item, "is_active", False)
        else:
            raise ValidationFailed("Coupon is not available.")
        session.add(db_item)
        try:
            session.commit()
        except Exception:
            raise CommitFailed("Failed to apply the coupon.")
