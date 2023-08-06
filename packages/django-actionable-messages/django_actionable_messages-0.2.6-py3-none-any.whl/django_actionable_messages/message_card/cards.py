import uuid
from typing import List, Union

from django_actionable_messages.exceptions import CardException
from django_actionable_messages.mixins import MESSAGE_CARD, Card


class MessageCard(Card):
    card_type = MESSAGE_CARD

    def __init__(self, title=None, text=None, originator: str = None, summary=None, theme_color: str = None,
                 correlation_id: str = None, auto_correlation_id=True, expected_actors: List[str] = None,
                 hide_original_body: bool = None, sections: list = None, actions: list = None, **kwargs):
        self._payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions"
        }
        super().__init__(**kwargs)
        if title is not None:
            self.set_title(title)
        if text is not None:
            self.set_text(text)
        if originator is not None:
            self.set_originator(originator)
        if summary is not None:
            self.set_summary(summary)
        if theme_color is not None:
            self.set_theme_color(theme_color)
        if correlation_id is not None or auto_correlation_id:
            self._payload["correlationId"] = correlation_id or str(uuid.uuid4())
        if expected_actors:
            self.set_expected_actors(expected_actors)
        if hide_original_body is not None:
            self.set_hide_original_body(hide_original_body)
        if sections:
            self.add_sections(sections)
        if actions:
            self.add_actions(actions)

    def set_title(self, title):
        self._payload["title"] = title

    def set_text(self, text):
        self._payload["text"] = text

    def set_originator(self, originator: str):
        self._payload["originator"] = originator

    def set_summary(self, summary):
        self._payload["summary"] = summary

    def set_theme_color(self, theme_color: str):
        self._payload["themeColor"] = theme_color

    def set_correlation_id(self, correlation_id: str):
        self._payload["correlationId"] = correlation_id

    def set_expected_actors(self, expected_actors: List[str]):
        self._payload["expectedActors"] = expected_actors

    def add_expected_actors(self, expected_actors: Union[str, List[str]]):
        self._payload.setdefault("expectedActors", [])
        if isinstance(expected_actors, (list, set, tuple)):
            self._payload["expectedActors"].extend(list(expected_actors))
        elif isinstance(expected_actors, str):
            self._payload["expectedActors"].append(expected_actors)
        else:
            raise CardException("Invalid expected_actors type")

    def set_hide_original_body(self, hide_original_body=True):
        self._payload["hideOriginalBody"] = hide_original_body

    def add_sections(self, sections):
        self._payload.setdefault("sections", [])
        if isinstance(sections, (list, set, tuple)):
            self._payload["sections"].extend(self._get_items_list(sections))
        else:
            self._payload["sections"].append(sections.as_data())

    def add_actions(self, actions):
        self._payload.setdefault("potentialAction", [])
        if isinstance(actions, (list, set, tuple)):
            self._payload["potentialAction"].extend(self._get_items_list(actions))
        else:
            self._payload["potentialAction"].append(actions.as_data())
