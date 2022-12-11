from rest_framework.exceptions import PermissionDenied, APIException
from rest_framework import status


class CodeDoesntExistException(PermissionDenied):
    """
    Exception that is raised when the provided code does not exist.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This Code does not exist"
    default_code = "invalid"

    def __init__(self, detail, status_code=None):
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code


class UpdateNotAllowedException(APIException):
    """
    Exception that is raised when an update is not allowed.
    """

    status_code = status.HTTP_403_FORBIDDEN
    default_code = "error"

    def __init__(self, detail, status_code=None):
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code
