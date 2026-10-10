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


from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Protocol

from pygame import Surface

if TYPE_CHECKING:
    from james._internals.base_elem import Element


# TODO: add support for `type AColour = tuple[int, int, int, int]`


type Colour = tuple[int, int, int]
type DrawFunc = Callable[[Surface, Element, SupportsGetItemColour], None]
type IntCoord2 = tuple[int, int]  # e.g. (width, height)

# something that can be indexed like obj[str] to return a Colour
class SupportsGetItemColour(Protocol):
    def __getitem__(self, key: Any) -> Colour: ...
