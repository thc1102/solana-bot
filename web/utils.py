import datetime
from typing import Union, Any


def update_object(obj, data):
    for field in obj.__fields__:
        if field in data.__fields__:
            setattr(obj, field, getattr(data, field))


def custom_datetime_serializer(dt: Union[datetime, None]) -> Any:
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')
