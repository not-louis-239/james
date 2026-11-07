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

from james._internals.constants import DUMMY_SURFACE, HOVER_TOOLTIP_MARGIN
from james.helpers import renderer as _renderer
from james.helpers.base_elem import Element
from james.helpers.custom_types import DrawFunc, SupportsGetItemColour

# This is an alias for clarity.
# By default, an element's tooltip is `None`, which shows no tooltip,
# but if it is nested inside an element that has one, shows that element's tooltip
# instead.
# With `NO_TOOLTIP` an element suppresses any tooltips provided by its parents.
NO_TOOLTIP = False


def _propagate_update(elem: Element, dt_s: float) -> None:
    elem.update(dt_s)
    for c in elem.children:
        _propagate_update(c, dt_s)


def _get_tooltip(hovered_elem: Element) -> Element | None:
    current = hovered_elem

    while current is not None:
        if current.hover_tooltip is NO_TOOLTIP:
            return None

        if current.hover_tooltip is not None:
            return current.hover_tooltip

        current = current.parent

    return None


class GUI:
    def __init__(
            self, *layers: Element, renderer: DrawFunc | None = None,
            hover_tooltip_margin: int = HOVER_TOOLTIP_MARGIN
        ):
        """Each layer in `layers` is treated as its own separate root element."""
        self.layers = list(layers)

        self.hovered: Element | None = None
        self.pressed: Element | None = None
        self.tooltip_margin = hover_tooltip_margin
        self.work_surface: pg.Surface = DUMMY_SURFACE
        self._set_renderer(renderer)

    def _prepare_work_surface(self, dims: tuple[int, int]) -> None:
        """Prepare a work surface of the correct size for drawing
        and clear it."""

        if self.work_surface.size != dims:
            self.work_surface = pg.Surface(dims, pg.SRCALPHA)
        self.work_surface.fill((0, 0, 0, 0))

    def _set_renderer(self, renderer: DrawFunc | None) -> None:
        self.renderer = renderer or _renderer.DEFAULT_RENDERER

    def hit_test(self, pos: tuple[int, int]) -> Element | None:
        """Returns the element under the given position,
        that is willing to accept a user input at `pos`,
        or None if no such element is found."""

        for root in self.layers[::-1]:
            if (hit := root.hit_test(pos)) is not None:
                return hit

        return None

    def update(self, dt_s: float) -> None:
        new_hovered = self.hit_test(pg.mouse.get_pos())

        for layer in self.layers:
            _propagate_update(layer, dt_s)

        if pg.mouse.get_pressed()[0]:
            new_pressed = new_hovered
        else:
            new_pressed = None

        if new_hovered is not self.hovered:
            if self.hovered is not None:
                self.hovered.hovered = False

            if new_hovered is not None:
                new_hovered.hovered = True

            self.hovered = new_hovered

        if new_pressed is not self.pressed:
            if self.pressed is not None:
                self.pressed.pressed = False

            if new_pressed is not None:
                new_pressed.pressed = True

            self.pressed = new_pressed

    def layout(self, rects: list[pg.Rect | None]) -> None:
        """Lay out layers according to `rects`.
        The number of rects must be equal to the number of layers.
        Use `None` as an entry in rects to leave a layer unchanged."""

        if len(rects) != len(self.layers):
            raise ValueError("The number of layout rects must match the number of layers")

        for root, rect in zip(self.layers, rects):
            if rect is not None:
                root.layout(rect)

    def draw(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        for root in self.layers:
            self._prepare_work_surface(surface.size)
            self.renderer(self.work_surface, root, theme)
            surface.blit(self.work_surface, (0, 0))

        # Draw hover tooltip
        if self.hovered and self.hovered is not None:
            # Calculate label position
            # Prefer bottom-right, but if there isn't enough space,
            # switch between bottom<->top or right<->left.

            mx, my = pg.mouse.get_pos()
            tooltip = _get_tooltip(self.hovered)
            if not tooltip:
                return  # no tooltip to show

            tw, th = tooltip.preferred_size()
            tooltip_rect = pg.Rect(mx + self.tooltip_margin, my + self.tooltip_margin, tw, th)

            if tooltip.layout_dirty:
                tooltip.layout(tooltip_rect)

            if tooltip_rect.right > surface.get_width():
                tooltip_rect.left = mx - tooltip_rect.width - self.tooltip_margin
                tooltip_rect.right = mx - self.tooltip_margin
            if tooltip_rect.bottom > surface.get_height():
                tooltip_rect.top = my - tooltip_rect.height - self.tooltip_margin
                tooltip_rect.bottom = my - self.tooltip_margin

            # Draw label
            tooltip.layout(tooltip_rect)
            self._prepare_work_surface(surface.size)
            self.renderer(self.work_surface, tooltip, theme)
            surface.blit(self.work_surface, (0, 0))
