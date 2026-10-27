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


from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

import pygame as pg

from james._internals.constants import HITBOX_COLOUR_0, HITBOX_W
from james.helpers import renderer as _renderer
from james.helpers.custom_types import Colour, DrawFunc, SupportsGetItemColour

if TYPE_CHECKING:
    from james.elements.static_leaves.label import Label


class Element(ABC):
    def __init__(
            self, *, flex: float = 0.0, shrink: float = 0.0,
            interactive: bool = False,
            hover_tooltip: Label | None = None,
        ) -> None:
        # The ratios of flex or shrink for different UI components
        # determines how the excess or shortage of space is distributed
        # by arrangement boxes such as `HBox`es, `VBox`es, etc.

        self.flex = flex  # expand if there is excess space
        self.shrink = shrink  # shrink if there is insufficient space
        self._fixed_shrink = shrink

        self.rect = pg.Rect(0, 0, 0, 0)

        self.children: list[Element] = []
        self.parent: Element | None = None

        # If an element is invisible, none of its children will be laid out,
        # drawn or hit-tested. Visibility cascades downwards.

        self.visible: bool = True  # should I be seen?
        self.layout_dirty: bool = True  # do I need to be re-laid out?

        self.pressed: bool = False
        self.hovered: bool = False
        self.disabled: bool = False  # am I supposed to block user input?

        # `interactive` is only applicable for containers.
        # It dictates: if a click doesn't hit any of `self`'s children, whether
        # `self` should take it.
        self.interactive = interactive

        self.hover_tooltip = hover_tooltip

        # Classes inheriting from `Element` should define their own
        # specialised drawing state rather than storing arbitrary renderer
        # attributes on the base Element.
        # Custom renderers receive the concrete Element or inherited instance,
        # so they can access any attributes defined by that element directly.

    def draw_hitbox(self, surface: pg.Surface) -> None:
        """Draw the hitbox of the UI element."""
        pg.draw.rect(surface, HITBOX_COLOUR_0, self.rect, HITBOX_W)

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

    def _set_visibility(self, val: bool) -> None:
        """Set the visibility of the UI element and all of its children, if any."""
        self.visible = val
        self.layout_dirty = True
        for child in self.children:
            child._set_visibility(val)

    def update(self, dt_s: float) -> None:
        """Note: only updates `self`, not its children."""
        pass

    def invalidate_layout(self) -> None:
        """Invalidate the layout of the element, and propagate it upwards."""
        self.layout_dirty = True
        if self.parent is not None:
            self.parent.invalidate_layout()

    def add_child(self, child: Element, index: int | None = None) -> None:
        """Add a `child` to `self` at a given `index`.  If no index is provided,
        the child is added to the end of `self`'s children list."""

        if index is not None:
            self.children.insert(index, child)
        else:
            self.children.append(child)

        child.parent = self

        # Propagate shrink unless an override is set
        if self._fixed_shrink is None:
            self.shrink = self.shrink + child.shrink

        # Layout shouldn't be trusted
        self.invalidate_layout()

    def rm_child(self, child: Element | int) -> bool:
        """Attempt to remove a child, or index from the group and return
        whether the child was removed."""
        if isinstance(child, int):
            if not 0 <= child < len(self.children):
                return False

            child = self.children[child]

        if child in self.children:
            self.children.remove(child)
            child.parent = None

            if self._fixed_shrink is None:
                self.shrink = self.shrink - child.shrink

            self.invalidate_layout()
            return True

        return False

    def clear_children(self) -> None:
        """Remove all children from the group."""
        for child in self.children:
            child.parent = None

        self.children.clear()

        if self._fixed_shrink is None:
            self.shrink = 0

        self.invalidate_layout()

    @property
    def parents(self) -> list[Element]:
        """Return the `Element`'s parent `Element`s."""

        parents: list[Element] = []
        x = self

        # Walk up the parent tree until we find an element with no parent
        while x.parent is not None:
            parents.append(x.parent)
            x = x.parent

        return parents

    def hide(self) -> None:
        """Hide the UI element and all of its children, if any."""
        self._set_visibility(False)

    def show(self) -> None:
        """Show the UI element and all of its children, if any."""
        self._set_visibility(True)

    def toggle_visibility(self) -> None:
        """Toggle the visibility of the UI element.
        If it is currently invisible, call `show()`.
        If it is currently visible, call `hide()`.
        And propagates the new value down to all of `self`'s children.
        """
        (self.hide if self.visible else self.show)()

    def to_local(self, pos: tuple[int, int]) -> tuple[int, int]:
        """Convert a global position to a local position within this element."""
        return pos

    def _contains_point(self, pos: tuple[int, int]) -> bool:
        """Return whether an `Element` encompasses a point at `pos`.
        This determines where an `Element` should begin to search its
        children if a click is received at `pos`.
        Default hitbox is assumed to be the element's `rect`."""

        return self.rect.collidepoint(pos)

    def hit_test(self, pos: tuple[int, int]) -> Element | None:
        """Given a `pos` in this element's parent's coordinate system,
        return the deepest element in the subtree contained by `self`
        that can receive pointer interaction at `pos`.
        If no such element is found, return `None`."""

        # print(f"[id:{id(self)}] Hit testing element '{type(self).__name__}', rect: {self.rect}")

        if not self.visible:
            # print(f"[id:{id(self)}] Invisible element: returning None")
            return None

        if not self._contains_point(pos):
            # print(f"[id:{id(self)}] Point not contained in element: returning None")
            return None

        pos = self.to_local(pos)
        # print(f"[id:{id(self)}] Point contained in element.")

        for child in self.children[::-1]:
            # print(f"[id:{id(child)}] Checking child '{type(child).__name__}', id: {id(child)}")
            if (hit := child.hit_test(pos)):
                # print(f"[id:{id(child)}] Child hit test returned '{type(hit).__name__}', id: {id(hit)}")
                return hit

        if self.interactive:
            # print(f"[id:{id(self)}] Interactive element: returning self")
            return self
        # print(f"[id:{id(self)}] No child hit test returned, returning None")
        return None

    def assign_rect(self, rect: pg.Rect) -> None:
        """Assign `rect` to `self.rect` and set `self.layout_dirty` to False."""
        self.rect = rect
        self.layout_dirty = False

    @abstractmethod
    def preferred_size(self) -> tuple[int, int]:
        """How big should this UI element be, given no constraints?"""
        raise NotImplementedError

    @abstractmethod
    def layout(self, rect: pg.Rect) -> None:
        """Assign the rect to `self` and divide space between
        any potential children of `self`."""
        raise NotImplementedError

    @abstractmethod
    def draw_default(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        """Default draw behaviour. You can use this or make your
        own draw function if you need specialised behaviour."""
        raise NotImplementedError
