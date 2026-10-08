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


from abc import abstractmethod
from pathlib import Path
from typing import Any

import pygame as pg

from widgets_and_stuff._custom_types import Colour
from widgets_and_stuff._img_cache import img_cache
from widgets_and_stuff.utils import get_text_surf, resize_to_fit

from ._base_elem import Element


class _Button(Element):
    def __init__(
            self, *, flex: float = 0,
            draw_attrs: dict[str, Any] | None = None,
            colours: dict[str, Colour] | None = None,
            text: str = "", font: pg.font.Font, inset: int = 0,
            fixed_size: tuple[int, int] | None = None, img_path: Path | None = None,
        ) -> None:
        super().__init__(flex=flex, draw_attrs=draw_attrs, colours=colours)
        self.text = text
        self.font = font
        self.inset = inset
        self.fixed_size = fixed_size
        self.img_path = img_path

    def _get_text_inset_size(self) -> tuple[int, int]:
        """Get text size, including inset."""
        text_size = self.font.size(self.text)
        return text_size[0] + self.inset * 2, text_size[1] + self.inset * 2

    @abstractmethod
    def check_click(self, mouse_pos: tuple[int, int]) -> bool:
        raise NotImplementedError


class RectButton(_Button):
    def check_click(self, mouse_pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(mouse_pos)

    def preferred_size(self) -> tuple[int, int]:
        return self.fixed_size or self._get_text_inset_size()

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect

    def draw_primitive(self, surface: pg.Surface, fg_colour: Colour, bg_colour: Colour | None = None) -> None:
        """Draws a primitive, borderless rectangular button."""

        # Draw the button's background
        if bg_colour is not None:
            pg.draw.rect(surface, bg_colour, self.rect)

        # Draw icon
        if self.img_path is not None:
            img_dims = resize_to_fit((img_cache.get_base_cache(self.img_path).get_size()), (self.rect.w, self.rect.h))
            img_surf = img_cache.get_tinted_scaled_img(self.img_path, fg_colour, (int(img_dims[0]), int(img_dims[1])))
            surface.blit(img_surf, img_surf.get_rect(center=self.rect.center))

        # Draw text
        text_surface = get_text_surf(self.font, self.text, fg_colour)
        surface.blit(text_surface, text_surface.get_rect(center=self.rect.center))


class CircleButton(_Button):
    def __init__(
            self, *, r: int, flex: float = 0,
            draw_attrs: dict[str, Any] | None = None,
            colours: dict[str, Colour] | None = None,
            text: str = "", font: pg.font.Font, inset: int = 0,
            fixed_size: tuple[int, int] | None = None, img_path: Path | None = None
        ) -> None:
        super().__init__(flex=flex, draw_attrs=draw_attrs, colours=colours, text=text, font=font, inset=inset, fixed_size=fixed_size, img_path=img_path)
        self.r = r

    def draw_primitive(self, surface: pg.Surface, fg_colour: Colour, bg_colour: Colour | None = None) -> None:
        """Draws a primitive, borderless circular button."""

        # Draw background
        if bg_colour is not None:
            pg.draw.circle(surface, bg_colour, self.rect.center, self.r)

        # Draw icon, but bound to the button circle
        if self.img_path is not None:
            img_surf = img_cache.get_tinted_scaled_img(self.img_path, fg_colour, self.preferred_size())
            surface.blit(img_surf, img_surf.get_rect(center=self.rect.center))

        # Draw the text
        if self.text:
            text_surf = get_text_surf(self.font, self.text, fg_colour)
            surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def check_click(self, mouse_pos: tuple[int, int]) -> bool:
        dx = mouse_pos[0] - self.rect.centerx
        dy = mouse_pos[1] - self.rect.centery
        return dx ** 2 + dy ** 2 <= self.r ** 2

    def preferred_size(self) -> tuple[int, int]:
        return (2 * self.r, 2 * self.r)

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect
