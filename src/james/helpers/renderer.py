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


from james.helpers.custom_types import DrawFunc

DEFAULT_RENDERER: DrawFunc | None = None


def set_default_renderer(renderer: DrawFunc) -> None:
    """Set the renderer function that will be used
    in the constructors of `Element`s that render children
    when no `renderer=` parameter is provided in their constructors."""

    global DEFAULT_RENDERER
    DEFAULT_RENDERER = renderer
