from django_actionable_messages.adaptive_card.outlook.mixins import ElementMixin
from django_actionable_messages.adaptive_card.utils import HorizontalAlignment, SpacingStyle


class ActionSet(ElementMixin):
    def __init__(self, item_id: str = None, spacing: SpacingStyle = None, separator: bool = None,
                 horizontal_alignment: HorizontalAlignment = None, actions=None, **kwargs):
        self._data = {
            "type": "ActionSet"
        }
        super().__init__(**kwargs)
        if item_id is not None:
            self.set_id(item_id)
        if spacing is not None:
            self.set_spacing(spacing)
        if separator is not None:
            self.set_separator(separator)
        if horizontal_alignment is not None:
            self. set_horizontal_alignment(horizontal_alignment)
        if actions:
            self.add_actions(actions)

    def set_id(self, item_id: str):
        self._data["id"] = item_id

    def set_spacing(self, spacing: SpacingStyle):
        self._data["spacing"] = spacing

    def set_separator(self, value=True):
        self._data["separator"] = value

    def set_horizontal_alignment(self, horizontal_alignment: HorizontalAlignment):
        self._data["horizontalAlignment"] = horizontal_alignment

    def add_actions(self, actions):
        self._data.setdefault("actions", [])
        if isinstance(actions, (list, set, tuple)):
            self._data["actions"].extend(self._get_items_list(actions))
        else:
            self._data["actions"].append(actions.as_data())
