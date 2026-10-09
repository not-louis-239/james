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

from james._constants import DUMMY_SURFACE
from james.scroll_physics import ScrollPhysics
from james._base_elem import Element
from james._custom_types import Colour, DrawFunc, SupportsGetItemColour


class ScrollableDisplay(Element):
    """Creates a display that is vertically scrollable.
    Its height depends on the preferred size of the contents inside of the display."""
    def __init__(
            self, *, flex: float = 0,
            draw_attrs: dict[str, Any] | None = None,
            colours: dict[str, Colour] | None = None,
            padding: int = 0,
            child: Element,
            renderer: DrawFunc,
            k_bg: str | None = None,
            k_border: str | None = None,
            border_w: int = 0
        ) -> None:
        super().__init__(flex=flex, draw_attrs=draw_attrs, colours=colours)
        self.padding = padding
        self.child = child

        self.children = [child]
        self.internal_surface = DUMMY_SURFACE
        self.internal_rect = pg.Rect(0, 0, 0, 0)
        self.physics = ScrollPhysics(disp_topleft=(0, 0), disp_botright=(0, 0))

        self.renderer = renderer
        self.k_bg = k_bg
        self.k_border = k_border
        self.border_w = border_w

    def _refresh_internal_surface(self, theme: SupportsGetItemColour) -> None:
        """Redraws `self`'s internal surface. Could be expensive depending
        on what is inside `self`. """

        # Resize the surface if needed
        if (required_size := self.child.preferred_size()) != self.internal_surface.get_size():
            self.internal_surface = pg.Surface(required_size, pg.SRCALPHA)

        # Then redraw the content
        self.internal_surface.fill((0, 0, 0, 0))
        self.renderer(self.internal_surface, self.child, theme)

    def get_displayable_rect(self) -> pg.Rect:
        return pg.Rect(self.physics.disp.x, self.physics.disp.y, self.rect.width - 2 * self.padding, self.rect.height - 2 * self.padding)

    def blit_relevant_surf(self, dest_surface: pg.Surface) -> None:
        """Blits the relevant portion of `self.internal_surface` to `dest_surface`."""
        displayable_rect = self.get_displayable_rect()
        dest_surface.blit(self.internal_surface, (self.rect.x + self.padding, self.rect.y + self.padding), area=displayable_rect)

    def update(self, dt_s: float) -> None:
        child_max_x, child_max_y = self.child.preferred_size()
        self.physics.disp_botright.x = max(0, child_max_x + 2 * self.padding - self.rect.width)
        self.physics.disp_botright.y = max(0, child_max_y + 2 * self.padding - self.rect.height)
        self.physics.update(dt_s=dt_s)

    def handle_scroll(self, event: pg.event.Event) -> None:
        if self.rect.collidepoint(pg.mouse.get_pos()):
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
        self.rect = rect
        self.child.layout(pg.Rect(0, 0, *self.child.preferred_size()))
