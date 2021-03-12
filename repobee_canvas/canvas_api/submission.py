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
"""Wrapper for a Canvas submission API object."""
from typing import List

from .api import CanvasAPI, GROUP, ID, COURSE, SUBMISSION_COMMENTS
from .canvas_object import CanvasObject
from .comment import Comment
from .course import Course
from .group import Group
from .peer_review import PeerReview
from .user import User

class Submission (CanvasObject):
    """Canvas submission.

    See https://canvas.instructure.com/doc/api/submissions.html
    """

    @staticmethod
    def load(course_id : int, assignment_id : int, user_id : int):
        """
        Load a Canvas submission object.

        Args:
        - course_id: The course id
        - assignment_id: The assignment id
        - user_id: The user id
        """
        return Submission(CanvasAPI().submission(course_id, assignment_id, user_id))

    def submitter(self) -> User:
        """Submitter"""
        if not self._submitter:
            self._submitter = User.load(self.user_id)

        return self._submitter

    def is_group_submission(self) -> bool:
        """Return True if this submission is a group submission; False
        otherwise.

        Note. A submission is only recognized as a groups submission after
        some student (or teacher) in that group submitted something. This
        can also be a comment, though.
        """
        return self._data[GROUP][ID] is not None

    def group(self) -> Group:
        """This submission's group, if any."""
        if not self._group and self.is_group_submission():
            self._group = Group.load(self._data[GROUP][ID])

        return self._group

    def course(self) -> Course:
        """The course this submission belongs to."""
        if not self._course:
            self._course = Course(self._data[COURSE])

        return self._course

    def comments(self) -> List[Comment]:
        """The comments made on this submission."""
        submission_comments = self._data[SUBMISSION_COMMENTS]
        if submission_comments:
            return [Comment(c) for c in submission_comments]

        return []

    def students(self) -> List[User]:
        """A list of students that worked on this submission."""
        if self.is_group_submission():
            return self.group().members()
        
        return [self.submitter()]

    def has_peer_reviews(self) -> bool:
        """Return True if this submission does have peer reviews; False
        otherwise."""
        return len(self.peer_reviews()) > 0

    def pending_peer_reviews(self) -> bool:
        """Return True if this submission has pending peer reviews; False
        otherwise."""
        return [p for p in self.peer_reviews() if p.pending]

    def finished_peer_reviews(self) -> bool:
        """Return True if any peer review for this submission has been
        completed; False otherwise."""
        return [p for p in self.peer_reviews() if p.finished]

    def peer_reviews_finished(self) -> bool:
        """Return True if all peer reviews for this submission have been
        completed; False otherwise."""
        return len(self.pending_peer_reviews()) == 0

    def peer_reviews(self) -> List[PeerReview]:
        """Return a list of peer reviews for this submission, if any."""
        if not self._peer_reviews:
            peer_reviews = CanvasAPI().peer_reviews(self.course().id, self.assignment_id, self.id)
            self._peer_reviews = [PeerReview(p) for p in peer_reviews]

        return self._peer_reviews

    def add_comment(self, msg : str, file_path : str = None):
        """Add a new comment to this submission."""
        return CanvasAPI().add_comment_to_submission(
                    self.course().id,
                    self.assignment_id,
                    self.user_id,
                    msg,
                    file_path
                )

    def submit_url(self, url : str, msg : str = None, submitted_at = None):
        """Submit an URL."""
        return CanvasAPI().submit_url(
                self.course().id,
                self.assignment_id,
                self.user_id,
                url,
                msg,
                submitted_at)

    def submit_text(self, text : str, msg : str = None, submitted_at = None):
        """Submit a text."""
        return CanvasAPI().submit_text(
                self.course().id,
                self.assignment_id,
                self.user_id,
                text,
                msg,
                submitted_at)

    def submit_file(self, file_path : str, msg :str = None, submitted_at = None):
        """Submit a file."""
        return CanvasAPI().submit_file(
                self.course().id,
                self.assignment_id,
                self.user_id,
                file_path,
                msg,
                submitted_at)
