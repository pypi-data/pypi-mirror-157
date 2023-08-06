from django_actionable_messages.adaptive_card.utils import (
    FallbackOption, BlockElementHeight, SpacingStyle, ActionStyle, ActionMode
)
from django_actionable_messages.exceptions import CardException
from django_actionable_messages.mixins import CardElement


class BaseElementMixin(CardElement):
    def __init__(self, fallback=None, separator: bool = None, spacing: SpacingStyle = None, item_id: str = None,
                 is_visible: bool = None, requires: dict = None, **kwargs):
        super().__init__(**kwargs)
        if fallback is not None:
            self.set_fallback(fallback)
        if separator is not None:
            self.set_separator(separator)
        if spacing is not None:
            self.set_spacing(spacing)
        if item_id is not None:
            self.set_id(item_id)
        if is_visible is not None:
            self.set_is_visible(is_visible)
        if requires is not None:
            self.set_requires(requires)

    def set_fallback(self, fallback):
        if isinstance(fallback, FallbackOption):
            self._data["fallback"] = fallback
        elif isinstance(fallback, BaseElementMixin):
            self._data["fallback"] = fallback.as_data()
        else:
            raise CardException("Invalid fallback type")

    def set_separator(self, value=True):
        self._data["separator"] = value

    def set_spacing(self, spacing: SpacingStyle):
        self._data["spacing"] = spacing

    def set_id(self, item_id: str):
        self._data["id"] = item_id

    def set_is_visible(self, visible=True):
        self._data["isVisible"] = visible

    def set_requires(self, requires: dict):
        self._data["requires"] = requires


class ElementMixin(BaseElementMixin):
    def __init__(self, height: BlockElementHeight = None, **kwargs):
        super().__init__(**kwargs)
        if height is not None:
            self.set_height(height)

    def set_height(self, height: BlockElementHeight):
        self._data["height"] = height


class InputMixin(ElementMixin):
    def __init__(self, label=None, **kwargs):
        super().__init__(**kwargs)
        if label is not None:
            self.set_label(label)

    def set_label(self, label):
        if isinstance(label, str):
            self._data["label"] = label
        else:
            self._data["label"] = label.as_data()


class DateTimeMixin(InputMixin):
    base_type = None

    def __init__(self, max_value: str = None, min_value: str = None, placeholder=None, value: str = None, **kwargs):
        self._data = {
            "type": self.base_type
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

    def set_max(self, value: str):
        self._data["max"] = value

    def set_min(self, value: str):
        self._data["min"] = value

    def set_placeholder(self, text):
        self._data["placeholder"] = text

    def set_value(self, value: str):
        self._data["value"] = value


class ActionMixin(CardElement):
    action_type = ""

    def __init__(self, title=None, icon_url: str = None, style: ActionStyle = None, fallback=None, tooltip: str = None,
                 is_enabled: bool = None, mode: ActionMode = None, requires: dict = None, **kwargs):
        self._data = {
            "type": self.action_type
        }
        super().__init__(**kwargs)
        if title is not None:
            self.set_title(title)
        if icon_url is not None:
            self.set_icon_url(icon_url)
        if style is not None:
            self.set_style(style)
        if fallback is not None:
            self.set_fallback(fallback)
        if tooltip is not None:
            self.set_tooltip(tooltip)
        if is_enabled is not None:
            self.set_is_enabled(is_enabled)
        if mode is not None:
            self.set_mode(mode)
        if requires is not None:
            self.set_requires(requires)

    def set_title(self, title):
        self._data["title"] = title

    def set_icon_url(self, url: str):
        self._data["iconUrl"] = url

    def set_style(self, style: ActionStyle):
        self._data["style"] = style

    def set_fallback(self, fallback):
        if isinstance(fallback, FallbackOption):
            self._data["fallback"] = fallback
        elif isinstance(fallback, ActionMixin):
            self._data["fallback"] = fallback.as_data()
        else:
            raise CardException("Invalid fallback type")

    def set_tooltip(self, tooltip: str):
        self._data["tooltip"] = tooltip

    def set_is_enabled(self, is_enabled: bool):
        self._data["isEnabled"] = is_enabled

    def set_mode(self, mode: ActionMode):
        self._data["mode"] = mode

    def set_requires(self, requires: dict):
        self._data["requires"] = requires
