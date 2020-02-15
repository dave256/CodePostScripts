from __future__ import annotations

import os
import codepost

# ----------------------------------------------------------------------

class CPComment:

    def __init__(self, comment):
        self._comment = comment
        comment.retrieve(id=comment.id)

    def comment(self):
        return self._comment.text

    def startLine(self):
        return self._comment.startLine

    def endLine(self):
        return self._comment.endLine

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
        return self._comments

    def formattedComments(self) -> str:
        lines = []
        filename = self.filename()
        for c in self.comments():
            startLine = c.startLine()
            endLine = c.endLine()
            lines.append(f"{filename} lines: {startLine}-{endLine}")
            lines.append(self.codeLines(startLine, endLine))
            lines.append(f"\n{c.comment()}\n")
        return "\n".join(lines)

    def firstComment(self) -> str:
        listOfComments = self.comments()
        if len(listOfComments) > 0:
            c = listOfComments[0]
            return f"{c.comment()}\n"
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

class CPAssignment:

    def __init__(self, assignment):
        self._assignment = assignment
        submissions = self._assignment.list_submissions()
        self._submissions = [CPSubmission(self._assignment, sub) for sub in submissions]
        self._studentToSubmissions = {}
        for sub in self._submissions:
            studentEmail = sub.firstStudent()
            self._studentToSubmissions[studentEmail] = sub

    def submissions(self):
        return self._submissions

    def submissionForStudent(self, studentEmail):
        return self._studentToSubmissions.get(studentEmail, None)

    def makeSubmissionForStudent(self, studentEmail):
        submission = codepost.submission.create(assignment=self._assignment.id, students=[studentEmail])
        submission = CPSubmission(self._assignment, submission)
        self._studentToSubmissions[studentEmail] = submission
        return submission

class CPCourse:

    def __init__(self, course):
        self._course = course

    def makeAssignment(self, name: str) -> CPAssignment:
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

def main():
    CP.init()

    c = CP.course("Test", "Spring 2020")
    a = c.assignment("LList")
    submissions = a.submissions()
    for sub in submissions:
        print(sub.firstStudent())
        files = sub.files()
        for f in files:
            filename = f.filename()
            if filename in ("LList.py", "grade.txt"):
                print(f.formattedComments())

if __name__ == "__main__":
    main()