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
                        the current working directory's parent directories
                        ''')
    parser.add_argument('-a', '--assignment-name', dest='assignment', default=None,
                        help='''name of assignment, if no name supplied will try to find directory with coursePrefix
                        and use directory after it as the assignment name
                        ''')
    parser.add_argument('-g', '--grade-file', dest='gradeFilename', default='grade.txt',
                        help='''name of file to download comments into''')
    parser.add_argument('-r', '--rubric-file', dest='rubricFilename', default='1rubric.txt',
                        help='''name of file that has rubric comment''')
    parser.add_argument('--text-file', dest='commentFilename', default='comments.txt',
                        help='''name of file to download comments into''')
    parser.add_argument('-d', '--directory', dest='oneDirectory', default=None,
                        help='''just download files for the one specified student directory''')
    parser.add_argument('--all-source-files', dest='allSource', action='store_true',
                        help='''upload all files with .py, .cpp, .hpp, .h, .swift extension''')
    parser.add_argument("files", nargs='*', default=None,
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

    sourceExtensions = set((".py", ".cpp", ".hpp", ".swift", ".java", ".c", ".h", ".txt"))

    cwd = os.getcwd()
    if options.oneDirectory is not None:
        directories = [options.oneDirectory]
    else:
        directoryInfo = DirectoryInfo(cwd)
        directories = directoryInfo.directories()

    directories = [FileInfo.filenameForFilePath(d) for d in directories]

    for directory in sorted(directories):
        submission = cpAssignment.submissionForStudent(directory)
        if submission is not None:
            gradeFileInfo = FileInfo(cwd, directory, options.gradeFilename)
            gradeText = gradeFileInfo.contentsOf()
            # download rubric comments for files
            if options.allSource:
                filesToDownload = files[:]
                # get files in the student directory
                studentDirectory = DirectoryInfo(cwd, directory)
                studentFiles = studentDirectory.files()
                for f in studentFiles:
                    info = FileInfo(f)
                    if info.extension() in sourceExtensions:
                        filesToDownload.append(info.fileName())
            else:
                filesToDownload = files


            rubricText = submission.rubricCommentsByFile(filesToDownload, cpAssignment)

            # create string with rubric comment and any existing text in the grade file
            s = f"{rubricText}\n\n{gradeText}"
            gradeFileInfo.writeTo(s)

            rubricFileInfo = FileInfo(cwd, directory, options.rubricFilename)
            rubricFileInfo.writeTo(rubricText)
            score = rubricText.split("\n")[0].strip()
            print(f"{directory}: {score}")


# ----------------------------------------------------------------------

if __name__ == '__main__':
    main()
