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


class ScrollPhysics:
    # Class-level constants so that if anyone needs to adjust them
    # somewhere for a project globally, they can do so via monkey-patching
    # the class itself.

    SCROLL_STRENGTH_COEFF = 50  # controls strength of scrolling input
    SCROLL_FRICTION = 0.935  # proportion of v dissipated per frame
    EPS = 1e-6

    def __init__(self, disp_topleft: tuple[int, int], disp_botright: tuple[int, int]) -> None:
        self.disp = pg.Vector2(0, 0)
        self.disp_topleft = pg.Vector2(disp_topleft)
        self.disp_botright = pg.Vector2(disp_botright)
        self.vel = pg.Vector2(0, 0)

    def handle_scroll(self, event: pg.event.Event) -> None:
        if event.type == pg.MOUSEWHEEL:
            self.vel -= pg.Vector2(event.x, event.y) * self.SCROLL_STRENGTH_COEFF

    def update(self, dt_s: float) -> None:
        self.disp += self.vel * dt_s
        self.vel *= (1 - self.SCROLL_FRICTION) ** dt_s  # apply friction

        # Clamp displacement to bounds
        if self.disp.x < self.disp_topleft.x:
            self.disp.x = self.disp_topleft.x
            self.vel.x = 0
        elif self.disp.x > self.disp_botright.x:
            self.disp.x = self.disp_botright.x
            self.vel.x = 0

        if self.disp.y < self.disp_topleft.y:
            self.disp.y = self.disp_topleft.y
            self.vel.y = 0
        elif self.disp.y > self.disp_botright.y:
            self.disp.y = self.disp_botright.y
            self.vel.y = 0

        # Cancel low velocity
        if self.vel.length_squared() < self.EPS:
            self.vel.update(0, 0)
