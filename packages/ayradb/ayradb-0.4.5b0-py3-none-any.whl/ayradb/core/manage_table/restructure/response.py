__all__ = ['RestructureTableResponse', 'RestructureTableError']

from ayradb.rest.http.response import Response
from ayradb.core.parse import parse_error
from dataclasses import dataclass


class RestructureTableError:    # TODO
    # Request errors (local)
    FIELD_MAX_LENGTH_REQUIRED = -1  # Also managed remotely
    KEY_MAX_LENGTH_REQUIRED = -2  # Also managed remotely
    NOT_ENOUGH_NODES = -3
    # AyraDB errors
    INTERNAL_ERROR = 100

ERROR_DICT = {

}


@dataclass
class RestructureTableResponse:

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
            return RestructureTableResponse(True, 0)
        else:
            # Case error returned by ayra
            error_msg = res.body.decode('ascii')
            try:
                error_code = ERROR_DICT[parse_error(error_msg)]
            except KeyError:
                error_code = RestructureTableError.INTERNAL_ERROR

            return RestructureTableResponse(False, error_code)
