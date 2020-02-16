from __future__ import annotations

import os
import codepost

# ----------------------------------------------------------------------

class CPComment:

    def __init__(self, comment):
        self._comment = comment
        comment.retrieve(id=comment.id)
        self._rubricCommentID = comment.rubricComment
        if comment.pointDelta is None:
            self._pointDelta = 0.0
        else:
            self._pointDelta = comment.pointDelta

    def text(self):
        return self._comment.text.rstrip()

    def startLine(self):
        return self._comment.startLine

    def endLine(self):
        return self._comment.endLine

    def pointDelta(self):
        return self._pointDelta

    def rubricCommentID(self):
        return self._rubricCommentID

    def __lt__(self, other: CPComment):
        return self._comment.startLine < other._comment.startLine

    def __str__(self):
        if self._pointDelta != 0.0:
            return f"{self.text()} ({(-self._comment.pointDelta):0.1f})"
        else:
            return self.text()

class CPRubricComment:

    def __init__(self, comment, category: CPRubricCategory):
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

    def category(self):
        return self._category

    def text(self):
        return self._comment.text.rstrip()

    def pointDelta(self):
        return self._pointDelta

    def __str__(self):
        if self._pointDelta != 0.0:
            return f"{self.text()} ({(-self._comment.pointDelta):0.1f})"
        else:
            return self.text()

class CPRubricCategory:

    def __init__(self, category):
        self._category = category
        category.retrieve(id=category.id)
        self._name = category.name
        self._pointLimit = category.pointLimit
        self._sortKey = category.sortKey
        self._comments = [CPRubricComment(c, self) for c in category.rubricComments]

    def name(self):
        return self._name

    def comments(self):
        return self._comments

    def pointLimit(self):
        return self._pointLimit

    def __lt__(self, other: CPRubricCategory):
        return self._sortKey < other._sortKey

    def __str__(self):
        return self._name

class CPFile:

    def __init__(self, file):
        self._file = file
        file.retrieve(id=file.id)
        self._comments = None
        self._code = None

    def codeLines(self, startLine, endLine):
        if self._code is None:
            self._code = self._file.code.split("\n")
        return "\n".join(self._code[startLine-1:endLine])

    def fileID(self):
        return self._file.id

    def delete(self):
        codepost.file.delete(self.fileID())

    def filename(self):
        return self._file.name

    def comments(self):
        if self._comments is None:
            self._comments = [CPComment(c) for c in self._file.comments]
        # sort by start line
        self._comments.sort()
        return self._comments

    def formattedComment(self, comment: CPComment, rubricComment: CPRubricComment = None) -> str:
        lines = []
        startLine = comment.startLine()
        endLine = comment.endLine()
        lines.append(f"{self.filename()} lines: {startLine}-{endLine}")
        lines.append(self.codeLines(startLine, endLine))
        if rubricComment is not None:
            line = f"\n{rubricComment}\n{comment}".rstrip()
            lines.append(f"{line}\n\n")
        else:
            lines.append(f"\n{comment}\n\n")
        return "\n".join(lines)

    # def formattedComments(self) -> str:
    #     lines = []
    #     filename = self.filename()
    #     for c in self.comments():
    #         startLine = c.startLine()
    #         endLine = c.endLine()
    #         lines.append(f"{filename} lines: {startLine}-{endLine}")
    #         lines.append(self.codeLines(startLine, endLine))
    #         lines.append(f"\n{c.text()}\n")
    #         lines.append(50 * '-' + "\n")
    #     return "\n".join(lines)

    def firstComment(self) -> str:
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

    def uploadFile(self, filename, text, overwrite=False, renameTo=None):
        if renameTo is None:
            renameTo = filename

        if overwrite:
            existingFile = self.fileWithName(renameTo)
            if existingFile is not None:
                codepost.file.delete(existingFile.fileID())

        extension = renameTo.split('.')[-1]
        codepost.file.create(name=renameTo, code=text, extension=extension, submission=self._submission.id)

    def rubricCommentsByFile(self, fileNamesToProcess, assignment: CPAssignment) -> str:

        rubricCategories = assignment.rubricCategories()
        deductions = { "Other": 0.0 }

        allComments = []
        for fileName in fileNamesToProcess:
            f = self.fileWithName(fileName)
            if f is not None:
                fileComments = []
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

        return allComments


class CPAssignment:

    def __init__(self, assignment):
        self._assignment = assignment
        submissions = self._assignment.list_submissions()
        self._submissions = [CPSubmission(self._assignment, sub) for sub in submissions]
        self._studentToSubmissions = {}
        for sub in self._submissions:
            studentEmail = sub.firstStudent()
            self._studentToSubmissions[studentEmail] = sub
        self._categories = None
        self._rubricCommentIDs = None

    def submissions(self):
        return self._submissions

    def submissionForStudent(self, studentEmail):
        return self._studentToSubmissions.get(studentEmail, None)

    def makeSubmissionForStudent(self, studentEmail):
        submission = codepost.submission.create(assignment=self._assignment.id, students=[studentEmail])
        submission = CPSubmission(self._assignment, submission)
        self._studentToSubmissions[studentEmail] = submission
        return submission

    def rubricCategories(self) -> []:
        if self._categories is None:
            self._loadRubricCategories()
        return self._categories

    def _loadRubricCategories(self):
        categories = self._assignment.rubricCategories
        self._categories = [CPRubricCategory(c) for c in categories]
        self._categories.sort()

        self._rubricCommentIDs = {}
        for cat in self._categories:
            for comment in cat.comments():
                self._rubricCommentIDs[comment.ID()] = comment

    def categoryNamed(self, name):
        if self._categories is None:
            self.loadRubricCategories()

    def rubricCommentForComment(self, comment: CPComment) -> CPRubricComment:
        if self._categories is None:
            self._loadRubricCategories()
        return self._rubricCommentIDs.get(comment.rubricCommentID(), None)


class CPCourse:

    def __init__(self, course):
        self._course = course

    def makeAssignment(self, name: str) -> CPAssignment:
        assignment = self._course.assignments.by_name(name)
        if assignment is None:
            assignment = codepost.assignment.create(course=self._course.id, name=name, points=100)
        return CPAssignment(assignment)

    def assignment(self, name: str) -> CPAssignment:
        return CPAssignment(self._course.assignments.by_name(name))

class CP:
    config = None

    @staticmethod
    def init(apiKey=""):
        if apiKey == "":
            CP.config = codepost.read_config_file()
        else:
            codepost.configure_api_key(apiKey)

    @staticmethod
    def period():
        if CP.config is None:
            return None
        else:
            return CP.config.get("period")

    @staticmethod
    def course(name: str, period: str = None) -> CPCourse:
        if period is None:
            period = CP.period()
        try:
            c = codepost.course.list_available(name=name, period=period)[0]
            return CPCourse(c)
        except:
            raise ValueError(f"Unable to retrieve course: {name} in period {period}.")
