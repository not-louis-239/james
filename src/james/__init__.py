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


from james.elements.collapsibles import collapsible
from james.elements.containers import alignment_boxes, panel, scrollable_display, table
from james.elements.interactive_leaves import button, input_box
from james.elements.static_leaves import label, spacer, divider
from james.gui import gui_cls
from james.helpers import base_elem, custom_types, renderer, utils


# Renderer / GUI
set_default_renderer = renderer.set_default_renderer
GUI = gui_cls.GUI

# Utilities
Element = base_elem.Element
Colour = custom_types.Colour
SupportsGetItemColour = custom_types.SupportsGetItemColour
HAlign = alignment_boxes.HAlign
VAlign = alignment_boxes.VAlign
AmbientMessage = utils.AmbientMessage

# Containers
HBox = alignment_boxes.HBox
VBox = alignment_boxes.VBox
SBox = alignment_boxes.SBox
Collapsible = collapsible.Collapsible
Table = table.Table
Panel = panel.Panel
ScrollableDisplay = scrollable_display.ScrollableDisplay

# Interactive elements
RectButton = button.RectButton
CircleButton = button.CircleButton
InputBox = input_box.InputBox

# Static elements
Spacer = spacer.Spacer
Label = label.Label
Divider = divider.Divider
