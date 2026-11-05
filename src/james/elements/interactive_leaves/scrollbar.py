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
from pygame import Rect, Surface

from james.elements.static_leaves.label import Label
from james.elements.containers.scrollable_display import ScrollableDisplay
from james.helpers.base_elem import Element
from james.helpers.custom_types import SupportsGetItemColour


class Scrollbar[K](Element[K]):
    def __init__(
            self, *, flex: float = 0, shrink: float = 0,
            interactive: bool = False, hover_tooltip: Label | None = None,
            tied_to: ScrollableDisplay,
            bar_thickness: int, groove_thickness: int,
            k_bar: K,
            k_bar_hovered: K | None = None,
            k_bar_pressed: K | None = None,
            k_groove: K
        ) -> None:
        super().__init__(flex=flex, shrink=shrink, interactive=interactive, hover_tooltip=hover_tooltip)
        self.tied_to = tied_to
        self.bar_thickness = bar_thickness
        self.groove_thickness = groove_thickness
        self.k_bar = k_bar
        self.k_bar_hovered = k_bar_hovered if k_bar_hovered is not None else k_bar
        self.k_bar_pressed = k_bar_pressed if k_bar_pressed is not None else k_bar
        self.k_groove = k_groove

    def _get_bar_height_ratio(self) -> float:
        """Calculate and return the scrollbar thumb height as a
        ratio of the total available groove height.
        Returns a value in [0..1]"""

        display = self.tied_to

        viewport_height = display.rect.height
        content_height = display.internal_surface.get_height()

        if content_height <= viewport_height:
            return 1.0
        return display.rect.height / content_height

    def preferred_size(self) -> tuple[int, int]:
        # Zero intrinsic height - it takes the height of whatever
        # space is left in its parent container.
        return (max(self.bar_thickness, self.groove_thickness), 0)

    def layout(self, rect: Rect) -> None:
        self.assign_rect(rect)

    def draw_default(self, surface: Surface, theme: SupportsGetItemColour) -> None:
        centre_x = self.rect.x + self.rect.w // 2

        # Draw the groove first
        groove_left_x = centre_x - self.groove_thickness // 2
        pg.draw.rect(surface, theme[self.k_groove], (groove_left_x, self.rect.y, self.groove_thickness, self.rect.h))

        # Draw the scroll bar
        if self.pressed:
            k_bar = self.k_bar_pressed
        elif self.hovered:
            k_bar = self.k_bar_hovered
        else:
            k_bar = self.k_bar

        # This assumes that the left will always allow the exact
        # amount of space for the bar to be centred in `self`'s rect.
        bar_left_x = self.rect.x
        bar_height = self._get_bar_height_ratio() * self.rect.h

        # How far down the bar is as a fraction in [0..1] of how far down it can go
        if self.tied_to.physics.disp_botright.y == 0:
            frac = 0
        else:
            frac = (self.tied_to.physics.disp.y / self.tied_to.physics.disp_botright.y)

        # Draw the scroll thumb itself
        bar_top_y = self.rect.y + (self.rect.h - bar_height) * frac
        pg.draw.rect(surface, theme[k_bar], (bar_left_x, bar_top_y, self.bar_thickness, bar_height))
