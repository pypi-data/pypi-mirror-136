# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2019-2021 Andrew Rechnitzer
# Copyright (C) 2020-2021 Colin B. Macdonald
# Copyright (C) 2020 Vala Vakilian

from datetime import datetime
import hashlib
import imghdr
from io import BytesIO
import json
import os
import logging

from plom.textools import texFragmentToPNG


log = logging.getLogger("server")


def MgetAllMax(self):
    """Get the maximum mark for each question in the exam.

    Returns:
        dict: A dictionary of the form {key: question_number, value: question_max_grade}
            for the exam questions.
    """

    max_grades = {}
    for q_number in range(1, self.testSpec["numberOfQuestions"] + 1):
        max_grades[q_number] = self.testSpec["question"][str(q_number)]["mark"]
    return max_grades


def MprogressCount(self, question_number, version_number):
    """Send back the marking progress count for question.

    Args:
        question_number (int): Question number.
        version_number (int): Version number.

    Returns:
        list: A list of two integers indicating the number of questions graded
            and the total number of assigned question to be graded of this question number
            and question version.
    """

    version_number = int(version_number)
    question_number = int(question_number)
    return [
        self.DB.McountMarked(question_number, version_number),
        self.DB.McountAll(question_number, version_number),
    ]


def MgetDoneTasks(self, username, question_number, version_number):
    """Respond with a list of the graded tasks.

    Args:
        username (str): Username string.
        question_number (int): Question number.
        version_number (int): Version number.

    Returns:
        list: Respond with a list of done tasks, each list includes
            [question_code string, maximum_mark, question_grade, question_tag string].
    """

    version_number = int(version_number)
    question_number = int(question_number)
    return self.DB.MgetDoneTasks(username, question_number, version_number)


def MgetNextTask(self, question_number, version_number):
    """Retrieve the next unmarked paper from the database.

    Args:
        question_number (int): Next question's question number.
        version_number (int): Next question's version number.

    Returns:
        list: Respond with a list with either value False or the value
            of True with the question code string for next task.
    """

    give = self.DB.MgetNextTask(question_number, version_number)
    if give is None:
        return [False]
    else:
        return [True, give]


def MlatexFragment(self, latex_fragment):
    """Respond with image data for a rendered latex of a text fragment.

    Args:
        latex_fragment (str): The string to be rendered.

    Returns:
        tuple: `(True, imgdata)`, or `(False, error_message)`.
    """
    return texFragmentToPNG(latex_fragment)


def MclaimThisTask(self, username, task_code):
    """Assign the specified paper to this user and return the task information.

    Args:
        username (str): User who requests the paper.
        task_code (str): Code string for the claimed task.

    Returns:
        list: A list which either only has a False value included or
            [True, `question_tag`, `integrity_check`, `list_of_image_md5s` `image_file1`, `image_file2`,...]
    """

    return self.DB.MgiveTaskToClient(username, task_code)


def MdidNotFinish(self, username, task_code):
    """Inform database that a user did not finish a task.

    Args:
        username (str): Owner of the unfinished task.
        task_code (str): Code string for the unfinished task.
    """

    self.DB.MdidNotFinish(username, task_code)
    return


