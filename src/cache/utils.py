from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.orm import InstanceState

from src.models import Dish
from src.models import Menu
from src.models import SubMenu

__all__ = ('serialize', 'key_gen')


def serialize(obj: DeclarativeMeta | list | dict) -> dict:
    if isinstance(obj, Dish | Menu | SubMenu):
        result = dict()
        for key, value in obj.__dict__.items():
            if not isinstance(value, InstanceState):
                result[key] = str(value) if 'id' in key else value
        return result
    result = dict(obj)
    result['id'] = str(result.get('id'))
    return result


def key_gen(*args) -> str:
    return ':'.join([str(arg) for arg in args])