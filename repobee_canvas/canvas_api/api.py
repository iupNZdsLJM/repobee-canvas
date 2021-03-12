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
"""Access to the Canvas API"""
import os
import requests

# HTTP header constants
AUTHORIZATION           = "Authorization"
LOCATION                = "Location"
BEARER                  = "Bearer {key}"

# Canvas API component names
ASSIGNMENTS             = "assignments"
BODY                    = "body"
COMMENT                 = "comment"
COMMENTS                = "comments"
COURSE                  = "course"
COURSE_ID               = "course_id"
COURSES                 = "courses"
EMPTY                   = ""
ERRORS                  = "errors"
FILE                    = "file"
FILE_IDS                = "file_ids"
FILES                   = "files"
GROUP                   = "group"
GROUP_COMMENT           = "group_comment"
GROUPS                  = "groups"
GROUPED                 = "grouped"
ID                      = "id"
INCLUDE                 = "include[]"
MEMBERSHIPS             = "memberships"
NAME                    = "name"
NEXT                    = "next"
ONLINE_TEXT_ENTRY       = "online_text_entry"
ONLINE_UPLOAD           = "online_upload"
ONLINE_URL              = "online_url"
OVERRIDES               = "overrides"
PEER_REVIEWS            = "peer_reviews"
PER_PAGE                = "per_page"
PROFILE                 = "profile"
SECTIONS                = "sections"
SIZE                    = "size"
STUDENTS                = "students"
SUBMISSION              = "submission"
SUBMISSION_COMMENTS     = "submission_comments"
SUBMISSION_TYPE         = "submission_type"
SUBMISSIONS             = "submissions"
SUBMITTED_AT            = "submitted_at"
TEXT_COMMENT            = "text_comment"
TOTAL_STUDENTS          = "total_students"
UPLOAD_PARAMS           = "upload_params"
UPLOAD_URL              = "upload_url"
URL                     = "url"
USER_ID                 = "user_id"
USERS                   = "users"

# Canvas API parameters
GROUPED_SUBMISSION      = {INCLUDE: [GROUP, COURSE, SUBMISSION_COMMENTS], GROUPED: True}
ASSIGNMENT_OVERRIDES    = {INCLUDE: [OVERRIDES]}
ALL_SECTIONS            = {INCLUDE: [SECTIONS, TOTAL_STUDENTS]}
ALL_STUDENTS            = {INCLUDE: [STUDENTS, TOTAL_STUDENTS]}
WITH_COURSE             = {INCLUDE: [COURSE, SUBMISSION_COMMENTS]}

# Canvas data parameters
COMMENT_TEXT_COMMENT    = COMMENT       + "[" + TEXT_COMMENT    + "]"
COMMENT_GROUP_COMMENT   = COMMENT       + "[" + GROUP_COMMENT   + "]"
COMMENT_FILE_IDS        = COMMENT       + "[" + FILE_IDS        + "][]"

SUB_SUBMISSION_TYPE     = SUBMISSION    + "[" + SUBMISSION_TYPE + "]"
SUB_FILE_IDS            = SUBMISSION    + "[" + FILE_IDS        + "][]"
SUB_BODY                = SUBMISSION    + "[" + BODY            + "]"
SUB_URL                 = SUBMISSION    + "[" + URL             + "]"
SUB_SUBMITTED_AT        = SUBMISSION    + "[" + SUBMITTED_AT    + "]"
SUB_USER_ID             = SUBMISSION    + "[" + USER_ID         + "]"
SUB_COMMENT             = SUBMISSION    + "[" + COMMENT         + "]"

# Canvas API constants
PAGE_SIZE               = 100
REDIRECT_STATUS_CODES   = [300, 301, 303, 304, 305, 306, 307, 308]
UPLOAD_OKAY_STATUS_CODE = 201

# Error messages
REQUEST_FAILED          = "Request failed: response code {code}, {reason}"
API_SETUP_PROBLEM       = "CanvasAPI is not setup properly. See CanvasAPI#setup for details."
INCORRECT_UPLOAD_STATUS = "Incorrect status code for upload: {c} - {r}"
FILE_READ_ERROR         = "Cannot read file at path '{p}'"
UPLOAD_ERRORS           = "Upload failed:  {errors}"

