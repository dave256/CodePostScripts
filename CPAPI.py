from __future__ import annotations
from typing import List, Optional

import codepost

# ----------------------------------------------------------------------

class CPComment:
    """class for accessing a codepost.io Comment object"""

    def __init__(self, comment):
        """
        :param comment: codepost.io comment
        """
        self._comment = comment
        comment.retrieve(id=comment.id)
        self._rubricCommentID = comment.rubricComment
        # have pointDelta default to zero if does not have one
        if comment.pointDelta is None:
            self._pointDelta = 0.0
        else:
            self._pointDelta = comment.pointDelta

    def text(self) -> str:
        """
        :return: text of the comment with trailing whitespace stripped
        """
        return self._comment.text.rstrip()

    def startLine(self) -> int:
        """
        :return: starting line number of the code that the comment is for
        """
        return self._comment.startLine

    def endLine(self) -> int:
        """
        :return: ending line number of the code that the comment is for
        """
        return self._comment.endLine

    def pointDelta(self) -> float:
        """
        :return: point delta for the comment
        """
        return self._pointDelta

    def rubricCommentID(self):
        """
        :return: the codepost.io id for the rubric comment this comment is associated with (may be None)
        """
        return self._rubricCommentID

    def __lt__(self, other: CPComment) -> bool:
        """
        comparision operator so we can sort comments by the line numbers they correspond to
        :param other:
        :return: True if self's starting line number is less than other's starting line number
        """
        return self._comment.startLine < other._comment.startLine

    def __str__(self) -> str:
        if self._pointDelta != 0.0:
            return f"{self.text()} ({(-self._comment.pointDelta):0.1f})"
        else:
            return self.text()

class CPRubricComment:
    """class for accessing codepost.io rubric comment"""

    def __init__(self, comment, category: CPRubricCategory):
        """
        :param comment: the codepost.io rubric comment
        :param category: the rubric category for this rubric comment
        """
        self._comment = comment
        self._category = category
        comment.retrieve(id=comment.id)
        self._text = comment.text
        if comment.pointDelta is None:
            self._pointDelta = 0.0
        else:
            self._pointDelta = comment.pointDelta

    def ID(self):
        return self._comment.id

    def category(self) -> CPRubricCategory:
        """
        :return: the rubric category for this comment
        """
        return self._category

    def text(self) -> str:
        """
        :return: text of the comment with trailing whitespace stripped
        """
        return self._comment.text.rstrip()

    def pointDelta(self) -> float:
        """
        :return: point delta for the comment
        """
        return self._pointDelta

    def __str__(self) -> str:
        if self._pointDelta != 0.0:
            return f"{self.text()} ({(-self._comment.pointDelta):0.1f})"
        else:
            return self.text()

class CPRubricCategory:

    def __init__(self, category):
        """
        :param category: codepost.io category object
        """
        self._category = category
        category.retrieve(id=category.id)
        self._name = category.name
        self._pointLimit = category.pointLimit
        self._sortKey = category.sortKey
        self._comments = [CPRubricComment(c, self) for c in category.rubricComments]

    def name(self) -> str:
        """
        :return: the name of the category
        """
        return self._name

    def comments(self) -> List[CPRubricComment]:
        """
        :return: the list of rubric comment objects for this category
        """
        return self._comments

    def pointLimit(self) -> float:
        """
        :return: the point limit for the category
        """
        return self._pointLimit

    def __lt__(self, other: CPRubricCategory) -> bool:
        """
        comparison operator for sorting rubric categories by the codepost.io sort key (which I believe is order they are listed)
        :param other: other rubric category to compare
        :return: True if self < other, False otherwise
        """
        return self._sortKey < other._sortKey

    def addRubricComment(self, text: str, pointDelta: int, sortKey: int) -> CPRubricComment:
        c = codepost.rubric_comment.create(category=self._category.id, text=text, pointDelta=pointDelta, sortKey=sortKey)
        return CPRubricComment(c, self)

    def hasRubricComment(self, text: str) -> bool:
        for comment in self._comments:
            if comment.text() == text:
                return True
        return False

    def __str__(self) -> str:
        return self._name

