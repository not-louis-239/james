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

from widgets_and_stuff._base_widget import Widget


class Panel(Widget):
    """A simple panel that can contain one child with padding."""
    def __init__(
            self, *, flex: float = 0,
            draw_attrs: dict[str, Any] | None = None,
            colours: dict[str, tuple[int, int, int]] | None = None,
            horiz_padding: int = 0, vert_padding: int = 0,
            child: Widget | None = None
        ) -> None:
        super().__init__(flex=flex, draw_attrs=draw_attrs, colours=colours)
        self.horiz_padding = horiz_padding
        self.vert_padding = vert_padding
        self.child = child
        self.children = [child] if child is not None else []

    def preferred_size(self) -> tuple[int, int]:
        if not self.child:
            return (self.horiz_padding * 2, self.vert_padding * 2)
        cw, ch = self.child.preferred_size()
        return (cw + 2 * self.horiz_padding, ch + 2 * self.vert_padding)

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect
        if self.child:
            child_rect = rect.inflate(-2 * self.horiz_padding, -2 * self.vert_padding)
            self.child.layout(child_rect)
