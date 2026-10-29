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


from pygame import Rect, Surface

from james.helpers.base_elem import Element
from james.helpers.custom_types import SupportsGetItemColour


class Spacer[K](Element[K]):
    def __init__(self, *, flex: float = 1.0, min_w: int = 0, min_h: int = 0) -> None:
        super().__init__(flex=flex)
        self.min_w = min_w
        self.min_h = min_h

    def hit_test(self, pos: tuple[int, int]) -> Element | None:
        return None

    def preferred_size(self) -> tuple[int, int]:
        return (self.min_w, self.min_h)

    def layout(self, rect: Rect) -> None:
        self.assign_rect(rect)

    def draw_default(self, surface: Surface, theme: SupportsGetItemColour) -> None:
        """Draws nothing, as a Spacer is invisible."""
