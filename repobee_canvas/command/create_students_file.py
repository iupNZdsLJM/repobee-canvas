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
"""Create a students file from a Canvas assignment for use with RepoBee.

"""
from pathlib                    import Path
import repobee_plug as plug

from ..canvas_api.api           import CanvasAPI
from ..canvas_api.assignment    import Assignment
from ..canvas_git_map           import CanvasGitMap

from .canvas_category          import CANVAS_CATEGORY

from ..common_options           import CANVAS_ACCESS_TOKEN_OPTION
from ..common_options           import CANVAS_API_BASE_URL_OPTION
from ..common_options           import CANVAS_ASSIGNMENT_ID_OPTION
from ..common_options           import CANVAS_COURSE_ID_OPTION
from ..common_options           import CANVAS_GIT_MAP_OPTION
from ..common_options           import CANVAS_STUDENTS_FILE_OPTION

from ..tui                      import inform, warn

class CreateStudentsFile(plug.Plugin, plug.cli.Command):
    """RepoBee command to create a students file from a Canvas assignment.

    The CanvasStudentsFile class is a RepoBee plugin to create a students file
    for a Canvas assignment: All students assigned to this assignment are
    listed and written to the students file. If the assignment is a group
    assignment, the student groups are written instead.

    You have to use this plugin first to create the students file and then use
    the student file to create and manage student repositories. See the Canvas
    plugin below for more information.

    Because the login ids of students can be different in Canvas and git, a
    mapping needs to be made via a database containing both login ids for each
    student. This database should be a csv file and have a canvas_id and git_id
    column.


    Usage:

    Assunming the course id, Canvas API URL, and Canvas API key have been
    configured, the command

    ```
    repobee -p canvas canvas create-students-file \
            --canvas-assignment-id 23 \
            --canvas-git-map student_data.csv
    ```

    will create file `students.lst` with all Git account names of the
    students involved in assignment with ID=23.

    If you want to use a different output filename use option
    `--canvas-students-file output.lst`.

    """
    __settings__ = plug.cli.command_settings(
            action      = CANVAS_CATEGORY.create_students_file,
            help        = "create students file",
            description = (
                "Create the students file for a Canvas assignment for use "
                "with RepoBee."
                )
            )

    canvas_access_token      = CANVAS_ACCESS_TOKEN_OPTION
    canvas_base_url          = CANVAS_API_BASE_URL_OPTION
    canvas_course_id         = CANVAS_COURSE_ID_OPTION
    canvas_assignment_id     = CANVAS_ASSIGNMENT_ID_OPTION
    canvas_students_file     = CANVAS_STUDENTS_FILE_OPTION
    canvas_git_map           = CANVAS_GIT_MAP_OPTION

    canvas_include_groupless = plug.cli.flag(
        help = "Include students who are not assigned to a group for group assignments.",
        )

    def command(self):
        CanvasAPI().setup(self.canvas_base_url, self.canvas_access_token)
        assignment = Assignment.load(self.canvas_course_id, self.canvas_assignment_id)
        canvas_git_mapping_table = CanvasGitMap.load(Path(self.canvas_git_map))
        create_students_file(
                assignment,
                canvas_git_mapping_table,
                Path(self.canvas_students_file),
                self.canvas_include_groupless
                )
        inform(f"Students file written to '{self.canvas_students_file}'.")

def create_students_file(
        assignment                  : Assignment,
        canvas_git_mapping_table    : CanvasGitMap,
        students_file               : Path,
        include_groupless_students  : bool = False
    ):
    """Create a students file for a Canvas assignment."""
    include_groupless = not assignment.is_group_assignment() or include_groupless_students

    submissions = assignment.submissions()
    group_submissions = [s for s in submissions if s.is_group_submission()]

    # Students who are not assigned to a group in a group assignment are
    # ignored by default when creating a students file. Most likely these
    # students are not actively participating in the course or have not yet
    # assigned themselves to a group. However, with parameter
    # include_groupless_students, you can override this default behavior.
    if assignment.is_group_assignment():
        if len(group_submissions) == 0:
            raise ValueError(
                ("No group submissions found for this group assignment. "
                "Please run command 'repobee canvas prepare-assignment' to "
                "resolve this issue. Or configure this assignment as an "
                "individual assignment."))

        if len(group_submissions) < len(submissions):
            message = ((
                f"The number of group submissions ({len(group_submissions)}) "
                f"is smaller than the number of submissions "
                f"({len(submissions)}). This means that not all students "
                 "in this assignment are assigned to a group. "
                ))

            if include_groupless:
                message += ((
                    "These groupless students are included in "
                    "the created students list file."
                    ))
            else:
                message += ((
                    "These groupless students are NOT included in the "
                    "created students list file."
                    "Use option '--canvas-include-groupless' to include "
                    "these groupless students."
                    ))

            warn(message)


    with students_file.open("w") as outfile:

        for submission in submissions:

            if submission.is_group_submission():

                group = [
                        canvas_git_mapping_table.canvas2git(u.login_id)
                        for u in submission.group().members()
                        ]

                outfile.write(" ".join(group))
                outfile.write("\n")

            elif include_groupless:
                # Individual students

                canvas_id   = submission.submitter().login_id
                git_id      = canvas_git_mapping_table.canvas2git(canvas_id)
                outfile.write(git_id)
                outfile.write("\n")

            else:
                # Skip individual students in a group assignment
                pass
