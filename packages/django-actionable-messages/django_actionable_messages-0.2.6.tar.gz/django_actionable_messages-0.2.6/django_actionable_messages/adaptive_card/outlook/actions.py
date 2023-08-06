from django_actionable_messages.adaptive_card.outlook.mixins import ElementMixin, DisplayFormMixin
from django_actionable_messages.exceptions import CardException

METHODS = ("GET", "POST")


class ActionHttp(ElementMixin):
    def __init__(self, method: str, url: str, title=None, headers: list = None, body=None, **kwargs):
        if method not in METHODS:
            raise CardException("Invalid method. Available methods are: {}".format(METHODS))
        if method == "POST" and not body:
            raise CardException("If method is POST body must be provided")
        self._data = {
            "type": "Action.Http",
            "method": method,
            "url": url
        }
        super().__init__(**kwargs)
        if title is not None:
            self.set_title(title)
        if headers:
            self.add_headers(headers)
        if body is not None:
            self.set_body(body)

    def set_title(self, title):
        self._data["title"] = title

    def add_headers(self, headers):
        self._data.setdefault("headers", [])
        if isinstance(headers, (list, set, tuple)):
            self._data["headers"].extend(self._get_items_list(headers))
        else:
            self._data["headers"].append(headers.as_data())

    def set_body(self, body):
        self._data["body"] = body


class InvokeAddInCommand(ElementMixin):
    def __init__(self, add_in_id: str, desktop_command_id: str, initialization_context, title=None, **kwargs):
        self._data = {
            "type": "Action.InvokeAddInCommand",
            "addInId": add_in_id,
            "desktopCommandId": desktop_command_id,
            "initializationContext": initialization_context
        }
        super().__init__(**kwargs)
        if title is not None:
            self.set_title(title)

    def set_add_in_id(self, add_in_id: str):
        self._data["addInId"] = add_in_id

    def set_desktop_command_id(self, cmd_id: str):
        self._data["desktopCommandId"] = cmd_id

    def set_initialization_context(self, context):
        self._data["initializationContext"] = context

    def set_title(self, title):
        self._data["title"] = title


class DisplayMessageForm(DisplayFormMixin):
    base_type = "Action.DisplayMessageForm"


class DisplayAppointmentForm(DisplayFormMixin):
    base_type = "Action.DisplayAppointmentForm"


class ToggleVisibility(ElementMixin):
    def __init__(self, target_elements, title=None, **kwargs):
        self._data = {
            "type": "Action.ToggleVisibility"
        }
        self.add_target_elements(target_elements)
        super().__init__(**kwargs)
        if title is not None:
            self.set_title(title)

    def set_title(self, title):
        self._data["title"] = title

    def add_target_elements(self, elements):
        self._data.setdefault("targetElements", [])
        if isinstance(elements, (list, set, tuple)):
            self._data["targetElements"].extend(self._get_items_list(elements))
        else:
            self._data["targetElements"].append(elements.as_data())
