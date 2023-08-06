from typing import Union

from django_actionable_messages.message_card.utils import OSType
from django_actionable_messages.mixins import CardElement


class Fact(CardElement):
    def __init__(self, name, value, **kwargs):
        self._data = {}
        super().__init__(**kwargs)
        self._data = {
            "name": name,
            "value": value
        }


class HeroImage(CardElement):
    def __init__(self, url: str, title=None, **kwargs):
        self._data = {
            "image": url
        }
        super().__init__(**kwargs)
        if title is not None:
            self.set_title(title)

    def set_url(self, url: str):
        self._data["image"] = url

    def set_title(self, title):
        self._data["title"] = title


class InputChoice(CardElement):
    def __init__(self, name, value: Union[str, int], **kwargs):
        self._data = {
            "value": value
        }
        super().__init__(**kwargs)
        self._set_display(name)

    def _set_display(self, name):
        self._data["display"] = name

    def _get_value(self):
        return self._data["value"]


class ActionTarget(CardElement):
    def __init__(self, os_type: OSType, url: str, **kwargs):
        self._data = {
            "os": os_type,
            "uri": url
        }
        super().__init__(**kwargs)

    def _get_os(self):
        return self._data["os"]
