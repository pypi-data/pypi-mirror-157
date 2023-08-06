import datetime
import json
import logging
import traceback

from py_fastapi_logging.formatters.base import BaseFormatter
from py_fastapi_logging.schemas.base import BaseJsonLogSchema
from py_fastapi_logging.utils.extra import get_env_extra


class JSONLogFormatter(BaseFormatter):
    @staticmethod
    def _format_log(record: logging.LogRecord) -> dict:
        now = datetime.datetime.fromtimestamp(record.created).astimezone().replace(microsecond=0).isoformat()

        json_log_fields = BaseJsonLogSchema(
            thread=record.process,
            timestamp=now,
            level=record.levelno,
        )

        for key in get_env_extra().keys():
            if hasattr(record, key):
                json_log_fields[key] = getattr(record, key)
            elif key == "progname":
                json_log_fields[key] = record.module
        if record.exc_info:
            json_log_fields["exceptions"] = traceback.format_exception(*record.exc_info)

        elif record.exc_text:
            json_log_fields["exceptions"] = record.exc_text

        if hasattr(record, "payload"):
            json_log_fields["payload"] = record.payload
        elif hasattr(record, "message"):
            json_log_fields["payload"] = {"message": record.message}
        elif hasattr(record, "msg"):
            json_log_fields["payload"] = {"message": record.msg}
        return json.dumps(json_log_fields, ensure_ascii=False)
