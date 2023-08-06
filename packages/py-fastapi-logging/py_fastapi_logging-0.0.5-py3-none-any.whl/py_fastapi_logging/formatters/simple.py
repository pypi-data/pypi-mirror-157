import datetime
import logging
import traceback

from py_fastapi_logging.formatters.base import BaseFormatter


class SimpleLogFormatter(BaseFormatter):
    @staticmethod
    def _format_log(record: logging.LogRecord) -> str:
        now = datetime.datetime.fromtimestamp(record.created).astimezone().replace(microsecond=0).isoformat()

        log_str = f"[{now}] "
        log_str += f"{record.levelname} "
        if hasattr(record, "progname"):
            progname = record.progname
        else:
            progname = record.module
        log_str += f" -- {progname}: "

        if hasattr(record, "request_id"):
            log_str += f"[{record.request_id}] "
        if hasattr(record, "tags"):
            log_str += f"{record.tags} "
        if hasattr(record, "message"):
            log_str += f"{record.message}"
        elif hasattr(record, "msg"):
            log_str += f"{record.msg}"

        if record.exc_info:
            log_str += f"\n{traceback.format_exception(*record.exc_info)}\n"

        elif record.exc_text:
            log_str += f"\n{record.exc_text}\n"

        if hasattr(record, "payload"):
            log_str += f"{record.payload}"

        return log_str