class CanvasAPI:
    """Canvas API"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args, **kwargs)
            
        return cls._instance

    def setup(self, api_url : str = None, api_key : str = None) -> None:
        """Setup this CanvasAPI with an url and api key."""
        self._session = requests.Session()

        if api_url:
            self._api_url = api_url.geturl()

        if api_key:
            self._session.headers.update({AUTHORIZATION: BEARER.format(key=api_key)})

    def assignment(self, course_id, assignment_id):
        """Get assignment"""
        return self.__get(
                components={COURSES: course_id, ASSIGNMENTS: assignment_id},
                params=ASSIGNMENT_OVERRIDES
                )

    def assignment_override(self, course_id, assignment_id, override_id):
        """Get assignment override"""
        return self.__get({
            COURSES: course_id,
            ASSIGNMENTS: assignment_id,
            OVERRIDES: override_id
            })

    def overrides(self, course_id, assignment_id):
        """Get assignment overrides"""
        return [o.extend({COURSE_ID: course_id}) for o in self.__get({
            COURSES: course_id,
            ASSIGNMENTS: assignment_id,
            OVERRIDES: EMPTY
            })]

    def submissions_per_course(self, course_id, assignment_id):
        """Get submissions for an assignment"""
        return self.__get({
            COURSES: course_id,
            ASSIGNMENTS: assignment_id,
            SUBMISSIONS: EMPTY
            }, params = GROUPED_SUBMISSION)

    def submissions_per_section(self, section_id, assignment_id):
        """Get submissions for an assignment belonging to a section"""
        return self.__get({
            SECTIONS: section_id,
            ASSIGNMENTS: assignment_id,
            SUBMISSIONS: EMPTY
            }, params = GROUPED_SUBMISSION)

    def course(self, course_id):
        """Get course"""
        return self.__get({
            COURSES: course_id
            }, params = ALL_SECTIONS)

    def group(self, group_id):
        """Get group"""
        return self.__get({GROUPS: group_id})

    def group_memberships(self, group_id):
        """Get group memberships"""
        return self.__get({GROUPS: group_id, MEMBERSHIPS: EMPTY})

    def peer_reviews(self, course_id, assignment_id, submission_id):
        """Get peer reviews"""
        return self.__get({
            COURSES: course_id,
            ASSIGNMENTS: assignment_id,
            SUBMISSIONS: submission_id,
            PEER_REVIEWS: EMPTY
            })

    def section(self, course_id, section_id):
        """Get section"""
        return self.__get(
                {COURSES: course_id, SECTIONS: section_id},
                params = ALL_STUDENTS
                )

    def submission(self, course_id, assignment_id, user_id):
        """Get submission"""
        return self.__get({
            COURSES: course_id,
            ASSIGNMENTS: assignment_id,
            SUBMISSIONS: user_id
            }, params = WITH_COURSE)

    def add_comment_to_submission(self, course_id, assignment_id, user_id, msg, file_path = None):
        """Add comment to submission"""
        comment = {
                COMMENT_TEXT_COMMENT: msg,
                COMMENT_GROUP_COMMENT: True
                }

        if file_path is not None:
            file_id = self.__upload({
                COURSES: course_id,
                ASSIGNMENTS: assignment_id,
                SUBMISSIONS: user_id,
                COMMENTS: EMPTY,
                FILES: EMPTY
                }, file_path)

            comment[COMMENT_FILE_IDS] = [file_id]

        return self.__put({
            COURSES: course_id,
            ASSIGNMENTS: assignment_id,
            SUBMISSIONS: user_id
            }, comment)

    def user(self, user_id):
        """Get user"""
        return self.__get({USERS: user_id, PROFILE: EMPTY})

    def submit_url(self, course_id, assignment_id, user_id, url, msg = None, submitted_at
            = None):
        """Submit URL"""
        submission = {
                SUB_SUBMISSION_TYPE: ONLINE_URL,
                SUB_URL: url,
                SUB_USER_ID: user_id
                }

        return self.__submit(
                course_id,
                assignment_id,
                submission,
                submitted_at,
                msg)

    def submit_text(self, course_id, assignment_id, user_id, text, msg = None, submitted_at
            = None):
        """Submit text"""
        submission = {
                SUB_SUBMISSION_TYPE: ONLINE_TEXT_ENTRY,
                SUB_BODY: text,
                SUB_USER_ID: user_id
                }

        return self.__submit(
                course_id,
                assignment_id,
                submission,
                submitted_at,
                msg
                )

    def submit_file(self, course_id, assignment_id, user_id, file_path, msg =
            None, submitted_at = None):
        """Submit file"""
        file_id = self.__upload({
            COURSES: course_id,
            ASSIGNMENTS: assignment_id,
            SUBMISSIONS: user_id,
            FILES: EMPTY
            }, file_path)

        submission = {
                SUB_SUBMISSION_TYPE: ONLINE_UPLOAD,
                SUB_FILE_IDS: [file_id],
                SUB_USER_ID: user_id
                }

        return self.__submit(
                course_id,
                assignment_id,
                submission,
                submitted_at,
                msg)


    # Private utility methods
    def __get(self, components, params = {}):
        url = self._create_url(components)
        params[PER_PAGE] = PAGE_SIZE
        response = self._session.get(url, params = params)

        self._check_response(response)

        # Handle multiple pages
        data = response.json()

        while NEXT in response.links:
            url = response.links[NEXT][URL]
            response = self._session.get(url, params=params)
            self._check_response(response)
            data.extend(response.json())

        return data

    def __post(self, components, data = {}):
        url = self._create_url(components)
        response = self._session.post(url, data = data)
        self._check_response(response, requests.codes.created)
        return response

    def __put(self, components, data = {}):
        url = self._create_url(components)
        response = self._session.put(url, data = data)
        self._check_response(response)
        return response

    def __upload(self, components, path):
        if not os.access(path, os.R_OK):
            raise ValueError(FILE_READ_ERROR.format(p=path))

        filename = os.path.basename(path)
        filesize = os.path.getsize(path)

        # Following four steps at https://canvas.instructure.com/doc/api/file.file_uploads.html
        # Step 1
        url = self._create_url(components)

        upload_config = self._session.post(
                url,
                json = {
                    NAME: filename,
                    SIZE: filesize
                    }
                ).json()

        if ERRORS in upload_config and upload_config[ERRORS]:
            raise ValueError(UPLOAD_ERRORS.format(errors=upload_config[ERRORS]))

        # Step 2
        upload_url = upload_config[UPLOAD_URL]
        upload_params = upload_config[UPLOAD_PARAMS]
        files = {FILE: open(path, "rb")}

        # post without headers
        upload = self._session.post(
                upload_url,
                json = upload_params,
                files = files,
                headers = {}
                )

        # Step 3
        if upload.status_code in REDIRECT_STATUS_CODES:
            # Step 4: "Get" the redirected URL to complete the request to mark
            # the new file as available.
            self.__get(upload.headers[LOCATION])
        elif upload.status_code != UPLOAD_OKAY_STATUS_CODE:
            raise ValueError(
                    INCORRECT_UPLOAD_STATUS.format(c = upload.status_code, r = upload.reason)
                    )

        return upload.json()[ID]

    def __submit(self, course_id, assignment_id, submission = {}, submitted_at = None,
            msg = None):
        if submitted_at is not None:
            submission[SUB_SUBMITTED_AT] = submitted_at

        if msg is not None:
            submission[SUB_COMMENT] = msg

        return self.__post({
            COURSES: course_id,
            ASSIGNMENTS: assignment_id,
            SUBMISSIONS: EMPTY
            }, submission)


    def _create_url(self, components):
        if self._api_url is None:
            raise ValueError(API_SETUP_PROBLEM)

        url = self._api_url

        for object, id in components.items():

            if id:
                url += f"/{object}/{id}"
            else:
                url += f"/{object}"

        return url

    def _check_response(self, response, expected = requests.codes.ok):
        if response.status_code != expected:
            raise ValueError(
                    REQUEST_FAILED.format(code=response.status_code, reason=response.reason)
                    )
