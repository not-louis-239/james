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
from widgets_and_stuff._custom_types import Colour
from widgets_and_stuff.utils import get_text_surf, wrap_text


class InputBox(Widget):
    DELETE_DELAY = 0.5
    DELETE_INTERVAL = 0.075

    CURSOR_FLASH_INTERVAL = 0.75
    CURSOR_VISUAL_W = 2

    TEXT_RENDER_LIMIT_CHARS = 255

    def __init__(
            self, *, flex: float = 0,
            draw_attrs: dict[str, Any] | None = None,
            colours: dict[str, tuple[int, int, int]] | None = None,
            font: pg.font.Font,
            inset: int = 0,
            sentinel_text: str = "",
            fixed_tooltip_w: int | None = None
        ) -> None:
        super().__init__(flex=flex, draw_attrs=draw_attrs, colours=colours)
        self.font = font
        self.inset = inset
        self.active = False
        self.sentinel_text = sentinel_text
        self.tooltip_msg: str | None = None
        self.fixed_tooltip_w = fixed_tooltip_w

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

    def draw_primitive(self, surface: pg.Surface, bg_colour: Colour, fg_colour: Colour, sentinel_colour: Colour) -> None:
        """Draw to a surface a basic solid background,
        and the text to be rendered, cropped to fit within the input box."""

        # Background
        pg.draw.rect(surface, bg_colour, self.rect)

        # Text - rendering only last 255 chars for performance
        fg_colour = fg_colour if self.text else sentinel_colour
        text = self.text[-255:] if self.text else self.sentinel_text
        text_surf = get_text_surf(self.font, text, fg_colour)
        text_visual_width = self.rect.width - 2 * self.inset

        # Draw the text aligned to left-centre
        dest = (
            self.rect.x + self.inset,
            self.rect.centery - text_surf.get_height() // 2,
        )

        source_rect = pg.Rect(
            max(0, text_surf.get_width() - text_visual_width),
            0,
            min(text_visual_width, text_surf.get_width()),
            text_surf.get_height()
        )

        surface.blit(text_surf, dest, source_rect)

    def draw_cursor(self, surface: pg.Surface, colour: Colour) -> None:
        # Draw the cursor
        if self.active and self.cursor_flash_time < self.CURSOR_FLASH_INTERVAL * 0.5:
            cursor_x = self.rect.x + self.inset + (0 if not self.text else min(self.CURSOR_VISUAL_W, surface.get_width()))
            cursor_top_y = self.rect.centery - surface.get_height() // 2
            cursor_bot_y = self.rect.centery + surface.get_height() // 2
            pg.draw.line(surface, colour, (cursor_x, cursor_top_y), (cursor_x, cursor_bot_y), width=self.CURSOR_VISUAL_W)

    def draw_tooltip(self, surface: pg.Surface, bg_colour: Colour, fg_colour: Colour) -> None:
        """Draws a borderless tooltip. Border is open to custom implementation."""

        if not self.tooltip_msg:
            return

        # Calculate tooltip width
        tooltip_w = self.fixed_tooltip_w or self.rect.w

        # Draw the text
        lines = wrap_text(text=self.tooltip_msg, font=self.font, maxwidth=tooltip_w - 2 * self.inset)
        font_h = self.font.get_height()
        text_height = font_h * len(lines)

        # Tooltip rect
        tooltip_rect = pg.Rect(self.rect.left, self.rect.bottom, tooltip_w, text_height + 2 * self.inset)

        start_x = self.rect.x + self.inset
        start_y = self.rect.bottom + self.inset

        # Draw background
        pg.draw.rect(surface, bg_colour, tooltip_rect)

        # Draw text
        for lineno, line in enumerate(lines):
            surface.blit(get_text_surf(self.font, line, fg_colour), (start_x, start_y + font_h * lineno))

    def preferred_size(self) -> tuple[int, int]:
        return (0, self.font.get_height() + 2 * self.inset)

    def layout(self, rect) -> None:
        self.rect = rect
