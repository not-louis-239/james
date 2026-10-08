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


from functools import lru_cache
from dataclasses import dataclass

import pygame as pg

from ._custom_types import Colour
from ._constants import DUMMY_BLACK


@dataclass(kw_only=True)
class AmbientMessage:
    text: str = ""
    colour: Colour = (0, 0, 0)
    duration: float = 0.0

    def set_msg(self, text: str, colour: Colour, duration: float) -> None:
        self.text = text
        self.colour = colour
        self.duration = duration

    def clear(self) -> None:
        self.set_msg("", DUMMY_BLACK, 0.0)

    def update(self, dt_s: float) -> None:
        self.duration = max(0, self.duration - dt_s)
        if not self.active:
            self.clear()

    @property
    def active(self) -> bool:
        return self.duration > 0


def crop_text_to_fit(text: str, font: pg.font.Font, maxwidth: int) -> str:
    """Truncate the text string to fit within a given width.
    Truncates with '...' at the end if necessary.
    Returns an empty string if even an ellipsis doesn't fit."""

    if font.size(text)[0] <= maxwidth:  # font.size(...) returns (width, height)
        return text

    ELLIPSIS_CHAR = '…'
    if font.size(ELLIPSIS_CHAR)[0] > maxwidth:
        return ""

    known_good = ""

    # Try to test increasingly large strings of the original text
    # plus the ellipsis, until one is greater than maxwidth
    # then return the last known-good string

    for char in text:
        test_text = known_good + char + ELLIPSIS_CHAR
        if font.size(test_text)[0] > maxwidth:
            return known_good + ELLIPSIS_CHAR
        known_good += char

    return known_good


def _tokenise(text: str) -> list[str]:
    return text.split()


def wrap_text(text: str, font: pg.font.Font, maxwidth: int) -> list[str]:
    """Wrap text to fixed-size rows each. This could be useful in something
    like a text box display where text wrapping is needed.
    Returns a list of text lines, each no wider than `maxwidth`."""

    if font.size(text)[0] < maxwidth:
        return [text]

    # tokens are required so that the wrapping doesn't cut words in half
    tokens = _tokenise(text)

    space_left = maxwidth
    lines: list[str] = []
    current_line: str = ""
    pos = 0

    while pos < len(tokens):
        tok_width = font.size(tokens[pos])[0]

        if tok_width > maxwidth:
            # cut a token up into characters if it's hopelessly wide
            # to fit inside `maxwidth`
            # then we have to recalculate tok_width
            tokens[pos:pos + 1] = iter(tokens[pos])
            tok_width = font.size(tokens[pos])[0]

        if tok_width > space_left:
            lines.append(current_line)
            current_line = ""
            space_left = maxwidth

            # consume trailing spaces
            while tokens[pos].isspace():
                pos += 1
            continue
        else:
            space_left -= tok_width
            current_line += tokens[pos]
            pos += 1

    # add the current line
    if current_line and not current_line.isspace():
        lines.append(current_line)

    return lines


def resize_to_fit(dims: tuple[float, float], bounding_box: tuple[float, float]) -> tuple[float, float]:
    """Calculates the largest dimensions that are in proportion
    with `dims` that fits cleanly into the `bounding_box`."""

    x1, y1 = dims
    x2, y2 = bounding_box

    x_ratio = x2 / x1
    y_ratio = y2 / y1

    scale_factor = min(x_ratio, y_ratio)
    return x1 * scale_factor, y1 * scale_factor


@lru_cache(maxsize=1024)
def get_text_surf(font: pg.font.Font, text: str, colour: Colour):
    """Just a wrapper around pg.font.Font().render() with caching.
    Perhaps this will be helpful and improve performance slightly."""
    return font.render(text, True, colour)
