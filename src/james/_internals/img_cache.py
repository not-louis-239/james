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


from pathlib import Path

import pygame as pg

from james._internals.custom_types import Colour, IntCoord2
from james.utils import make_tinted_scaled_surface, resize_to_fit

type _TintSizeCtx = tuple[Path, Colour, IntCoord2]    # file path, tint, scale
type _TintSizeCache = dict[_TintSizeCtx, pg.Surface]  # {(colour, size): tinted_surface}


class _ImageCache:
    """Class for storing a base image, plus tinted and scaled versions.
    Derivatives of the original image are cached to avoid wasteful recalculations."""

    def __init__(self):
        self.base_cache: dict[Path, pg.Surface] = {}  # the untinted, unscaled original image - not to be modified after it is set
        self.tint_scale_cache: _TintSizeCache = {}

    def get_base_cache(self, fp: Path) -> pg.Surface:
        if fp not in self.base_cache:
            self.base_cache[fp] = pg.image.load(fp).convert_alpha()
        return self.base_cache[fp]

    def get_tinted_scaled_img(self, fp: Path, colour: Colour, size: IntCoord2, constrain_proportions: bool = False) -> pg.Surface:
        """Get an image from the path `fp`, tinted and scaled to a specific
        `colour` and `size`. With `constrain_proportions`, scales the image to fit inside
        a `size`-sized bounding box instead."""

        # Get the base cache first
        if fp not in self.base_cache:
            self.base_cache[fp] = pg.image.load(fp).convert_alpha()

        if constrain_proportions:
            x, y = resize_to_fit(self.base_cache[fp].get_size(), size)
            size = int(x), int(y)

        key: _TintSizeCtx = (fp, colour, size)

        if key not in self.tint_scale_cache:
            self.tint_scale_cache[key] = make_tinted_scaled_surface(
                surface=self.base_cache[fp], colour=colour,
                size=size if size != self.base_cache[fp].get_size() else None  # skip resizing if the requested size is the same as the original size
            )

        return self.tint_scale_cache[key]


img_cache = _ImageCache()
