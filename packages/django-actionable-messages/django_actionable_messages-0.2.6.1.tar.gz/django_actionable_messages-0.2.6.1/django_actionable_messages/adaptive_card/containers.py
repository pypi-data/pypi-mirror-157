from typing import Union, List

from django_actionable_messages.adaptive_card.actions import OpenUrl, Submit, ToggleVisibility, Execute
from django_actionable_messages.adaptive_card.mixins import ElementMixin
from django_actionable_messages.adaptive_card.types import BackgroundImage
from django_actionable_messages.adaptive_card.utils import (
    FallbackOption, Style, HorizontalAlignment, VerticalAlignment, SpacingStyle, ImageSize, Width
)
from django_actionable_messages.exceptions import CardException
from django_actionable_messages.mixins import CardElement


class ActionSet(ElementMixin):
    def __init__(self, actions: list, **kwargs):
        self._data = {
            "type": "ActionSet"
        }
        super().__init__(**kwargs)
        self._set_base_actions(actions)

    def _set_base_actions(self, actions: list):
        self._data["actions"] = self._get_items_list(actions)

    def add_actions(self, actions):
        if isinstance(actions, (list, set, tuple)):
            self._data["actions"].extend(self._get_items_list(actions))
        else:
            self._data["actions"].append(actions.as_data())


class Container(ElementMixin):
    def __init__(self, items: list, select_action=None, style: Style = None,
                 vertical_content_alignment: VerticalAlignment = None, bleed: bool = None,
                 background_image: Union[str, BackgroundImage] = None, min_height: str = None,
                 rtl: bool = None, **kwargs):
        self._data = {
            "type": "Container"
        }
        super().__init__(**kwargs)
        self._set_base_items(items)
        if select_action:
            self.set_select_action(select_action)
        if style is not None:
            self.set_style(style)
        if vertical_content_alignment:
            self.set_vertical_content_alignment(vertical_content_alignment)
        if bleed is not None:
            self.set_bleed(bleed)
        if background_image is not None:
            self.set_background_image(background_image)
        if min_height is not None:
            self.set_min_height(min_height)
        if rtl is not None:
            self.set_rtl(rtl)

    def _set_base_items(self, items: list):
        self._data["items"] = self._get_items_list(items)

    def add_items(self, items):
        if isinstance(items, (list, set, tuple)):
            self._data["items"].extend(self._get_items_list(items))
        else:
            self._data["items"].append(items.as_data())

    def set_select_action(self, action):
        self._data["selectAction"] = action.as_data()

    def set_style(self, style: Style):
        self._data["style"] = style

    def set_vertical_content_alignment(self, alignment: VerticalAlignment):
        self._data["verticalContentAlignment"] = alignment

    def set_bleed(self, value=True):
        self._data["bleed"] = value

    def set_background_image(self, image: Union[str, BackgroundImage]):
        if isinstance(image, str):
            self._data["backgroundImage"] = image
        elif isinstance(image, BackgroundImage):
            self._data["backgroundImage"] = image.as_data()
        else:
            raise CardException("Invalid image type")

    def set_min_height(self, height: str):
        self._data["minHeight"] = height

    def set_rtl(self, value: bool):
        self._data["rtl"] = value


