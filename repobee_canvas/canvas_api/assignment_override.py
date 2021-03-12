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
"""Wrapper for a Canvas assignment override API object."""
from typing import List

from .api import CanvasAPI
from .canvas_object import CanvasObject
from .user import User
from .group import Group
from .section import Section

class AssignmentOverride (CanvasObject):
    """Canvas assignment override.

    See https://canvas.instructure.com/doc/api/assignments.html
    """

    @staticmethod
    def load(course_id, assignment_id, override_id):
        """
        Load a Canvas assignment override object.

        :param int course_id: The course id
        :param int assignment_id: The assignment id
        :param int override_id: The override id
        """
        return AssignmentOverride(
                CanvasAPI().assignment_override(course_id, assignment_id, override_id)
                )

    def students(self) -> List[User]:
        """All students in this group, regardless if this override is for
        individual students, group, or section."""
        if not self._students:
            self._students = []
            if self.student_ids:
                self._students += [User.load(id) for id in self._student_ids]

            if self.group():
                self._students += self.group().members()

            if self.section():
                self._students += self.section().students()

        return self._students

    def group(self) -> Group:
        """This assignment override's group, if any."""
        if self.group_id is not None and not self._group:
            self._group = Group.load(self.group_id)

        return self._group

    def section(self) -> Section:
        """This assignment override's section"""
        if self.course_section_id is not None and not self._section:
            self._section = Section.load(self.course_id, self.course_section_id)

        return self._section
