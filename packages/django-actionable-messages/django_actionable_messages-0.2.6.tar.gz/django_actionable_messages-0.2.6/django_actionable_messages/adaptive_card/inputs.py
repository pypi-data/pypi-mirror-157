from typing import List, Union

from django_actionable_messages.adaptive_card.mixins import InputMixin, DateTimeMixin
from django_actionable_messages.adaptive_card.utils import ChoiceInputStyle, TextInputStyle
from django_actionable_messages.mixins import CardElement


class TextInput(InputMixin):
    def __init__(self, is_multiline: bool = None, max_length: int = None, placeholder=None,
                 style: TextInputStyle = None, inline_action=None, value=None, **kwargs):
        self._data = {
            "type": "Input.Text"
        }
        super().__init__(**kwargs)
        if is_multiline is not None:
            self.set_is_multiline(is_multiline)
        if max_length is not None:
            self.set_max_length(max_length)
        if placeholder is not None:
            self.set_placeholder(placeholder)
        if style is not None:
            self.set_style(style)
        if inline_action is not None:
            self.set_inline_action(inline_action)
        if value is not None:
            self.set_value(value)

    def set_is_multiline(self, value=True):
        self._data["isMultiline"] = value

    def set_max_length(self, value: int):
        self._data["maxLength"] = value

    def set_placeholder(self, text):
        self._data["placeholder"] = text

    def set_style(self, style: TextInputStyle):
        self._data["style"] = style

    def set_inline_action(self, action):
        self._data["inlineAction"] = action.as_data()

    def set_value(self, value):
        self._data["value"] = value


class NumberInput(InputMixin):
    def __init__(self, max_value: int = None, min_value: int = None, placeholder=None, value: int = None, **kwargs):
        self._data = {
            "type": "Input.Number"
        }
        super().__init__(**kwargs)
        if max_value is not None:
            self.set_max(max_value)
        if min_value is not None:
            self.set_min(min_value)
        if placeholder is not None:
            self.set_placeholder(placeholder)
        if value is not None:
            self.set_value(value)

    def set_max(self, value: int):
        self._data["max"] = value

    def set_min(self, value: int):
        self._data["min"] = value

    def set_placeholder(self, text):
        self._data["placeholder"] = text

    def set_value(self, value: int):
        self._data["value"] = value


class DateInput(DateTimeMixin):
    base_type = "Input.Date"


class TimeInput(DateTimeMixin):
    base_type = "Input.Time"


class ToggleInput(InputMixin):
    def __init__(self, title, value: str = None, value_off: str = None, value_on: str = None, wrap: bool = None,
                 **kwargs):
        self._data = {
            "type": "Input.Toggle"
        }
        super().__init__(**kwargs)
        self.set_title(title)
        if value is not None:
            self.set_value(value)
        if value_off is not None:
            self.set_value_off(value_off)
        if value_on is not None:
            self.set_value_on(value_on)
        if wrap is not None:
            self.set_wrap(wrap)

    def set_title(self, title):
        self._data["title"] = title

    def set_value(self, value: str):
        self._data["value"] = value

    def set_value_off(self, value: str):
        self._data["valueOff"] = value

    def set_value_on(self, value: str):
        self._data["valueOn"] = value

    def set_wrap(self, value=True):
        self._data["wrap"] = value


class InputChoice(CardElement):
    def __init__(self, title, value: Union[str, int], **kwargs):
        self._data = {
            "value": value
        }
        super().__init__(**kwargs)
        self._set_title(title)

    def _set_title(self, title):
        self._data["title"] = title


class ChoiceSetInput(InputMixin):
    def __init__(self, choices: List[InputChoice], is_multi_select: bool = None, style: ChoiceInputStyle = None,
                 value: str = None, wrap: bool = None, **kwargs):
        self._data = {
            "type": "Input.ChoiceSet"
        }
        super().__init__(**kwargs)
        self.set_choices(choices)
        if is_multi_select is not None:
            self.set_is_multi_select(is_multi_select)
        if style is not None:
            self.set_style(style)
        if value is not None:
            self.set_value(value)
        if wrap is not None:
            self.set_wrap(wrap)

    def set_choices(self, choices: List[InputChoice]):
        self._data["choices"] = self._get_items_list(choices)

    def set_is_multi_select(self, value=True):
        self._data["isMultiSelect"] = value

    def set_style(self, style: ChoiceInputStyle):
        self._data["style"] = style

    def set_value(self, value: str):
        self._data["value"] = value

    def set_wrap(self, value=True):
        self._data["wrap"] = value
