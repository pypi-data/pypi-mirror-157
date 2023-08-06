from typing import Union

from django_actionable_messages.mixins import CardElement


class Header(CardElement):
    def __init__(self, name: str, value: Union[str, int], **kwargs):
        self._data = {
            "name": name,
            "value": value
        }
        super().__init__(**kwargs)
