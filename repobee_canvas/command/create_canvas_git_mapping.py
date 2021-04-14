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
"""Create a Canvas-Git mapping table."""
from pathlib import Path
import repobee_plug as plug

from ..canvas_api.api           import CanvasAPI
from ..canvas_api.course        import Course

from .canvas_category           import CANVAS_CATEGORY
from ..canvas_git_map           import canvas_git_map_table_wizard

from ..common_options           import CANVAS_ACCESS_TOKEN_OPTION
from ..common_options           import CANVAS_API_BASE_URL_OPTION
from ..common_options           import CANVAS_COURSE_ID_OPTION
from ..common_options           import CANVAS_GIT_MAP_OPTION

from ..tui                      import inform, warn

class CreateCanvasGitMapping(plug.Plugin, plug.cli.Command):
    """Create a Canvas-Git mapping table and write to file.
    """
    __settings__ = plug.cli.command_settings(
            action = CANVAS_CATEGORY.create_canvas_git_mapping,
            help = ("create a Canvas-Git mapping table"),
            description = (
                "Create a Canvas-Git mapping table for a Canvas course "
                "via a wizard and write the table to file."
                ),
            )

    canvas_access_token                 = CANVAS_ACCESS_TOKEN_OPTION
    canvas_base_url                     = CANVAS_API_BASE_URL_OPTION
    canvas_course_id                    = CANVAS_COURSE_ID_OPTION
    canvas_git_map                      = CANVAS_GIT_MAP_OPTION

    def command(self):
        """Command to create a Canvas-Git mapping table and write it to a file."""
        CanvasAPI().setup(self.canvas_base_url, self.canvas_access_token)
        course = Course.load(self.canvas_course_id)
        canvas_git_mapping_table = canvas_git_map_table_wizard(course)

        if canvas_git_mapping_table.empty():
            warn("Canvas-Git mapping table CSV is not created.")
        else:
            path = Path(self.canvas_git_map)
            canvas_git_mapping_table.write(path)
            inform(f"Created file:  {str(path)}     ⇝  the Canvas-Git mapping table CSV file")
