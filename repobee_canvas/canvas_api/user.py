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
"""Wrapper for a Canvas user API object."""
from .api import CanvasAPI
from .canvas_object import CanvasObject

TEST_STUDENT_NAME = "Test Student"
PUBLIC_USER_FIELDS = ["name", "sortable_name", "short_name", "sis_user_id",
        "integration_id", "login_id", "email"]

class User (CanvasObject):
    """Canvas user

    See https://canvas.instructure.com/doc/api/users.html
    """

    @staticmethod
    def load(user_id : int):
        """
        Load a Canvas user object.

        Args:
        - user_id: The user id
        """
        return User(CanvasAPI().user(user_id))

    def is_test_student(self) -> bool:
        """Return True if this user is the test student; False otherwise."""
        return self.name == TEST_STUDENT_NAME

    def fields(self):
        """Return the fields of this object."""
        fields = {}
        for key in PUBLIC_USER_FIELDS:
            if key in self._data:
                fields[key] = self._data[key]
            else:
                fields[key] = ""

        return fields
