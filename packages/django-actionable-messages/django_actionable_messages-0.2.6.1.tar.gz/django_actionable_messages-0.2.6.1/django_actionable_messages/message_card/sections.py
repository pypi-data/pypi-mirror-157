from django_actionable_messages.mixins import CardElement


class Section(CardElement):
    def __init__(self, start_group: bool = False, title=None, text=None, activity_image: str = None,
                 activity_title=None, activity_subtitle=None, activity_text=None, hero_image=None, facts=None,
                 actions=None, **kwargs):
        self._data = {}
        super().__init__(**kwargs)
        if start_group:
            self.set_start_group(start_group)
        if title is not None:
            self.set_title(title)
        if text is not None:
            self.set_text(text)
        if activity_image is not None:
            self.set_activity_image(activity_image)
        if activity_title is not None:
            self.set_activity_title(activity_title)
        if activity_subtitle is not None:
            self.set_activity_subtitle(activity_subtitle)
        if activity_text is not None:
            self.set_activity_text(activity_text)
        if hero_image is not None:
            self.set_hero_image(hero_image)
        if facts:
            self.add_facts(facts)
        if actions:
            self.add_potential_actions(actions)

    def set_start_group(self, start_group=True):
        self._data["startGroup"] = start_group

    def set_title(self, title):
        self._data["title"] = title

    def set_text(self, text):
        self._data["text"] = text

    def set_activity(self, image: str = None, title=None, subtitle=None, text=None):
        if image is not None:
            self.set_activity_image(image)
        if title is not None:
            self.set_activity_title(title)
        if subtitle is not None:
            self.set_activity_subtitle(subtitle)
        if text is not None:
            self.set_activity_text(text)

    def set_activity_image(self, image: str):
        self._data["activityImage"] = image

    def set_activity_title(self, title):
        self._data["activityTitle"] = title

    def set_activity_subtitle(self, subtitle):
        self._data["activitySubtitle"] = subtitle

    def set_activity_text(self, text):
        self._data["activityText"] = text

    def set_hero_image(self, hero_image):
        self._data["heroImage"] = hero_image.as_data()

    def add_facts(self, facts):
        self._data.setdefault("facts", [])
        if isinstance(facts, (list, set, tuple)):
            self._data["facts"].extend(self._get_items_list(facts))
        else:
            self._data["facts"].append(facts.as_data())

    def add_potential_actions(self, actions):
        self._data.setdefault("potentialAction", [])
        if isinstance(actions, (list, set, tuple)):
            self._data["potentialAction"].extend(self._get_items_list(actions))
        else:
            self._data["potentialAction"].append(actions.as_data())
