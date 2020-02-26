#!/usr/bin/env python3

# ----------------------------------------------------------------------
# cpUploadFilesInDirectory.py
# Dave Reed
# 02/14/2020
# ----------------------------------------------------------------------

from argparse import ArgumentParser
from CPAPI import *
from FileUtils import *

# ----------------------------------------------------------------------

def main():
    parser = ArgumentParser(description='upload specified files to codepost.io')
    parser.add_argument('--course-prefix', dest='coursePrefix', default='CS',
                        help='''directory prefix for course names (i.e., if all your codepost.io course names and 
                        local directories start with CS such as CS160 then use the default
                        ''')
    parser.add_argument('-c', '--course-name', dest='course', default=None,
                        help='''name of course, if no name supplied, will try to find directory with coursePrefix in
                        the current working directory's parent directories
                        ''')
    parser.add_argument('-a', '--assignment-name', dest='assignment', default=None,
                        help='''name of assignment, if no name supplied will try to find directory with coursePrefix
                        and use directory after it as the assignment name
                        ''')
    parser.add_argument('--rename', dest='rename', action='store_true',
                        help='''rename files so arguments are: file1 renamedFile1 file2 renamedFile2''')
    parser.add_argument('--overwrite', dest='overwrite', action='store_true',
                        help='''overwrite files if already exist''')

    parser.add_argument("files", nargs='+', default=None)

    options = parser.parse_args()
    if options.course is None:
        course, _, _ = FileInfo.infoForFilePath(os.getcwd())
    else:
        course = options.course

    if options.assignment is None:
        _, assignment, _ = FileInfo.infoForFilePath(os.getcwd())
    else:
        assignment = options.assignment

    files = options.files

    CP.init()
    cpCourse = CP.course(course)
    cpAssignment = cpCourse.assignment(assignment)


    cwd = os.getcwd()
    _, _, studentEmail = FileInfo.infoForFilePath(cwd)
    if "@" not in studentEmail:
        print(f"{studentEmail} does not appear to be a student directory as no @ sign")
        return

    print(course, assignment, studentEmail)

    # get files in the student directory
    studentDirectory = DirectoryInfo(cwd)
    studentFiles = studentDirectory.files()

    # if we have some files
    if len(studentFiles) != 0:
        # get the submission
        submission = cpAssignment.submissionForStudent(studentEmail)
        if submission is None:
            submission = cpAssignment.makeSubmissionForStudent(studentEmail)

        if options.rename:
            files = tuple(zip(*(iter(files),) * 2))
            for f, renamedF in files:
                info = FileInfo(cwd, f)
                if info.filePath() in studentFiles:
                    text = info.contentsOf()
                    if text != "":
                        print(f"upload {info.filePath()} as {renamedF}")
                        submission.uploadFile(renamedF, text, overwrite=options.overwrite)
        else:
            for f in files:
                info = FileInfo(cwd, f)
                if info.filePath() in studentFiles:
                    text = info.contentsOf()
                    if text != "":
                        print(f"upload {info.filePath()}")
                        submission.uploadFile(f, text, overwrite=options.overwrite)
            print()


# ----------------------------------------------------------------------

if __name__ == '__main__':
    main()
