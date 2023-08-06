from django_actionable_messages.mixins import Card


class CardMixin(Card):
    content_type = ""

    def __init__(self, title=None, subtitle=None, text=None, images=None, buttons=None, **kwargs):
        self._payload = {
             "contentType": self.content_type
        }
        super().__init__(**kwargs)
        if title is not None:
            self.set_title(title)
        if subtitle is not None:
            self.set_subtitle(subtitle)
        if text is not None:
            self.set_text(text)
        if images:
            self.add_images(images)
        if buttons:
            self.add_buttons(buttons)

    def set_title(self, title):
        self._payload.setdefault("content", {})
        self._payload["content"]["title"] = title

    def set_subtitle(self, subtitle):
        self._payload.setdefault("content", {})
        self._payload["content"]["subtitle"] = subtitle

    def set_text(self, text):
        self._payload.setdefault("content", {})
        self._payload["content"]["text"] = text

    def add_images(self, images):
        self._payload.setdefault("content", {})
        self._payload["content"].setdefault("images", [])
        if isinstance(images, (list, set, tuple)):
            self._payload["content"]["images"].extend(self._get_items_list(images))
        else:
            self._payload["content"]["images"].append(images.as_data())

    def add_buttons(self, buttons):
        self._payload.setdefault("content", {})
        self._payload["content"].setdefault("buttons", [])
        if isinstance(buttons, (list, set, tuple)):
            self._payload["content"]["buttons"].extend(self._get_items_list(buttons))
        else:
            self._payload["content"]["buttons"].append(buttons.as_data())
