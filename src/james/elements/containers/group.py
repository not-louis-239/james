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


from typing import Any, Iterator

from pygame import Rect, Surface

from james.helpers.base_elem import Element
from james.helpers.custom_types import Colour, SupportsGetItemColour


class Group(Element):
    def __init__(self, *children: Element, flex: float = 1.0, draw_attrs: dict[str, Any] | None = None, colours: dict[str, Colour] | None = None) -> None:
        """Create a group of elements that aren't necessarily connected."""
        super().__init__(flex=flex, draw_attrs=draw_attrs, colours=colours)
        self.children = list(children)  # type: ignore

    def __getitem__(self, index: int) -> Element:
        return self.children[index]

    def __iter__(self) -> Iterator[Element]:
        yield from self.children

    def hit_test(self, pos: tuple[int, int]) -> Element | None:
        for child in self.children[::-1]:
            if (hit := child.hit_test(pos)) is not None:
                return hit

        return None

    def clear_children(self) -> None:
        """Remove all children from the group."""
        self.children.clear()

    def preferred_size(self) -> tuple[int, int]:
        """A group without spatially connected elements has no intrinsic size."""
        return (0, 0)

    def layout(self, rect: Rect) -> None:
        self.rect = rect
        self.layout_dirty = False

    def draw_default(self, surface: Surface, theme: SupportsGetItemColour) -> None:
        for child in self.children:
            child.draw_default(surface, theme)
