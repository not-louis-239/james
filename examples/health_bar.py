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


# Create a health bar by inheriting a James element and using Pygame.
# It should look something like:
# [         80 / 100         ]
# [  Take Damage  ] [  Heal  ]


import pygame as pg

from james import GUI, Element, HBox, Label, Panel, RectButton, VBox
from james.helpers.custom_types import Colour, SupportsGetItemColour
from james.helpers.utils import get_text_surf

# This example just uses strings for the theme keys,
# but you could also totally use an Enum, StrEnum, int, whatever.
THEME: dict[str, Colour] = {
    "bg": (100, 100, 100),
    "bg_hovered": (125, 125, 125),
    "bg_pressed": (150, 150, 150),
    "border": (179, 179, 179),
    "fg_high": (56, 181, 108),
    "fg_low": (255, 48, 48),
    "fg": (255, 255, 255),
}


class HealthBar[K](Element[K]):
    def __init__(
            self, *, flex: float = 0, shrink: float = 0,
            interactive: bool = False, hover_tooltip: Label | None = None,
            current_health: int = 0, max_health: int = 100,
            k_bg: K, k_fg_high: K, k_fg_low: K, k_fg_text: K,
            k_border: K, border_w: int = 2, font: pg.font.Font, inset: int = 0,
        ) -> None:
        super().__init__(flex=flex, shrink=shrink, interactive=interactive, hover_tooltip=hover_tooltip)

        self.current_health = max(0, min(max_health, current_health))
        self.max_health = max_health

        self.k_bg = k_bg
        self.k_fg_high = k_fg_high
        self.k_fg_low = k_fg_low
        self.k_fg_text = k_fg_text
        self.k_border = k_border
        self.border_w = border_w

        self.font = font
        self.inset = inset

    def set_health(self, new_health: int) -> None:
        self.current_health = max(0, min(new_health, self.max_health))

    def intrinsic_text(self) -> str:
        return f"{self.current_health} / {self.max_health}"

    def preferred_size(self) -> tuple[int, int]:
        text_w, text_h = self.font.size(self.intrinsic_text())
        return text_w + 2 * self.inset, text_h + 2 * self.inset

    def layout(self, rect: pg.Rect) -> None:
        self.assign_rect(rect)

    def draw_default(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        # Draw background
        pg.draw.rect(surface, theme[self.k_bg], self.rect)

        # Draw health bar
        health_ratio = self.current_health / self.max_health

        if health_ratio > 0.2:
            k_fg_bar = self.k_fg_high
        else:
            k_fg_bar = self.k_fg_low

        pg.draw.rect(
            surface, theme[k_fg_bar],
            (self.rect.x, self.rect.y, self.rect.w * health_ratio, self.rect.height)
        )

        # Draw text
        text_surf = get_text_surf(self.font, self.intrinsic_text(), theme[self.k_fg_text])
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

        # Draw border
        pg.draw.rect(surface, theme[self.k_border], self.rect, width=self.border_w)


def main():
    pg.init()
    WN_W, WN_H = 800, 250

    screen = pg.display.set_mode((WN_W, WN_H))
    pg.display.set_caption("James Health Bar Example")

    font = pg.font.SysFont("Arial", 32)
    panel = Panel(
        VBox(
            bar := HealthBar(
                flex=1,
                k_bg="bg",
                k_fg_high="fg_high",
                k_fg_low="fg_low",
                k_border="border",
                k_fg_text="fg",
                border_w=2,
                current_health=80,
                max_health=100,
                font=font,
                inset=15
            ),
            HBox(
                damage_button := RectButton(
                    flex=1,
                    text="Take Damage",
                    k_bg_colour="bg",
                    k_bg_hovered="bg_hovered",
                    k_bg_pressed="bg_pressed",
                    k_fg_colour="fg",
                    font=font,
                    inset=15,
                ),
                heal_button := RectButton(
                    flex=1,
                    text="Heal",
                    k_bg_colour="bg",
                    k_bg_hovered="bg_hovered",
                    k_bg_pressed="bg_pressed",
                    k_fg_colour="fg",
                    font=font,
                    inset=15,
                ),
                gap=30,
            ),
            gap=30,
        ),
        horiz_padding=30,
        vert_padding=30,
    )

    gui = GUI(panel)
    gui.layout([pg.Rect(0, 0, WN_W, WN_H)])

    fps = 60
    clock = pg.time.Clock()

    running = True
    while running:
        events = pg.event.get()

        dt_s = clock.tick(fps) / 1000.0
        elem = gui.hit_test(pg.mouse.get_pos())

        for ev in events:
            if ev.type == pg.QUIT:
                running = False

            if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                if elem is damage_button:
                    bar.set_health(bar.current_health - 5)
                if elem is heal_button:
                    bar.set_health(bar.current_health + 5)

        gui.update(dt_s)
        screen.fill((0, 0, 0))
        gui.draw(screen, THEME)
        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()
