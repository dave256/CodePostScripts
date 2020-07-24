#!/usr/bin/env python3

# ----------------------------------------------------------------------
# cpAddRubric.py
# Dave Reed
# 06/16/2020
# ----------------------------------------------------------------------

from argparse import ArgumentParser
from CPAPI import *
from FileUtils import *

# ----------------------------------------------------------------------

def makeRubric(assignment: CPAssignment, rubricFilename: str):
    """
    add rubric to the assignment using the filename
    :param assignment: CPAssignment to add rubric to
    :param rubricFilename: filename containing rubric
    :return: None

rubric file should contain something like this    
75 Correctness
2 minor correctness issue
5 minor correctness issue
10 significant correctness issue
15 significant correctness issue
20 significant correctness issue
25 multiple significant issues with code
30 multiple significant issues with code
35 multiple significant issues with code
40 multiple significant issues with code
45 multiple significant issues with code
50 multiple significant issues with code
60 multiple significant issues with code
75 no code or numerous issues with code

15 Organization/Style
0 other style issue
2 other style issue
2 use descriptive variable names
5 use descriptive variable names
2 follow naming conventions (camelCase for variables/functions, CamelCase for classes)
2 spacing between sections of code and functions
2 extra unnecessary code
5 code not organized into functions/methods

10 Comments
1 needs comments
3 needs comments
5 needs comments
10 code has no comments
    """
    with open(rubricFilename) as infile:
        state = "category"
        categoryPosition = 0
        for line in infile:
            line = line.strip()
            if state == "category":
                if line != "":
                    spacePos = line.find(" ")
                    pointLimit = int(line[:spacePos])
                    name = line[spacePos+1:]
                    rubricCategory = assignment.categoryNamed(name)
                    if rubricCategory is None:
                        print(f"add category: {name}")
                        rubricCategory = assignment.addRubricCategory(name, pointLimit, categoryPosition)
                    categoryPosition += 1
                    commentPosition = 0
                    state = "comment"
            elif state == "comment":
                if line == "":
                    state = "category"
                else:
                    spacePos = line.find(" ")
                    pointDelta = int(line[:spacePos])
                    text = line[spacePos+1:]
                    if not rubricCategory.hasRubricComment(text):
                        print(f"add comment: {text}")
                        rubricComment = rubricCategory.addRubricComment(text, pointDelta, commentPosition)
                        commentPosition += 1

# ----------------------------------------------------------------------

def main():
    parser = ArgumentParser(description='add a rubric to a codepost.io assignment for a course')
    parser.add_argument('--course-prefix', dest='coursePrefix', default='CS',
                        help='''directory prefix for course names (i.e., if all your codepost.io course names and 
                        local directories start with CS such as CS160 then use the default
                        ''')
    parser.add_argument('-c', '--course-name', dest='course', default=None,
                        help='''name of course, if no name supplied, will try to find directory with coursePrefix in
                        the current working directory's parent directories
                        ''')
    parser.add_argument('-r', '--rubric-file', dest='rubricFile', default=None,
                        help='''name of file containing rubric''')

    parser.add_argument("assignment")
    parser.add_argument("rubricFilename")


    options = parser.parse_args()
    if options.course is None:
        course, _, _, _ = FileInfo.infoForFilePath(os.getcwd())
    else:
        course = options.course

    if options.assignment is None:
        assignment = input("enter assignment name: ")
    else:
        assignment = options.assignment[0]

    CP.init()
    c = CP.course(course)
    a = c.assignment(options.assignment)
    makeRubric(a, options.rubricFilename)

    print(f"add rubric from {options.rubricFilename} for {options.assignment} in {course}")

# ----------------------------------------------------------------------

if __name__ == '__main__':
    main()
