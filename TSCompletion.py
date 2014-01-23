import os, re, logging, threading
import sublime, sublime_plugin

##############################

# Manual call to TSCompletion
class TscompletionCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        ExtractEngine.run(False)
        sublime.active_window().show_quick_panel(TSC_Global.TSC_TsClassList, self.onClassChoice)

    def onClassChoice(self, value):
        if value != -1:
            TSC_Global.TSC_ClassChoice = TSC_Global.TSC_TsClassList[value]
            if len(TSC_Global.TSC_ProjectDictionary[TSC_Global.TSC_ClassChoice]) == 0:
                sublime.error_message("Sorry, no method in class " + TSC_Global.TSC_ClassChoice + "\nIf you find a bug, leave issue on \nhttps://github.com/RonanDrouglazet/TSCompletion")
            sublime.set_timeout(lambda: sublime.active_window().show_quick_panel(TSC_Global.TSC_ProjectDictionary[TSC_Global.TSC_ClassChoice], self.onMethodChoice), 10)

    def onMethodChoice(self, value):
        if value == 0:
            sublime.set_timeout(lambda: sublime.active_window().run_command("tscompletion"), 10)
            return
        if value != -1:
            patternMethodNake = re.compile("\s.+\)")
            methodString = patternMethodNake.findall(TSC_Global.TSC_ProjectDictionary[TSC_Global.TSC_ClassChoice][value])[0].lstrip()
            sublime.set_timeout(lambda: sublime.active_window().run_command("inserttscompletion", {"method": methodString}), 10)

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
    TSC_ProjectDictionary = {}
    TSC_DefaultFileEncoding = "utf-8"
    TSC_ModuleRegex = ".*module\s.+{"
    TSC_ModuleNameRegex = r"\b(?!module|export|declare)\w+\b"
    TSC_ClassRegex = "\s*(export )*class \w+"
    TSC_ClassNameRegex = r"\b(?!export|class|extends|implements)\w+\b"
    TSC_MethodRegex = "\s*(public|private|static|function)\s+(static\s+)*\w+\s*\("
    TSC_MethodNameRegex = r"\w+\s\w+\(.*"
    TSC_UserCustomProjectPath = ""
    TSC_AutoCompletListTuple = []
    TSC_AutoCompletListString = []
    TSC_PreviousText = "<==== Return in class choice"
    TSC_ProjectPathList = []
    TSC_TsFileList = []
    TSC_TsClassList = []
    TSC_ClassChoice = []

    def clear():
        TSC_Global.TSC_ProjectPathList = []
        TSC_Global.TSC_TsFileList = []
        TSC_Global.TSC_TsClassList = []
        TSC_Global.TSC_ClassChoice = []
        TSC_Global.TSC_AutoCompletListTuple = []
        TSC_Global.TSC_AutoCompletListString = []
        TSC_Global.TSC_ProjectDictionary = {}

    def genAutoCompletList():
        reMethodNameNake = re.compile("\s\w+")
        reMethodNameInsert = re.compile("\s.+\)")
        for module in TSC_Global.TSC_ProjectDictionary:
            for method in TSC_Global.TSC_ProjectDictionary[module]:
                if method != TSC_Global.TSC_PreviousText:
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
        className = ""

        # Method
        patternMethod = re.compile(TSC_Global.TSC_MethodRegex)
        patternMethodName = re.compile(TSC_Global.TSC_MethodNameRegex)
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
                ExtractEngine.insertClassInDic(className)

            # Method
            if patternMethod.match(line):
                methodName = patternMethodName.findall(line)[0].strip(" {")
                if className == "":
                    className = moduleName
                ExtractEngine.insertClassInDic(className)
                if not methodName in TSC_Global.TSC_ProjectDictionary[className]:
                    TSC_Global.TSC_ProjectDictionary[className].append(methodName)

    def insertClassInDic(className):
        if not className in TSC_Global.TSC_TsClassList:
            TSC_Global.TSC_TsClassList.append(className)
        if not className in TSC_Global.TSC_ProjectDictionary:
            TSC_Global.TSC_ProjectDictionary[className] = [TSC_Global.TSC_PreviousText]

##############################

# Util
def TSC_IsTypeScript(filename):
    return filename.endswith(".ts") & (not filename.endswith(".d.ts"))
