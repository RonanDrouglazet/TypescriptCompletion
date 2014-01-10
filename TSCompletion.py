import os
import re
import logging
import sublime, sublime_plugin

class TscompletionCommand(sublime_plugin.TextCommand):

    ## Constant plugin
    defaultFileEncoding = "utf-8"
    extInclude = ".ts" #TODO do a list
    extExclude = ".d.ts" #TODO do a list
    moduleRegex = ".*module\s.+{"
    classRegex = "\s*export class \w+"
    methodRegex = "\s*(public|private|static)\s+(static\s+)*\w+\s*\("
    userCustomProjectPath = ""

    ## Variable plugin
    projectPathList = []
    tsFileList = []
    tsProjectDictionary = {}
    tsClassList = []
    classChoice = []

    ## Method plugin
    def run(self, edit):
        # Reset
        self.projectPathList = []
        self.tsFileList = []
        self.tsProjectDictionary = {}
        self.tsClassList = []
        self.classChoice = []

        try:
            self.projectPathList = self.getCurrentProjectPath()
            self.tsFileList = self.getTsFileList(self.projectPathList)

            self.genProjectDictionary(self.tsFileList)

        except ValueError:
            logging.warning(self.projectPathList)
            logging.warning(self.tsFileList)
            logging.warning(self.tsProjectDictionary)
            logging.warning(ValueError)

        sublime.active_window().show_quick_panel(self.tsClassList, self.onClassChoice)

    def getCurrentProjectPath(self):
        dirList = []

        if "folders" in sublime.active_window().project_data():
            projectFolderList = sublime.active_window().project_data()["folders"]

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
        else:
            if self.userCustomProjectPath != "":
                dirList.append(self.userCustomProjectPath)
            else:
                sublime.message_dialog("Sorry you are not in a project or the plugin does not find your project path \n\nPlease fill it on the bottom input and TSCompletion will remember this path for this session \n\nIf you are in a project so plugin have a bug, please leave issue and project conf on https://github.com/RonanDrouglazet/TSCompletion")
                sublime.active_window().show_input_panel("Please fill TypeScript project path to analyse: ", "/Users/drouglazet/Desktop/work/TSCompletion/", self.onFillDone, None, None)

        logging.warning("Project Path: " + str(dirList))

        return dirList

    def onFillDone(self, value):
        self.userCustomProjectPath = value
        sublime.active_window().run_command("tscompletion")

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
        for file in fileList:
            tmpFile = open(file, 'r', -1, self.defaultFileEncoding)
            self.extractFromFile(tmpFile)
            tmpFile.close()

    def extractFromFile(self, file):
        # Module
        patternModule = re.compile(self.moduleRegex)
        patternModuleName = re.compile(r"\b(?!module|export|declare)\w+\b")
        moduleName = ""

        # Class
        patternClass = re.compile(self.classRegex)
        patternClassName = re.compile(r"\b(?!export|class|extends|implements)\w+\b")
        className = ""

        # Method
        patternMethod = re.compile(self.methodRegex)
        patternMethodName = re.compile(r"\w+\s\w+\(.*")
        methodName = ""

        for line in file.readlines():
            # Module
            if patternModule.match(line):
                # If a module are manually export into an other module and not simply module.submodule
                if "export" in line:
                    moduleName = moduleName + "." + ".".join(patternModuleName.findall(patternModule.findall(line)[0]))
                else:
                    moduleName = ".".join(patternModuleName.findall(patternModule.findall(line)[0]))

            # Class
            if patternClass.match(line):
                className = moduleName + "." + patternClassName.findall(line)[0]
                if not className in self.tsClassList:
                    self.tsClassList.append(className)
                if not className in self.tsProjectDictionary:
                    self.tsProjectDictionary[className] = []
                else:
                    break

            # Method
            if patternMethod.match(line):
                methodName = patternMethodName.findall(line)[0].strip(" {")
                if className == "":
                    if moduleName == "":
                        moduleName = "window"
                    className = moduleName
                    if not className in self.tsClassList:
                        self.tsClassList.append(className)
                    if not className in self.tsProjectDictionary:
                        self.tsProjectDictionary[className] = []
                if not methodName in self.tsProjectDictionary[className]:
                    self.tsProjectDictionary[className].append(methodName)

    def onClassChoice(self, value):
        #logging.warning(self.tsClassList[value])
        #logging.warning(self.tsProjectDictionary[self.tsClassList[value]])
        if value != -1:
            self.classChoice = self.tsClassList[value]
            if len(self.tsProjectDictionary[self.classChoice]) == 0:
                sublime.error_message("Sorry, no method in class " + self.classChoice + "\nIf you find a bug, leave issue on \nhttps://github.com/RonanDrouglazet/TSCompletion")
            sublime.set_timeout(lambda: sublime.active_window().show_quick_panel(self.tsProjectDictionary[self.classChoice], self.onMethodChoice), 10)

    def onMethodChoice(self, value):
        if value != -1:
            patternMethodNake = re.compile("\s.+\)")
            methodString = patternMethodNake.findall(self.tsProjectDictionary[self.classChoice][value])[0].lstrip()
            sublime.set_timeout(lambda: sublime.active_window().run_command("inserttscompletion", {"method": methodString}), 10)

class InserttscompletionCommand(sublime_plugin.TextCommand):

    def run(self, edit, method):
        caretPos = self.view.sel()[0].begin()
        self.view.insert(edit, caretPos, method)
