__all__ = ['GetStructureResponse', 'GetStructureError']

from ayradb.rest.http.response import Response
from ayradb.core.parse import parse_error
import json
from dataclasses import dataclass
from ayradb.core.manage_table.column import Column


class GetStructureError:
    # Request errors (local)
    INVALID_FIELD_NAME = -1
    # AyraDB errors
    TABLE_NOT_FOUND = 1
    INTERNAL_ERROR = 100


ERROR_DICT = {
    "00005": GetStructureError.TABLE_NOT_FOUND,
    # Errors that shouldn't happen since they are internally managed
    "00016": GetStructureError.INTERNAL_ERROR,
    "00019": GetStructureError.INTERNAL_ERROR
}


@dataclass
class GetStructureResponse:

    success: bool
    error_code: int
    _error_msg: str
    structure: list

    def __init__(self, success, error_code,_error_msg="", description=None):
        self.success = success
        self.error_code = error_code
        self._error_msg = _error_msg
        self.structure = description

    @staticmethod
    def from_http_response(res: Response):
        error_code = 0
        fields = []
        if res.status_code == 200:
            success = True
            body = json.loads(res.body)
            body_description = body["column_descriptions"]
            for idx in range(0, body_description.__len__()):
                fields.append({Column.NAME: body_description[idx]["column_label"]})
                if "column_max_net_length" in body_description[idx] and body_description[idx]["column_max_net_length"] is not None:
                    fields[idx][Column.MAX_LENGTH] = body_description[idx]["column_max_net_length"] / 2  # FIXME: Remove /2 if escape factor is enabled
        else:
            # Case error returned by ayra
            success = False
            error_msg = res.body.decode('ascii')
            try:
                error_code = ERROR_DICT[parse_error(error_msg)]
            except KeyError:
                error_code = GetStructureError.INTERNAL_ERROR

        return GetStructureResponse(success, error_code, description=fields)
