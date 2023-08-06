__all__ = ['ScanInitResponse', 'ScanInitError']

from ayradb.rest.http.response import Response
from ayradb.core.parse import parse_error
from dataclasses import dataclass
import json


class ScanInitError:
    # Request errors (local)
    # AyraDB errors
    TABLE_NOT_FOUND = 1
    INTERNAL_ERROR = 100


ERROR_DICT = {
    "00005": ScanInitError.TABLE_NOT_FOUND,
    # Errors that shouldn't happen since they are internally managed
    "00016": ScanInitError.INTERNAL_ERROR,
    "00019": ScanInitError.INTERNAL_ERROR,
}


@dataclass
class ScanInitResponse:

    success: bool
    error_code: int
    _error_msg: str
    segments: int

    def __init__(self, success, error_code, n_segments=0, _error_msg=""):
        self.success = success
        self.error_code = error_code
        self.segments = n_segments
        self._error_msg = _error_msg

    @staticmethod
    def from_http_response(res: Response):
        if res.status_code == 200:
            body = json.loads(res.body)
            return ScanInitResponse(True, 0, n_segments=body["n_segments"])
        else:
            error_msg = res.body.decode('ascii')
            try:
                error_code = ERROR_DICT[parse_error(error_msg)]
            except KeyError:
                error_code = ScanInitError.INTERNAL_ERROR

            return ScanInitResponse(False, error_code)
