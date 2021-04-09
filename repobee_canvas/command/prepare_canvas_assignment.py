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
"""Prepare a Canvas assignment for use with repobee

"""
import repobee_plug as plug

from ..canvas_api.api           import CanvasAPI
from ..canvas_api.assignment    import Assignment

from .canvas_category           import CANVAS_CATEGORY

from ..common_options           import CANVAS_ACCESS_TOKEN_OPTION
from ..common_options           import CANVAS_API_BASE_URL_OPTION
from ..common_options           import CANVAS_COURSE_ID_OPTION
from ..common_options           import CANVAS_ASSIGNMENT_ID_OPTION
from ..common_options           import CANVAS_START_ASSIGNMENT_MESSAGE_OPTION

from ..tui                      import inform, warn

from .send_message              import send_message

UPLOAD_SUBMISSION               = "online_upload"

def check(requirement, success : str, failure : str) -> bool:
    """Check requirement. If okay, show success message and return True.
    Otherwise, show failure message and return False.
    """
    if requirement():
        inform("☒ " + success)
        return True

    inform("☐ " + failure)
    return False


class PrepareCanvasAssignment(plug.Plugin, plug.cli.Command):
    """ The PrepareCanvasAssignment class is a RepoBee plugin to check the
    configuration of an assignment: Is it configured correctly for use with the
    Canvas plugin? In particular, does the assignment have both URL and file
    upload submission types enabled.

    Usage:

        repobee -p canvas prepare-assignment \
                --canvas-assignment-id N \
                [--canvas-start-assignment-message MSG]

    Checks if assignment with ID N is configured correctly and allows file
    uploads. Furthermore, to enable group assignments and be transparent to
    students that this assignment is being managed by repobee-canvas, an
    initial message is send. The message is only send once, and only if all
    checks pass.

    You can configure your own message, or supply it via a command-line
    argument. By default, the message is "This assignment is managed by
    repobee-canvas.".

    Hack: You can use this command to send messages to students in Canvas
    submission: as long as the new message is different from any already in
    the submission, it will get posted if checks pass.
    """
    __settings__ = plug.cli.command_settings(
            action = CANVAS_CATEGORY.prepare_assignment,
            help = ("check configuration of the Canvas assignment and "
                    "prepare the assignment for group work"),
            description = (
                "Check the configuration of the supplied Canvas "
                "assignment for compatibility with the Canvas plugin "
                "and prepare it for group assignments."
                ),
            )

    canvas_access_token                 = CANVAS_ACCESS_TOKEN_OPTION
    canvas_base_url                     = CANVAS_API_BASE_URL_OPTION
    canvas_course_id                    = CANVAS_COURSE_ID_OPTION
    canvas_assignment_id                = CANVAS_ASSIGNMENT_ID_OPTION
    canvas_start_assignment_message     = CANVAS_START_ASSIGNMENT_MESSAGE_OPTION

    def command(self):
        """Command to prepare a Canvas assignment for use with RepoBee."""
        CanvasAPI().setup(self.canvas_base_url, self.canvas_access_token)
        assignment = Assignment.load(self.canvas_course_id, self.canvas_assignment_id)

        requirements = [
            check(
                lambda: UPLOAD_SUBMISSION in assignment.submission_types,
                "File upload submission enabled",
                "File upload submission disabled"
            ),
        ]

        if all(requirements):
            # Prepare for group assignments by adding a comment. In Canvas,
            # submissions are linked to a single student until the first
            # comment or submission.
            send_message(assignment, self.canvas_start_assignment_message)
            inform(("Assignment configuration is OKAY. "
                    "All Canvas submissions have been initialized."))
        else:
            warn((
                "Assignment configuration is NOT okay. "
                "Please fix the above issues and run this command again."
                ))
