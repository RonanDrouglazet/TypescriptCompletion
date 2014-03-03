import os, re, logging, threading
import sublime, sublime_plugin

##############################

# Manual call to TSCompletion
class TscompletionCommand(sublime_plugin.TextCommand):

    tabPanel = []
    objectPanel = {}

    def run(self, edit):
        ExtractEngine.run(False)
        self.tabPanel = []
        self.objectPanel = TSC_Global.TSC_ProjectDictionary

        for module in self.objectPanel:
            self.tabPanel.append("module " + module)

        self.tabPanel.sort()
        sublime.active_window().show_quick_panel(self.tabPanel, self.onChoice)

    def onChoice(self, value):
        panelChoice = self.tabPanel[value]

        if (value == 0) & (panelChoice == ".."):
            sublime.set_timeout(lambda: sublime.active_window().run_command("tscompletion"), 10)
            return

        if value != -1:
            type1 = re.compile(r"^\b(module|class)\b\s")
            type2 = re.compile(r"^\b(function|static|private|public)\b\s")

            if type1.match(panelChoice):
                extractedName = panelChoice.replace("module", "").lstrip()
                self.objectPanel = self.objectPanel[extractedName]
                self.tabPanel = self.fillPanel(self.objectPanel)
                sublime.set_timeout(lambda: sublime.active_window().show_quick_panel(self.tabPanel, self.onChoice), 10)
                return

            if type2.match(panelChoice):
                patternMethodNake = re.compile("\s.+\)")
                methodString = patternMethodNake.findall(panelChoice)[0].lstrip()
                sublime.set_timeout(lambda: sublime.active_window().run_command("inserttscompletion", {"method": methodString}), 10)
                return

    def fillPanel(self, parentObject):
        panel = []
        for child in parentObject:
            if (child != ".function") & (child != ".var"):
                panel.append(child)
            else:
                for prop in parentObject[child]:
                    if (not prop.startswith("var")) & (not prop.startswith("private")):
                        panel.append(prop)

        panel.insert(0, "..");
        panel.sort()

        return panel


##############################

# Auto complet event
class TsAutoCompletion(sublime_plugin.EventListener):

    _collector_thread = None

    def startThread(self):
        if self._collector_thread != None:
            self._collector_thread.stop()
        self._collector_thread = TsCompletionThread(self)
        self._collector_thread.start()

    # Invoked when user save a file
    def on_post_save(self, view):
        self.startThread()

    # Change autocomplete suggestions
    def on_query_completions(self, view, prefix, locations):
        current_file = view.file_name()
        completions = []
        if TSC_IsTypeScript(current_file):
            if len(TSC_Global.TSC_AutoCompletListTuple) == 0:
                self.startThread()
            return TSC_Global.TSC_AutoCompletListTuple
            completions.sort()
        return (completions,sublime.INHIBIT_EXPLICIT_COMPLETIONS)

    def on_modified(self, view):
        reg = view.line(view.sel()[0])
        if TSC_IsTypeScript(view.file_name()) & view.substr(reg).endswith('..'):
            if len(TSC_Global.TSC_AutoCompletListString) == 0:
                ExtractEngine.run(True)
            view.show_popup_menu(TSC_Global.TSC_AutoCompletListString, None)



##############################

# Thread for better perf
class TsCompletionThread(threading.Thread):

    def __init__(self, collector):
        threading.Thread.__init__(self)

    def run(self):
        ExtractEngine.run(True)

    def stop(self):
        if self.isAlive():
            self._Thread__stop()

##############################

