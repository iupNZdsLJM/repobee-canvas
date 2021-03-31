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
"""Start managing a Canvas course for use with RepoBee.

"""
from pathlib             import Path
import re
from urllib.parse        import urlparse, urlunparse

import repobee_plug as plug

from ..canvas_api.api    import CanvasAPI
from ..canvas_api.course import Course
from ..canvas_category   import CANVAS_CATEGORY
from ..canvas_git_map    import CANVAS_GIT_MAP_FILENAME, CANVAS_ID, GIT_ID
from ..canvas_git_map    import canvas_git_map_table_wizard

from ..tui               import inform, warn, ask_closed, ask_dir, ask_open, ask_password

CANVAS                      = "canvas"
CANVAS_API_URL              = "canvas_base_url"
CANVAS_COURSE_ID            = "canvas_course_id"
CANVAS_GIT_MAP              = "canvas_git_map"
CANVAS_ID_KEY               = "login_id"
CANVAS_TOKEN                = "canvas_api_key"

REPOBEE                     = "repobee"
REPOBEE_BASE_URL            = "base_url"
REPOBEE_CONFIG_FILENAME     = "repobee.ini"
REPOBEE_ORG_NAME            = "org_name"
REPOBEE_TEMPLATE_ORG_NAME   = "template_org_name"
REPOBEE_TOKEN               = "token"
REPOBEE_USER                = "user"


class InitCourse(plug.Plugin, plug.cli.Command):
    """Canvas command to start managing a Canvas course for RepoBee.

    Usage (assuming Canvas plugin installed and activated):

        repobee canvas init-course https://your.canvas.edu/courses/345


    """
    __settings__ = plug.cli.command_settings(
            action      = CANVAS_CATEGORY.init_course,
            help        = "Start managing Canvas course",
            description = (
                "Create a directory for the course and populate with "
                "RepoBee configuration and Canvas-Git mapping file."
                )
            )

    course_url = plug.cli.positional(help = "URL of your course on Canvas")

    def handle_config(self, config : plug.Config):
        """Get access to the current RepoBee configuration."""
        self._config = config

    def command(self):
        """The RepoBee "init-course" command hook method."""
        inform("Initializing a Canvas course for use with RepoBee")

        # Step 1. Collecting information about the course on Canvas and Git.
        if _valid_git_setup(self._config):
            repobee_user            = self._config[REPOBEE][REPOBEE_USER]
            repobee_base_url        = self._config[REPOBEE][REPOBEE_BASE_URL]
            repobee_token           = self._config[REPOBEE][REPOBEE_TOKEN]

            if ask_closed(
                f"Use existing Git setup for user '{repobee_user}'? "):
                repobee_token       = self._config[REPOBEE][REPOBEE_TOKEN]
            else:
                repobee_base_url    = ask_open(
                        "Enter the Git base URL: ",
                        repobee_base_url
                        )
                repobee_user        = ask_open("Enter your Git username: ")
                repobee_token       = ask_password("Enter your Git access token: ")

        else:
            raise ValueError((
                    "Cannot find a working Git setup in your RepoBee "
                    "configuration. Please, run `repobee config wizard` to "
                    "configure git. See "
                    "https://docs.repobee.org/en/stable/getting_started.html "
                    "for more information."))

        repobee_template_org_name   = ask_open((
            "Enter the template organization containing the "
            "template repositories used in this course: "))
        repobee_org_name            = ask_open((
            "Enter the target organization that is to contain the "
            "student repositories used in this course's instance: "))

        course_id      = _extract_course_id(self.course_url)
        canvas_api_url = _extract_api_url(self.course_url)

        if _valid_canvas_setup(self._config, canvas_api_url):
            canvas_access_token = self._config[CANVAS][CANVAS_TOKEN]
        else:
            canvas_access_token = ask_password("Enter your Canvas access token: ")

        CanvasAPI().setup(canvas_api_url, canvas_access_token)
        course = Course.load(course_id)

        course_dir     = ask_dir("Enter course directory name: ", _str_to_path(course.name))
        mapping_table  = canvas_git_map_table_wizard(course)
        invalid_rows   = [r for r in mapping_table.rows() if not r[CANVAS_ID] or not r[GIT_ID]]

        if len(invalid_rows) > 0:
            warn((f"{len(invalid_rows)} students do not have a Canvas or "
                    "Git login ID. Please resolve this issue before using "
                    "RepoBee to manage assignments for this course."))


        # Step 2. Creating and filling a course directory with a Canvas-Git mapping
        # table and a RepoBee configuration file.
        inform("")
        inform(f"Created: {course_dir}")
        Path(course_dir).mkdir()

        path = f"{course_dir}/{CANVAS_GIT_MAP_FILENAME}"
        inform(f"Created: {path}  ⇝  the Canvas-Git mapping table CSV file")
        mapping_table.write(Path(path))

        path = f"{course_dir}/{REPOBEE_CONFIG_FILENAME}"
        inform(f"Created: {path}  ⇝  the RepoBee configuration file")
        repobee_config = plug.Config(Path(path))

        repobee_config.create_section(REPOBEE)
        repobee_config[REPOBEE][REPOBEE_BASE_URL]           = repobee_base_url
        repobee_config[REPOBEE][REPOBEE_USER]               = repobee_user
        repobee_config[REPOBEE][REPOBEE_TOKEN]              = repobee_token
        repobee_config[REPOBEE][REPOBEE_TEMPLATE_ORG_NAME]  = repobee_template_org_name
        repobee_config[REPOBEE][REPOBEE_ORG_NAME]           = repobee_org_name

        repobee_config.create_section(CANVAS)
        repobee_config[CANVAS][CANVAS_TOKEN]                = canvas_access_token
        repobee_config[CANVAS][CANVAS_API_URL]              = urlunparse(canvas_api_url)
        repobee_config[CANVAS][CANVAS_COURSE_ID]            = str(course_id)
        repobee_config[CANVAS][CANVAS_GIT_MAP]              = CANVAS_GIT_MAP_FILENAME

        repobee_config.store()

        inform(f"Initialization course '{course.name}' complete!")


