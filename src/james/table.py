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

from james._internals.base_elem import Element
from james._internals.custom_types import DrawFunc, SupportsGetItemColour
from james.alignment_boxes import HBox


class Table(Element):
    def __init__(
            self, *rows: HBox, flex: float = 0,
            cell_inset: int = 0,
            row_flexes: list[float] | None = None,
            column_flexes: list[float] | None = None,
            cell_renderer: DrawFunc,
            draw_attrs: dict[str, Any] | None = None,
            colours: dict[str, tuple[int, int, int]] | None = None
        ) -> None:
        super().__init__(flex=flex, draw_attrs=draw_attrs, colours=colours)

        self.cell_inset = cell_inset
        self.cell_renderer = cell_renderer

        self.row_flexes = row_flexes or []
        self.column_flexes = column_flexes or []

        self.children: list[HBox] = list(rows)  # type: ignore
        for child in rows:
            child.parent = self

        self._validate()

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
        preferred_sizes = [
            [c.preferred_size() for c in row.children]
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

        return (sum(column_widths), sum(row_heights))

    def layout(self, rect: pg.Rect) -> None:
        self._validate()

        self.rect = rect

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
            for cn, cell in enumerate(row.children):
                cell.layout(pg.Rect(
                    cell_left + self.cell_inset, cell_top + self.cell_inset,
                    max(0, column_widths[cn] - 2 * self.cell_inset), max(0, row_heights[rn] - 2 * self.cell_inset)
                ))
                cell_left += column_widths[cn]
            row.rect = pg.Rect(cell_left, cell_top, sum(column_widths), row_heights[rn])
            cell_left = rect.left
            cell_top += row_heights[rn]

    def draw_default(self, surface: pg.Surface, theme: SupportsGetItemColour) -> None:
        for row in self.children:
            for elem in row.children:
                self.cell_renderer(surface, elem, theme)
