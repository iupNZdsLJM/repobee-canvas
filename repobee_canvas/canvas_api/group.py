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
"""Wrapper for a Canvas group API object."""
from typing import List

from .canvas_object import CanvasObject
from .api import CanvasAPI
from .user import User

class Group (CanvasObject):
    """Canvas group.

    See https://canvas.instructure.com/doc/api/groups.html
    """

    @staticmethod
    def load(group_id : int):
        """
        Load a Canvas group object.

        Args:
        - group_id: The group id
        """
        return Group(CanvasAPI().group(group_id))

    def members(self) -> List[User]:
        """Group members."""
        if not self._members:
            memberships = CanvasAPI().group_memberships(self.id)
            self._members = [User.load(m["user_id"]) for m in memberships]

        return self._members
