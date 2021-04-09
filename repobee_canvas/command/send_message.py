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
"""Send a message to each submission of a Canvas assignment."""
import repobee_plug as plug

from ..canvas_api.api           import CanvasAPI
from ..canvas_api.assignment    import Assignment

from .canvas_category          import CANVAS_CATEGORY

from ..common_options           import CANVAS_ACCESS_TOKEN_OPTION
from ..common_options           import CANVAS_API_BASE_URL_OPTION
from ..common_options           import CANVAS_COURSE_ID_OPTION
from ..common_options           import CANVAS_ASSIGNMENT_ID_OPTION

class SendMessage(plug.Plugin, plug.cli.Command):
    """Send a message to each submission for an assignment.
    """
    __settings__ = plug.cli.command_settings(
            action = CANVAS_CATEGORY.send_message,
            help = ("send message to each submission of an assignment"),
            description = (
                "Send a message to each submission of a Canvas assignment. "
                "If the message already appears in a submission's comments, "
                "no new message is send."
                ),
            )

    canvas_access_token                 = CANVAS_ACCESS_TOKEN_OPTION
    canvas_base_url                     = CANVAS_API_BASE_URL_OPTION
    canvas_course_id                    = CANVAS_COURSE_ID_OPTION
    canvas_assignment_id                = CANVAS_ASSIGNMENT_ID_OPTION
    message                             = plug.cli.positional(help = "URL of your course on Canvas")
    resend                              = plug.cli.flag(
        help = ("Send message regardless if it already appears in "
                "a submission's comments"),
    )

    def command(self):
        """Command to send a message to each submission of an assignment."""
        CanvasAPI().setup(self.canvas_base_url, self.canvas_access_token)
        assignment = Assignment.load(self.canvas_course_id, self.canvas_assignment_id)
        send_message(assignment, self.message, self.resend)

def send_message(assignment : Assignment, message : str, resend : bool = False):
    """Send message to each submission of assignment.

    By default, if a message already appears in a submission's comments, it is
    not resend. Use argument `resend` to change this behavior and send it
    again anyway.
    """
    for submission in assignment.submissions():
        comments = [sc.comment for sc in submission.comments()]

        if resend or message not in comments:
            submission.add_comment(message)
