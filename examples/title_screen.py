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


# Let's make a full title screen using Pygame, James elements
# and a custom renderer.


from enum import Enum, auto

import pygame as pg
from james import GUI, Panel, VBox, HBox, RectButton, Label, Spacer


WN_W, WN_H = 800, 600
PADDING = 30
FPS = 60


class ThemeKey(Enum):
    BG = auto()
    BG_HOVERED = auto()
    BG_PRESSED = auto()

    BG_BUTTON = auto()
    BG_BUTTON_HOVERED = auto()
    BG_BUTTON_PRESSED = auto()

    FG = auto()

    BORDER = auto()
    BORDER_HOVERED = auto()
    BORDER_PRESSED = auto()


THEME: dict[ThemeKey, tuple[int, int, int]] = {
    ThemeKey.BG: (40, 40, 40),
    ThemeKey.BG_HOVERED: (55, 55, 55),
    ThemeKey.BG_PRESSED: (70, 70, 70),
    ThemeKey.BG_BUTTON: (230, 67, 67),
    ThemeKey.BG_BUTTON_HOVERED: (240, 81, 81),
    ThemeKey.BG_BUTTON_PRESSED: (252, 101, 101),
    ThemeKey.FG: (255, 255, 255),
}


def main():
    pg.init()

    screen = pg.display.set_mode((WN_W, WN_H))
    clock = pg.time.Clock()

    title_font = pg.font.SysFont("Helvetica", 50)
    button_font = pg.font.SysFont("Helvetica", 30)

    gui = GUI(
        Panel(
            VBox(
                Spacer(),
                HBox(
                    Spacer(),
                    Label(
                        text="Foo Bar",
                        inset=PADDING,
                        font=title_font,
                        k_fg=ThemeKey.FG
                    ),
                    Spacer(),
                ),
                Spacer(),
                HBox(
                    RectButton(
                        text="Begin",
                        font=button_font,
                        inset=PADDING,
                        k_bg_colour=ThemeKey.BG_BUTTON,
                        k_bg_hovered=ThemeKey.BG_BUTTON_HOVERED,
                        k_bg_pressed=ThemeKey.BG_BUTTON_PRESSED,
                        k_fg_colour=ThemeKey.FG,
                        flex=1,
                    ),
                    RectButton(
                        text="Quit",
                        font=button_font,
                        inset=PADDING,
                        k_bg_colour=ThemeKey.BG_BUTTON,
                        k_bg_hovered=ThemeKey.BG_BUTTON_HOVERED,
                        k_bg_pressed=ThemeKey.BG_BUTTON_PRESSED,
                        k_fg_colour=ThemeKey.FG,
                        flex=1,
                    ),
                    gap=PADDING,
                ),
                Spacer(),
                gap=PADDING,
            ),
            horiz_padding=PADDING,
            vert_padding=PADDING,
        )
    )

    gui.layout([pg.Rect(0, 0, WN_W, WN_H)])

    running = True

    while running:
        dt_s = clock.tick(FPS)
        events = pg.event.get()

        for ev in events:
            if ev.type == pg.QUIT:
                running = False

        gui.update(dt_s)
        screen.fill(THEME[ThemeKey.BG])
        gui.draw(screen, THEME)
        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()
