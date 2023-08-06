# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2018-2020 Andrew Rechnitzer
# Copyright (C) 2019-2021 Colin B. Macdonald
# Copyright (C) 2021 Peter Lee

from io import BytesIO
import logging
import ssl
import threading

import urllib3
import requests
from requests_toolbelt import MultipartDecoder

from plom import __version__, Plom_API_Version, Default_Port
from plom.plom_exceptions import PlomBenignException, PlomSeriousException
from plom.plom_exceptions import (
    PlomAuthenticationException,
    PlomAPIException,
    PlomExistingLoginException,
    PlomTaskChangedError,
    PlomTaskDeletedError,
)

log = logging.getLogger("messenger")
# requests_log = logging.getLogger("urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

# If we use unverified ssl certificates we get lots of warnings,
# so put in this to hide them.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BaseMessenger:
    """Basic communication with a Plom Server.

    Handles authentication and other common tasks; subclasses can add
    other features.
    """

    def __init__(self, s=None, port=Default_Port):
        sslContext = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
        sslContext.check_hostname = False
        # Server defaults
        self.session = None
        self.user = None
        self.token = None
        if s:
            server = s
        else:
            server = "127.0.0.1"
        self.server = "{}:{}".format(server, port)
        self.SRmutex = threading.Lock()
        # base = "https://{}:{}/".format(s, mp)

    @classmethod
    def clone(cls, m):
        """Clone an existing messenger, keeps token.

        In particular, we have our own mutex.
        """
        log.debug("cloning a messeger, but building new session...")
        x = cls(s=m.server.split(":")[0], port=m.server.split(":")[1])
        x.start()
        log.debug("copying user/token into cloned messenger")
        x.user = m.user
        x.token = m.token
        return x

    def whoami(self):
        return self.user

    def start(self):
        """Start the messenger session"""
        if self.session:
            log.debug("already have an requests-session")
        else:
            log.debug("starting a new requests-session")
            self.session = requests.Session()
            # TODO: not clear retries help: e.g., requests will not redo PUTs.
            # More likely, just delays inevitable failures.
            self.session.mount("https://", requests.adapters.HTTPAdapter(max_retries=3))
        try:
            response = self.session.get(
                "https://{}/Version".format(self.server),
                verify=False,
            )
            response.raise_for_status()
        except requests.ConnectionError as err:
            raise PlomBenignException(
                "Cannot connect to server. Please check server details."
            ) from None
        except requests.exceptions.InvalidURL as err:
            raise PlomBenignException(
                "The URL format was invalid. Please try again."
            ) from None
        r = response.text
        return r

    def stop(self):
        """Stop the messenger"""
        if self.session:
            log.debug("stopping requests-session")
            self.session.close()
            self.session = None

    def isStarted(self):
        return bool(self.session)

    # ------------------------
    # ------------------------
    # Authentication stuff

    def requestAndSaveToken(self, user, pw):
        """Get a authorisation token from the server.

        The token is then used to authenticate future transactions with the server.

        raises:
            PlomAPIException: a mismatch between server/client versions.
            PlomExistingLoginException: user already has a token:
                currently, we do not support getting another one.
            PlomAuthenticationException: wrong password, account
                disabled, etc: check contents for details.
            PlomSeriousException: something else unexpected such as a
                network failure.
        """
        self.SRmutex.acquire()
        try:
            response = self.session.put(
                "https://{}/users/{}".format(self.server, user),
                json={
                    "user": user,
                    "pw": pw,
                    "api": Plom_API_Version,
                    "client_ver": __version__,
                },
                verify=False,
                timeout=5,
            )
            # throw errors when response code != 200.
            response.raise_for_status()
            self.token = response.json()
            self.user = user
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException(response.json()) from None
            elif response.status_code == 400:
                raise PlomAPIException(response.json()) from None
            elif response.status_code == 409:
                raise PlomExistingLoginException(response.json()) from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        except requests.ConnectionError as err:
            raise PlomSeriousException(
                "Cannot connect to server\n {}\n Please check details before trying again.".format(
                    self.server
                )
            ) from None
        finally:
            self.SRmutex.release()

    def clearAuthorisation(self, user, pw):
        self.SRmutex.acquire()
        try:
            response = self.session.delete(
                "https://{}/authorisation".format(self.server),
                json={"user": user, "password": pw},
                verify=False,
            )
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        finally:
            self.SRmutex.release()

    def closeUser(self):
        """User self-indicates they are logging out, surrender token and tasks.

        Raises:
            PlomAuthenticationException: Ironically, the user must be
                logged in to call this.  A second call will raise this.
            PlomSeriousException: other problems such as trying to close
                another user, other than yourself.
        """
        self.SRmutex.acquire()
        try:
            response = self.session.delete(
                "https://{}/users/{}".format(self.server, self.user),
                json={"user": self.user, "token": self.token},
                verify=False,
            )
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        finally:
            self.SRmutex.release()

        return True

    # ----------------------
    # ----------------------
    # Test information

    def getInfoShortName(self):
        self.SRmutex.acquire()
        try:
            response = self.session.get(
                "https://{}/info/shortName".format(self.server), verify=False
            )
            response.raise_for_status()
            shortName = response.text
        except requests.HTTPError as e:
            if response.status_code == 404:
                raise PlomSeriousException(
                    "Server could not find the spec - this should not happen!"
                ) from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        finally:
            self.SRmutex.release()

        return shortName

    def get_spec(self):
        """Get the specification of the exam from the server.

        Returns:
            dict: the server's spec file, as in :func:`plom.SpecVerifier`.
        """
        self.SRmutex.acquire()
        try:
            response = self.session.get(
                "https://{}/info/spec".format(self.server),
                verify=False,
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if response.status_code == 404:
                raise PlomSeriousException("Server could not find the spec") from None
            else:
                raise PlomSeriousException("Some other sort of error {}".format(e))
        finally:
            self.SRmutex.release()

    def IDrequestClasslist(self):
        """Ask server for the classlist.

        Returns:
            list: list of dict, each with at least the keys
                `id` and `studentName` and possibly others.
                Corresponding values are both strings.

        Raises:
            PlomAuthenticationException: login troubles.
            PlomBenignException: server has no classlist.
            PlomSeriousException: all other failures.
        """
        self.SRmutex.acquire()
        try:
            response = self.session.get(
                "https://{}/ID/classlist".format(self.server),
                json={"user": self.user, "token": self.token},
                verify=False,
            )
            # throw errors when response code != 200.
            response.raise_for_status()
            # you can assign to the encoding to override the autodetection
            # TODO: define API such that classlist must be utf-8?
            # print(response.encoding)
            # response.encoding = 'utf-8'
            # classlist = StringIO(response.text)
            classlist = response.json()
            return classlist
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            elif response.status_code == 404:
                raise PlomBenignException("Server cannot find the class list") from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        finally:
            self.SRmutex.release()

    def McreateRubric(self, new_rubric):
        """Ask server to make a new rubric and get key back.

        Args:
            new_rubric (dict): the new rubric info as dict.

        Raises:
            PlomAuthenticationException: Authentication error.
            PlomSeriousException: Other error types, possible needs fix or debugging.

        Returns:
            list: A list of:
                [False] If operation was unsuccessful.
                [True, updated_commments_list] including the new comments.
        """
        self.SRmutex.acquire()
        try:
            response = self.session.put(
                "https://{}/MK/rubric".format(self.server),
                json={
                    "user": self.user,
                    "token": self.token,
                    "rubric": new_rubric,
                },
                verify=False,
            )
            response.raise_for_status()

            new_key = response.json()
            messenger_response = [True, new_key]

        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            elif response.status_code == 406:
                raise PlomSeriousException("Rubric sent was incomplete.") from None
            else:
                raise PlomSeriousException(
                    "Error of type {} when creating new rubric".format(e)
                ) from None
            messenger_response = [False]

        finally:
            self.SRmutex.release()
        return messenger_response

    def MgetRubrics(self):
        """Retrieve list of all rubrics from server.

        Raises:
            PlomAuthenticationException: Authentication error.
            PlomSeriousException: any other unexpected error.

        Returns:
            list: list of dicts, possibly an empty list if server has no
                rubrics.
        """
        self.SRmutex.acquire()
        try:
            response = self.session.get(
                "https://{}/MK/rubric".format(self.server),
                json={
                    "user": self.user,
                    "token": self.token,
                },
                verify=False,
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            else:
                raise PlomSeriousException(
                    "Error of type {} getting rubric list".format(e)
                ) from None
        finally:
            self.SRmutex.release()

    def MgetRubricsByQuestion(self, question_number):
        """Retrieve list of all rubrics from server for given question.

        Args:
            question_number (int)

        Raises:
            PlomAuthenticationException: Authentication error.
            PlomSeriousException: Other error types, possible needs fix or debugging.

        Returns:
            list: list of dicts, possibly an empty list if server has no
                rubrics for this question.
        """
        self.SRmutex.acquire()
        try:
            response = self.session.get(
                "https://{}/MK/rubric/{}".format(self.server, question_number),
                json={
                    "user": self.user,
                    "token": self.token,
                },
                verify=False,
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            else:
                raise PlomSeriousException(
                    "Error of type {} getting rubric list".format(e)
                ) from None
        finally:
            self.SRmutex.release()

    def MmodifyRubric(self, key, new_rubric):
        """Ask server to modify a rubric and get key back.

        Args:
            rubric (dict): the modified rubric info as dict.

        Raises:
            PlomAuthenticationException: Authentication error.
            PlomSeriousException: Other error types, possible needs fix or debugging.

        Returns:
            list: A list of:
                [False] If operation was unsuccessful.
                [True, updated_commments_list] including the new comments.
        """
        self.SRmutex.acquire()
        try:
            response = self.session.patch(
                "https://{}/MK/rubric/{}".format(self.server, key),
                json={
                    "user": self.user,
                    "token": self.token,
                    "rubric": new_rubric,
                },
                verify=False,
            )
            response.raise_for_status()

            new_key = response.json()
            messenger_response = [True, new_key]

        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            elif response.status_code == 400:
                raise PlomSeriousException("Key mismatch in request.") from None
            elif response.status_code == 406:
                raise PlomSeriousException("Rubric sent was incomplete.") from None
            elif response.status_code == 409:
                raise PlomSeriousException("No rubric with that key found.") from None
            else:
                raise PlomSeriousException(
                    "Error of type {} when creating new rubric".format(e)
                ) from None
            messenger_response = [False]

        finally:
            self.SRmutex.release()
        return messenger_response

    def request_ID_images(self, code):
        self.SRmutex.acquire()
        try:
            response = self.session.get(
                "https://{}/ID/images/{}".format(self.server, code),
                json={"user": self.user, "token": self.token},
                verify=False,
            )
            response.raise_for_status()
            if response.status_code == 204:
                return []  # 204 is empty list
            return [
                BytesIO(img.content).getvalue()
                for img in MultipartDecoder.from_response(response).parts
            ]
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            elif response.status_code == 404:
                raise PlomSeriousException(
                    "Cannot find image file for {}.".format(code)
                ) from None
            elif response.status_code == 410:
                raise PlomBenignException(
                    "That ID group of {} has not been scanned.".format(code)
                ) from None
            elif response.status_code == 409:
                raise PlomSeriousException(
                    "Another user has the image for {}. This should not happen".format(
                        code
                    )
                ) from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        finally:
            self.SRmutex.release()

    def request_donotmark_images(self, papernum):
        """Get the various Do Not Mark images for a paper."""
        self.SRmutex.acquire()
        try:
            response = self.session.get(
                f"https://{self.server}/ID/donotmark_images/{papernum}",
                json={"user": self.user, "token": self.token},
                verify=False,
            )
            response.raise_for_status()
            if response.status_code == 204:
                return []  # 204 is empty list
            return [
                BytesIO(img.content).getvalue()
                for img in MultipartDecoder.from_response(response).parts
            ]
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            elif response.status_code == 404:
                raise PlomSeriousException(
                    f"Cannot find DNW image files for {papernum}."
                ) from None
            elif response.status_code == 410:
                raise PlomBenignException(
                    f"The DNM group of {papernum} has not been scanned."
                ) from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        finally:
            self.SRmutex.release()

    def get_annotations(self, num, question, edition=None, integrity=None):
        """Download the latest annotations (or a particular set of annotations).

        Args:
            num (int): the paper number.
            question (int): the question number.
            edition (int/None): which annotation set or None for latest.
            integrity (str/None): a checksum to ensure the server hasn't
                changed under us.  Can be omitted if not relevant.

        Returns:
            dict: contents of the plom file.

        Raises:
            PlomAuthenticationException
            PlomTaskChangedError
            PlomTaskDeletedError
            PlomSeriousException
        """
        if edition is None:
            url = f"https://{self.server}/annotations/{num}/{question}"
        else:
            url = f"https://{self.server}/annotations/{num}/{question}/{edition}"
        if integrity is None:
            integrity = ""
        self.SRmutex.acquire()
        try:
            response = self.session.get(
                url,
                json={
                    "user": self.user,
                    "token": self.token,
                    "integrity": integrity,
                },
                verify=False,
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            elif response.status_code == 404:
                raise PlomSeriousException(
                    "Cannot find image file for {}.".format(num)
                ) from None
            elif response.status_code == 406:
                raise PlomTaskChangedError(
                    "Task {} has been changed by manager.".format(num)
                ) from None
            elif response.status_code == 410:
                raise PlomTaskDeletedError(
                    "Task {} has been deleted by manager.".format(num)
                ) from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        finally:
            self.SRmutex.release()

    def get_annotations_image(self, num, question, edition=None):
        """Download image of the latest annotations (or a particular set of annotations).

        Args:
            num (int): the paper number.
            question (int): the question number.
            edition (int/None): which annotation set or None for latest.

        Returns:
            dict: contents of the plom file.

        Raises:
            PlomAuthenticationException
            PlomTaskChangedError: TODO: add this back again, with integriy_check??
            PlomTaskDeletedError
            PlomSeriousException
        """
        if edition is None:
            url = f"https://{self.server}/annotations_image/{num}/{question}"
        else:
            url = f"https://{self.server}/annotations_image/{num}/{question}/{edition}"
        self.SRmutex.acquire()
        try:
            response = self.session.get(
                url,
                json={
                    "user": self.user,
                    "token": self.token,
                },
                verify=False,
            )
            response.raise_for_status()
            return BytesIO(response.content).getvalue()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise PlomAuthenticationException() from None
            elif response.status_code == 404:
                raise PlomSeriousException(
                    "Cannot find image file for {}.".format(num)
                ) from None
            elif response.status_code == 406:
                raise PlomTaskChangedError(
                    "Task {} has been changed by manager.".format(num)
                ) from None
            elif response.status_code == 410:
                raise PlomTaskDeletedError(
                    "Task {} has been deleted by manager.".format(num)
                ) from None
            else:
                raise PlomSeriousException(
                    "Some other sort of error {}".format(e)
                ) from None
        finally:
            self.SRmutex.release()
