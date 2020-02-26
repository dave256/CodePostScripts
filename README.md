# CodePostScripts

This repository contains classes and scripts for use with [https://codepost.io](https://codepost.io).

[https://codepost.io](https://codepost.io) is a fantastic website for adding comments to student code and grading them 
using rubric comments. These scripts use their API to upload student code and more importantly download your
comments so you have your own record of the comments you made for each student submission.

See their documentation at [https://docs.codepost.io/docs](https://docs.codepost.io/docs) for installing the Python
codepost module and creating your `codepost-config.yaml` file.

The CPAPI.py file contains some wrapper classes for the [https://codepost.io](https://codepost.io) API classes. These classes
provide convenient access to common operations and provide better code completion than the existing 
[https://codepost.io](https://codepost.io) classes.

The [https://codepost.io](https://codepost.io) site has a web interface for uploading files by dragging a directory containing
student submissions but I first run some scripts to test the students' code and include output. This leaves some extra
files in the student directory so I can easily rerun a test later if I make a change to a student's file. My scripts allow
upload of only the files I want to see and mark up. By default the `cpUploadFilesForAssignment.py` takes the contents of a file 
named `grade.txt` and uploads it as `1output.txt` so it is the first file visible when grading a student submission. The 
`cpUploadFilesForAssignment.py` takes command line arguments to use a file named differently than `grade.txt` or to not upload
this extra file. The following would create an assignment named `Lab3` for the current period (as specified in your
`codepost-config.yaml` file) in your `CS161` course and upload the files named `LList.py` and `test_LList.py` along with
uploading the contents of the `grade.txt` file as `1output.txt`. These script should be executed in the directory that contains
the student directories by their email address and each student directory contains the files for that student.

```
cpMakeAssignment.py -c CS161 Lab3
cpUploadFilesForAssignment.py -c CS161 -a Lab3 LList.py test_LList.py 
```

After adding comments on the [https://codepost.io](https://codepost.io) site using a rubric to grade each submission, execute
the following script in the directory containing each student directory:

```
cpDownloadRubricAndComments.py -c CS161 -a Lab3 LList.py test_LList.py
```

For each student, this downloads the comments in the specified files (in this case `LList.py` and `test_LList.py`) and will
insert the following at the beginning of the `grade.txt` file (so that the output of my grading scripts is below the
downloaded text).

1. the numeric grade from the rubric
2. the breakdown of points for each rubric category
3. for each file it shows the comments made on the codepost site. Each comment consists of the lines of code the comment 
refers to and the text you added for the comment. If it is a rubric comment, it also includes the text of the rubric comment.

Note both the `cpUploadFilesForAssignment.py` and `cpDownloadRubricAndComments.py` optionally take a `-d` flag which allows 
you to just upload or download one student's files. This is useful for late submissions.

