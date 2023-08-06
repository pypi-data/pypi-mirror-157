__all__ = ['DeleteResponse', 'DeleteError']

from ayradb.rest.http.response import Response
from ayradb.core.parse import parse_error
from dataclasses import dataclass


class DeleteError:
    # Request errors (local)
    INVALID_FIELD_NAME = -1
    # AyraDB errors
    TABLE_NOT_FOUND = 1
    FIELD_NOT_FOUND = 2
    INTERNAL_ERROR = 100


ERROR_DICT = {
    "00405": DeleteError.TABLE_NOT_FOUND,
    "00017": DeleteError.FIELD_NOT_FOUND,
    # Errors that shouldn't happen since they are internally managed
    "00016": DeleteError.INTERNAL_ERROR,
}


@dataclass
class DeleteResponse:

    success: bool
    error_code: int
    _error_msg: str

    def __init__(self, success, error_code, _error_msg=""):
        self.success = success
        self.error_code = error_code
        self._error_msg = _error_msg

    @staticmethod
    def from_http_response(res: Response):
        error_code = 0
        if res.status_code == 200:
            success = True
        else:
            # Case error returned by ayra
            success = False
            error_msg = res.body.decode('ascii')
            try:
                error_code = ERROR_DICT[parse_error(error_msg)]
            except KeyError:
                error_code = DeleteError.INTERNAL_ERROR

        return DeleteResponse(success, error_code)
