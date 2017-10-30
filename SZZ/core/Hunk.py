import re

class Hunk:
    def __init__(self, positionOld, sizeOld, positionNew, sizeNew):
        self.positionOld = positionOld
        self.sizeOld = sizeOld
        self.positionNew = positionNew
        self.sizeNew = sizeNew
        self.linesType = []
        self.linesDetails = []
        self.linesAdded = 0
        self.linesRemoved = 0
        self.linesBefore = 0
        self.linesTotal = 0
        self.pair = []

    def addDetailAboutLines(self, type, line):
        self.linesType.append(type)
        self.linesDetails.append(line)

    def getListOfRemovedLines(self):
        i = 0
        for line in self.linesType:
            if line == "-":
                startLine = self.positionOld + i
                self.pair.append(startLine)
            if line == "=" or line == "-":
                i += 1
        return self.pair

    def isABug(self, lineNumber):
        return True

    def isAJavaComment(self, lineNumber):
        line = self.linesDetails[lineNumber]
        line = line.replace("'", "")
        if re.match('^[-+][ \t]*\/\/', line):
            return True
        elif re.match('^[-+][ \t]*\/\*', line):
            return True
        elif re.match('^[-+][ \t]*\*', line):
            return True
        elif re.match('\*\/[ \t]*$', line):
            return True
        elif re.match('^.*[;,+:()\[\]{}][ \t\']*$', line):
            return False
        else:
            return False

    def isAPerlComment(self, lineNumber):
        line = self.linesDetails[lineNumber]
        line = line.replace("'", "")
        if re.match('^[-+][ \t]*\#', line):
            return True
        elif re.match('^.*[;,+:()\[\]{}\/*][ \t\']*$', line):
            return False
        else:
            return False

    def isAComment(self, lineNumber, file):
        if file.endswith(".java") or file.endswith(".js"):
            return self.isAJavaComment(lineNumber)
        elif file.endswith(".pm") or file.endswith(".pl"):
            return self.isAPerlComment(lineNumber)
        else:
            return self.isAComment(lineNumber)

    def isACode(self, lineNumber, file):
        return not self.isAComment(lineNumber, file)