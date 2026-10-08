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


from abc import abstractmethod
from pathlib import Path
from typing import Any

import pygame as pg

from widgets_and_stuff._custom_types import Colour

from ._base_elem import Element


class _Button(Element):
    def __init__(
            self, *, flex: float = 0,
            draw_attrs: dict[str, Any] | None = None,
            colours: dict[str, tuple[int, int, int]] | None = None,
            text: str = "", font: pg.font.Font, inset: int = 0,
            fixed_size: tuple[int, int] | None = None, img_path: Path | None = None,
        ) -> None:
        super().__init__(flex=flex, draw_attrs=draw_attrs, colours=colours)
        self.text = text
        self.font = font
        self.inset = inset
        self.fixed_size = fixed_size
        self.img_path = img_path

    def _get_text_inset_size(self) -> tuple[int, int]:
        """Get text size, including inset."""
        text_size = self.font.size(self.text)
        return text_size[0] + self.inset * 2, text_size[1] + self.inset * 2

    @abstractmethod
    def check_click(self, mouse_pos: tuple[int, int]) -> bool:
        raise NotImplementedError


class RectButton(_Button):
    def check_click(self, mouse_pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(mouse_pos)

    def preferred_size(self) -> tuple[int, int]:
        return self.fixed_size or self._get_text_inset_size()

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect


class CircleButton(_Button):
    def __init__(
            self, *, r: int, flex: float = 0,
            draw_attrs: dict[str, Any] | None = None,
            colours: dict[str, tuple[int, int, int]] | None = None,
            text: str = "", font: pg.font.Font, inset: int = 0,
            fixed_size: tuple[int, int] | None = None, img_path: Path | None = None
        ) -> None:
        super().__init__(flex=flex, draw_attrs=draw_attrs, colours=colours, text=text, font=font, inset=inset, fixed_size=fixed_size, img_path=img_path)
        self.r = r

    def check_click(self, mouse_pos: tuple[int, int]) -> bool:
        dx = mouse_pos[0] - self.rect.centerx
        dy = mouse_pos[1] - self.rect.centery
        return dx ** 2 + dy ** 2 <= self.r ** 2

    def preferred_size(self) -> tuple[int, int]:
        return (2 * self.r, 2 * self.r)

    def layout(self, rect: pg.Rect) -> None:
        self.rect = rect