class Column(CardElement):
    def __init__(self, items: list = None, background_image: Union[str, BackgroundImage] = None, bleed: bool = None,
                 fallback=None, min_height: str = None, rtl: bool = None, separator: bool = None,
                 spacing: SpacingStyle = None, select_action=None, style: Style = None,
                 vertical_content_alignment: VerticalAlignment = None, width: Union[str, int, Width] = None,
                 item_id: str = None, is_visible: bool = None, requires: dict = None, **kwargs):
        self._data = {
            "type": "Column"
        }
        super().__init__(**kwargs)
        if items:
            self.add_items(items)
        if background_image is not None:
            self.set_background_image(background_image)
        if bleed is not None:
            self.set_bleed(bleed)
        if fallback is not None:
            self.set_fallback(fallback)
        if min_height is not None:
            self.set_min_height(min_height)
        if rtl is not None:
            self.set_rtl(rtl)
        if separator is not None:
            self.set_separator(separator)
        if spacing is not None:
            self.set_spacing(spacing)
        if select_action is not None:
            self.set_select_action(select_action)
        if style is not None:
            self.set_style(style)
        if vertical_content_alignment:
            self.set_vertical_content_alignment(vertical_content_alignment)
        if width is not None:
            self.set_width(width)
        if item_id is not None:
            self.set_id(item_id)
        if is_visible is not None:
            self.set_is_visible(is_visible)
        if requires is not None:
            self.set_requires(requires)

    def add_items(self, items):
        self._data.setdefault("items", [])
        if isinstance(items, (list, set, tuple)):
            self._data["items"].extend(self._get_items_list(items))
        else:
            self._data["items"].append(items.as_data())

    def set_background_image(self, image: Union[str, BackgroundImage]):
        if isinstance(image, str):
            self._data["backgroundImage"] = image
        elif isinstance(image, BackgroundImage):
            self._data["backgroundImage"] = image.as_data()
        else:
            raise CardException("Invalid image type")

    def set_bleed(self, value=True):
        self._data["bleed"] = value

    def set_fallback(self, fallback):
        if isinstance(fallback, FallbackOption):
            self._data["fallback"] = fallback
        elif isinstance(fallback, Column):
            self._data["fallback"] = fallback.as_data()
        else:
            raise CardException("Invalid fallback type")

    def set_min_height(self, height: str):
        self._data["minHeight"] = height

    def set_rtl(self, value: bool):
        self._data["rtl"] = value

    def set_separator(self, value=True):
        self._data["separator"] = value

    def set_spacing(self, spacing: SpacingStyle):
        self._data["spacing"] = spacing

    def set_select_action(self, action):
        self._data["selectAction"] = action.as_data()

    def set_style(self, style: Style):
        self._data["style"] = style

    def set_vertical_content_alignment(self, alignment: VerticalAlignment):
        self._data["verticalContentAlignment"] = alignment

    def set_width(self, width: Union[str, int, Width]):
        if isinstance(width, Width):
            self._data["width"] = width
        elif isinstance(width, (str, int)):
            self._data["width"] = width
        else:
            raise CardException("Invalid width type")

    def set_id(self, item_id: str):
        self._data["id"] = item_id

    def set_is_visible(self, value=True):
        self._data["isVisible"] = value

    def set_requires(self, requires: dict):
        self._data["requires"] = requires


class ColumnSet(ElementMixin):
    def __init__(self, columns: list = None, select_action=None, style: Style = None, bleed: bool = None,
                 min_height: str = None, **kwargs):
        self._data = {
            "type": "ColumnSet"
        }
        super().__init__(**kwargs)
        if columns:
            self.add_columns(columns)
        if select_action is not None:
            self.set_select_action(select_action)
        if style is not None:
            self.set_style(style)
        if bleed is not None:
            self.set_bleed(bleed)
        if min_height is not None:
            self.set_min_height(min_height)

    def add_columns(self, columns):
        self._data.setdefault("columns", [])
        if isinstance(columns, (list, set, tuple)):
            self._data["columns"].extend(self._get_items_list(columns))
        else:
            self._data["columns"].append(columns.as_data())

    def set_select_action(self, action):
        self._data["selectAction"] = action.as_data()

    def set_style(self, style: Style):
        self._data["style"] = style

    def set_bleed(self, value=True):
        self._data["bleed"] = value

    def set_min_height(self, value: str):
        self._data["minHeight"] = value


class Fact(CardElement):
    def __init__(self, title, value, **kwargs):
        self._data = {}
        super().__init__(**kwargs)
        self._data = {
            "title": title,
            "value": value
        }


class FactSet(ElementMixin):
    def __init__(self, facts: List[Fact], **kwargs):
        self._data = {
            "type": "FactSet"
        }
        super().__init__(**kwargs)
        self._set_base_facts(facts)

    def _set_base_facts(self, facts: List[Fact]):
        self._data["facts"] = self._get_items_list(facts)

    def add_facts(self, facts):
        if isinstance(facts, (list, set, tuple)):
            self._data["facts"].extend(self._get_items_list(facts))
        else:
            self._data["facts"].append(facts.as_data())


class ImageSet(ElementMixin):
    def __init__(self, images: list, image_size: ImageSize = None, **kwargs):
        self._data = {
            "type": "ImageSet"
        }
        super().__init__(**kwargs)
        self._set_base_images(images)
        if image_size is not None:
            self.set_image_size(image_size)

    def _set_base_images(self, images: list):
        self._data["images"] = self._get_items_list(images)

    def add_images(self, images):
        if isinstance(images, (list, set, tuple)):
            self._data["images"].extend(self._get_items_list(images))
        else:
            self._data["images"].append(images.as_data())

    def set_image_size(self, size: ImageSize):
        self._data["imageSize"] = size


