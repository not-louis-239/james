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

from james._internals.constants import HOVER_TOOLTIP_MARGIN
from james.helpers.base_elem import Element
from james.helpers.custom_types import DrawFunc, SupportsGetItemColour
from james.helpers import renderer as _renderer


def _propagate_update(elem: Element, dt_s: float) -> None:
    elem.update(dt_s)
    for c in elem.children:
        _propagate_update(c, dt_s)


class GUI:
    def __init__(
            self, *layers: Element, renderer: DrawFunc | None,
            hover_tooltip_margin: int = HOVER_TOOLTIP_MARGIN
        ):
        """Each layer in `layers` is treated as its own separate root element."""
        self.layers = list(layers)

        self.hovered: Element | None = None
        self.pressed: Element | None = None
        self.tooltip_margin = hover_tooltip_margin
        self._set_renderer(renderer)

    def _set_renderer(self, renderer: DrawFunc | None) -> None:
        chosen = renderer or _renderer.DEFAULT_RENDERER
        if chosen is None:
            raise RuntimeError(
                f"No renderer set for {type(self).__name__}. "
                "Use set_default_renderer() to set one "
                "or provide renderer= with a valid "
                "draw function in the constructor."
            )

        self.renderer = chosen

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
            self.renderer(surface, root, theme)

        # Draw hover tooltip
        if self.hovered and self.hovered.hover_tooltip is not None:
            # Calculate label position
            # Prefer bottom-right, but if there isn't enough space,
            # switch between bottom<->top or right<->left.

            mx, my = pg.mouse.get_pos()
            label = self.hovered.hover_tooltip
            label_w, label_h = label.rect.size
            label_rect = pg.Rect(mx + self.tooltip_margin, my + self.tooltip_margin, label_w, label_h)

            if label_rect.right > surface.get_width():
                label_rect.left = mx - label_rect.width - self.tooltip_margin
                label_rect.right = mx - self.tooltip_margin
            if label_rect.bottom > surface.get_height():
                label_rect.top = my - label_rect.height - self.tooltip_margin
                label_rect.bottom = my - self.tooltip_margin

            # Draw label
            self.renderer(surface, label, theme)