class CPFile:

    def __init__(self, file):
        """
        :param file: the codepost.io File object
        """
        self._file = file
        file.retrieve(id=file.id)
        self._comments = None
        self._code = None

    def codeLines(self, startLine, endLine) -> str:
        """
        :param startLine: starting line number
        :param endLine: ending line number
        :return: a string containing the lines of code from startLine to endLine
        """
        if self._code is None:
            self._code = self._file.code.split("\n")
        return "\n".join(self._code[startLine:endLine+1])

    def fileID(self):
        return self._file.id

    def delete(self) -> None:
        """delete the file from codepost.io"""
        codepost.file.delete(self.fileID())

    def filename(self) -> str:
        """
        :return: the name of the file
        """
        return self._file.name

    def comments(self) -> List[CPComment]:
        """
        :return: list of comments for the file sorted by starting line number
        """
        if self._comments is None:
            self._comments = [CPComment(c) for c in self._file.comments]
        # sort by start line
        self._comments.sort()
        return self._comments

    def formattedComment(self, comment: CPComment, rubricComment: CPRubricComment = None) -> str:
        """
        :param comment:
        :param rubricComment:
        :return: string containing the filename, lines of code, the rubricComment (if exists) and the comment
        """
        lines = []
        startLine = comment.startLine()
        endLine = comment.endLine()
        lines.append(f"{self.filename()} lines: {startLine+1}-{endLine+1}")
        lines.append(self.codeLines(startLine, endLine))
        if rubricComment is not None:
            line = f"\n{rubricComment}\n{comment}".rstrip()
            lines.append(f"{line}\n\n")
        else:
            lines.append(f"\n{comment}\n\n")
        return "\n".join(lines)

    def firstComment(self) -> str:
        """
        :return: the text of the first comment for the file
        """
        listOfComments = self.comments()
        if len(listOfComments) > 0:
            c = listOfComments[0]
            return f"{c.text()}\n"
        return ""

class CPSubmission:

    def __init__(self, assignment, submission):
        self._assignment = assignment
        self._submission = submission
        self._students = submission.students
        self._files = [CPFile(f) for f in submission.files]

    def firstStudent(self):
        return self._students[0]

    def files(self):
        return self._files

    def fileWithName(self, name):
        for f in self._files:
            filename = f.filename()
            if filename == name:
                return f
        return None

    def uploadFile(self, filename: str, text: str, overwrite: bool =False, renameTo=None) -> None:
        """
        upload file to codepost
        :param filename: name of file in codepost
        :param text: content of the file to upload
        :param overwrite: if True, overwrite the existing file
        :param renameTo: optionally rename the file
        :return: None
        """
        if renameTo is None:
            renameTo = filename

        # delete existing file if overwrite specified
        if overwrite:
            existingFile = self.fileWithName(renameTo)
            if existingFile is not None:
                codepost.file.delete(existingFile.fileID())

        # get file extension
        extension = renameTo.split('.')[-1]
        # upload to codepost
        codepost.file.create(name=renameTo, code=text, extension=extension, submission=self._submission.id)

    def rubricCommentsByFile(self, fileNamesToProcess: List[str], assignment: CPAssignment) -> str:
        """
        :param fileNamesToProcess: the files to get the comments for
        :param assignment: the assignment we are to get the comments for
        :return: grade, totals per category, and each comment for the files in the submission
        """
        rubricCategories = assignment.rubricCategories()
        deductions = { "Other": 0.0 }

        allComments = []
        for fileName in fileNamesToProcess:
            f = self.fileWithName(fileName)
            fileComments = []
            if f is not None:
                for comment in f.comments():
                    rubricComment = assignment.rubricCommentForComment(comment)
                    fileComments.append(f.formattedComment(comment, rubricComment))
                    if rubricComment is not None:
                        category = rubricComment.category()
                        deductions[category.name()] = deductions.get(category.name(), 0) + rubricComment.pointDelta()
                    else:
                        deductions["Other"] = deductions.get("Other", 0) + comment.pointDelta()

            if len(fileComments) > 0:
                sep = 50 * "-" + "\n"
                allComments.append(sep.join(fileComments))

        sep = 50 * "=" + "\n\n"
        allComments = sep.join(allComments)

        rubricLines = []
        totalPoints = 0.0

        # get totals for each category
        for cat in rubricCategories:
            name = cat.name()
            pointLimit = cat.pointLimit()
            points = deductions.get(name, 0)
            if name == "Deductions":
                if points != 0:
                    totalPoints -= points
                    rubricLines.append(f"{(-points):5.1f}         : Deductions")
            elif name == "Bonus":
                if points != 0:
                    totalPoints -= points
                    rubricLines.append(f"{abs(points):5.1f}         : Bonus")
            elif pointLimit is None:
                print(f"point limit is None {points}")
                totalPoints -= points
                rubricLines.append(f"{abs(points):5.1f}         : {name}")
            else:
                points = min(points, pointLimit)
                points = pointLimit - min(points, pointLimit)
                totalPoints += points
                rubricLines.append(f"{points:5.1f} / {pointLimit:5.1f} : {name}")

        otherPoints = deductions["Other"]
        if otherPoints != 0:
            totalPoints -= otherPoints
            rubricLines.append(f"{-otherPoints:5.1f}         : Other")

        rubricLines.insert(0, f"{totalPoints:0.1f}\n")
        rubricLines = "\n".join(rubricLines)

        sep = f"\n\nFeedback:\n\n{50 * '='}\n\n"

        return f"{rubricLines}{sep}{allComments}"