# Private functions
def _valid_git_setup(config) -> bool:
    if REPOBEE not in config:
        return False

    if REPOBEE_USER not in config[REPOBEE]:
        return False

    if REPOBEE_TOKEN not in config[REPOBEE]:
        return False

    return True


def _valid_canvas_setup(config, api_url) -> bool:
    if CANVAS not in config:
        return False

    if CANVAS_API_URL not in config[CANVAS]:
        return False

    if CANVAS_TOKEN not in config[CANVAS]:
        return False

    if config[CANVAS][CANVAS_API_URL] != api_url:
        return False

    return ask_closed((
            "Use existing Canvas setup with API URL "
            f"'{api_url}'? "))


def _extract_api_url(url : str) -> str:
    """Extract the Canvas API URL from a Canvas website course URL."""
    url_parts = urlparse(url)
    return urlparse(f"{url_parts.scheme}://{url_parts.netloc}/api/v1")


def _extract_course_id(url : str) -> int:
    """Extract the course ID from a Canvas website course URL."""
    parts = urlparse(url).path.split("/")

    try:
        course_id  = int(parts[-1])
        courses_part = parts[-2]

        if courses_part != "courses":
            raise ValueError(
                    "Second to last element of URL should be \"courses\"."
                    )

        return course_id

    except (IndexError, ValueError) as url_error:
        raise ValueError((
            f"Canvas course URL {url} is incorrect. "
             "Expected the URL to end like \"…/courses/1234\""
            )) from url_error


def _str_to_path(string_path : str) -> str:
    """Convert a string to a string suitable as a path."""
    path = re.sub(r"\s+", "_", string_path)
    path = re.sub(r"[^\w]", "", path)
    return path
