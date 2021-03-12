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
"""Command-line and configuration options shared by the various canvas plugin
commands.
"""
from urllib.parse import urlparse
import repobee_plug as plug

CANVAS_API_KEY_OPTION = plug.cli.option(
            help = "The Canvas API key",
            required = True,
            configurable = True
            )

CANVAS_API_BASE_URL_OPTION = plug.cli.option(
            help = "The base URL to your Canvas installation",
            converter = urlparse,
            required = True,
            configurable = True
            )

CANVAS_COURSE_ID_OPTION = plug.cli.option(
            help = "Canvas course id",
            converter = int,
            required = True,
            configurable = True
            )

CANVAS_ASSIGNMENT_ID_OPTION = plug.cli.option(
            help = "Canvas assignment id",
            converter = int,
            required = True
            )

STUDENTS_FILE = "students.lst"

CANVAS_STUDENTS_FILE = plug.cli.option(
        help = "File with students for a Canvas assignment",
        default = STUDENTS_FILE
        )


CANVAS_UPLOAD_ZIP = plug.cli.flag(
        help = "Upload students' cloned repositories as a ZIP file to Canvas.",
        default = False
        )

CANVAS_ZIP_NAME = plug.cli.option(
        help = "Name of the ZIP file to generate of the cloned repository and to upload to Canvas.",
        required = False
        )

CANVAS_GIT_MAP = plug.cli.option(
        help = "Map Canvas IDs to Git IDs and vice versa.",
        required = True
        )
