#!/usr/bin/env python3

# ----------------------------------------------------------------------
# cpUploadFilesForAssignment.py
# Dave Reed
# 02/14/2020
# ----------------------------------------------------------------------

from argparse import ArgumentParser
from CPAPI import *
from FileUtils import *

# ----------------------------------------------------------------------

def main():
    parser = ArgumentParser(description='upload specified files to a codepost.io assignment for all students')
    parser.add_argument('--course-prefix', dest='coursePrefix', default='CS',
                        help='''directory prefix for course names (i.e., if all your codepost.io course names and 
                        local directories start with CS such as CS160 then use the default
                        ''')
    parser.add_argument('-c', '--course-name', dest='course', default=None,
                        help='''name of course, if no name supplied, will try to find directory with coursePrefix in
                        the current working directory
                        ''')
    parser.add_argument('-a', '--assignment-name', dest='assignment', default=None,
                        help='''name of assignment, if no name supplied will try to find directory with coursePrefix
                        and use directory after it as the assignment name
                        ''')
    parser.add_argument('-d','--directory', dest='oneDirectory', default=None,
                        help='''just upload files for the one specified student directory''')
    parser.add_argument('-g', '--grade-file', dest='gradeFilename', default='grade.txt',
                        help='''name of file to upload contents for rubric''')
    parser.add_argument('-r', '--rubric', dest='addRubric', action='store_true',
                        help='''add 1rubric.txt''')

    parser.add_argument('--overwrite', dest='overwrite', action='store_true',
                        help='''overwrite files if already exist''')

    parser.add_argument("files", nargs='+', default=None)

    options = parser.parse_args()
    if options.course is None:
        course, _, _, _ = FileInfo.infoForFilePath(os.getcwd())
    else:
        course = options.course

    if options.assignment is None:
        _, assignment, _, _ = FileInfo.infoForFilePath(os.getcwd())
    else:
        assignment = options.assignment

    files = options.files

    CP.init()
    cpCourse = CP.course(course)
    cpAssignment = cpCourse.assignment(assignment)

    print(course, assignment)

    cwd = os.getcwd()
    if options.oneDirectory is not None:
        directories = [options.oneDirectory]
    else:
        directoryInfo = DirectoryInfo(cwd)
        directories = directoryInfo.directories()

    for directory in directories:
        # if it appears to be a directory with an email address name
        if "@" in directory:
            print(directory)
            # get the last part of path which is the email address
            studentEmail = FileInfo.filenameForFilePath(directory)

            # get files in the student directory
            studentDirectory = DirectoryInfo(cwd, directory)
            studentFiles = studentDirectory.files()

            # if we have some files
            if len(studentFiles) != 0:
                # get the submission
                submission = cpAssignment.submissionForStudent(studentEmail)
                if submission is None:
                    submission = cpAssignment.makeSubmissionForStudent(studentEmail)

                for f in files:
                    info = FileInfo(cwd, studentEmail, f)
                    if info.filePath() in studentFiles:
                        text = info.contentsOf()
                        if text != "":
                            print(f"upload {info.filePath()}")
                            submission.uploadFile(f, text, overwrite=options.overwrite)

                if options.addRubric:
                    gradeFile = FileInfo(cwd, studentEmail, options.gradeFilename)
                    text = gradeFile.contentsOf()
                    if text == "":
                        text = "file for adding rubric comment\n"
                    submission.uploadFile('1rubric.txt', text, overwrite=options.overwrite)
            print()

# ----------------------------------------------------------------------

if __name__ == '__main__':
    main()
