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


import sys
from dataclasses import dataclass

import pygame as pg

from james.elements.static_leaves.label import Label
from james.helpers.base_elem import Element
from james.helpers.custom_types import SupportsGetItemColour
from james.helpers.utils import clamp, get_text_surf, wrap_text

_COMMAND_KEY = pg.KMOD_CTRL if sys.platform == "win32" else pg.KMOD_META

@dataclass
class _EditState:
    text: str
    cursor_pos: int
    selection_anchor: int | None


class InputBox[K](Element[K]):
    """An InputBox with an optional attached tooltip. The attached tooltip
    differs from the hover tooltip in that it appears as if it is attached
    under the InputBox instead of appearing when the mouse hovers over the
    InputBox."""

    CURSOR_FLASH_INTERVAL = 0.75
    CURSOR_VISUAL_W = 2

    def __init__(
            self, *, flex: float = 0, shrink: float = 0.0,
            font: pg.font.Font,
            inset: int = 0,
            sentinel_text: str = "",
            fixed_tooltip_w: int | None = None,
            border_w: int = 0,
            tooltip_inset: int | None = None,
            tooltip_font: pg.font.Font | None = None,
            k_tooltip: K | None = None,
            k_bg_colour: K | None = None,
            k_bg_hovered: K | None = None,
            k_bg_pressed: K | None = None,
            k_bg_active: K | None = None,
            k_fg_colour: K,
            k_fg_hovered: K | None = None,
            k_fg_pressed: K | None = None,
            k_fg_active: K | None = None,
            k_border_colour: K | None = None,
            k_border_hovered: K | None = None,
            k_border_pressed: K | None = None,
            k_border_active: K | None = None,
            k_cursor: K,
            k_bg_selection: K | None = None,
            k_sentinel: K | None = None,
            text_size_limit: int = 255,
            hover_tooltip: Label | None = None,
        ) -> None:
        super().__init__(
            flex=flex, shrink=shrink, hover_tooltip=hover_tooltip, interactive=True
        )

        self.text: str = ""
        self.font = font
        self.inset = inset

        # whether the InputBox is currently ready to accept user input
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
        self.k_bg_pressed = k_bg_pressed if k_bg_pressed is not None else k_bg_colour
        self.k_bg_active = k_bg_active if k_bg_active is not None else self.k_bg_pressed

        self.k_fg_colour = k_fg_colour
        self.k_fg_hovered = k_fg_hovered if k_fg_hovered is not None else k_fg_colour
        self.k_fg_pressed = k_fg_pressed if k_fg_pressed is not None else k_fg_colour
        self.k_fg_active = k_fg_active if k_fg_active is not None else self.k_fg_pressed

        self.k_border_colour = k_border_colour
        self.k_border_hovered = k_border_hovered if k_border_hovered is not None else k_border_colour
        self.k_border_pressed  = k_border_pressed if k_border_pressed is not None else k_border_colour
        self.k_border_active = k_border_active if k_border_active is not None else self.k_border_pressed

        self.k_cursor = k_cursor
        self.k_bg_selection = k_bg_selection
        self.k_sentinel = k_sentinel if k_sentinel is not None else self.k_fg_colour

        self.cursor_flash_time = 0
        self.cursor_pos = 0
        self.scroll_offset = 0
        self.mouse_selecting = False
        self.selection_anchor: int | None = None
        self.text_size_limit = text_size_limit
        self._undo_stack: list[_EditState] = []
        self._redo_stack: list[_EditState] = []

    @property
    def k_bg(self) -> K | None:
        return (
            self.k_bg_active if self.active
            else self.k_bg_hovered if self.hovered
            else self.k_bg_colour
        )

    @property
    def k_fg(self) -> K:
        return (
            self.k_sentinel if not self.text
            else self.k_fg_active if self.active
            else self.k_fg_hovered if self.hovered
            else self.k_fg_colour
        )

    @property
    def k_border(self) -> K | None:
        return (
            self.k_border_active if self.active
            else self.k_border_hovered if self.hovered
            else self.k_border_colour
        )

    def _get_cursor_pos_from_x(self, x_pos: int) -> int:
        """Get cursor position in terms of index from x-position in
        local coordinates."""

        x = (
            x_pos
            - self.rect.x
            - self.inset
            + self.scroll_offset
        )

        for i in range(len(self.text)):
            char_mid = self.font.size(self.text[:i])[0]
            next_mid = self.font.size(self.text[:i + 1])[0]

            if x < (char_mid + next_mid) / 2:
                return i

        return len(self.text)

    def _save_undo_state(self) -> None:
        """Add a new action to the undo stack. This will clear the redo stack."""
        self._undo_stack.append(
            _EditState(
                self.text,
                self.cursor_pos,
                self.selection_anchor,
            )
        )
        self._redo_stack.clear()

    def _ensure_cursor_visible(self) -> None:
        cursor_x = self.font.size(self.text[:self.cursor_pos])[0]
        visible_w = self.rect.width - 2 * self.inset

        if cursor_x - self.scroll_offset > visible_w:
            self.scroll_offset = cursor_x - visible_w

        elif cursor_x - self.scroll_offset < 0:
            self.scroll_offset = cursor_x

    def _delete_selection(self) -> bool:
        if not (selection := self.get_selection_range()):
            return False

        start, end = selection
        self.text = self.text[:start] + self.text[end:]
        self.cursor_pos = start
        self.selection_anchor = None
        self.cursor_flash_time = 0

        return True

    def _previous_word_pos(self) -> int:
        pos = self.cursor_pos

        # Skip whitespace to the right of the word
        while pos > 0 and not self.text[pos - 1].isalnum():
            pos -= 1

        # Skip the word itself
        while pos > 0 and self.text[pos - 1].isalnum():
            pos -= 1

        return pos

    def _next_word_pos(self) -> int:
        pos = self.cursor_pos

        # Skip whitespace to the left of the word
        while pos < len(self.text) and not self.text[pos].isalnum():
            pos += 1

        # Skip the word itself
        while pos < len(self.text) and self.text[pos].isalnum():
            pos += 1

        return pos

    def get_selection_range(self) -> tuple[int, int] | None:
        if self.selection_anchor is None or self.selection_anchor == self.cursor_pos:
            return None

        return (
            min(self.selection_anchor, self.cursor_pos),
            max(self.selection_anchor, self.cursor_pos),
        )

    def get_selected_text(self) -> str | None:
        selection = self.get_selection_range()
        if selection is None:
            return None
        return self.text[selection[0]:selection[1]]

    def delete_selection(self) -> bool:
        """Delete the text currently selected, and return True if successful,
        otherwise return False. """

        if self.get_selection_range() is None:
            return False

        self._save_undo_state()
        self._delete_selection()

        self.cursor_flash_time = 0
        return True

    def insert_text(self, text: str) -> None:
        if not text:
            return

        self._save_undo_state()
        self._delete_selection()

        self.text = (
            self.text[:self.cursor_pos]
            + text
            + self.text[self.cursor_pos:]
        )
        self.cursor_pos += len(text)

        self.text = self.text[:self.text_size_limit]
        self.cursor_pos = min(self.cursor_pos, self.text_size_limit)

        self.cursor_flash_time = 0

    def select_all(self) -> None:
        self.selection_anchor = 0
        self.cursor_pos = len(self.text)
        self.cursor_flash_time = 0

    def copy_text(self) -> None:
        if text := self.get_selected_text():
            pg.scrap.put_text(text)
            self.cursor_flash_time = 0

    def cut_text(self) -> None:
        if text := self.get_selected_text():
            pg.scrap.put_text(text)
            self.delete_selection()
            self.cursor_flash_time = 0

    def paste_text(self) -> None:
        if text := pg.scrap.get_text():
            self.insert_text(text)
            self.cursor_flash_time = 0

    def undo(self) -> None:
        if not self._undo_stack:
            return

        self._redo_stack.append(
            _EditState(
                self.text,
                self.cursor_pos,
                self.selection_anchor,
            )
        )

        state = self._undo_stack.pop()

        self.text = state.text
        self.cursor_pos = state.cursor_pos
        self.selection_anchor = state.selection_anchor

        self.cursor_flash_time = 0
        self._ensure_cursor_visible()

    def redo(self) -> None:
        if not self._redo_stack:
            return

        self._undo_stack.append(
            _EditState(
                self.text,
                self.cursor_pos,
                self.selection_anchor,
            )
        )

        state = self._redo_stack.pop()

        self.text = state.text
        self.cursor_pos = state.cursor_pos
        self.selection_anchor = state.selection_anchor

        self.cursor_flash_time = 0
        self._ensure_cursor_visible()

    def move_cursor(self, position: int, *, selecting: bool = False) -> None:
        position = clamp(position, 0, len(self.text))

        if selecting:
            if self.selection_anchor is None:
                self.selection_anchor = self.cursor_pos
        else:
            self.selection_anchor = None

        self.cursor_pos = position

    def set_tooltip(self, msg: str | None = None) -> None:
        self.tooltip_msg = msg

    def clear_tooltip(self) -> None:
        self.set_tooltip(None)

    def on_focus(self, x_pos: int) -> None:
        """Call this when the mouse goes down while hovering over `self`."""

        self.active = True

        self.cursor_pos = self._get_cursor_pos_from_x(x_pos)
        self.selection_anchor = self.cursor_pos
        self.mouse_selecting = True

        self.cursor_flash_time = 0

    def on_unfocus(self) -> None:
        """Call this when the mouse goes down while not hovering over `self`."""

        self.active = False
        self.mouse_selecting = False
        self.selection_anchor = None

    def on_mouse_up(self) -> None:
        """Call this when the mouse goes up."""

        # Stop selecting
        self.mouse_selecting = False

        # If cursor and selection are at the same place, cancel selection.
        if self.cursor_pos == self.selection_anchor:
            self.selection_anchor = None

    def handle_input(self, events: list[pg.event.Event], dt_s: float) -> bool:
        """Handles user input and returns True if `self`'s contents were changed."""

        mods = pg.key.get_mods()
        old_contents = self.text

        # Cursor flash time
        if self.active:
            self.cursor_flash_time = (self.cursor_flash_time + dt_s) % self.CURSOR_FLASH_INTERVAL
        else:
            self.cursor_flash_time = 0

        # Handle KEYDOWN events
        for event in events:
            if event.type == pg.MOUSEMOTION and self.mouse_selecting:
                self.cursor_pos = self._get_cursor_pos_from_x(event.pos[0])
                self.cursor_flash_time = 0

            elif event.type == pg.KEYDOWN and self.active:
                # Select all
                if (mods & _COMMAND_KEY) and event.key == pg.K_a:
                    self.select_all()

                # Copy text
                elif (mods & _COMMAND_KEY) and event.key == pg.K_c:
                    self.copy_text()

                # Cut text
                elif (mods & _COMMAND_KEY) and event.key == pg.K_x:
                    self.cut_text()

                # Paste text
                elif (mods & _COMMAND_KEY) and event.key == pg.K_v:
                    self.paste_text()

                # Redo - must come before undo
                elif (
                    (mods & _COMMAND_KEY) and
                    (
                        (mods & pg.KMOD_SHIFT) and event.key == pg.K_z
                        or event.key == pg.K_y
                    )
                ):
                    self.redo()

                # Undo
                elif (mods & _COMMAND_KEY) and event.key == pg.K_z:
                    self.undo()

                # Delete
                elif event.key == pg.K_BACKSPACE:
                    if not self.delete_selection() and self.cursor_pos > 0:
                        self._save_undo_state()

                        if mods & _COMMAND_KEY:
                            dest_pos = 0
                        elif mods & pg.KMOD_ALT:
                            dest_pos = self._previous_word_pos()
                        else:
                            dest_pos = self.cursor_pos - 1

                        self.text = (
                            self.text[:dest_pos]
                            + self.text[self.cursor_pos:]
                        )
                        self.cursor_pos = dest_pos

                    self.cursor_flash_time = 0

                # Forward delete
                elif event.key == pg.K_DELETE:
                    if not self.delete_selection() and self.cursor_pos < len(self.text):
                        if mods & pg.KMOD_ALT:
                            dest_pos = self._next_word_pos()
                        else:
                            dest_pos = self.cursor_pos + 1

                        self._save_undo_state()
                        self.text = (
                            self.text[:self.cursor_pos]
                            + self.text[dest_pos:]
                        )

                    self.cursor_flash_time = 0

                # Move cursor left
                elif event.key == pg.K_LEFT:
                    if mods & _COMMAND_KEY:
                        dest_pos = 0
                    elif mods & pg.KMOD_ALT:
                        dest_pos = self._previous_word_pos()
                    elif self.selection_anchor is not None and not (mods & pg.KMOD_SHIFT):
                        dest_pos = min(self.cursor_pos, self.selection_anchor)
                    else:
                        dest_pos = self.cursor_pos - 1

                    self.move_cursor(
                        dest_pos,
                        selecting=bool(mods & pg.KMOD_SHIFT),
                    )
                    self.cursor_flash_time = 0

                # Move cursor right
                elif event.key == pg.K_RIGHT:
                    if mods & _COMMAND_KEY:
                        dest_pos = len(self.text)
                    elif mods & pg.KMOD_ALT:
                        dest_pos = self._next_word_pos()
                    elif self.selection_anchor is not None and not (mods & pg.KMOD_SHIFT):
                        dest_pos = max(self.cursor_pos, self.selection_anchor)
                    else:
                        dest_pos = self.cursor_pos + 1

                    self.move_cursor(
                        dest_pos,
                        selecting=bool(mods & pg.KMOD_SHIFT),
                    )
                    self.cursor_flash_time = 0

                # Add characters
                elif event.key not in (pg.K_RETURN, pg.K_ESCAPE, pg.K_TAB):
                    if text := event.unicode:
                        # Append character
                        self.insert_text(text)

        self._ensure_cursor_visible()
        return self.text != old_contents

    def draw_primitive(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        """Draw to a surface a basic solid background,
        and the text to be rendered, cropped to fit within the input box."""

        # Background
        if self.k_bg is not None:
            pg.draw.rect(surface, theme[self.k_bg], self.rect)

        text_max_width = self.rect.width - 2 * self.inset
        text_top = self.rect.y + (self.rect.h - self.font.get_height()) // 2

        text_left = self.rect.x + self.inset

        # Draw selection highlight
        if self.selection_anchor is not None:
            left, right = min(self.selection_anchor, self.cursor_pos), max(self.selection_anchor, self.cursor_pos)
            select_left = text_left + max(0, self.font.size(self.text[:left])[0] - self.scroll_offset)
            select_right = text_left + min(text_max_width, self.font.size(self.text[:right])[0] - self.scroll_offset)
            pg.draw.rect(surface, theme[self.k_bg_selection], (select_left, text_top, select_right - select_left, self.font.get_height()))

        text_surf = self.font.render(self.text, True, theme[self.k_fg])
        source_rect = pg.Rect(
            self.scroll_offset,
            0,
            text_max_width,
            self.font.get_height()
        )

        dest = (self.rect.x + self.inset, text_top)
        surface.blit(text_surf, dest, source_rect)

    def draw_default_border(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        if self.border_w and self.k_border is not None:
            pg.draw.rect(surface, theme[self.k_border], self.rect, self.border_w)

    def draw_cursor(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        # Draw the cursor
        if self.active and self.cursor_flash_time < self.CURSOR_FLASH_INTERVAL * 0.5:
            cursor_x = self.rect.x + self.inset + (
                0 if not self.text else clamp(
                    self.font.size(self.text[:self.cursor_pos])[0] - self.scroll_offset,
                    0,
                    self.rect.width - 2 * self.inset,
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

    def preferred_size(self) -> tuple[int, int]:
        return (0, self.font.get_height() + 2 * self.inset)

    def layout(self, rect) -> None:
        self.assign_rect(rect)

    def draw_default(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        if not self.visible:
            return

        # Primitive
        self.draw_primitive(surface, theme)
        self.draw_cursor(surface, theme)
        self.draw_default_border(surface, theme)

        # Tooltip
        self.draw_tooltip_background(surface, theme)
        self.draw_tooltip(surface, theme)
        self.draw_default_tooltip_border(surface, theme)