# TSCompletion Global var
class TSC_Global:
    TSC_ProjectDictionary = {"window": {}}
    TSC_DefaultFileEncoding = "utf-8"
    TSC_ModuleRegex = ".*module\s.+{"
    TSC_ModuleNameRegex = r"\b(?!export|declare|module)\w+\b"
    TSC_ClassRegex = "\s*(export )*(class|interface) \w+"
    TSC_ClassNameRegex = r"\b(?!export|extends|implements)\w+\b"
    TSC_MethodRegex = "\s*(public|private|static|function)\s+(static\s+)*\w+\s*\("
    TSC_MethodNameRegex = r"\w+\s\w+\(.*"
    TSC_PropRegex = r"\s*(public|private|static|var)\s+\w+\s*:"
    TSC_PropRegexName = r"\b\w+\.*\w+\b"
    TSC_UserCustomProjectPath = ""
    TSC_AutoCompletListTuple = []
    TSC_AutoCompletListString = []
    TSC_ProjectPathList = []
    TSC_TsFileList = []

    def clear():
        TSC_Global.TSC_ProjectPathList = []
        TSC_Global.TSC_TsFileList = []
        TSC_Global.TSC_AutoCompletListTuple = []
        TSC_Global.TSC_AutoCompletListString = []
        TSC_Global.TSC_ProjectDictionary = {"window": {}}

    def genAutoCompletList():
        reMethodNameNake = re.compile("\s\w+")
        reMethodNameInsert = re.compile("\s.+\)")
        for module in TSC_Global.TSC_ProjectDictionary:
            for className in TSC_Global.TSC_ProjectDictionary[module]:
                if (className != ".var") & (className != ".function"):
                    for method in TSC_Global.TSC_ProjectDictionary[module][className][".function"]:
                        methodName = reMethodNameNake.findall(method)[0].strip()

                        if len(reMethodNameInsert.findall(method)) > 0:
                            methodInsert = reMethodNameInsert.findall(method)[0].strip()
                        else:
                            methodInsert = methodName + "()"

                        TSC_Global.TSC_AutoCompletListTuple.append((methodName + '\t' + module, methodInsert))
                        TSC_Global.TSC_AutoCompletListString.append(methodName + '\t' + module)
                        TSC_Global.TSC_AutoCompletListTuple.sort()
                        TSC_Global.TSC_AutoCompletListString.sort()

##############################

# Insert method in view command
class InserttscompletionCommand(sublime_plugin.TextCommand):

    def run(self, edit, method):
        caretPos = self.view.sel()[0].begin()
        self.view.insert(edit, caretPos, method)

##############################

