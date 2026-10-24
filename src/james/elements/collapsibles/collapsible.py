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

from pygame import Surface

from james.helpers.base_elem import Element
from james.helpers.custom_types import Colour, SupportsGetItemColour


class Collapsible(Element):
    def __init__(
            self, *,
            flex: float = 0, shrink: float = 0,
            trigger: Element, content: Element,
            draw_attrs: dict[str, Any] | None = None,
            colours: dict[str, Colour] | None = None
        ) -> None:
        super().__init__(flex=flex, shrink=shrink, draw_attrs=draw_attrs, colours=colours)

        self.trigger = trigger
        self.content = content
        self.expanded = False

    def toggle(self) -> None:
        self.expanded = not self.expanded

    def draw_default(self, surface: Surface, theme: SupportsGetItemColour) -> None:
        if self.expanded:
            self.trigger.draw_default(surface, theme)
            self.content.draw_default(surface, theme)
        else:
            self.trigger.draw_default(surface, theme)
