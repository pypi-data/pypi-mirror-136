from .core import (
    ApiClient,
    BaseClient,
    who_am_i
)
from .user_info import UserInfo


class AccountClient(BaseClient):
    jelastic_group = "users"

    jelastic_class = "account"

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    def get_user_info(self) -> UserInfo:
        response = self._execute(who_am_i())
        return UserInfo(response)