# Extract class / method / module from file
class ExtractEngine:

    ## Method plugin
    def run(autoComplete):
        # Reset
        TSC_Global.clear()

        try:
            TSC_Global.TSC_ProjectPathList = ExtractEngine.getCurrentProjectPath(autoComplete)
            TSC_Global.TSC_TsFileList = ExtractEngine.getTsFileList(TSC_Global.TSC_ProjectPathList)

            ExtractEngine.genProjectDictionary(TSC_Global.TSC_TsFileList)
            TSC_Global.genAutoCompletList();

        except ValueError:
            logging.warning(TSC_Global.TSC_ProjectPathList)
            logging.warning(TSC_Global.tsFileList)
            logging.warning(TSC_Global.TSC_ProjectDictionary)
            logging.warning(ValueError)

    def getCurrentProjectPath(autoComplete):
        dirList = []

        if len(sublime.active_window().folders()) > 0:
            projectFolderList = sublime.active_window().folders()

            for path in projectFolderList:
                if os.path.isdir(path):
                    dirList.append(path)
        else:
            if TSC_Global.TSC_UserCustomProjectPath != "":
                dirList.append(TSC_Global.TSC_UserCustomProjectPath)
            else:
                if not autoComplete:
                    sublime.message_dialog("Sorry you are not in a sublime project or the plugin does not find your project path \n\nPlease fill it on the bottom input and TSCompletion will remember this path for this session \n\nIf you are in a project so plugin have a bug, please leave issue and project conf on https://github.com/RonanDrouglazet/TSCompletion")
                    sublime.active_window().show_input_panel("Please fill TypeScript project path to analyse: ", "/Users/yourname/etc..", ExtractEngine.onFillDone, None, None)
                else:
                    sublime.status_message("Sorry you are not in a sublime project or the plugin does not find your project path \n\nPlease fill it with cmd+shift+a if you want auto completion")
                    logging.warning("TSCompletion: Sorry you are not in a project or the plugin does not find your project path \n\nPlease fill it with cmd+shift+a if you want auto completion")

        return dirList

    def onFillDone(value):
        TSC_Global.TSC_UserCustomProjectPath = value
        sublime.active_window().run_command("tscompletion")

    def getTsFileList(pathList):
        fileList = []
        for path in pathList:
            for root, dirs, files in os.walk(path):
                for name in files:
                    if TSC_IsTypeScript(name):
                        fileList.append(os.path.join(root, name))

        return fileList

    def genProjectDictionary(fileList):
        for file in fileList:
            tmpFile = open(file, 'r', -1, TSC_Global.TSC_DefaultFileEncoding)
            ExtractEngine.extractFromFile(tmpFile)
            tmpFile.close()

    def extractFromFile(file):
        # Module
        patternModule = re.compile(TSC_Global.TSC_ModuleRegex)
        patternModuleName = re.compile(TSC_Global.TSC_ModuleNameRegex)
        moduleName = "window"

        # Class
        patternClass = re.compile(TSC_Global.TSC_ClassRegex)
        patternClassName = re.compile(TSC_Global.TSC_ClassNameRegex)
        className = "window"

        # Method
        patternMethod = re.compile(TSC_Global.TSC_MethodRegex)
        patternMethodName = re.compile(TSC_Global.TSC_MethodNameRegex)
        methodName = ""

        # Propertie
        patternProp = re.compile(TSC_Global.TSC_PropRegex);
        patternPropName = re.compile(TSC_Global.TSC_PropRegexName);

        for line in file.readlines():
            # Module
            if patternModule.match(line):
                # If a module are manually export into an other module and not simply module.submodule
                if "export" in line:
                    moduleName = moduleName + "." + ".".join(patternModuleName.findall(patternModule.findall(line)[0]))
                else:
                    moduleName = ".".join(patternModuleName.findall(patternModule.findall(line)[0]))
                ExtractEngine.insertModuleInDic(moduleName)
                className = moduleName

            # Class
            if patternClass.match(line):
                className = patternClassName.findall(line)[0] + " " + patternClassName.findall(line)[1]
                ExtractEngine.insertClassInDic(className, moduleName)

            # Method
            if patternMethod.match(line):
                methodName = patternMethodName.findall(line)[0].strip(" {")
                if className == moduleName:
                    TSC_Global.TSC_ProjectDictionary[moduleName][".function"].append(methodName)
                else:
                    TSC_Global.TSC_ProjectDictionary[moduleName][className][".function"].append(methodName)


            if patternProp.match(line):
                listMatch = patternPropName.findall(line)
                if len(listMatch) > 2:
                    #tmp = ""
                    if className == moduleName:
                        TSC_Global.TSC_ProjectDictionary[moduleName][".var"].append(listMatch[0] + " " + listMatch[1] + " : " + listMatch[2])
                    else:
                        TSC_Global.TSC_ProjectDictionary[moduleName][className][".var"].append(listMatch[0] + " " + listMatch[1] + " : " + listMatch[2])
                    #for className in TSC_Global.TSC_ProjectDictionary:
                    #    if className.endswith(listMatch[2]):
                    #        tmp = listMatch[1] + ": " + listMatch[2]
                    #        logging.warning(listMatch[1] + ": " + listMatch[2])
                    #if tmp == "":
                    #    logging.warning("#" + listMatch[1] + ": " + listMatch[2])

    def insertClassInDic(className, module):
        if not className in TSC_Global.TSC_ProjectDictionary[module]:
            TSC_Global.TSC_ProjectDictionary[module][className] = {".function": [], ".var": []}

    def insertModuleInDic(moduleName):
        if not moduleName in TSC_Global.TSC_ProjectDictionary:
            TSC_Global.TSC_ProjectDictionary[moduleName] = {".function": [], ".var": []}

##############################

# Util
def TSC_IsTypeScript(filename):
    return filename.endswith(".ts") & (not filename.endswith(".d.ts"))
