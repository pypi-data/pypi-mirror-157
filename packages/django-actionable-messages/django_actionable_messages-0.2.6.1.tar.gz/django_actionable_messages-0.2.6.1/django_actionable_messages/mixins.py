import copy
import json

from django.template.loader import render_to_string

from django_actionable_messages.settings import card_settings

MESSAGE_CARD = 1
ADAPTIVE_CARD = 2
HERO_CARD = 3
THUMBNAIL_CARD = 4


class BaseMixin:
    def __init__(self, *args, **kwargs):
        self.language_code = kwargs.pop("lang_code", card_settings.LANGUAGE_CODE)
        super().__init__()

    def get_language_code(self):
        return self.language_code

    def _get_items_list(self, items):
        return list([item.as_data() for item in items])


class CardElement(BaseMixin):
    _data = None

    def as_data(self):
        return self._data


class Card(BaseMixin):
    json_encoder = card_settings.JSON_ENCODER

    _payload = None
    card_type = None
    script_types = {
        MESSAGE_CARD: "application/ld+json",
        ADAPTIVE_CARD: "application/adaptivecard+json"
    }
    signed_card_types = {
        MESSAGE_CARD: "SignedMessageCard",
        ADAPTIVE_CARD: "SignedAdaptiveCard"
    }

    @property
    def payload(self):
        return self.get_payload()

    @property
    def json_payload(self):
        return self.get_payload(fmt="json")

    @property
    def html_payload(self):
        return self.get_payload(fmt="html")

    @property
    def signed_html_payload(self):
        return self.get_payload(fmt="signed_html")

    def get_payload(self, fmt=None):
        payload = copy.deepcopy(self._payload)
        if fmt == "json":
            payload = self._get_json_payload(payload)
        elif fmt == "html":
            payload = self._get_html_payload(payload)
        elif fmt == "signed_html":
            payload = self._get_signed_html_payload()
        return payload

    def get_signed_payload(self):
        raise NotImplementedError

    def get_json_dump_kwargs(self):
        return {}

    def _get_json_payload(self, payload):
        kwargs = {
            "cls": self.json_encoder,
            "lang_code": self.get_language_code()
        }
        kwargs.update(**self.get_json_dump_kwargs())
        return json.dumps(payload, **kwargs)

    def _get_html_payload(self, payload):
        context = {
            "type": self.script_types[self.card_type],
            "payload": self._get_json_payload(payload)
        }
        return render_to_string("django_actionable_messages/email.html", context=context)

    def _get_signed_html_payload(self):
        context = {
            "type": self.signed_card_types[self.card_type],
            "payload": self.get_signed_payload()
        }
        return render_to_string("django_actionable_messages/signed_email.html", context=context)
