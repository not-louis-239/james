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

from james._internals.base_elem import Element
from james._internals.custom_types import Colour, DrawFunc, SupportsGetItemColour


class Panel(Element):
    """A simple panel that can contain one child with padding."""
    def __init__(
            self, *, flex: float = 0,
            draw_attrs: dict[str, Any] | None = None,
            colours: dict[str, Colour] | None = None,
            horiz_padding: int = 0, vert_padding: int = 0,
            child: Element | None = None,
            k_bg: str | None = None,
            k_border: str | None = None,
            border_w: int = 0,
            renderer: DrawFunc
        ) -> None:
        super().__init__(flex=flex, draw_attrs=draw_attrs, colours=colours)
        self.horiz_padding = horiz_padding
        self.vert_padding = vert_padding

        self.child = child
        if child is not None:
            child.parent = self

        self.children = [child] if child is not None else []
        self.renderer = renderer

        self.k_bg = k_bg
        self.k_border = k_border
        self.border_w = border_w

    def preferred_size(self) -> tuple[int, int]:
        if not self.child:
            return (self.horiz_padding * 2, self.vert_padding * 2)
        cw, ch = self.child.preferred_size()
        return (cw + 2 * self.horiz_padding, ch + 2 * self.vert_padding)

    def draw_primitive(self, surface: pg.Surface, theme: SupportsGetItemColour, renderer: DrawFunc) -> None:
        """Draws a primitive panel background, followed by the Panel's child."""
        if self.k_bg is not None:
            pg.draw.rect(surface, theme[self.k_bg], self.rect)

        if self.child:
            renderer(surface, self.child, theme)

    def draw_default_border(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        if self.border_w and self.k_border is not None:
            pg.draw.rect(surface, theme[self.k_border], self.rect, self.border_w)

    def draw_default(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        self.draw_primitive(surface, theme, renderer=self.renderer)
        self.draw_default_border(surface, theme)

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect
        if self.child:
            child_rect = rect.inflate(-2 * self.horiz_padding, -2 * self.vert_padding)
            self.child.layout(child_rect)
