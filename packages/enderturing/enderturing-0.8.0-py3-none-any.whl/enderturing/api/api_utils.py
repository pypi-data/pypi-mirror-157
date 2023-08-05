from datetime import date
from typing import Optional, Union


def _to_date_range(from_date: Union[str, date], to_date: Union[str, date]) -> Optional[str]:
    if not from_date and not to_date:
        return None
    start = from_date
    end = to_date
    if isinstance(start, date):
        start = start.isoformat()
    if isinstance(end, date):
        end = end.isoformat()
    res = start
    if end:
        res += ";" + end
    return res


def _to_time_range(from_time: str, to_time: str) -> Optional[str]:
    if not any((from_time, to_time)):
        return None
    return ";".join((from_time or "", to_time or ""))
