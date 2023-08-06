from typing import List

from django_actionable_messages.adaptive_card.utils import HorizontalAlignment, VerticalAlignment, FillMode
from django_actionable_messages.mixins import CardElement


class BackgroundImage(CardElement):
    def __init__(self, url: str, fill_mode: FillMode = None, horizontal_alignment: HorizontalAlignment = None,
                 vertical_alignment: VerticalAlignment = None, **kwargs):
        self._data = {
            "url": url
        }
        super().__init__(**kwargs)
        if fill_mode is not None:
            self.set_fill_mode(fill_mode)
        if horizontal_alignment is not None:
            self.set_horizontal_alignment(horizontal_alignment)
        if vertical_alignment is not None:
            self.set_vertical_alignment(vertical_alignment)

    def set_url(self, url: str):
        self._data["url"] = url

    def set_fill_mode(self, fill_mode: FillMode):
        self._data["fillMode"] = fill_mode

    def set_horizontal_alignment(self, alignment: HorizontalAlignment):
        self._data["horizontalAlignment"] = alignment

    def set_vertical_alignment(self, alignment: VerticalAlignment):
        self._data["verticalAlignment"] = alignment


class Refresh(CardElement):
    def __init__(self, action=None, user_ids: List[str] = None, **kwargs):
        self._data = {}
        super().__init__(**kwargs)
        if action is not None:
            self.set_action(action)
        if user_ids is not None:
            self.set_user_ids(user_ids)

    def set_action(self, action):
        self._data["action"] = action.as_data()

    def set_user_ids(self, user_ids: List[str]):
        self._data["userIds"] = user_ids


class TokenExchangeResource(CardElement):
    def __init__(self, token_id: str, uri: str, provider_id: str, **kwargs):
        self._data = {
            "id": token_id,
            "uri": uri,
            "providerId": provider_id
        }
        super().__init__(**kwargs)

    def set_id(self, token_id: str):
        self._data["id"] = token_id

    def set_uri(self, uri: str):
        self._data["uri"] = uri

    def set_provider_id(self, provider_id: str):
        self._data["providerId"] = provider_id


class AuthCardButton(CardElement):
    def __init__(self, btn_type: str, value: str, title: str = None, image: str = None, **kwargs):
        self._data = {
            "type": btn_type,
            "value": value
        }
        super().__init__(**kwargs)
        if title is not None:
            self.set_title(title)
        if image is not None:
            self.set_image(image)

    def set_title(self, title: str):
        self._data["title"] = title

    def set_image(self, image: str):
        self._data["image"] = image


class Authentication(CardElement):
    def __init__(self, text: str = None, connection_name: str = None,
                 token_exchange_resource: TokenExchangeResource = None,
                 buttons: List[AuthCardButton] = None, **kwargs):
        self._data = {}
        super().__init__(**kwargs)
        if text is not None:
            self.set_text(text)
        if connection_name is not None:
            self.set_connection_name(connection_name)
        if token_exchange_resource is not None:
            self.set_token_exchange_resource(token_exchange_resource)
        if buttons is not None:
            self.set_buttons(buttons)

    def set_text(self, text: str):
        self._data["text"] = text

    def set_connection_name(self, connection_name: str):
        self._data["connectionName"] = connection_name

    def set_token_exchange_resource(self, token_exchange_resource: TokenExchangeResource):
        self._data["tokenExchangeResource"] = token_exchange_resource.as_data()

    def set_buttons(self, buttons: List[AuthCardButton]):
        self._data["buttons"] = self._get_items_list(buttons)
