import os
import re
import logging
import sublime, sublime_plugin

class TscompletionCommand(sublime_plugin.TextCommand):

    ## Constant plugin
    defaultFileEncoding = "utf-8"
    extInclude = ".ts" #TODO do a list
    extExclude = ".d.ts" #TODO do a list
    moduleRegex = "module\s.+{"

    ## Variable plugin
    projectPathList = []
    tsFileList = []
    tsProjectDictionary = {}

    ## Method plugin
    def run(self, edit):
        self.projectPathList = self.getCurrentProjectPath()
        self.tsFileList = self.getTsFileList(self.projectPathList)
        self.tsProjectDictionary = self.genProjectDictionary(self.tsFileList)
        sublime.active_window().show_quick_panel(self.tsFileList, self.on_choice)

    def getCurrentProjectPath(self):
        projectFolderList = sublime.active_window().project_data()["folders"]
        dirList = []

        for pathDic in projectFolderList:

            # Absolute path => ok
            if os.path.isdir(pathDic["path"]):
                dirList.append(pathDic["path"])

            # Relative path => not ok
            else:
                userPathList = sublime.packages_path().rsplit(os.sep)
                userPath = os.sep + os.sep.join((userPathList[1], userPathList[2], "Documents")) + os.sep
                if os.path.isdir(userPath + pathDic["path"]):
                    dirList.append(userPath + pathDic["path"])

        #logging.warning("Project Path: " + str(dirList))

        return dirList

    def getTsFileList(self, pathList):
        fileList = []
        for path in pathList:
            for root, dirs, files in os.walk(path):
                for name in files:
                    if name.endswith(self.extInclude) & (not name.endswith(self.extExclude)):
                        fileList.append(os.path.join(root, name))

        #logging.warning("File List: " + str(fileList))

        return fileList

    def genProjectDictionary(self, fileList):
        projectDictionary = {}
        for file in fileList:
            tmpFile = open(file, 'r', -1, self.defaultFileEncoding)
            self.extractModuleFromFile(tmpFile, projectDictionary)
            self.extractClassFromFile(tmpFile, projectDictionary)
            self.extractInterfaceFromFile(tmpFile, projectDictionary)
            self.extractMethodFromFile(tmpFile, projectDictionary)
            tmpFile.close()

        logging.warning("Class List: " + str(projectDictionary))
        return projectDictionary

    def extractModuleFromFile(self, file, dic):
        patternM = re.compile(self.moduleRegex)
        patternMN = re.compile(r"\b(?!module)\w+\b")
        for matchedLine in patternM.findall( file.read() ):
            topLevel = patternMN.findall(matchedLine)[0]
            for moduleName in patternMN.findall(matchedLine):
                if not moduleName in dic:
                    if moduleName != topLevel:
                        topLevel = topLevel + "." + moduleName

                    dic[topLevel] = {}


    def extractClassFromFile(self, file, dic):
        tabLines = file.readlines()

    def extractInterfaceFromFile(self, file, dic):
        tabLines = file.readlines()

    def extractMethodFromFile(self, file, dic):
        tabLines = file.readlines()

    def on_choice(self, value):
        logging.warning("Choosen value:" + self.tsFileList[value])