class TableCell(CardElement):
    def __init__(self, items, select_action: Union[Execute, OpenUrl, Submit, ToggleVisibility] = None,
                 style: Style = None, vertical_content_alignment: VerticalAlignment = None, bleed: bool = None,
                 background_image: Union[BackgroundImage, str] = None, min_height: str = None, rtl: bool = None,
                 **kwargs):
        self._data = {
            "type": "TableCell"
        }
        super().__init__(**kwargs)
        self.add_items(items)
        if select_action is not None:
            self.set_select_action(select_action)
        if style is not None:
            self.set_style(style)
        if vertical_content_alignment is not None:
            self.set_vertical_content_alignment(vertical_content_alignment)
        if bleed is not None:
            self.set_bleed(bleed)
        if background_image is not None:
            self.set_background_image(background_image)
        if min_height is not None:
            self.set_min_height(min_height)
        if rtl is not None:
            self.set_rtl(rtl)

    def add_items(self, items):
        self._data.setdefault("items", [])
        if isinstance(items, (list, set, tuple)):
            self._data["items"].extend(self._get_items_list(items))
        else:
            self._data["items"].append(items.as_data())

    def set_select_action(self, action: Union[Execute, OpenUrl, Submit, ToggleVisibility]):
        self._data["selectAction"] = action.as_data()

    def set_style(self, style: Style):
        self._data["style"] = style

    def set_vertical_content_alignment(self, alignment: VerticalAlignment):
        self._data["verticalContentAlignment"] = alignment

    def set_bleed(self, value: bool):
        self._data["bleed"] = value

    def set_background_image(self, image: Union[BackgroundImage, str]):
        if isinstance(image, str):
            self._data["backgroundImage"] = image
        elif isinstance(image, BackgroundImage):
            self._data["backgroundImage"] = image.as_data()
        else:
            raise CardException("Invalid image type")

    def set_min_height(self, min_height: str):
        self._data["minHeight"] = min_height

    def set_rtl(self, value: bool):
        self._data["rtl"] = value


class TableRow(CardElement):
    def __init__(self, cells: Union[TableCell, List[TableCell]], **kwargs):
        self._data = {
            "type": "TableRow"
        }
        super().__init__(**kwargs)
        self.add_cells(cells)

    def add_cells(self, cells):
        self._data.setdefault("cells", [])
        if isinstance(cells, (list, set, tuple)):
            self._data["cells"].extend(self._get_items_list(cells))
        else:
            self._data["cells"].append(cells.as_data())


class Table(ElementMixin):
    def __init__(self, columns: Union[dict, List[dict]] = None, rows: Union[TableRow, List[TableRow]] = None,
                 horizontal_cell_content_alignment: HorizontalAlignment = None,
                 vertical_cell_content_alignment: VerticalAlignment = None,
                 first_row_as_header: bool = None, show_grid_lines: bool = None,
                 grid_style: Style = None, **kwargs):
        self._data = {
            "type": "Table"
        }
        super().__init__(**kwargs)
        if columns is not None:
            self.add_columns(columns)
        if rows is not None:
            self.add_rows(rows)
        if horizontal_cell_content_alignment is not None:
            self.set_horizontal_cell_content_alignment(horizontal_cell_content_alignment)
        if vertical_cell_content_alignment is not None:
            self.set_vertical_cell_content_alignment(vertical_cell_content_alignment)
        if first_row_as_header is not None:
            self.set_first_row_as_header(first_row_as_header)
        if show_grid_lines is not None:
            self.set_show_grid_lines(show_grid_lines)
        if grid_style is not None:
            self.set_grid_style(grid_style)

    def add_columns(self, columns: Union[dict, List[dict]]):
        self._data.setdefault("columns", [])
        if isinstance(columns, (list, set, tuple)):
            self._data["columns"].extend(columns)
        else:
            self._data["columns"].append(columns)

    def add_rows(self, rows: Union[TableRow, List[TableRow]]):
        self._data.setdefault("rows", [])
        if isinstance(rows, (list, set, tuple)):
            self._data["rows"].extend(self._get_items_list(rows))
        else:
            self._data["rows"].append(rows.as_data())

    def set_horizontal_cell_content_alignment(self, alignment: HorizontalAlignment):
        self._data["horizontalCellContentAlignment"] = alignment

    def set_vertical_cell_content_alignment(self, alignment: VerticalAlignment):
        self._data["verticalCellContentAlignment"] = alignment

    def set_first_row_as_header(self, value: bool = True):
        self._data["firstRowAsHeader"] = value

    def set_show_grid_lines(self, value: bool = True):
        self._data["showGridLines"] = value

    def set_grid_style(self, style: Style = Style.DEFAULT):
        self._data["style"] = style