class CPAssignment:

    def __init__(self, assignment):
        """
        :param assignment: codepost.io assignment object
        """
        self._assignment = assignment
        submissions = self._assignment.list_submissions()
        self._submissions = [CPSubmission(self._assignment, sub) for sub in submissions]
        self._studentToSubmissions = {}
        for sub in self._submissions:
            studentEmail = sub.firstStudent()
            self._studentToSubmissions[studentEmail] = sub
        self._categories = None
        self._rubricCommentIDs = None

    def submissions(self) -> List[CPSubmission]:
        """
        :return: list of submissions for the assignment
        """
        return self._submissions

    def submissionForStudent(self, studentEmail) -> Optional[CPSubmission]:
        """
        :param studentEmail: email address of submission for student
        :return: CPSubmission for the student or None if submission for studentEmail does not exist
        """
        return self._studentToSubmissions.get(studentEmail, None)

    def makeSubmissionForStudent(self, studentEmail) -> CPSubmission:
        """
        create submission for student
        :param studentEmail: email address of student to make submission for
        :return: CPSubmission for the student
        """
        submission = codepost.submission.create(assignment=self._assignment.id, students=[studentEmail])
        submission = CPSubmission(self._assignment, submission)
        self._studentToSubmissions[studentEmail] = submission
        return submission

    def rubricCategories(self) -> List[CPRubricCategory]:
        """
        :return: list of the rubric categories for the assignment
        """
        if self._categories is None:
            self._loadRubricCategories()
        return self._categories

    def _loadRubricCategories(self) -> None:
        """
        load the rubric categories for the assignment
        :return: None
        """
        categories = self._assignment.rubricCategories
        self._categories = [CPRubricCategory(c) for c in categories]
        self._categories.sort()

        self._rubricCommentIDs = {}
        for cat in self._categories:
            for comment in cat.comments():
                self._rubricCommentIDs[comment.ID()] = comment

    def categoryNamed(self, name: str) -> Optional[CPRubricCategory]:
        """
        rubric category with the specified name for the assignment
        :param name: name of category to find
        :return: rubric category with the specified name or None if it does not exist
        """
        if self._categories is None:
            self._loadRubricCategories()
        for cat in self._categories:
            if cat.name() == name:
                return cat
        return None

    def rubricCommentForComment(self, comment: CPComment) -> Optional[CPRubricComment]:
        """
        :param comment: comment for which to find the rubric comment
        :return: the rubric comment for the comment or None if the comment does not have a rubric comment
        """
        if self._categories is None:
            self._loadRubricCategories()
        return self._rubricCommentIDs.get(comment.rubricCommentID(), None)

    def addRubricCategory(self, name: str, pointLimit: int, sortKey: int, helpText: str = "") -> CPRubricCategory:
        rc = codepost.rubric_category.create(name=name, assignment=self._assignment.id, pointLimit=pointLimit, sortKey=sortKey, helpText=helpText)
        return CPRubricCategory(rc)

class CPCourse:

    def __init__(self, course):
        """
        :param course: the codepost.io course object
        """
        self._course = course

    def makeAssignment(self, name: str, points: int = 100) -> CPAssignment:
        """
        create an assignment with the specified name unless it already exists
        :param name: name of the assignment to make
        :param points: number of points for the assignment
        :return: the Assignment object that existed or is created
        """
        assignment = self._course.assignments.by_name(name)
        if assignment is None:
            assignment = codepost.assignment.create(course=self._course.id, name=name, points = points,
                                                    forcedRubricMode = True, collaborativeRubricMode = True,
                                                    showFrequentlyUsedRubricComments = True, commentFeedback = False,
                                                    liveFeedbackMode = False)
        return CPAssignment(assignment)

    def assignment(self, name: str) -> CPAssignment:
        """
        :param name: name of the assignment
        :return: the assignment with specified name
        """
        return CPAssignment(self._course.assignments.by_name(name))

class CP:
    """class to initialize connection to codepost.io"""

    config = None

    @staticmethod
    def init(apiKey:str = ""):
        """
        :param apiKey: codepost.io api key or if empty string, uses ~/.codepost-config.yaml
        """
        if apiKey == "":
            CP.config = codepost.read_config_file()
        else:
            codepost.configure_api_key(apiKey)

    @staticmethod
    def period() -> Optional[str]:
        """
        :return: the period in the codepost.io configuration or None if no period in configuration
        """
        if CP.config is None:
            return None
        else:
            return CP.config.get("period")

    @staticmethod
    def course(name: str, period: str = None) -> CPCourse:
        """
        :param name: name of course to get
        :param period: period to get the course in
        :return: the course with the specified name and period
        """
        if period is None:
            period = CP.period()
        try:
            c = codepost.course.list_available(name=name, period=period)[0]
            return CPCourse(c)
        except:
            raise ValueError(f"Unable to retrieve course: {name} in period {period}.")
