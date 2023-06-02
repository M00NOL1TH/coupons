class ServiceException(Exception):
    """
    Base exception raise by a service.
    """

    pass


class CommitFailed(ServiceException):
    """
    Raise by a service when a commit fails.
    """

    pass


class NotFound(ServiceException):
    """
    Raise by a service when an item is not found.
    """

    pass


class ValidationFailed(ServiceException):
    """
    Raise by a service when an item is not valid.
    """

    pass
