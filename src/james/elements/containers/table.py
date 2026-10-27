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


from typing import Any

import pygame as pg

from james._internals.constants import HITBOX_COLOUR_0, HITBOX_COLOUR_1, HITBOX_COLOUR_2, HITBOX_W
from james.elements.containers.alignment_boxes import HBox
from james.helpers.base_elem import Element
from james.helpers.custom_types import Colour, DrawFunc, SupportsGetItemColour
from james.elements.static_leaves.label import Label


class Table(Element):
    def __init__(
            self, *rows: HBox, flex: float = 0, shrink: float = 0.0,
            cell_inset: int = 0,
            row_flexes: list[float] | None = None,
            column_flexes: list[float] | None = None,
            cell_renderer: DrawFunc | None = None,
            hover_tooltip: Label | None = None
        ) -> None:
        super().__init__(flex=flex, shrink=shrink, hover_tooltip=hover_tooltip)

        self.cell_inset = cell_inset
        self._set_renderer(cell_renderer)

        self.row_flexes = row_flexes or []
        self.column_flexes = column_flexes or []

        for row in rows:
            self.add_child(row)

        self._validate()

    def draw_hitbox(self, surface: pg.Surface) -> None:
        pg.draw.rect(surface, HITBOX_COLOUR_0, self.rect, HITBOX_W)

        for row in self.children:
            pg.draw.rect(surface, HITBOX_COLOUR_1, row.rect, HITBOX_W)

            for cell in row.children:
                pg.draw.rect(surface, HITBOX_COLOUR_2, cell.rect, HITBOX_W)

    def _validate(self) -> None:
        length = len(self.children[0].children)
        if not all(len(row.children) == length for row in self.children):
            raise ValueError("All rows must have the same number of columns")

        num_rows, num_cols = len(self.children), len(self.children[0].children)

        num_row_flexes = len(self.row_flexes)
        if num_row_flexes < num_rows:
            self.row_flexes.extend([0.0] * (num_rows - num_row_flexes))
        elif num_row_flexes > num_rows:
            self.row_flexes = self.row_flexes[:num_rows]

        num_column_flexes = len(self.column_flexes)
        if num_column_flexes < num_cols:
            self.column_flexes.extend([0.0] * (num_cols - num_column_flexes))
        elif num_column_flexes > num_cols:
            self.column_flexes = self.column_flexes[:num_cols]

    def preferred_size(self) -> tuple[int, int]:
        # Measurement pass - find the maximum width and height of each column and row
        preferred_sizes: list[list[tuple[int, int]]] = []

        for row in self.children:
            row_sizes: list[tuple[int, int]] = []
            for cell in row.children:
                cell_w, cell_h = cell.preferred_size()
                row_sizes.append((cell_w + 2 * self.cell_inset, cell_h + 2 * self.cell_inset))
            preferred_sizes.append(row_sizes)

        # Row heights
        row_heights = [max(size[1] for size in row) for row in preferred_sizes]

        # Column widths
        column_widths = [
            max(preferred_sizes[row_idx][col_idx][0]
            for row_idx in range(len(self.children)))
            for col_idx in range(len(preferred_sizes[0]))
        ]

        return (sum(column_widths), sum(row_heights))

    def layout(self, rect: pg.Rect) -> None:
        self._validate()

        self.rect = rect
        self.layout_dirty = False

        # Measurement pass - find the maximum width and height of each column and row
        preferred_sizes = [
            [tuple(n + 2 * self.cell_inset for n in c.preferred_size()) for c in row.children]
            for row in self.children
        ]

        # Row heights
        row_heights = [max(size[1] for size in row) for row in preferred_sizes]

        # Column widths
        column_widths = [
            max(preferred_sizes[row_idx][col_idx][0]
            for row_idx in range(len(self.children)))
            for col_idx in range(len(preferred_sizes[0]))
        ]

        # Assign flex space
        leftover_w = rect.width - sum(column_widths)
        leftover_h = rect.height - sum(row_heights)

        column_flex_indices = [i for i in range(len(self.column_flexes)) if self.column_flexes[i]]
        row_flex_indices = [i for i in range(len(self.row_flexes)) if self.row_flexes[i]]

        total_row_flex = sum(self.row_flexes)
        total_column_flex = sum(self.column_flexes)

        for idx in row_flex_indices:
            row_heights[idx] += round(leftover_h * self.row_flexes[idx] / total_row_flex)
        for idx in column_flex_indices:
            column_widths[idx] += round(leftover_w * self.column_flexes[idx] / total_column_flex)

        # Assignment pass - assign space
        cell_left, cell_top = rect.topleft

        for rn, row in enumerate(self.children):
            row.rect = pg.Rect(cell_left, cell_top, sum(column_widths), row_heights[rn])

            for cn, cell in enumerate(row.children):
                cell.layout(pg.Rect(
                    cell_left + self.cell_inset, cell_top + self.cell_inset,
                    max(0, column_widths[cn] - 2 * self.cell_inset), max(0, row_heights[rn] - 2 * self.cell_inset)
                ))
                cell_left += column_widths[cn]

            cell_left = rect.left
            cell_top += row_heights[rn]

    def draw_default(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        if not self.visible:
            return

        for row in self.children:
            for elem in row.children:
                if elem.visible:
                    self.renderer(surface, elem, theme)
