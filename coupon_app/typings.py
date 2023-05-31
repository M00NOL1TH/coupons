from typing import Generator, Protocol
from sqlmodel import Session


class SessionContextProvider(Protocol):
    """
    Session context provider
    """

    def __call__(self) -> Generator[Session, None, None]:
        ...
