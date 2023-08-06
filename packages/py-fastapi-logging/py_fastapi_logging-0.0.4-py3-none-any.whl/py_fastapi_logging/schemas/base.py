from typing import Optional, TypedDict, Union


class BaseJsonLogSchema(TypedDict):
    thread: Union[int, str]
    level: int
    request_id: Optional[str]
    progname: Optional[str]
    timestamp: str
    exceptions: Union[list[str], str] = None
