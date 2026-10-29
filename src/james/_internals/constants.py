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


import pygame as pg

__version__ = (0, 3, 0)


# Well, you found something here!
__pronouns__: list[str] = ["he", "him"]


# dummy values
DUMMY_BLACK = (0, 0, 0)
DUMMY_SURFACE = pg.Surface((1, 1), flags=pg.SRCALPHA)


# default constants
HOVER_TOOLTIP_MARGIN = 10

HITBOX_COLOUR_0 = (255, 0, 255)
HITBOX_COLOUR_1 = (0, 255, 255)
HITBOX_COLOUR_2 = (255, 255, 0)
HITBOX_W = 1
