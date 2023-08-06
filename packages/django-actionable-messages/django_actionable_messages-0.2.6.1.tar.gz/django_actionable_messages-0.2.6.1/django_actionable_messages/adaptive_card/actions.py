from typing import Union

from django_actionable_messages.adaptive_card.mixins import ActionMixin, BaseElementMixin
from django_actionable_messages.adaptive_card.utils import FallbackOption, ActionStyle, ActionMode, AssociatedInputs
from django_actionable_messages.exceptions import CardException
from django_actionable_messages.mixins import CardElement


class OpenUrl(ActionMixin):
    action_type = "Action.OpenUrl"

    def __init__(self, url: str, **kwargs):
        super().__init__(**kwargs)
        self.set_url(url)

    def set_url(self, url: str):
        self._data["url"] = url


class Submit(ActionMixin):
    action_type = "Action.Submit"

    def __init__(self, data: Union[str, dict] = None, **kwargs):
        super().__init__(**kwargs)
        if data is not None:
            self.set_data(data)

    def set_data(self, data: Union[str, dict]):
        self._data["data"] = data


class ShowCard(ActionMixin):
    action_type = "Action.ShowCard"

    def __init__(self, card=None, **kwargs):
        super().__init__(**kwargs)
        if card is not None:
            self.set_card(card)

    def set_card(self, card):
        self._data["card"] = card.payload


class TargetElement(CardElement):
    def __init__(self, element_id: str, is_visible: bool = None, **kwargs):
        self._data = {
            "elementId": element_id
        }
        super().__init__(**kwargs)
        if is_visible is not None:
            self.set_is_visible(is_visible)

    def set_element_id(self, element_id: str):
        self._data["elementId"] = element_id

    def set_is_visible(self, value=True):
        self._data["isVisible"] = value


class ToggleVisibility(ActionMixin):
    action_type = "Action.ToggleVisibility"

    def __init__(self, target_elements: list = None, **kwargs):
        super().__init__(**kwargs)
        if target_elements:
            self.set_target_elements(target_elements)

    def set_target_elements(self, elements: list):
        self._data["targetElements"] = []
        for element in elements:
            if isinstance(element, TargetElement):
                self._data["targetElements"].append(element.as_data())
            else:
                self._data["targetElements"].append(element)


class Execute(CardElement):
    action_type = "Action.Execute"

    def __init__(self, verb: str = None, data: Union[str, object] = None, associated_inputs: AssociatedInputs = None,
                 title: str = None, icon_url: str = None, style: ActionStyle = None, fallback=None,
                 tooltip: str = None, is_enabled: bool = None, mode: ActionMode = None,
                 requires: dict = None, **kwargs):
        self._data = {
            "type": self.action_type
        }
        super().__init__(**kwargs)
        if verb is not None:
            self.set_verb(verb)
        if data is not None:
            self.set_data(data)
        if associated_inputs is not None:
            self.set_associated_inputs(associated_inputs)
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

    def set_verb(self, verb: str):
        self._data["verb"] = verb

    def set_data(self, data: Union[str, object]):
        self._data["data"] = data

    def set_associated_inputs(self, associated_inputs: AssociatedInputs):
        self._data["associatedInputs"] = associated_inputs

    def set_title(self, title: str):
        self._data["title"] = title

    def set_icon_url(self, icon_url: str):
        self._data["iconUrl"] = icon_url

    def set_style(self, style: ActionStyle):
        self._data["style"] = style

    def set_fallback(self, fallback):
        if isinstance(fallback, FallbackOption):
            self._data["fallback"] = fallback
        elif isinstance(fallback, BaseElementMixin):
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
