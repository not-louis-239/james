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


from typing import Any, Literal

from pygame import Rect, Surface

from james.helpers.base_elem import Element
from james.helpers.custom_types import Colour, SupportsGetItemColour
from james.elements.static_leaves.label import Label


class Collapsible(Element):
    def __init__(
            self, *,
            flex: float = 0, shrink: float = 0,
            trigger: Element, content: Element,
            gap: int = 0,  # gap between trigger and content when expanded
            expand_direction: Literal["up", "down", "left", "right"] = "down",
            hover_tooltip: Label | None = None,
        ) -> None:
        super().__init__(flex=flex, shrink=shrink, hover_tooltip=hover_tooltip)

        self.trigger = trigger
        self.content = content
        self.gap = gap
        self.expand_direction = expand_direction

        self.add_child(trigger)
        self.add_child(content)

        self.expanded = False

    def preferred_size(self) -> tuple[int, int]:
        trigger_w, trigger_h = self.trigger.preferred_size()
        content_w, content_h = self.content.preferred_size()

        if not self.expanded:
            return trigger_w, trigger_h

        if self.expand_direction in ["up", "down"]:
            return (
                max(trigger_w, content_w),
                trigger_h + self.gap + content_h
            )

        return (
            trigger_w + self.gap + content_w,
            max(trigger_h, content_h),
        )

    def layout(self, rect: Rect) -> None:
        self.assign_rect(rect)

        trigger_w, trigger_h = self.trigger.preferred_size()

        # Not expanded
        if not self.expanded:
            self.trigger.layout(rect)
            return

        # Expand vertically
        if self.expand_direction in ("up", "down"):
            available_h = rect.height - trigger_h - self.gap

            if self.expand_direction == "down":
                trigger_rect = Rect(
                    rect.x,
                    rect.y,
                    rect.width,
                    trigger_h,
                )
                content_rect = Rect(
                    rect.x,
                    rect.y + trigger_h + self.gap,
                    rect.width,
                    available_h,
                )

            else:  # up
                content_rect = Rect(
                    rect.x,
                    rect.y,
                    rect.width,
                    available_h,
                )
                trigger_rect = Rect(
                    rect.x,
                    rect.bottom - trigger_h,
                    rect.width,
                    trigger_h,
                )

        # Expand horizontally
        else:
            available_w = rect.width - trigger_w - self.gap

            if self.expand_direction == "right":
                trigger_rect = Rect(
                    rect.x,
                    rect.y,
                    trigger_w,
                    rect.height,
                )
                content_rect = Rect(
                    rect.x + trigger_w + self.gap,
                    rect.y,
                    available_w,
                    rect.height,
                )

            else:  # left
                content_rect = Rect(
                    rect.left,
                    rect.y,
                    available_w,
                    rect.height,
                )
                trigger_rect = Rect(
                    rect.right - trigger_w,
                    rect.y,
                    trigger_w,
                    rect.height,
                )

        self.trigger.layout(trigger_rect)
        self.content.layout(content_rect)

    def toggle(self) -> None:
        self.expanded = not self.expanded
        self.invalidate_layout()

    def draw_default(self, surface: Surface, theme: SupportsGetItemColour) -> None:
        if not self.visible:
            return

        if self.expanded:
            self.trigger.draw_default(surface, theme)
            self.content.draw_default(surface, theme)
        else:
            self.trigger.draw_default(surface, theme)
