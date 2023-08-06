from dataclasses import dataclass
from functools import cached_property
from typing import Union, Dict


@dataclass
class BotConfig:
    token: str
    bot_id: Union[int, str]
    webhook_url: str
    webhook_secret: str = ''
    is_debug: bool = True
    debug_filter_substring: str = '<bot_debug>'
    is_send_process_error_message: bool = True
    name: str = ''
    optional_data: Dict = None

    @cached_property
    def bot_id_string(self):
        return str(self.bot_id)

    @property
    def _data(self):
        if not isinstance(self.optional_data, dict):
            return {}
        return self.optional_data

    def get(self, key, default_value=None):
        return self._data.get(key, default_value)

