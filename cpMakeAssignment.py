#!/usr/bin/env python3

# ----------------------------------------------------------------------
# cpMakeAssignment.py
# Dave Reed
# 02/14/2020
# ----------------------------------------------------------------------

from argparse import ArgumentParser
from CPAPI import *
from FileUtils import *

# ----------------------------------------------------------------------

def main():
    parser = ArgumentParser(description='make a codepost.io assignment for a course')
    parser.add_argument('--course-prefix', dest='coursePrefix', default='CS',
                        help='''directory prefix for course names (i.e., if all your codepost.io course names and 
                        local directories start with CS such as CS160 then use the default
                        ''')
    parser.add_argument('-c', '--course-name', dest='course', default=None,
                        help='''name of course, if no name supplied, will try to find directory with coursePrefix in
                        the current working directory
                        ''')
    parser.add_argument("assignment", nargs='*', default=None)

    options = parser.parse_args()
    if options.course is None:
        course, _, _, _ = FileInfo.infoForFilePath(os.getcwd())
    else:
        course = options.course

    if options.assignment == []:
        assignment = input("enter assignment name: ")
    else:
        assignment = options.assignment[0]

    print(f"make assignment {assignment} for {course}")
    CP.init()
    c = CP.course(course)
    c.makeAssignment(assignment)

# ----------------------------------------------------------------------

if __name__ == '__main__':
    main()
