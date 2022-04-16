#!/usr/bin/env python3

# ----------------------------------------------------------------------
# cpDownloadRubricAndComments.py
# Dave Reed
# 02/15/2020
# ----------------------------------------------------------------------


from argparse import ArgumentParser
from CPAPI import *
from FileUtils import *

# ----------------------------------------------------------------------

def main():
    parser = ArgumentParser(description='download codepost.io submitted files')
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
    parser.add_argument('-d', '--directory', dest='oneDirectory', default=None,
                        help='''just download files for the one specified student email''')


    options = parser.parse_args()
    if options.course is None:
        course, _, _, _ = FileInfo.infoForFilePath(os.getcwd())
    else:
        course = options.course

    if options.assignment is None:
        _, assignment, _, _ = FileInfo.infoForFilePath(os.getcwd())
    else:
        assignment = options.assignment

    CP.init()
    cpCourse = CP.course(course)
    cpAssignment = cpCourse.assignment(assignment)

    print(course, assignment)

    cwd = os.getcwd()
    submissions = cpAssignment.submissions()

    if options.oneDirectory is not None:
        directories = [options.oneDirectory]
    else:
        directories = [s.firstStudent() for s in submissions]


    directories = [FileInfo.filenameForFilePath(d) for d in directories]

    for directory in sorted(directories):
        dirPath = FileInfo(cwd, directory)
        if not dirPath.exists():
            os.mkdir(dirPath.filePath())
        submission = cpAssignment.submissionForStudent(directory)
        if submission is not None:
            files = submission.files()
            print(directory)
            for f in files:
                filename = f.filename()
                contents = f.contents()
                fullPath = FileInfo(cwd, directory, filename)
                fullPath.writeTo(contents)
                print(filename)
            print()

# ----------------------------------------------------------------------

if __name__ == '__main__':
    main()
