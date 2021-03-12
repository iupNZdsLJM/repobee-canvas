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
"""Map IDs from Git to Canvas and the other way around."""
import csv

GIT_ID = "git_id"
CANVAS_ID = "canvas_id"

def _check_id(service : str, service_id : str, service_map : str) -> bool:
    if not service_id:
        raise ValueError(f"The {service} ID cannot be empty.")

    if service_id in service_map:
        raise ValueError(f"The {service} ID '{service_id}' is not unique.")

class CanvasGitMap:
    """Map Canvas IDs to Git IDs and vice versa. The CanvasGitMap uses a
    database, a CSV file, with columns "git_id" and "canvas_id", to perform
    the mapping."""

    def __init__(self, path : str):
        self._canvas2git = {}
        self._git2canvas = {}

        with open(path) as csvfile:
            read_csv = csv.DictReader(csvfile, delimiter=",")
            for row in read_csv:
                canvas_id = row[CANVAS_ID]
                _check_id("Canvas", canvas_id, self._canvas2git)

                git_id = row[GIT_ID]
                _check_id("Git", git_id, self._git2canvas)

                self._canvas2git[canvas_id] = row[GIT_ID]
                self._git2canvas[git_id] = row[CANVAS_ID]

    def canvas2git(self, canvas_id : str) -> str:
        """Convert a Canvas ID to the correspondibg Git ID."""
        if canvas_id in self._canvas2git:
            return self._canvas2git[canvas_id]

        raise ValueError(f"Canvas ID '{canvas_id}' not mapped to a Git ID.")

    def git2canvas(self, git_id : str) -> str:
        """Convert a Git ID to the corresponding Canvas ID."""
        if git_id in self._git2canvas:
            return self._git2canvas[git_id]

        raise ValueError(f"Git ID '{git_id}' not mapped to a Canvas ID.")
