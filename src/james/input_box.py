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

from james._internals.base_elem import Element
from james._internals.custom_types import Colour, SupportsGetItemColour
from james.utils import get_text_surf, wrap_text


class InputBox(Element):
    DELETE_DELAY = 0.5
    DELETE_INTERVAL = 0.075

    CURSOR_FLASH_INTERVAL = 0.75
    CURSOR_VISUAL_W = 2

    TEXT_RENDER_LIMIT_CHARS = 255

    def __init__(
            self, *, flex: float = 0,
            draw_attrs: dict[str, Any] | None = None,
            colours: dict[str, Colour] | None = None,
            font: pg.font.Font,
            inset: int = 0,
            sentinel_text: str = "",
            fixed_tooltip_w: int | None = None,
            border_w: int = 0,
            tooltip_inset: int | None = None,
            tooltip_font: pg.font.Font | None = None,
            k_tooltip: str | None = None,
            k_bg_colour: str | None = None,
            k_bg_hovered: str | None = None,
            k_bg_active: str | None = None,
            k_fg_colour: str,
            k_fg_hovered: str | None = None,
            k_fg_active: str | None = None,
            k_border_colour: str | None = None,
            k_border_hovered: str | None = None,
            k_border_active: str | None = None,
            k_cursor: str,
            k_sentinel: str | None = None
        ) -> None:
        super().__init__(flex=flex, draw_attrs=draw_attrs, colours=colours)

        self.text: str = ""
        self.font = font
        self.inset = inset
        self.active = False

        self.sentinel_text = sentinel_text
        self.tooltip_msg: str | None = None
        self.fixed_tooltip_w = fixed_tooltip_w
        self.border_w = border_w

        self.tooltip_inset = tooltip_inset if tooltip_inset is not None else inset
        self.tooltip_font = tooltip_font or font
        self.k_tooltip = k_tooltip if k_tooltip is not None else k_fg_colour

        self.k_bg_colour = k_bg_colour
        self.k_bg_hovered = k_bg_hovered if k_bg_hovered is not None else k_bg_colour
        self.k_bg_active = k_bg_active if k_bg_active is not None else k_bg_colour

        self.k_fg_colour = k_fg_colour
        self.k_fg_hovered = k_fg_hovered if k_fg_hovered is not None else k_fg_colour
        self.k_fg_active = k_fg_active if k_fg_active is not None else k_fg_colour

        self.k_border_colour = k_border_colour
        self.k_border_hovered = k_border_hovered if k_border_hovered is not None else k_border_colour
        self.k_border_active = k_border_active if k_border_active is not None else k_border_colour

        self.k_cursor = k_cursor
        self.k_sentinel = k_sentinel if k_sentinel is not None else self.k_fg_colour

        self.delete_timer = self.DELETE_DELAY
        self.cursor_flash_time = 0

    @property
    def k_bg(self) -> str | None:
        return (
            self.k_bg_active if self.active
            else self.k_bg_hovered if self.rect.collidepoint(pg.mouse.get_pos())
            else self.k_bg_colour
        )

    @property
    def k_fg(self) -> str:
        return (
            self.k_sentinel if not self.text
            else self.k_fg_active if self.active
            else self.k_fg_hovered if self.rect.collidepoint(pg.mouse.get_pos())
            else self.k_fg_colour
        )

    @property
    def k_border(self) -> str | None:
        return (
            self.k_border_active if self.active
            else self.k_border_hovered if self.rect.collidepoint(pg.mouse.get_pos())
            else self.k_border_colour
        )

    def set_tooltip(self, msg: str | None = None) -> None:
        self.tooltip_msg = msg

    def clear_tooltip(self) -> None:
        self.set_tooltip(None)

    def handle_input(self, keys: pg.key.ScancodeWrapper, events: list[pg.event.Event], dt_s: float) -> bool:
        """Handles user input and returns True if `self`'s contents were changed."""

        old_contents = self.text

        # Cursor flash time
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

        return self.text != old_contents

    def draw_primitive(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        """Draw to a surface a basic solid background,
        and the text to be rendered, cropped to fit within the input box."""

        # Background
        if self.k_bg is not None:
            pg.draw.rect(surface, theme[self.k_bg], self.rect)

        # Text - rendering only last 255 chars for performance
        text = self.text[-255:] if self.text else self.sentinel_text
        text_surf = get_text_surf(self.font, text, theme[self.k_fg])
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

    def draw_default_border(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        if self.border_w and self.k_border is not None:
            pg.draw.rect(surface, theme[self.k_border], self.rect, self.border_w)

    def draw_cursor(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        # Draw the cursor
        if self.active and self.cursor_flash_time < self.CURSOR_FLASH_INTERVAL * 0.5:
            cursor_x = self.rect.x + self.inset + (
                0 if not self.text else min(
                    self.rect.width - 2 * self.inset,
                    self.font.size(self.text)[0]
                )
            )
            cursor_top_y = self.rect.centery - self.font.get_height() // 2
            cursor_bot_y = self.rect.centery + self.font.get_height() // 2
            pg.draw.line(surface, theme[self.k_cursor], (cursor_x, cursor_top_y), (cursor_x, cursor_bot_y), width=self.CURSOR_VISUAL_W)

    def _tooltip_lines_and_rect(self) -> tuple[list[str], pg.Rect]:
        """Return (lines, rect) for tooltip drawing."""

        if not self.tooltip_msg:
            return [], pg.Rect(self.rect.left, self.rect.bottom, 0, 0)

        # Calculate tooltip width
        tooltip_w = self.fixed_tooltip_w or self.rect.w

        # Draw the text
        lines = wrap_text(text=self.tooltip_msg, font=self.tooltip_font, maxwidth=tooltip_w - 2 * self.tooltip_inset)
        font_h = self.tooltip_font.get_height()
        text_height = font_h * len(lines)

        # Tooltip rect
        tooltip_rect = pg.Rect(self.rect.left, self.rect.bottom, tooltip_w, text_height + 2 * self.tooltip_inset)

        return lines, tooltip_rect

    def draw_tooltip_background(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        _, rect = self._tooltip_lines_and_rect()

        # Draw background
        if self.k_bg_colour is not None:
            pg.draw.rect(surface, theme[self.k_bg_colour], rect)

    def draw_tooltip(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        """Draws borderless, colourless, tooltip text."""

        if not self.tooltip_msg:
            return

        lines, _ = self._tooltip_lines_and_rect()

        start_x = self.rect.x + self.tooltip_inset
        start_y = self.rect.bottom + self.tooltip_inset

        # Draw text
        font_h = self.tooltip_font.get_height()
        for lineno, line in enumerate(lines):
            surface.blit(get_text_surf(self.tooltip_font, line, theme[self.k_tooltip]), (start_x, start_y + font_h * lineno))

    def draw_default_tooltip_border(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        """Draws a default-style border for `self`'s tooltip
        using `self.border_w` and `self.k_border` if set."""

        _, rect = self._tooltip_lines_and_rect()

        if self.border_w and self.k_border is not None:
            pg.draw.rect(surface, theme[self.k_border], rect, self.border_w)

    def draw_default(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        # Primitive
        self.draw_primitive(surface, theme)
        self.draw_cursor(surface, theme)
        self.draw_default_border(surface, theme)

        # Tooltip
        self.draw_tooltip_background(surface, theme)
        self.draw_tooltip(surface, theme)
        self.draw_default_tooltip_border(surface, theme)

    def preferred_size(self) -> tuple[int, int]:
        return (0, self.font.get_height() + 2 * self.inset)

    def layout(self, rect) -> None:
        self.rect = rect
