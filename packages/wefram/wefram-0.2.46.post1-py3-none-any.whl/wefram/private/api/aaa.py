from typing import *
from ...api import register, ModelAPI
from ...aaa.tools import hash_password
from ...models import User, Role, SessionLog
from ..const.aaa import PERMISSION_ADMINUSERSROLES


@register
class User(ModelAPI):
    model = User
    requires = PERMISSION_ADMINUSERSROLES

    @staticmethod
    async def encode_value(key: str, s: Any) -> Any:
        if key == 'secret':
            if s is None:
                return ''
            return hash_password(s) if s else ...
        return s

    @staticmethod
    async def decode_value(key: str, s: Any) -> Any:
        if key == 'secret':
            return None
        return s


@register
class Role(ModelAPI):
    model = Role
    requires = PERMISSION_ADMINUSERSROLES


@register
class SessionLog(ModelAPI):
    model = SessionLog
    requires = PERMISSION_ADMINUSERSROLES
    allow_create = False
    allow_delete = False
    allow_update = False

