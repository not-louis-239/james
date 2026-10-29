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


# Create a ScrollableDisplay using James elements, Pygame and a ThemeKey enum.


from enum import Enum, auto

import pygame as pg

from james import GUI, Label, Panel, ScrollableDisplay, VBox


class ThemeKey(Enum):
    BG = auto()
    FG = auto()
    BORDER = auto()


THEME = {
    ThemeKey.BG: (255, 255, 255),
    ThemeKey.FG: (0, 0, 0),
    ThemeKey.BORDER: (100, 100, 100),
}


def main():
    pg.init()

    WN_W, WN_H = 300, 600

    screen = pg.display.set_mode((WN_W, WN_H))
    pg.display.set_caption("James Scrollable Display Demo")

    clock = pg.time.Clock()
    fps = 60

    # Some text to display
    messages = [
        "Hello, world!",
        "This is a scrollable display.",
        "James elements are easily inheritable.",
        "Python is fun to use!",
        "Here is another message.",
        "And another one.",
        "The quick brown fox",
        "jumps over the lazy dog",
        "and runs away",
        "while the clock ticks towards midnight",
        "and the sun sets.",
    ]

    gui = GUI(
        Panel(
            scrollable := ScrollableDisplay(
                VBox(
                    *[
                        Label(
                            text=message,
                            font=pg.font.SysFont("Helvetica", 20),
                            inset=15,
                            border_w=2,
                            k_border=ThemeKey.BORDER,
                            k_fg=ThemeKey.FG,
                        )
                        for message in messages
                    ],
                    gap=15,
                ),
                k_border=ThemeKey.BORDER,
                border_w=2,
            ),
            horiz_padding=30,
            vert_padding=30,
        )
    )

    gui.layout([pg.Rect(0, 0, WN_W, WN_H)])

    running = True
    while running:
        dt_s = clock.tick(fps) / 1_000.0
        events = pg.event.get()
        elem = gui.hit_test(pg.mouse.get_pos())

        if elem is not None:
            # And here's how to calculate local coordinates!
            print(f"Hit a '{type(elem).__name__}'!")
            print(f"Parents: {' > '.join(f"'{type(e).__name__}'" for e in [*elem.parents[::-1], elem])}")
            print(f"Screen Pos: {pg.mouse.get_pos()}")

            local_pos = pg.mouse.get_pos()
            for e in [*elem.parents[::-1], elem]:
                local_pos = e.to_local(local_pos)

            print(f"Local Pos: {local_pos}")

        for event in events:
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.MOUSEWHEEL:
                if (
                    elem is not None
                    and elem.parents is not None
                    and (
                        elem is scrollable
                        or scrollable in elem.parents
                    )
                ):
                    scrollable.handle_scroll(event)

        screen.fill(THEME[ThemeKey.BG])
        gui.update(dt_s)
        gui.draw(screen, THEME)
        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()
