# James

*Just A Modular Element Structure*

**Version**: 0.3.0

*James* is a rectless construction GUI library for Pygame that contains various classes for common element types with default draw functions. In essence, James lets you describe what your UI contains without calculating where everything goes.

```py
gui = GUI(
    Panel(
        VBox(
            HealthBar(...),
            HBox(
                RectButton(...),
                RectButton(...),
            ),
        )
    )
)

gui.layout([window_rect])
```

## Why James?

James separates "what is this element?" from "where does it go?". You can construct elements without passing in any `pygame.Rect`s. Such as:

```py
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
```

The application only needs to supply one `pygame.Rect` for each layer of a GUI via `gui.layout(rects)`, where `rects` is an array of `pygame.Rect` objects: one for each layer of the GUI.

```py
    gui = GUI(panel)
    gui.layout([pg.Rect(0, 0, WN_W, WN_H)])
```

James calculates the rectangles of each descendant in the element hierarchy based on available space, intrinsic sizes (from element content), padding, flex, shrink (if there is a space shortage).

### Custom Elements

James elements are designed to be easily extensible via normal Python class inheritance, e.g.:

```py

import pygame
import james

class HealthBar[K](james.Element[K]):
    ...
```

This allows for easy customisation and control over adding new elements.
A custom element only needs to define:

```py
    def preferred_size(self) -> tuple[int, int]:
        """How big the UI element should be if there are no constraints."""

    def layout(self, rect: pygame.Rect) -> None:
        """Function to assign the rect to `self` and calculate space
        and rects for children."""
        
        # Call this method to bind the `rect` to `self` and
        # reset `self.layout_dirty` to False.
        self.assign_rect(rect)

        # Then your custom layout code for any children goes here.

    def draw_default(self, surface: pygame.Surface, theme: james.SupportsGetItemColour) -> None:
        """Add your custom drawing code for your custom element here.
        Use `self.k_*` attributes to retrieve colours from the `theme`.
        such as `theme[self.k_bg]`, so you can use them in your drawing code."""
```

### Rectless Construction

When an element is created, its size and final position are often not yet known, or tedious to calculate by hand for complicated layouts. It may depend on:
* parents
* siblings
* window space
* intrinsic content size
* flex, if there is excess space
* shrink, if there is not enough space
* padding and gaps
* mouse position if it's a hover element
* scrolling

Thus, James requires no descendant rectangles while constructing elements. Instead, element rect calculation is delegated to when `Element.layout` is called and available space is known.

## Dependencies

Intended for use with Pygame if used as part of a larger (Pygame) project. Hence:
- Pygame-ce (developed with v2.5.8)
- Python (developed with v3.14.0)
See `requirements.txt` for more details.

## Installation

To install `james` into your Python packages or current virtual environment, run `pip install git+https://github.com/not-louis-239/james` in your terminal.

Then to use James objects:

```py
import james
```

or

```py
from james import HBox, VBox, Panel, GUI, ...
```

## Examples

See [examples](./examples/) for some example scripts and classes that use or inherit from James components.

## Licence

Licensed under the Apache Licence v2.0.
