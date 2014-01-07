import os
import logging
import sublime, sublime_plugin

class TscompletionCommand(sublime_plugin.TextCommand):
    projectPathList = []
    tsFileList = []
    tsClassList = []

    def getCurrentProjectPath(self):
        projectFolderList = sublime.active_window().project_data()["folders"] #user project currently open folders
        dirList = []

        for pathDic in projectFolderList:
            dirList.append(pathDic["path"])

        return dirList

    def getTsFileList(self, pathList):
        fileList = []
        for path in pathList:
            for root, dirs, files in os.walk(path):
                for name in files:
                    if name.endswith(".ts") & (name.endswith(".d.ts") == False):
                        fileList.append(os.path.join(root, name))
                        #logging.warning(os.path.join(root, name))

        return fileList

    def genClassList(self, fileList):
        classList = []
        for file in fileList:
            classList.append(self.extractClassAndMethodFromFile(file))

    def extractClassAndMethodFromFile(self, file):
        logging.warning(file)
        tmpFile = open(file, 'r', -1, 'utf-8')
        test = tmpFile.readlines()
        tmpFile.close()


    def run(self, edit):
        self.projectPathList = self.getCurrentProjectPath()
        self.tsFileList = self.getTsFileList(self.projectPathList)
        self.tsClassList = self.genClassList(self.tsFileList)

        sublime.active_window().show_quick_panel(self.tsFileList, self.on_choice)

    def on_choice(self, value):
        logging.warning("Finish:" + self.tsFileList[value])
