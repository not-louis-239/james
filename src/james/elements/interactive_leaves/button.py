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


from pathlib import Path
from typing import Any

import pygame as pg

from james._internals.img_cache import img_cache
from james.helpers.base_elem import Element
from james.helpers.custom_types import Colour, SupportsGetItemColour
from james.helpers.utils import get_text_surf, resize_to_fit
from james.elements.static_leaves.label import Label


class _Button[K](Element[K]):
    def __init__(
            self, *, flex: float = 0, shrink: float = 0.0,
            text: str = "", font: pg.font.Font, inset: int = 0,
            fixed_size: tuple[int, int] | None = None, img_path: Path | None = None,
            img_inset: int = 0,
            k_bg_colour: str | None = None,
            k_bg_hovered: str | None = None,
            k_bg_pressed: str | None = None,
            k_fg_colour: str,
            k_fg_hovered: str | None = None,
            k_fg_pressed: str | None = None,
            k_border_colour: str | None = None,
            k_border_hovered: str | None = None,
            k_border_pressed: str | None = None,
            border_w: int = 0,
            hover_tooltip: Label | None = None,
        ) -> None:
        super().__init__(flex=flex, shrink=shrink, hover_tooltip=hover_tooltip, interactive=True)

        self.text = text
        self.font = font
        self.inset = inset
        self.fixed_size = fixed_size
        self.img_path = img_path
        self.img_inset = img_inset

        self.k_bg_colour = k_bg_colour
        self.k_bg_hovered = k_bg_hovered if k_bg_hovered is not None else k_bg_colour
        self.k_bg_pressed = k_bg_pressed if k_bg_pressed is not None else k_bg_colour

        self.k_fg_colour = k_fg_colour
        self.k_fg_hovered = k_fg_hovered if k_fg_hovered is not None else k_fg_colour
        self.k_fg_pressed = k_fg_pressed if k_fg_pressed is not None else k_fg_colour

        self.k_border_colour = k_border_colour
        self.k_border_hovered = k_border_hovered if k_border_hovered is not None else k_border_colour
        self.k_border_pressed = k_border_pressed if k_border_pressed is not None else k_border_colour

        self.border_w = border_w

    def _get_text_size_with_inset(self) -> tuple[int, int]:
        """Get text size, including inset."""
        text_size = self.font.size(self.text)
        return text_size[0] + self.inset * 2, text_size[1] + self.inset * 2

    @property
    def k_bg(self) -> str | None:
        return (
            self.k_bg_pressed if self.pressed
            else self.k_bg_hovered if self.hovered
            else self.k_bg_colour
        )

    @property
    def k_fg(self) -> str | None:
        return (
            self.k_fg_pressed if self.pressed
            else self.k_fg_hovered if self.hovered
            else self.k_fg_colour
        )

    @property
    def k_border(self) -> str | None:
        return (
            self.k_border_pressed if self.pressed
            else self.k_border_hovered if self.hovered
            else self.k_border_colour
        )


class RectButton[K](_Button):
    def preferred_size(self) -> tuple[int, int]:
        return self.fixed_size or self._get_text_size_with_inset()

    def layout(self, rect: pg.Rect) -> None:
        self.assign_rect(rect)

    def draw_primitive(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        """Draws a primitive, borderless rectangular button."""

        # Draw the button's background
        if self.k_bg is not None:
            pg.draw.rect(surface, theme[self.k_bg], self.rect)

        # Draw icon
        if self.img_path is not None and self.k_fg is not None:
            img_w = max(0, self.rect.width - 2 * self.img_inset)
            img_h = max(0, self.rect.height - 2 * self.img_inset)
            img_dims = resize_to_fit((img_cache.get_base_cache(self.img_path).get_size()), (img_w, img_h))
            img_surf = img_cache.get_tinted_scaled_img(self.img_path, theme[self.k_fg], (int(img_dims[0]), int(img_dims[1])))
            surface.blit(img_surf, img_surf.get_rect(center=self.rect.center))

        # Draw text
        if self.k_fg is not None:
            text_surface = get_text_surf(self.font, self.text, theme[self.k_fg])
            surface.blit(text_surface, text_surface.get_rect(center=self.rect.center))

    def draw_default_border(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        """Draws a default border style using `self.border_w` and `self.k_border_colour` if set."""
        if self.k_border is not None and self.border_w:
            pg.draw.rect(surface, theme[self.k_border], self.rect, self.border_w)

    def draw_default(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        if not self.visible:
            return

        self.draw_primitive(surface, theme)
        self.draw_default_border(surface, theme)


class CircleButton[K](_Button):
    def __init__(
            self, *, r: int, flex: float = 0, shrink: float = 0.0,
            text: str = "", font: pg.font.Font, inset: int = 0,
            fixed_size: tuple[int, int] | None = None, img_path: Path | None = None,
            img_inset: int = 0,
            k_bg_colour: str | None = None,
            k_bg_hovered: str | None = None,
            k_bg_pressed: str | None = None,
            k_fg_colour: str,
            k_fg_hovered: str | None = None,
            k_fg_pressed: str | None = None,
            k_border_colour: str | None = None,
            k_border_hovered: str | None = None,
            k_border_pressed: str | None = None,
            border_w: int = 0,
            hover_tooltip: Label | None = None
        ) -> None:
        super().__init__(
            flex=flex, shrink=shrink, text=text, font=font, inset=inset,
            fixed_size=fixed_size, img_path=img_path, img_inset=img_inset,
            k_bg_colour=k_bg_colour, k_bg_hovered=k_bg_hovered, k_bg_pressed=k_bg_pressed,
            k_fg_colour=k_fg_colour, k_fg_hovered=k_fg_hovered, k_fg_pressed=k_fg_pressed,
            k_border_colour=k_border_colour, k_border_hovered=k_border_hovered,
            k_border_pressed=k_border_pressed, border_w=border_w, hover_tooltip=hover_tooltip
        )
        self.r = r

    def _contains_point(self, pos: tuple[int, int]) -> bool:
        dx = pos[0] - self.rect.centerx
        dy = pos[1] - self.rect.centery
        return (dx * dx) + (dy * dy) <= (self.r * self.r)

    def draw_primitive(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        """Draws a primitive, borderless circular button."""

        # Draw background
        if self.k_bg is not None:
            pg.draw.circle(surface, theme[self.k_bg], self.rect.center, self.r)

        # Draw icon, but bound to the button circle
        if self.img_path is not None and self.k_fg is not None:
            img_w = max(0, self.rect.width - 2 * self.img_inset)
            img_h = max(0, self.rect.height - 2 * self.img_inset)
            img_surf = img_cache.get_tinted_scaled_img(
                self.img_path, theme[self.k_fg], (img_w, img_h),
                constrain_proportions=True
            )
            surface.blit(img_surf, img_surf.get_rect(center=self.rect.center))

        # Draw the text
        if self.text and self.k_fg is not None:
            text_surf = get_text_surf(self.font, self.text, theme[self.k_fg])
            surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def draw_default_border(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        """Draws a default circular button border."""
        if self.k_border is not None and self.border_w:
            pg.draw.circle(surface, theme[self.k_border], self.rect.center, self.r, width=self.border_w)

    def draw_default(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        if not self.visible:
            return

        self.draw_primitive(surface, theme)
        self.draw_default_border(surface, theme)

    def preferred_size(self) -> tuple[int, int]:
        return (2 * self.r, 2 * self.r)

    def layout(self, rect: pg.Rect) -> None:
        self.assign_rect(rect)
