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


class InputBox(Widget):
    DELETE_DELAY = 0.5
    DELETE_INTERVAL = 0.075
    CURSOR_FLASH_INTERVAL = 0.75

    def __init__(
            self, *, flex: float = 0,
            draw_attrs: dict[str, Any] | None = None,
            colours: dict[str, tuple[int, int, int]] | None = None,
            font: pg.font.Font,
            inset: int = 0,
            sentinel_text: str = "",
        ) -> None:
        super().__init__(flex=flex, draw_attrs=draw_attrs, colours=colours)
        self.font = font
        self.inset = inset
        self.active = False
        self.sentinel_text = sentinel_text
        self.tooltip_msg: str | None = None

        self.delete_timer = self.DELETE_DELAY
        self.cursor_flash_time = 0

    def set_tooltip(self, msg: str | None = None) -> None:
        self.tooltip_msg = msg

    def clear_tooltip(self) -> None:
        self.set_tooltip(None)

    def handle_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.event.Event], dt_s: float) -> None:
        if self.active:
            self.cursor_flash_time = (self.cursor_flash_time + dt_s) % self.CURSOR_FLASH_INTERVAL
        else:
            self.cursor_flash_time = 0

        # Handle KEYDOWN events
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.active = self.rect.collidepoint(event.pos)
                self.cursor_flash_time = 0
            elif event.type == pg.KEYDOWN:
                if self.active:
                    if event.key == pg.K_BACKSPACE:
                        self.text = self.text[:-1]
                        self.cursor_flash_time = 0
                    elif event.key not in (pg.K_RETURN, pg.K_ESCAPE, pg.K_TAB):
                        # Append character
                        self.text += event.unicode
                        self.cursor_flash_time = 0

        # Handle delete
        if keys[pg.K_BACKSPACE] and self.active:
            self.delete_timer -= dt_s
            if self.delete_timer <= 0:
                self.text = self.text[:-1]
                self.delete_timer += self.DELETE_INTERVAL
                self.cursor_flash_time = 0
        else:
            # If delete is not held down, reset the delete timer
            self.delete_timer = self.DELETE_DELAY

    def preferred_size(self) -> tuple[int, int]:
        return (0, self.font.get_height() + 2 * self.inset)

    def layout(self, rect) -> None:
        self.rect = rect