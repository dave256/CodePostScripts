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
    parser = ArgumentParser(description='download codepost.io comments into rubric grade file')
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
    parser.add_argument('-g', '--grade-file', dest='gradeFilename', default='grade.txt',
                        help='''name of file to download comments into''')
    parser.add_argument('-r', '--rubric-file', dest='rubricFilename', default='1rubric.txt',
                        help='''name of file that has rubric comment''')
    parser.add_argument('--comment-file', dest='commentFilename', default='comments.txt',
                        help='''name of file to download comments into''')
    parser.add_argument('-d', '--directory', dest='oneDirectory', default=None,
                        help='''just download files for the one specified student directory''')
    parser.add_argument("files", nargs='+', default=None,
                        help='''files we want to grab comments from''')

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

    directories = [FileInfo.filenameForFilePath(d) for d in directories]

    for directory in directories:
        print(directory)
        submission = cpAssignment.submissionForStudent(directory)
        if submission is not None:
            gradeFileInfo = FileInfo(cwd, directory, options.gradeFilename)
            gradeText = gradeFileInfo.contentsOf()
            rubricText = ""
            comments = []
            for name in files:
                f = submission.fileWithName(name)
                if f is not None:
                    if name != options.rubricFilename:
                        comments.append(f.formattedComments())

            f = submission.fileWithName(options.rubricFilename)
            if f is not None:
                rubricText = f.firstComment()

            comments = "\n".join(comments)
            s = f"{rubricText}\nComments:\n\n{comments}\n\n{gradeText}"
            gradeFileInfo.writeTo(s)

            commentFileInfo = FileInfo(cwd, directory, options.commentFilename)
            commentFileInfo.writeTo(comments)

            rubricFileInfo = FileInfo(cwd, directory, options.rubricFilename)
            rubricFileInfo.writeTo(rubricText)

# ----------------------------------------------------------------------

if __name__ == '__main__':
    main()
