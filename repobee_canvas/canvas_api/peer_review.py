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
"""Wrapper for a Canvas peer review API object."""
from typing import List

from .canvas_object import CanvasObject
from .user import User

COMPLETED   = "completed"
ASSIGNED    = "assigned"

class PeerReview (CanvasObject):
    """Canvas peer review.

    See https://canvas.instructure.com/doc/api/peer_reviews.html
    """

    def finished(self) -> bool:
        """Return True if this peer review has been completed; False
        otherwise."""
        return self.workflow_state == COMPLETED

    def pending(self) -> bool:
        """Return True if this peer review has been assigned, but is not yet
        completed; False otherwise."""
        return self.workflow_state == ASSIGNED

    def user(self) -> User:
        """The Canvas user which work is being peer reviewed."""
        if not self._user:
            self._user = User.load(self.user_id)

        return self._user

    def reviewer(self) -> List[User]:
        """The Canvas users that are doing this peer review."""
        if not self._reviewer:
            self._reviewer = User.load(self.assessor_id)

        return self._reviewer
