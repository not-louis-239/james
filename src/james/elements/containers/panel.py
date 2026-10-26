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


from typing import Any

import pygame as pg

from james.helpers.base_elem import Element
from james.helpers.custom_types import Colour, DrawFunc, SupportsGetItemColour
from james.elements.static_leaves.label import Label


class Panel(Element):
    """A simple panel that can contain one child with padding."""
    def __init__(
            self, child: Element | None = None,
            *, flex: float = 0, shrink: float = 0.0,
            draw_attrs: dict[str, Any] | None = None,
            colours: dict[str, Colour] | None = None,
            horiz_padding: int = 0, vert_padding: int | None = None,
            k_bg: str | None = None,
            k_border: str | None = None,
            border_w: int = 0,
            renderer: DrawFunc | None = None,
            interactive: bool = True,
            hover_tooltip: Label | None = None,
        ) -> None:
        super().__init__(
            flex=flex, shrink=shrink, draw_attrs=draw_attrs,
            colours=colours, interactive=True, hover_tooltip=hover_tooltip,
        )
        self.horiz_padding = horiz_padding
        self.vert_padding = vert_padding if vert_padding is not None else horiz_padding

        self.child = child
        if child is not None:
            child.parent = self

        self.children = [child] if child is not None else []
        self._set_renderer(renderer)

        self.k_bg = k_bg
        self.k_border = k_border
        self.border_w = border_w
        self.interactive = interactive

    def preferred_size(self) -> tuple[int, int]:
        if not self.child:
            return (self.horiz_padding * 2, self.vert_padding * 2)
        cw, ch = self.child.preferred_size()
        return (cw + 2 * self.horiz_padding, ch + 2 * self.vert_padding)

    def draw_primitive(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        """Draws a primitive panel background, followed by the Panel's child."""
        if self.k_bg is not None:
            pg.draw.rect(surface, theme[self.k_bg], self.rect)

        if self.child:
            self.renderer(surface, self.child, theme)

    def draw_default_border(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        if self.border_w and self.k_border is not None:
            pg.draw.rect(surface, theme[self.k_border], self.rect, self.border_w)

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect
        self.layout_dirty = False

        if self.child:
            child_rect = rect.inflate(-2 * self.horiz_padding, -2 * self.vert_padding)
            self.child.layout(child_rect)

    def draw_default(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        if not self.visible:
            return

        self.draw_primitive(surface, theme)
        self.draw_default_border(surface, theme)
