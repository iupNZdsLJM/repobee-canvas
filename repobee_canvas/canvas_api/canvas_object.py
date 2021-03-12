# Copyright 2021 Huub de Beer <h.t.d.beer@tue.nl>
#
# Licensed under the EUPL, Version 1.2 or later. You may not use this work
# except in compliance with the EUPL. You may obtain a copy of the EUPL at:
#
# https://joinup.ec.europa.eu/software/page/eupl
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the EUPL is distributed on an "AS IS" basis, WITHOUT
# WARRANTY OR CONDITIONS OF ANY KIND, either express or implied. See the EUPL
# for the specific language governing permissions and limitations under the
# licence.
"""Base object for all Canvas API objects."""

class CanvasObject:
    """Base class for Canvas API objects"""

    def __init__(self, data = {}):
        """Create a new CanvasObject"""
        self._data = data


    def __getattr__(self, name):
        """Return value of named attribubte if it exists, None otherwise."""
        if self.has_field(name):
            return self._data[name]

        return None


    def has_field(self, name):
        """Return True if this Canvas object has a field named 'name'. Return
        False otherwise."""
        return name in self._data


    def unique(self, elts, prop):
        """Return a list of unique elements from the properties."""
        unique_elts = []
        unique_props = set()

        for elt in elts:
            prop_elt = prop(elt)
            if prop_elt in unique_props:
                pass
            else:
                unique_props.add(prop_elt)
                unique_elts.append(elt)

        return unique_elts
