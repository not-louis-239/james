# Copyright 2026 Louis Masarei-Boulton

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from typing import Any, Literal

import pygame as pg

from james.helpers.base_elem import Element
from james.helpers.custom_types import Colour, SupportsGetItemColour
from james.elements.static_leaves.label import Label


class Divider(Element):
    """A dividing line that can be used to visually separate
    sections of a UI."""

    def __init__(
            self, *,
            flex: int = 1,
            draw_attrs: dict[str, Any] | None = None,
            colours: dict[str, Colour] | None = None,
            orientation: Literal["horiz", "vert"] = "horiz",
            k_fg: str, thickness: int = 2,
            hover_tooltip: Label | None = None,
        ) -> None:
        super().__init__(
            flex=flex, draw_attrs=draw_attrs, colours=colours,
            hover_tooltip=hover_tooltip, interactive=True
        )

        self.orientation = orientation
        self.k_fg = k_fg
        self.thickness = thickness

    def preferred_size(self) -> tuple[int, int]:
        """A divider is a visual decoration with no inherent width nor
        inherent height. Therefore, it's preferred size is 0 on the
        axis along which it is oriented, and its width along the other one."""

        if self.orientation == "vert":
            return (self.thickness, 0)
        return (0, self.thickness)

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect
        self.layout_dirty = False

    def draw_primitive(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        pg.draw.rect(surface, theme[self.k_fg], self.rect)

    def draw_default(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        if not self.visible:
            return

        self.draw_primitive(surface, theme)
