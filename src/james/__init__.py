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


"""
James - 'Just A Modular Element Structurer'

UI library for pygame, designed to be modular and easy to use.
"""


from . import (
    alignment_boxes,
    button,
    input_box,
    label,
    panel,
    scrollable_display,
    spacer,
    table,
)
from ._internals import base_elem, custom_types

SupportsGetItemColour = custom_types.SupportsGetItemColour

Element = base_elem.Element

HBox = alignment_boxes.HBox
VBox = alignment_boxes.VBox
SBox = alignment_boxes.SBox
Table = table.Table

RectButton = button.RectButton
CircleButton = button.CircleButton

Spacer = spacer.Spacer
ScrollableDisplay = scrollable_display.ScrollableDisplay
Panel = panel.Panel
Label = label.Label
InputBox = input_box.InputBox
