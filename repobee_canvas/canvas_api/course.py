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
"""Wrapper for a Canvas course API object."""
from typing             import List

from .api               import CanvasAPI, ID, SECTIONS, ASSIGNMENTS
from .canvas_object     import CanvasObject
from .section           import Section
from .user              import User

class Course (CanvasObject):
    """Canvas course.

    See https://canvas.instructure.com/doc/api/courses.html
    """

    @staticmethod
    def load(course_id : int):
        """
        Load a Canvas course object.

        :param int course_id: The course id
        """
        return Course(CanvasAPI().course(course_id))

    def assignments(self):
        """The assignments of this course.
        """
        if not self._assignments:
            from .assignment import Assignment
            self._assignments = [
                                    Assignment.load(self.id, a[ID]) for a in
                                    CanvasAPI().assignments_per_course(self.id)
                                ]
        
        return self._assignments

    def sections(self, names : List[str] = []) -> List[Section]:
        """The sections of this course.

        Args:
        - names: List of section names. If names is not empty, only those
          sections with a name in the list are returned.

        Returns:
        A list of Canvas section objects for this course.
        """
        if not self._sections:
            sections = [Section.load(self.id, s[ID]) for s in self._data[SECTIONS]]
            self._sections = self.unique(sections, lambda s: s.id)

        if len(names) > 0:
            return [s for s in self._sections if s.name in names]

        return self._sections

    def students(self) -> List[User]:
        """The students in this course.

        Returns:
        A list of Canvas user objects representing all students in this
        course.
        """
        if not self._students:
            students = CanvasAPI().students_per_course(self.id)
            self._students = [User(s) for s in students]

        return self._students
