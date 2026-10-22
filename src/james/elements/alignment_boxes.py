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

from james.helpers.base_elem import Element
from james.helpers.custom_types import DrawFunc, SupportsGetItemColour, Colour


class HAlign(StrEnum):
    LEFT = "left"
    CENTRE = "centre"
    RIGHT = "right"

class VAlign(StrEnum):
    TOP = "top"
    CENTRE = "centre"
    BOTTOM = "bottom"


# TODO: implement `shrink` attribute interpretation
# boxes choose elements to shrink to fit the box based on their `shrink` property


class _Box(Element):
    """Generic base class to store attributes common to both `HBox`es and `VBox`es"""

    def __init__(
            self, *children: Element,
            flex: float = 0.0, padding: int = 0, gap: int = 0,
            renderer: DrawFunc | None = None,
            k_bg_colour: str | None = None,
        ) -> None:
        """Initialises a new box.
        padding = space between the box's edge and the first or last child
        gap     = space between children in the box"""
        super().__init__(flex=flex)

        self.padding = padding
        self.gap = gap
        self.k_bg_colour = k_bg_colour
        self.shrink = sum(c.shrink for c in children)
        self._set_renderer(renderer)

        if children is not None:
            for child in children:
                self.add_child(child)

    def add_child(self, child: Element) -> None:
        self.children.append(child)
        child.parent = self

    def draw_default(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        if not self.visible:
            return

        if self.k_bg_colour is not None:
            pg.draw.rect(surface, theme[self.k_bg_colour], self.rect)
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

        # Measure preferred sizes
        preferred_widths: dict[Element, float] = {
            child: child.preferred_size()[0]
            for child in self.children
        }

        # Get children who can flex and shrink, and total gap width
        flex_children = [c for c in self.children if c.flex > 0]
        shrink_children = [c for c in self.children if c.shrink > 0]

        print(f"[{id(self)}] Number of shrink children before layout: {len(shrink_children)}")

        total_gaps = self.gap * max(0, len(self.children) - 1)
        remaining = (
            rect.width
            - 2 * self.padding
            - sum(preferred_widths.values())
            - total_gaps
        )
        print(f"Remaining space: {remaining}")

        # No need to `.copy()` because `preferred_widths` is not used from here onwards
        widths: dict[Element, float] = preferred_widths

        if remaining > 0:
            # Distribute excess space according to `flex`
            total_flex = sum(c.flex for c in flex_children)

            for c in flex_children:
                flex_amount = remaining * (c.flex / total_flex)
                widths[c] += flex_amount

        elif remaining < 0:
            # Distribute shortage according to `shrink`
            total_shrink = sum(c.shrink for c in shrink_children)

            print(
                f"[{id(self)}] SHORTAGE: "
                f"remaining={remaining}, "
                f"total_shrink={total_shrink}"
            )

            print(f"[{id(self)}] Number of shrink children during space assignment: {len(shrink_children)}")
            for c in shrink_children:
                shrink_amount = -remaining * (c.shrink / total_shrink)
                widths[c] = max(0, widths[c] - shrink_amount)
                print(f"[{id(self)}] Subtracted {shrink_amount} from {c}")

        # Arrange children
        h = rect.height - 2 * self.padding
        x = rect.x + self.padding
        y = rect.y + self.padding

        for child in self.children:
            w = widths[child]
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

        # Measure preferred sizes
        preferred_heights: dict[Element, float] = {
            child: child.preferred_size()[1]
            for child in self.children
        }

        # Get children who can flex and shrink, and total gap height
        flex_children = [c for c in self.children if c.flex > 0]
        shrink_children = [c for c in self.children if c.shrink > 0]

        total_gaps = self.gap * max(0, len(self.children) - 1)
        remaining = (
            rect.height
            - 2 * self.padding
            - sum(preferred_heights.values())
            - total_gaps
        )

        # No need to `.copy()` because `preferred_heights` is not used from here onwards
        heights: dict[Element, float] = preferred_heights

        if remaining > 0:
            # Distribute excess space according to `flex`
            total_flex = sum(c.flex for c in flex_children)

            for c in flex_children:
                flex_amount = remaining * (c.flex / total_flex)
                heights[c] += flex_amount

        elif remaining < 0:
            # Distribute shortage according to `shrink`
            total_shrink = sum(c.shrink for c in shrink_children)

            for c in shrink_children:
                shrink_amount = -remaining * (c.shrink / total_shrink)
                heights[c] = max(0, heights[c] - shrink_amount)

        # Arrange children
        w = rect.width - 2 * self.padding
        x = rect.x + self.padding
        y = rect.y + self.padding

        for child in self.children:
            h = heights[child]
            child_rect = pg.Rect(x, y, w, h)
            child.layout(child_rect)
            y += h + self.gap

class SBox(_Box):
    """Sized box that gives its child a fixed-size slot, with alignment.
    Without `strict`, `SBox` will only constrain an element.
    With `strict`, `SBox` ignores the child's preferred size entirely."""

    def __init__(
            self, child: Element, *,
            forced_width: int | None = None, forced_height: int | None = None,
            renderer: DrawFunc | None = None,
            h_align: HAlign = HAlign.CENTRE,
            v_align: VAlign = VAlign.CENTRE,
            strict: bool = False
        ) -> None:
        super().__init__(renderer=renderer)
        self.child = child
        self.children = [child]

        self.forced_width = forced_width
        self.forced_height = forced_height
        self.h_align = h_align
        self.v_align = v_align
        self.strict = strict
        self._set_renderer(renderer)

    def preferred_size(self) -> tuple[int, int]:
        # Ask the child what it wants, but override it if we have a forced constraint
        child_w, child_h = self.child.preferred_size()
        w = self.forced_width if self.forced_width is not None else child_w
        h = self.forced_height if self.forced_height is not None else child_h
        return (w, h)

    def layout(self, rect: pg.Rect) -> None:
        if self.strict:
            child_rect = pg.Rect(0, 0, *rect.size)
        else:
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
