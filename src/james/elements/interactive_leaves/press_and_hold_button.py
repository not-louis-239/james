# repo at: https://github.com/not-louis-239/palladium
# Palladium - Pygame terrain and star system generator
# Copyright (C) 2026 Louis Masarei-Boulton <243234869+not-louis-239@users.noreply.github.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import math
from pathlib import Path

import pygame as pg
from pygame import Font, Surface

from james.elements.interactive_leaves.button import CircleButton  # importing from James directly causes an ImportError due to circular imports
from james.elements.static_leaves.label import Label
from james.helpers.custom_types import SupportsGetItemColour
from james.helpers.utils import clamp
from james._internals.constants import DUMMY_SURFACE, DUMMY_CLEAR


class PressAndHoldButton[K](CircleButton[K]):
    def __init__(
            self, *, r: int, flex: float = 0, shrink: float = 0,
            text: str = "", font: Font | None = None, inset: int = 0,
            fixed_size: tuple[int, int] | None = None,
            img_path: Path | None = None, img_inset: int = 0,
            k_bg_colour: K | None = None, k_bg_hovered: K | None = None, k_bg_pressed: K | None = None,
            k_fg_colour: K, k_fg_hovered: K | None = None, k_fg_pressed: K | None = None,
            k_border_colour: K | None = None, k_border_hovered: K | None = None, k_border_pressed: K | None = None,
            k_fg_arc: K,
            border_w: int = 0, hover_tooltip: Label | None = None,
            hold_duration_secs: float = 2.5
        ) -> None:

        super().__init__(
            r=r, flex=flex, shrink=shrink, text=text, font=font, inset=inset,
            fixed_size=fixed_size, img_path=img_path, img_inset=img_inset,
            k_bg_colour=k_bg_colour, k_bg_hovered=k_bg_hovered, k_bg_pressed=k_bg_pressed,
            k_fg_colour=k_fg_colour, k_fg_hovered=k_fg_hovered, k_fg_pressed=k_fg_pressed,
            k_border_colour=k_border_colour, k_border_hovered=k_border_hovered, k_border_pressed=k_border_pressed,
            border_w=border_w, hover_tooltip=hover_tooltip
        )

        self.work_surface = DUMMY_SURFACE
        self.mask_surface = DUMMY_SURFACE

        self.hold_duration_secs = hold_duration_secs
        self.duration_held = 0
        self.k_fg_arc = k_fg_arc

    def refresh_work_surfaces(self, required_size: tuple[int, int]) -> None:
        """Create a new surface of the `required_size` if it isn't already,
        for `self.work_surface`, and clear it."""
        if self.work_surface.get_size() != required_size:
            self.work_surface = pg.Surface(required_size, pg.SRCALPHA)
        if self.mask_surface.get_size() != required_size:
            self.mask_surface = pg.Surface(required_size, pg.SRCALPHA)

        self.work_surface.fill(DUMMY_CLEAR)
        self.mask_surface.fill(DUMMY_CLEAR)

    @property
    def progress(self) -> float:
       return clamp(self.duration_held / self.hold_duration_secs, 0, 1)

    @property
    def is_full(self) -> bool:
        return self.progress == 1

    def update(self, dt_s: float) -> None:
        # If `self` is pressed, increment duration, else reset completely.
        if self.pressed:
            self.duration_held += dt_s
        else:
            self.duration_held = 0

    def draw_default(self, surface: Surface, theme: SupportsGetItemColour) -> None:
        super().draw_default(surface, theme)

        # Draw the gradually filling arc
        required_length = self.r * 2
        self.refresh_work_surfaces(required_size=(required_length, required_length))

        # Start angle and stop angle for `pygame.draw.arc` is in radians,
        # and the arc is drawn counterclockwise from the `start_angle` to the `stop_angle`.

        prog = self.progress

        if self.is_full:
            # Must draw to `self.work_surface` first, then blit to `surface`,
            # otherwise alpha channel is overwritten instead of blended, leading to ugly,
            # unexpected artefacts.
            pg.draw.circle(
                self.work_surface, theme[self.k_fg_arc], center=(self.r, self.r),
                radius=self.r, width=self.border_w
            )
            surface.blit(self.work_surface, (self.rect.centerx - self.r, self.rect.centery - self.r))

        elif prog > 0:
            # Draw a circle onto the work surface
            pg.draw.circle(self.work_surface, theme[self.k_fg_arc], (self.r, self.r), self.r, width=self.border_w)

            # Then "cut out" the arc shape using a sector and a mask
            # Pygame doesn't have a dedicated `pygame.draw.sector()` or `pygame.draw.filled_arc()`
            # so we draw a white arc onto the mask surface with a width just higher (+1) than
            # the `border_w` to cover any pixels which might otherwise get cut.
            # Then blit with the multiply blend mode onto the work surface.
            # Also draw it slightly wider as well, since increasing `width` only extends the arc inwards.
            start_angle = 0.5 * math.pi - 2 * math.pi * prog
            stop_angle = 0.5 * math.pi

            # These constants: -1, 2; they look funny, but James asks you to PLEASE not question them,
            # as they are the result of much trial and error to get the arc to align visually with the border.
            arc_rect = pg.Rect(-1, -1, self.r * 2 + 2, self.r * 2 + 2)

            pg.draw.arc(
                self.mask_surface, (255, 255, 255), arc_rect,
                start_angle, stop_angle, width=self.border_w + 2  # it needs 2 to compensate for 1 pixel outwards and 1 pixel inwards.
            )

            self.work_surface.blit(self.mask_surface, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

            # Finally, blit the work surface onto the main surface
            # This arc-and-mask approach is used because otherwise
            # it might not align visually with the border.
            surface.blit(self.work_surface, (self.rect.centerx - self.r, self.rect.centery - self.r))
