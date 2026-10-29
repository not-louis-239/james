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

from james._internals.constants import DUMMY_SURFACE
from james.helpers.base_elem import Element
from james.helpers.custom_types import Colour, DrawFunc, SupportsGetItemColour
from james.helpers.scroll_physics import ScrollPhysics
from james.elements.static_leaves.label import Label


class ScrollableDisplay[K](Element[K]):
    """Creates a display that is vertically scrollable.
    Its height depends on the preferred size of the contents inside of the display."""
    def __init__(
            self, *, flex: float = 0, shrink: float = 0.0,
            padding: int = 0,
            child: Element,
            renderer: DrawFunc | None = None,
            k_bg: str | None = None,
            k_border: str | None = None,
            border_w: int = 0,
            hover_tooltip: Label | None = None,
            min_internal_w: int = 0,
            min_internal_h: int = 0
        ) -> None:
        super().__init__(flex=flex, shrink=shrink, interactive=True, hover_tooltip=hover_tooltip)
        self.padding = padding

        self.child = child
        self.children = [child]
        if child is not None:
            child.parent = self

        self.internal_surface = DUMMY_SURFACE
        self.internal_rect = pg.Rect(0, 0, 0, 0)
        self.physics = ScrollPhysics(disp_topleft=(0, 0), disp_botright=(0, 0))

        self._set_renderer(renderer)
        self.k_bg = k_bg
        self.k_border = k_border
        self.border_w = border_w

        self.min_internal_w = min_internal_w
        self.min_internal_h = min_internal_h

    def _calc_internal_rect(self) -> pg.Rect:
        child_preferred_w, child_preferred_h = self.child.preferred_size()
        w, h = max(self.min_internal_w, child_preferred_w), max(self.min_internal_h, child_preferred_h)
        child_rect = pg.Rect(0, 0, w, h)

        return child_rect

    def _refresh_internal_surface(self, theme: SupportsGetItemColour) -> None:
        """Redraws `self`'s internal surface. Could be expensive depending
        on what is inside `self`. """

        # Resize the surface if needed
        if (required_size := self._calc_internal_rect().size) != self.internal_surface.get_size():
            self.internal_surface = pg.Surface(required_size, pg.SRCALPHA)

        # Then redraw the content
        self.internal_surface.fill((0, 0, 0, 0))
        self.renderer(self.internal_surface, self.child, theme)

    def to_local(self, pos: tuple[int, int]) -> tuple[int, int]:
        dx, dy = pos[0] - self.rect.x, pos[1] - self.rect.y
        s_x, s_y = self.physics.disp
        return int(dx + s_x), int(dy + s_y)

    def _get_displayable_rect(self) -> pg.Rect:
        return pg.Rect(
            self.physics.disp.x,
            self.physics.disp.y,
            self.rect.width - 2 * self.padding,
            self.rect.height - 2 * self.padding
        )

    def blit_relevant_surf(self, dest_surface: pg.Surface) -> None:
        """Blits the relevant portion of `self.internal_surface` to `dest_surface`."""
        displayable_rect = self._get_displayable_rect()
        dest_surface.blit(
            self.internal_surface, (
                self.rect.x + self.padding,
                self.rect.y + self.padding
            ), area=displayable_rect
        )

    def update(self, dt_s: float) -> None:
        child_max_x, child_max_y = self.child.preferred_size()
        self.physics.disp_topleft.x = -self.padding
        self.physics.disp_topleft.y = -self.padding
        self.physics.disp_botright.x = max(0, child_max_x + self.padding - self.rect.width)
        self.physics.disp_botright.y = max(0, child_max_y + self.padding - self.rect.height)
        self.physics.update(dt_s=dt_s)

    def handle_scroll(self, event: pg.event.Event) -> None:
        self.physics.handle_scroll(event)

    def draw_primitive(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        """Draw the content of `self` to the given surface (borderless)."""

        self._refresh_internal_surface(theme)

        # Background
        if self.k_bg is not None:
            pg.draw.rect(surface, theme[self.k_bg], self.rect)

        # Get the relevant part of `self`'s internal surface
        # and draw it on the given surface.
        self.blit_relevant_surf(surface)

    def draw_default_border(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        # Draw border
        if self.border_w and self.k_border is not None:
            pg.draw.rect(surface, theme[self.k_border], self.rect, width=self.border_w)

    def preferred_size(self) -> tuple[int, int]:
        cw, ch = self.child.preferred_size()
        return cw + 2 * self.padding, ch + 2 * self.padding

    def layout(self, rect: pg.Rect) -> None:
        # Layout oneself to the rect to which it has been assigned (from a parent)
        # Then calculate the size of `self`'s internal rect and layout children according to it.
        self.assign_rect(rect)

        # Enforce minimum size constraints so that the child doesn't collapse in on themself.
        child_rect = self._calc_internal_rect()

        # Layout
        self.child.layout(child_rect)

    def draw_default(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        if not self.visible:
            return

        self.draw_primitive(surface, theme)
        self.draw_default_border(surface, theme)
