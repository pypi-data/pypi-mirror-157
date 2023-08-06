__all__ = ['ContainsResponse', 'ContainsError']

from ayradb.core.parse import parse_error
from dataclasses import dataclass

from ayradb.rest.http.response import Response


class ContainsError:
    # Request errors (local)
    INVALID_FIELD_NAME = -1
    # AyraDB errors
    RECORD_NOT_FOUND = 1
    INTERNAL_ERROR = 100


ERROR_DICT = {
    "00002": ContainsError.RECORD_NOT_FOUND,
    # Errors that shouldn't happen since they are internally managed
    "00016": ContainsError.INTERNAL_ERROR,
}


@dataclass
class ContainsResponse:

    success: bool
    error_code: int
    _error_msg: str

    def __init__(self, success, error_code, _error_msg=""):
        self.success = success
        self.error_code = error_code
        self._error_msg = _error_msg

    @staticmethod
    def from_http_response(res: Response):
        if res.status_code == 200:
            return ContainsResponse(True, 0)
        else:
            # Case error returned by ayra
            success = False
            error_msg = res.body.decode('ascii')
            try:
                error_code = ERROR_DICT[parse_error(error_msg)]
            except KeyError:
                error_code = ContainsError.INTERNAL_ERROR

            return ContainsResponse(success, error_code)
