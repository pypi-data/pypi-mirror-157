__all__ = ['ReadResponse', 'ReadError']

from ayradb.rest.http.response import Response
from ayradb.core.manage_record.unescape import *
from ayradb.core.parse import parse_error
from dataclasses import dataclass

UNESCAPE_ERR_MSG = "Error during unescaping"
SEPARATOR = b'\x3b'


class ReadError:
    # Request errors (local)
    INVALID_FIELD_NAME = -1
    # AyraDB errors
    TABLE_NOT_FOUND = 1
    RECORD_NOT_FOUND = 2
    INTERNAL_ERROR = 100


ERROR_DICT = {
    "00405": ReadError.TABLE_NOT_FOUND,
    "00002": ReadError.RECORD_NOT_FOUND,
    # Errors that shouldn't happen since they are internally managed
    "00016": ReadError.INTERNAL_ERROR,
}


@dataclass
class ReadResponse:

    success: bool
    content: dict
    error_code: int
    _error_msg: str

    def __init__(self, success, error_code, content=None, _error_msg=""):
        self.success = success
        self.error_code = error_code
        self.content = content
        self._error_msg = _error_msg

    @staticmethod
    def from_http_response(res: Response):
        error_code = 0
        content = {}
        if res.status_code == 200:
            success = True
            try:
                body: bytes = res.body
                splitted_body = body.split(SEPARATOR)
                # Parse body
                for cursor in range(0, splitted_body.__len__(), 2):
                    # splitted body is organized as [key, value, key, value,...]
                    field_key = splitted_body[cursor]
                    field_value = unescape(splitted_body[cursor+1])
                    content[field_key.decode('utf-8')] = field_value

            except UnescapeException:
                success = False
                error_code = ReadError.INTERNAL_ERROR
                _error_msg = UNESCAPE_ERR_MSG
        else:
            # Case error returned by ayra
            success = False
            error_msg = res.body.decode('ascii')
            try:
                error_code = ERROR_DICT[parse_error(error_msg)]
            except KeyError:
                error_code = ReadError.INTERNAL_ERROR

        return ReadResponse(success, error_code, content=content)
