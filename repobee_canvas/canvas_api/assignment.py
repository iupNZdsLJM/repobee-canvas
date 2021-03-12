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
"""Wrapper for a Canvas assignment API object."""
from datetime import datetime
from .api import CanvasAPI, OVERRIDES
from .canvas_object import CanvasObject
from .course import Course
from .submission import Submission
from .assignment_override import AssignmentOverride

class Assignment (CanvasObject):
    """Canvas assignment.

    See https://canvas.instructure.com/doc/api/assignments.html
    """

    @staticmethod
    def load(course_id : int, assignment_id : int):
        """
        Load a Canvas assignment object.

        :param int course_id: The course id the assignment is part of
        :param int assignment_id: The id of the assignment to load
        """
        return Assignment(CanvasAPI().assignment(course_id, assignment_id))


    def overrides(self):
        """Get overrides for this assignment"""
        if self.has_overrides and not self._overrides:
            if OVERRIDES not in self._data:
                overrides_data = CanvasAPI().overrides(self.course_id, self.id)
                self._data[OVERRIDES] = overrides_data

            self._overrides = [AssignmentOverride(o) for o in self._data[OVERRIDES]]

        return self._overrides


    def course(self):
        """The course this assignment is part of."""
        if not self._course:
            self._course = Course.load(self.course_id)

        return self._course


    def is_group_assignment(self):
        """Is this assignment a group assignment?"""
        return self.group_category_id is not None


    def get_submission(self, students):
        """Get all submissions by given students for this assignment.

        Parameters:
        - students: A list of student IDs to get submissions for.
        """
        submissions = self.submissions(students = students)
        for submission in submissions:
            students_set = set(students)
            submission_students_set = {s.login_id for s in submission.students()}

            if students_set == submission_students_set:
                return submission

        raise ValueError(f"""No submission found for '{', '.join(students)}'.""")


    def submissions(self,
            skip_test_student = True,
            sections = [],  # list of section names to look for submission,
                            # empty list means all sections
            due_dates = [], # list of due dates to look for submissions.
                            # empty list means all due dates
            students = [],  # Only get info about these students. If not
                            # found, warning or error?
            filters = [],   # List of filters, each filter has type Submission -> Boolean
            reset = False,  # Reload data from the server
            ):
        """A list of submissions associated with this assignment."""
        if not self._submissions or reset:

            if len(sections) > 0:
                # Only get the submissions in the listed sections
                submissions_data = []
                for section_id in [section.id for section in self.course().sections(sections)]:
                    submissions_data += CanvasAPI().submissions_per_section(section_id, self.id)
            else:
                # Otherwise get all the submissions
                submissions_data = CanvasAPI().submissions_per_course(self.course_id, self.id)

            # Convert submission data from JSON to Submission objects
            submissions = [Submission(s) for s in submissions_data]

            # Filter out the test student
            if skip_test_student:
                submissions = [s for s in submissions if not s.submitter().is_test_student()]

            self._submissions = submissions


        # Filtering
        all_filters = []

        if skip_test_student:
            all_filters.append(lambda s: not s.submitter().is_test_student())

        if students is not None and len(students) > 0:
            all_filters.append(lambda s: s.submitter().login_id in students)

        if filters is not None and len(filters) > 0:
            all_filters.extend(filters)

        if len(due_dates) > 0:
            # Filter out based on due dates (should match exactly?)
            to_date = lambda d: datetime.strptime(d, "%Y-%m-%dT%H:%M:%S%z").date()
            overrides = [o for o in self.overrides() if to_date(o.due_at) in due_dates]
            override_students = []
            for override in overrides:
                override_students += override.students()

            print(due_dates, [to_date(o.due_at) for o in self.overrides()])


            submissions = [s for s in submissions if any([u in override_students for u in s.students()])]


        include = lambda s : all([f(s) for f in all_filters])


        # Only intersted in one submission per group. Note. For a group
        # assignment, before any student or teacher has submitted
        # anything, no group submissions show up.
        groups = set()
        submissions = []

        for submission in self._submissions:
            if submission.is_group_submission():
                if not submission.group().id in groups and include(submission):
                    groups.add(submission.group().id)
                    submissions.append(submission)
            else:
                if include(submission):
                    submissions.append(submission)


        return submissions
