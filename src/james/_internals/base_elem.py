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


from __future__ import annotations

from typing import Any
from abc import ABC, abstractmethod

import pygame as pg


from .custom_types import Colour, SupportsGetItemColour


class Element(ABC):
    def __init__(
            self, *, flex: float = 0.0,
            draw_attrs: dict[str, Any] | None = None,
            colours: dict[str, Colour] | None = None,
        ) -> None:
        self.flex = flex
        self.rect = pg.Rect(0, 0, 0, 0)
        self.children: list[Element] = []
        self.visible: bool = True
        self.active: bool = False

        # These dicts are to allow implementation of custom draw functions
        # and attaching custom attributes for drawing and colouring
        # I would recommend attaching these to your objects using a
        # StrEnum for the different attrs you want to have.
        # Only needed if there is an attribute that you need that isn't already
        # supplied.

        # Like:
        # (
        #     # ... the rest of your instantiated element's constructor...
        #     draw_attrs={DrawAttr.BORDER_W: 3},
        #     colours={ColourAttr.BORDER: ThemeKey.BORDER}
        # )

        # Other attributes that may be present in inherited classes
        # are of the form `self.k_*` - these are colour keys,
        # intended for use with a theme-type object.

        self.draw_attrs = draw_attrs or {}
        self.colours = colours or {}

    @abstractmethod
    def preferred_size(self) -> tuple[int, int]:
        """How big should this UI element be, given no constraints?"""
        raise NotImplementedError

    @abstractmethod
    def layout(self, rect: pg.Rect) -> None:
        """Assign the rect to `self` and divide space between
        any potential children of `self`."""
        raise NotImplementedError

    @abstractmethod
    def draw_default(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        """Default draw behaviour. You can use this or make your
        own draw function if you need specialised behaviour."""
        raise NotImplementedError
