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
"""Wrapper for a Canvas section API object."""
from typing import List

from .canvas_object import CanvasObject
from .api import CanvasAPI, STUDENTS
from .user import User

class Section (CanvasObject):
    """Canvas section.

    See https://canvas.instructure.com/doc/api/sections.html
    """

    @staticmethod
    def load(course_id : int, section_id : int):
        """
        Load a Canvas section object.

        :param int course_id: The course id
        :param int section_id: The section id
        """
        return Section(CanvasAPI().section(course_id, section_id))

    def students(self) -> List[User]:
        """A list with the students in this section."""
        if not self._students:
            self._students = [User(u) for u in self._data[STUDENTS]]

        return self._students
