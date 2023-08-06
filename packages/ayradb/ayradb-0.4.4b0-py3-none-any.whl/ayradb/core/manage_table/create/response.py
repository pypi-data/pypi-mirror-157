__all__ = ['CreateTableResponse', 'CreateTableError']

from ayradb.rest.http.response import Response
from ayradb.core.parse import parse_error
import re
from dataclasses import dataclass


class CreateTableError:
    # Request errors (local)
    FIELD_MAX_LENGTH_REQUIRED = -1  # Also managed remotely
    KEY_MAX_LENGTH_REQUIRED = -2  # Also managed remotely
    NOT_ENOUGH_NODES = -3
    INVALID_FIELD_NAME = -4
    # AyraDB errors
    ALREADY_EXISTS = 1
    INTERNAL_ERROR = 100


ERROR_DICT = {
    "00019": CreateTableError.ALREADY_EXISTS,
    # Errors that should be verified also locally
    # "ERROR: [00019]:(00001): CTDFJ_030.001: column_descriptions: column_max_net_length: not found": CreateTableError.FIELD_MAX_LENGTH_REQUIRED,
    # "ERROR: [00019]:(00001): CTDFJ_030.002: column_descriptions: column_max_net_length: not a number": CreateTableError.KEY_MAX_LENGTH_REQUIRED,
    # Errors that shouldn't happen since they are internally managed
    "00016": CreateTableError.INTERNAL_ERROR,
}


@dataclass
class CreateTableResponse:

    success: bool
    error_code: int
    _error_msg: str

    def __init__(self, success, error_code,_error_msg=""):
        self.success = success
        self.error_code = error_code
        self._error_msg = _error_msg

    @staticmethod
    def from_http_response(res: Response):
        if res.status_code == 200:
            return CreateTableResponse(True, 0)
        else:
            # Case error returned by ayra
            error_msg = res.body.decode('ascii')
            try:
                error_code = ERROR_DICT[parse_error(error_msg)]
            except KeyError:
                error_code = CreateTableError.INTERNAL_ERROR

            return CreateTableResponse(False, error_code)
