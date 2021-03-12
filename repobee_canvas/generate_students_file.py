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
"""Generate a students file from a Canvas assignment for use with RepoBee.

"""
import repobee_plug as plug

from .canvas_api.api import CanvasAPI
from .canvas_api.assignment import Assignment
from .canvas_git_map import CanvasGitMap

from .common_options import CANVAS_API_KEY_OPTION
from .common_options import CANVAS_COURSE_ID_OPTION
from .common_options import CANVAS_ASSIGNMENT_ID_OPTION
from .common_options import CANVAS_STUDENTS_FILE
from .common_options import CANVAS_API_BASE_URL_OPTION
from .common_options import CANVAS_GIT_MAP

from .logging import inform, warn

class GenerateStudentsFile(plug.Plugin, plug.cli.Command):
    """RepoBee command to generate a students file from a Canvas assignment.

    The CanvasStudentsFile class is a RepoBee plugin to generate a students file
    for a Canvas assignment: All students assigned to this assignment are
    listed and written to the students file. If the assignment is a group
    assignment, the student groups are written instead.

    You have to use this plugin first to generate the students file and then use
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
    repobee -p canvas generate-students-file \
            --canvas-assignment-id 23 \
            --canvas-git-map student_data.csv
    ```

    will generate file `students.lst` with all Git account names of the
    students involved in assignment with ID=23.

    If you want to use a different output filename use option
    `--canvas-students-file output.lst`.

    """
    __settings__ = plug.cli.command_settings(
            action      = "generate-students-file",
            help        = "generate students file",
            description = "Generate the students file for a Canvas assignment for use with repobee",
            )

    canvas_api_key          = CANVAS_API_KEY_OPTION
    canvas_base_url         = CANVAS_API_BASE_URL_OPTION
    canvas_course_id        = CANVAS_COURSE_ID_OPTION
    canvas_assignment_id    = CANVAS_ASSIGNMENT_ID_OPTION
    canvas_students_file    = CANVAS_STUDENTS_FILE
    canvas_git_map          = CANVAS_GIT_MAP

    def command(self):
        CanvasAPI().setup(self.canvas_base_url, self.canvas_api_key)
        assignment = Assignment.load(self.canvas_course_id, self.canvas_assignment_id)

        try:
            id_mapper = CanvasGitMap(self.canvas_git_map)

            inform((f"""Generating students file for Canvas assignment """
                    f"""{self.canvas_assignment_id} …"""))

            with open(self.canvas_students_file, "w") as students_file:

                for submission in assignment.submissions():

                    if submission.is_group_submission():
                        group = [
                                id_mapper.canvas2git(u.login_id)
                                for u in submission.group().members()
                                ]
                        students_file.write(" ".join(group))
                    else:
                        students_file.write(id_mapper.canvas2git(submission.submitter().login_id))

                    students_file.write("\n")


            inform(f"""Students file written to "{self.canvas_students_file}".""")

        except ValueError as error:
            warn((f"""Error reading/using Canvas/Git ID mapper file """
                  f"""'{self.canvas_git_map}'. Reason: """), error)
