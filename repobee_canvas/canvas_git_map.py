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
"""Map student IDs from Canvas to Git and vice versa.

To map IDs from Git to Canvas, and the other way around, use the CanvasGitMap
class. The CanvasGitMap class is a table with, for each student in a course,
at least two columns: canvas_id and git_id. Furthermore, for readability, you
can have more columns in the table. For example, an email address or student
name is convenient.

A CanvasGitMap is valid if each student has both a Canvas ID and a Git ID, and
both IDs are unique in the map.

The CanvasGitMap extends the Table class. The Table class offers basic
functionality to deal with a table, like access to its column names, its rows,
and reading from and writing to CSV files.
"""
import csv
from pathlib            import Path
from typing             import List

from bullet             import Bullet, Check, VerticalPrompt
from tabulate           import tabulate
from .canvas_api.course import Course
from .canvas_api.user   import PUBLIC_USER_FIELDS
from .tui               import warn, inform

CANVAS_ID               = "canvas_id"
CANVAS_GIT_MAP_FILENAME = "canvas-git-map.csv"
CANVAS_LOGIN_ID         = "login_id"
FIELD_SEP               = ","
GIT_ID                  = "git_id"
HEAD                    = 5

class Table:
    """Table"""

    def __init__(self, data : List):
        self._data = data

    @classmethod
    def load(cls, path : Path):
        """Load Table from a csv file."""
        with path.open() as csv_file:
            return cls(csv.DictReader(csv_file, delimiter = FIELD_SEP))

    def write(self, path : Path):
        """Write this Canvas-Git map to csv file."""
        with path.open("w") as csv_file:

            csv_writer = csv.DictWriter(
                    csv_file,
                    delimiter   = FIELD_SEP,
                    fieldnames  = list(self.columns()),
                    )

            csv_writer.writeheader()

            for row in self.rows():
                csv_writer.writerow(row)

    def columns(self):
        """Generator for the column names of this Table."""
        columns = []

        if len(self._data) > 0:
            columns = list(self._data[0].keys())

        return columns

    def rows(self):
        """Generator for each row of this Table."""
        for row in self._data:
            yield row

class CanvasGitMap(Table):
    """Map Canvas IDs to Git IDs and vice versa. The CanvasGitMap uses a
    data table with at least two columns, "git_id" and "canvas_id", to perform
    the mapping."""

    def __init__(self, data : List):
        super().__init__(data)

        self._canvas2git = {}
        self._git2canvas = {}

        for row in self.rows():
            canvas_id   = row[CANVAS_ID]
            git_id      = row[GIT_ID]

            _check_id("Canvas", canvas_id, self._canvas2git)
            _check_id("Git", git_id, self._git2canvas)

            self._canvas2git[canvas_id] = row[GIT_ID]
            self._git2canvas[git_id]    = row[CANVAS_ID]

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

# Guide the user in creating a potential Canvas-Git mapping table for a
# Canvas course.

ASK_GIT_ID          = ("Which column do you want to use as the students' "
                        "Git ID in the Canvas-Git mapping table?")
ASK_EXTRA_COLUMNS   = ("Which extra columns to you want to add to the "
                        "Canvas-Git mapping table? "
                        "Press SPACE to select an item; multiple items "
                        "can be selected. Press ENTER to confirm your choice.")

def canvas_git_map_table_wizard(course : Course) -> Table:
    """Create a Canvas-Git map CSV file."""
    students = course.students()

    if len(students) <= 0:
        warn((f"No users found for course '{course.name}'. "
               "Creating an empty Canvas-Git mapping table."))
        return []

    number_of_students  = len(students)
    head                = min(number_of_students, HEAD)
    number_shown        = head if head < number_of_students else "all"
    table               = tabulate([s.fields() for s in students[:head]], headers = "keys")

    inform((f"Found {len(students)} students for this course. "
            f"Showing available data for {number_shown} of them: \n\n"
            f"{table}\n"))

    canvas_id_key = CANVAS_LOGIN_ID
    inform((f"The column '{canvas_id_key}' contains students' Canvas ID."))

    cli = VerticalPrompt([
        Bullet(
            prompt  = ASK_GIT_ID,
            choices = PUBLIC_USER_FIELDS,
            bullet  = " >",
            margin  = 2,
            align   = 1,
            shift   = 1,
        ),
        Check(
            prompt  = ASK_EXTRA_COLUMNS,
            choices = PUBLIC_USER_FIELDS,
            check   = " >",
            margin  = 2,
            align   = 1,
            shift   = 1,
        ),
    ])

    git_id_key, extra_columns = [r for (p, r) in cli.launch()]

    data = []

    for student in students:
        row = {}
        fields = student.fields()

        if canvas_id_key in fields:
            row[CANVAS_ID] = fields[canvas_id_key]
        else:
            row[CANVAS_ID] = ""

        if git_id_key in fields:
            row[GIT_ID] = fields[git_id_key]
        else:
            row[GIT_ID] = ""

        for column in extra_columns:
            if column in fields:
                row[column] = fields[column]
            else:
                row[column] = ""

        data.append(row)

    return Table(data)

# Private functions
def _check_id(service : str, service_id : str, service_map : str) -> bool:
    if not service_id:
        raise ValueError(f"The {service} ID cannot be empty.")

    if service_id in service_map:
        raise ValueError(f"The {service} ID '{service_id}' is not unique.")
