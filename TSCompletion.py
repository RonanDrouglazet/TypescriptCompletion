import os
import logging
import sublime, sublime_plugin

class TscompletionCommand(sublime_plugin.TextCommand):

    ## Constant plugin
    defaultFileEncoding = "utf-8"
    extInclude = ".ts" #TODO do a list
    extExclude = ".d.ts" #TODO do a list
    osDelimiter = "/" #TODO dif between os ? actually OSX

    ## Variable plugin
    projectPathList = []
    tsFileList = []
    tsClassList = []

    ## Method plugin
    def run(self, edit):
        self.projectPathList = self.getCurrentProjectPath()
        self.tsFileList = self.getTsFileList(self.projectPathList)
        self.tsClassList = self.genClassList(self.tsFileList)
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
                userPathList = sublime.packages_path().rsplit(self.osDelimiter)
                userPath = self.osDelimiter + self.osDelimiter.join((userPathList[1], userPathList[2], "Documents")) + self.osDelimiter
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

    def genClassList(self, fileList):
        classList = []
        for file in fileList:
            classList.append(self.extractClassAndMethodFromFile(file))

        #logging.warning("Class List: " + str(classList))

    def extractClassAndMethodFromFile(self, file):
        tmpFile = open(file, 'r', -1, self.defaultFileEncoding)
        tmpFile.close()

    def on_choice(self, value):
        logging.warning("Choosen value:" + self.tsFileList[value])
