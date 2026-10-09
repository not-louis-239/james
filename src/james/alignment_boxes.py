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


from enum import StrEnum

import pygame as pg

from james._internals.base_elem import Element
from james._internals.custom_types import DrawFunc, SupportsGetItemColour


class HAlign(StrEnum):
    LEFT = "left"
    CENTRE = "centre"
    RIGHT = "right"

class VAlign(StrEnum):
    TOP = "top"
    CENTRE = "centre"
    BOTTOM = "bottom"


class _Box(Element):
    """Generic base class to store attributes common to both `HBox`es and `VBox`es"""

    def __init__(self, *children: Element, padding: int = 0, gap: int = 0, renderer: DrawFunc) -> None:
        """Initialises a new box.
        padding = space between the box's edge and the first or last child
        gap     = space between children in the box"""
        super().__init__()
        self.padding = padding
        self.gap = gap
        self.renderer = renderer

        if children is not None:
            for child in children:
                self.add_child(child)

    def add_child(self, child: Element) -> None:
        self.children.append(child)

    def draw_default(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        for child in self.children:
            self.renderer(surface, child, theme)

class HBox(_Box):
    """Horizontal box"""

    def preferred_size(self) -> tuple[int, int]:
        total_w = 0
        max_h = 0

        # calculate preferred size of children
        for child in self.children:
            w, h = child.preferred_size()
            total_w += w
            max_h = max(max_h, h)

        # add gap between children
        total_w += self.gap * max(0, len(self.children) - 1)

        # add padding
        total_w += self.padding * 2
        total_h = max_h + self.padding * 2

        return (total_w, total_h)

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect

        # measure fixed sizes
        total_fixed_width = 0
        flex_children: list[Element] = []

        for child in self.children:
            flex = child.flex
            if flex:
                flex_children.append(child)
                continue
            w, _ = child.preferred_size()
            total_fixed_width += w

        total_gaps = self.gap * max(0, len(self.children) - 1)

        remaining = max(0, rect.width - 2 * self.padding - total_fixed_width - total_gaps)

        # assign flex space
        total_flex = sum(c.flex for c in flex_children)
        flex_widths = {}

        if total_flex > 0:
            for c in flex_children:
                flex_widths[c] = remaining * (c.flex / total_flex)

        # place children
        h = rect.height - 2 * self.padding
        x = rect.x + self.padding
        y = rect.y + self.padding

        for child in self.children:
            w, _ = child.preferred_size()

            if child in flex_widths:
                w = int(flex_widths[child])

            child_rect = pg.Rect(x, y, w, h)
            child.layout(child_rect)

            x += w + self.gap

class VBox(_Box):
    """Vertical box"""

    def preferred_size(self) -> tuple[int, int]:
        total_h = 0
        max_w = 0

        # calculate preferred size of children
        for child in self.children:
            w, h = child.preferred_size()
            total_h += h
            max_w = max(max_w, w)

        # add gaps
        total_h += self.gap * max(0, len(self.children) - 1)

        # add padding
        total_h += self.padding * 2
        total_w = max_w + self.padding * 2

        return total_w, total_h

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect

        total_fixed_height = 0
        flex_children = []

        for child in self.children:
            flex = child.flex
            if flex:
                flex_children.append(child)
            else:
                _, h = child.preferred_size()
                total_fixed_height += h

        total_gaps = self.gap * max(0, len(self.children) - 1)
        remaining = max(0, rect.height - 2 * self.padding - total_fixed_height - total_gaps)

        total_flex = sum(c.flex for c in flex_children)
        flex_heights = {}

        # Assign flex space
        if total_flex > 0:
            for c in flex_children:
                flex_heights[c] = remaining * (c.flex / total_flex)

        # place children
        w = rect.width - 2 * self.padding
        x = rect.x + self.padding
        y = rect.y + self.padding

        for child in self.children:
            _, h = child.preferred_size()

            if child in flex_heights:
                h = int(flex_heights[child])

            child_rect = pg.Rect(x, y, w, h)
            child.layout(child_rect)

            y += h + self.gap

class SBox(_Box):
    """Sized box that gives its child a fixed-size slot, with alignment."""

    def __init__(
            self, child: Element, *,
            forced_width: int | None = None, forced_height: int | None = None,
            renderer: DrawFunc,
            h_align: HAlign = HAlign.CENTRE,
            v_align: VAlign = VAlign.CENTRE
        ) -> None:
        super().__init__(renderer=renderer)
        self.child = child
        self.children = [child]

        self.forced_width = forced_width
        self.forced_height = forced_height
        self.h_align = h_align
        self.v_align = v_align

    def preferred_size(self) -> tuple[int, int]:
        # Ask the child what it wants, but override it if we have a forced constraint
        child_w, child_h = self.child.preferred_size()
        w = self.forced_width if self.forced_width is not None else child_w
        h = self.forced_height if self.forced_height is not None else child_h
        return (w, h)

    def layout(self, rect: pg.Rect) -> None:
        child_w, child_h = self.child.preferred_size()
        child_rect = pg.Rect(0, 0, min(child_w, rect.width), min(child_h, rect.height))

        match self.h_align:
            case HAlign.LEFT:
                child_rect.left = rect.left
            case HAlign.CENTRE:
                child_rect.centerx = rect.centerx
            case HAlign.RIGHT:
                child_rect.right = rect.right

        # Vertical alignment
        match self.v_align:
            case VAlign.TOP:
                child_rect.top = rect.top
            case VAlign.CENTRE:
                child_rect.centery = rect.centery
            case VAlign.BOTTOM:
                child_rect.bottom = rect.bottom

        self.rect = rect
        self.child.layout(child_rect)
