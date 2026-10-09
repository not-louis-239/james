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


import pygame as pg

from typing import Any

from james._internals.custom_types import Colour, SupportsGetItemColour
from james.utils import crop_text_to_fit, get_text_surf
from james._internals.base_elem import Element


class Label(Element):
    def __init__(
            self, *, flex: float = 0,
            draw_attrs: dict[str, Any] | None = None,
            colours: dict[str, Colour] | None = None,
            text: str = "", font: pg.font.Font, inset: int = 0,
            k_fg: str, k_bg: str | None = None, k_border: str | None = None,
            border_w: int = 0
        ) -> None:
        super().__init__(flex=flex, draw_attrs=draw_attrs, colours=colours)
        self.text = text
        self.font = font
        self.inset = inset

        self.k_fg = k_fg
        self.k_bg = k_bg
        self.k_border = k_border
        self.border_w = border_w

    def set_text(self, text: str) -> None:
        self.text = text

    def preferred_size(self) -> tuple[int, int]:
        text_w, text_h = self.font.size(self.text)
        return (text_w + 2 * self.inset, text_h + 2 * self.inset)

    def draw_primitive(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        """Draws a label to a surface. If a `self.k_bg` is set and not None,
        draws a solid background."""

        # Background
        if self.k_bg is not None:
            pg.draw.rect(surface, theme[self.k_bg], self.rect)

        # Text
        text = crop_text_to_fit(self.text, self.font, self.rect.width - 2 * self.inset)
        text_surf = get_text_surf(self.font, text, theme[self.k_fg])
        surface.blit(text_surf, self.rect.inflate(-2 * self.inset, -2 * self.inset))

    def draw_default_border(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        if self.border_w and self.k_border is not None:
            pg.draw.rect(surface, theme[self.k_border], self.rect, width=self.border_w)

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect
