__all__ = ['UpsertResponse', 'UpsertError']

from ayradb.rest.http.response import Response
from ayradb.core.parse import parse_error
from dataclasses import dataclass


class UpsertError:
    # Request errors (local)
    INVALID_FIELD_NAME = -1
    # AyraDB errors
    TABLE_NOT_FOUND = 1
    FIELD_NOT_FOUND = 2
    FIELD_TOO_LONG = 3
    INTERNAL_ERROR = 100


ERROR_DICT = {
    "00405": UpsertError.TABLE_NOT_FOUND,
    "00017": UpsertError.FIELD_NOT_FOUND,
    "00014": UpsertError.FIELD_TOO_LONG,
    # Errors that shouldn't happen since they are internally managed
    "00016": UpsertError.INTERNAL_ERROR,
}   


@dataclass
class UpsertResponse:

    success: bool
    error_code: int
    _error_msg: str

    def __init__(self, success, error_code, _error_msg=""):
        self.success = success
        self.error_code = error_code
        self._error_msg = _error_msg

    @staticmethod
    def from_http_response(res: Response):
        _error_msg = ""
        if res.status_code == 200:
            return UpsertResponse(True, 0)
        else:
            # Case error returned by ayra
            success = False
            error_msg = res.body.decode('ascii')
            try:
                error_code = ERROR_DICT[parse_error(error_msg)]
            except KeyError:
                error_code = UpsertError.INTERNAL_ERROR

            return UpsertResponse(success,error_code,_error_msg=_error_msg)