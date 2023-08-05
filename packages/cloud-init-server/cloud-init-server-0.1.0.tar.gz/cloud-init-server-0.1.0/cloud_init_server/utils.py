import datetime
from typing import Any, Dict, Optional

def get_time_sec_age(when: Optional[datetime.datetime], now: datetime.datetime):
    if not when:
        return "N/A"
    sec_age = int((now-when).total_seconds())
    return f"{sec_age} SEC"

def get_time_str(when: Optional[datetime.datetime]):
    if not when:
        return "N/A"
    time_str = when.strftime("%Y/%m/%d %H:%M:%S")
    return time_str

def get_key(src: Dict[str, Any], key: str) -> Optional[Any]:
    return (src[key] if key in src else None)