def MreturnMarkedTask(
    self,
    username,
    task_code,
    question_number,
    version_number,
    mark,
    annotated_image,
    plomdat,
    rubrics,
    time_spent_marking,
    tags,
    annotated_image_md5,
    integrity_check,
    image_md5s,
):
    """Save the marked paper's information to database and respond with grading progress.

    Args:
        username (str): User who marked the paper.
        task_code (str): Code string for the task.
        question_number (int): Marked queston number.
        version_number (int): Marked question version number.
        mark (int): Question mark.
        annotated_image (bytearray): Marked image of question.
        plomdat (bytearray): Plom data file used for saving marking information in
            editable format.   TODO: should be json?
        rubrics (list[str]): Return the list of rubric IDs used
        time_spent_marking (int): Seconds spent marking the paper.
        tags (str): Tag assigned to the paper.
        annotated_image_md5 (str): MD5 hash of the annotated image.
        integrity_check (str): the integrity_check string for this task
        image_md5s (list[str]): list of image md5sums used.


    Returns:
        list: Respond with a list which includes:
            [False, Error message of either mismatching codes or database owning the task.]
            [True, number of graded tasks, total number of tasks.]
    """
    annotated_filename = "markedQuestions/G{}.png".format(task_code[1:])
    plom_filename = "markedQuestions/plomFiles/G{}.plom".format(task_code[1:])

    # do sanity checks on incoming annotation image file
    # Check the annotated_image is valid png - just check header presently
    imgtype = imghdr.what(annotated_filename, h=annotated_image)
    if imgtype != "png":
        errstr = f'Malformed annotated image file: expected png got "imgtype"'
        log.error(errstr)
        return [False, errstr]

    # Also check the md5sum matches
    md5 = hashlib.md5(annotated_image).hexdigest()
    if md5 != annotated_image_md5:
        errstr = f"Checksum mismatch: annotated image data has {md5} but client said {annotated_image_md5}"
        log.error(errstr)
        return [False, errstr]

    # Sanity check the plomfile
    # TODO: ok to read plomdat twice?  Maybe save the json later
    try:
        plom_data = json.load(BytesIO(plomdat))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        return [False, f"Invalid JSON in plom file data: {str(e)}"]
    if plom_data.get("currentMark") != mark:
        return [False, f"Mark mismatch: {mark} does not match plomfile content"]
    for x, y in zip(image_md5s, plom_data["base_images"]):
        if x != y["md5"]:
            errstr = (
                "data mismatch: base image md5s do not match plomfile: "
                + f'{image_md5s} versus {plom_data["base_images"]}'
            )
            return [False, errstr]

    # now update the database
    database_task_response = self.DB.MtakeTaskFromClient(
        task_code,
        username,
        mark,
        annotated_filename,
        plom_filename,
        rubrics,
        time_spent_marking,
        tags,
        annotated_image_md5,
        integrity_check,
        image_md5s,
    )

    if database_task_response[0] is False:
        return database_task_response

    # db successfully updated
    #  check if those files exist already - back up if so
    for filename in (annotated_filename, plom_filename):
        if os.path.isfile(filename):
            os.rename(
                filename,
                filename + ".rgd" + datetime.now().strftime("%d_%H-%M-%S"),
            )

    # now write in the files
    with open(annotated_filename, "wb") as file_header:
        file_header.write(annotated_image)
    with open(plom_filename, "wb") as file_header:
        file_header.write(plomdat)

    self.MrecordMark(username, mark, annotated_filename, time_spent_marking, tags)
    # return ack with current counts.
    return [
        True,
        (
            self.DB.McountMarked(question_number, version_number),
            self.DB.McountAll(question_number, version_number),
        ),
    ]


def MrecordMark(self, username, mark, annotated_filename, time_spent_marking, tags):
    """Saves the marked paper information as a backup, independent of the server

    Args:
        username (str): User who marked the paper.
        mark (int): Question mark.
        annotated_filename (str): Name of the annotated image file.
        time_spent_marking (int): Seconds spent marking the paper.
        tags (str): Tag assigned to the paper.
    """

    with open("{}.txt".format(annotated_filename), "w") as file_header:
        file_header.write(
            "{}\t{}\t{}\t{}\t{}\t{}".format(
                annotated_filename,
                mark,
                username,
                datetime.now().strftime("%Y-%m-%d,%H:%M"),
                time_spent_marking,
                tags,
            )
        )


# TODO: Have to figure this out.  Please needs documentation.
def MgetOriginalImages(self, task):
    return self.DB.MgetOriginalImages(task)


def MsetTag(self, username, task_code, tag):
    """Assign a tag string to a paper.

    Args:
        username (str): User who assigned tag to the paper.
        task_code (str): Code string for the task.
        tags (str): Tag assigned to the paper.

    Returns:
        bool: True or False indicating if tag was set in database successfully.
    """

    return self.DB.MsetTag(username, task_code, tag)


def MgetWholePaper(self, test_number, question_number):
    """Respond with all the images of the paper including the given question.

    Args:
        test_number (str): A string which has the test number in the format `0011`
            for example.
        question_number (str): Question number.

    Returns:
        list: A list including the following information:
            Boolean of whether we got the paper images.
            A list of lists including [`test_version`, `image_md5sum_list`, `does_page_belong_to_question`].
            Followed by a series of image paths for the pages of the paper.
    """
    return self.DB.MgetWholePaper(test_number, question_number)


def MreviewQuestion(self, test_number, question_number, version_number):
    """Save question results in database.

    Args:
        test_number (int): Reviewed test number.
        question_number (int): Review queston number.
        version_number (int): Marked question version number.

    Returns:
        list: Respond with a list with value of either True or False.
    """

    return self.DB.MreviewQuestion(test_number, question_number, version_number)


# TODO: Deprecated.
# TODO: Should be removed.
def MrevertTask(self, code):
    rval = self.DB.MrevertTask(code)
    # response is [False, "NST"] or [False, "NAC"] or [True]
    return rval
