#!/usr/bin/env python3

# ----------------------------------------------------------------------
# FileUtils.py
# Dave Reed
# 02/14/2020
# ----------------------------------------------------------------------

import os.path
import glob

# ----------------------------------------------------------------------

class DirectoryInfo:

    def __init__(self, dirPath, *args):
        self._dirPath = os.path.join(dirPath, *args)
        self._files = set()
        self._directories = set()
        self.updateFileInfo()

    def __str__(self) -> str:
        return self._dirPath

    def updateFileInfo(self):
        self._files.clear()
        self._directories.clear()
        allFiles = glob.glob(f"{self._dirPath}/*")
        for f in allFiles:
            if os.path.isdir(f):
                self._directories.add(f)
            else:
                self._files.add(f)

    def directories(self) -> set:
        return self._directories

    def files(self) -> set:
        return self._files

    def __contains__(self, item):
        return item in self._files or item in self._directories

    def containsFile(self, filename):
        return filename in self._files

    def containsDirectory(self, directory):
        return directory in self._directories

# ----------------------------------------------------------------------

class FileInfo:

    @staticmethod
    def extensionForFilePath(filePath):
        return os.path.splitext()[-1]

    @staticmethod
    def filenameForFilePath(filePath):
        return os.path.split(filePath)[-1]

    @staticmethod
    def joinPath(dirPath, filename):
        return os.path.join(dirPath, filename)

    @staticmethod
    def infoForFilePath(filePath=None, coursePrefix="CS"):
        if filePath is None:
            filePath = os.getcwd()
        courseName, other = FileInfo.findDirectoryStartingWith(filePath, coursePrefix)
        if len(other) == 0:
            return courseName, None, None, None
        elif len(other) == 1:
            # course, assignment
            return courseName, other[0], None, None
        elif len(other) == 2:
            # course, assignment, studentEmail
            return courseName, other[0], other[1]
        elif len(other) == 3:
            # courseName, assignment, studentEmail, filename
            return courseName, other[0], other[1], other[2]

    @staticmethod
    def findDirectoryStartingWith(filePath=None, prefix="CS"):
        if filePath is None:
            filePath = os.getcwd()

        paths = []
        if not os.path.isdir(filePath):
            filePath, name = os.path.split(filePath)
            paths.append(name)

        while filePath != os.path.sep:
            filePath, directory = os.path.split(filePath)
            if directory.startswith(prefix):
                paths.reverse()
                return directory, paths
            else:
                paths.append(directory)
        return None

    def __init__(self, filePath, *args):
        self._filePath = os.path.join(filePath, *args)
        self._contents = None

    def __str__(self) -> str:
        return self._filePath

    def filePath(self) -> str:
        return self._filePath

    def exists(self) -> bool:
        return os.path.exists(self._filePath)

    def isDir(self) -> (bool, bool):
        if not os.path.exists(self._filePath):
            return False, False
        else:
            return True, os.path.isdir(self._filePath)

    def fileName(self) -> str:
        return FileInfo.filenameForFilePath(self._filePath)

    def extension(self) -> str:
        return FileInfo.extensionForFilePath(self._filePath)

    def contentsOf(self) -> str:
        if self._contents is None:
            if os.path.exists(self._filePath):
                with open(self._filePath, 'r') as f:
                    self._contents = f.read()
            else:
                self._contents = ""
        return self._contents

    def cpInfo(self):
        """
        if it is a directory, returns Course, Assignment, StudentEmail
        else if not a directory, return Course, Assignment, StudentEmail, filename
        :return: tuple of info for use with CodePost
        """
        if self.isDir():
            return self._lastThreePaths()
        else:
            return self._lastFourPaths()

    def filePathWithNewName(self, newName) -> str:
        directoryPath, fileName = os.path.split(self._filePath)
        return os.path.join(directoryPath, newName)

    def _lastTwoPaths(self):
        remaining, two = os.path.split(self._filePath)
        remaining, one = os.path.split(remaining)
        return one, two

    def _lastThreePaths(self):
        remaining, three = os.path.split(self._filePath)
        remaining, two = os.path.split(remaining)
        remaining, one = os.path.split(remaining)
        return one, two, three

    def _lastFourPaths(self):
        remaining, four = os.path.split(self._filePath)
        remaining, three = os.path.split(remaining)
        remaining, two = os.path.split(remaining)
        remaining, one = os.path.split(remaining)
        return one, two, three, four

    def writeTo(self, newContents) -> None:
        with open(self._filePath, 'w') as f:
            f.write(newContents)

# ----------------------------------------------------------------------

def main():
    info = FileInfo("/Users/dreed/Labs/CS161/Lab1/dreed@capital.edu/file.txt")
    print(info)
    info = FileInfo("/Users/dreed/Labs/CS161/Lab1/dreed@capital.edu", "file.txt")
    print(info)
    info = FileInfo("/Users/dreed/Labs/CS161/Lab1", "dreed@capital.edu", "file.txt")
    print(info)
    info = FileInfo("/Users/dreed/Labs/CS161", "Lab1", "dreed@capital.edu", "file.txt")
    print(info)
    info = FileInfo("/Users/dreed/Labs", "CS161", "Lab1", "dreed@capital.edu", "file.txt")
    print(info)

    info = DirectoryInfo(os.getcwd())
    print("\nfiles")
    for f in info.files():
        print(f)
    print("\ndirectories")
    for d in info.directories():
        print(d)

    print(FileInfo.findDirectoryStartingWith(prefix="Pr"))
    print(FileInfo.findDirectoryStartingWith(prefix="dr"))

    print(FileInfo.infoForFilePath("/Users/dreed/Labs/CS161"))
    print(FileInfo.infoForFilePath("/Users/dreed/Labs/CS161/LList"))
    print(FileInfo.infoForFilePath("/Users/dreed/Labs/CS161/LList/dreed@capital.edu"))
    print(FileInfo.infoForFilePath("/Users/dreed/Labs/CS161/LList/dreed@capital.edu/LList.py"))


if __name__ == '__main__':
    main()
