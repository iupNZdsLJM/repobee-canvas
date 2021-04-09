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
"""Start managing a Canvas assignment with RepoBee.

"""
import datetime
from pathlib                    import Path
import re
import sys
from urllib.parse               import urlparse, urlunparse

from bullet                     import Bullet
import repobee_plug as plug
import repobee_plug.platform as platform

from ..canvas_api.api           import CanvasAPI
from ..canvas_api.assignment    import Assignment
from ..canvas_api.course        import Course
from .canvas_category           import CANVAS_CATEGORY
from ..canvas_git_map           import CANVAS_GIT_MAP_FILENAME, CANVAS_ID, GIT_ID
from ..canvas_git_map           import canvas_git_map_table_wizard

from ..common_options           import CANVAS_ACCESS_TOKEN_OPTION
from ..common_options           import CANVAS_API_BASE_URL_OPTION
from ..common_options           import CANVAS_COURSE_ID_OPTION
from ..common_options           import CANVAS_START_ASSIGNMENT_MESSAGE_OPTION

from ..tui                      import inform, warn, ask_closed, ask_open, ask_password
from ..tui                      import ask_dir, str_to_path

CANVAS                      = "canvas"
CANVAS_API_URL              = "canvas_base_url"
CANVAS_COURSE_ID            = "canvas_course_id"
CANVAS_GIT_MAP              = "canvas_git_map"
CANVAS_ID_KEY               = "login_id"
CANVAS_TOKEN                = "canvas_access_token"

REPOBEE                     = "repobee"
REPOBEE_BASE_URL            = "base_url"
REPOBEE_CONFIG_FILENAME     = "repobee.ini"
REPOBEE_ORG_NAME            = "org_name"
REPOBEE_TEMPLATE_ORG_NAME   = "template_org_name"
REPOBEE_TOKEN               = "token"
REPOBEE_USER                = "user"


class InitAssignment(plug.Plugin, plug.cli.Command):
    """Canvas command to start managing a Canvas assignment with RepoBee.

    Usage (assuming Canvas plugin installed and activated):

        repobee canvas init-assignment

    Starts a wizard. Requirements: valid configuration for a Canvas course and
    Git.

    """
    __settings__ = plug.cli.command_settings(
            action      = CANVAS_CATEGORY.init_assignment,
            help        = "Start managing Canvas assignment",
            description = (
                "Create a directory for the assignment and populate with "
                "RepoBee configuration and students list."
                )
            )

    canvas_access_token                 = CANVAS_ACCESS_TOKEN_OPTION
    canvas_base_url                     = CANVAS_API_BASE_URL_OPTION
    canvas_course_id                    = CANVAS_COURSE_ID_OPTION
    canvas_start_assignment_message     = CANVAS_START_ASSIGNMENT_MESSAGE_OPTION

    def handle_config(self, config : plug.Config):
        """Get access to the current RepoBee configuration."""
        self._config = config

    def command(self, api):
        """The RepoBee "init-assignment" command hook method."""

        # Step 1: Pick assignment from course to initialize from list
        CanvasAPI().setup(self.canvas_base_url, self.canvas_access_token)
        course              = Course.load(self.canvas_course_id)
        assignment          = _select_assignment(course)
        assignment_dir      = ask_dir("Enter assignment directory name: ", str_to_path(assignment.name))

        # Step 2: Pick template from Git group to use
        assignment_template = _select_template_repo(api)


        # Step 3: Prepare assignment by sending welcome message (also warn?)

        # Step 4: Create directory, write RepoBee config, and write
        # students.lst

        # Step 5: Tell user that she now can use RepoBee to manage repos.

# Private functions
NOT_IN_LIST = "The assignment I want is not in this list!"

def _select_assignment(course : Course) -> Assignment:
    """Ask the user to select an assignment from the course."""
    assignments = course.assignments()
    choices = []
    field_size = max([len(str(a.id)) for a in assignments])

    for assignment in assignments:
        assignment_str = f"{assignment.id : >{field_size}} — \"{assignment.name}\""
        if assignment.due_at:
            date = datetime.datetime.strptime(assignment.due_at, "%Y-%m-%dT%H:%M:%SZ")
            assignment_str += f", {date : %Y-%m-%d, %H:%M}"

        choices.append(assignment_str)

    choices.append(f"{'X'*field_size} — {NOT_IN_LIST}")

    cli = Bullet(
            prompt = "Select the assignment you want to initalize: ",
            choices = choices,
            bullet  = " >",
            margin  = 2,
            align   = 1,
            shift   = 1,
            )
    choice = cli.launch()
    if choice == choices[-1]:
        inform(("\n"
            "If the assignment you want to initalize was not listed above, "
            "then that assignment was incorrectly configured in "
            "Canvas for use with RepoBee."
            "\n\n"
            "Make sure your assignment has submission type "
            "\"online_upload\"."
            ))
        sys.exit()
    else:
        assignment_id, _ = choice.split("—")
        return [a for a in assignments if int(a.id) ==
                int(assignment_id)][0]

def _select_template_repo(git_api : platform.PlatformAPI) -> str:
    """Ask the user to select a template repository to use for this
    assignment."""
    repos = git_api.get_repos()
    for r in repos:
        print(r)
    template = ""
    return template
