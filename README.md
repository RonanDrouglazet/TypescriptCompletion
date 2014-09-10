# TypescriptCompletion

[TypeScript](http://www.typescriptlang.org/) Auto Completion with your project method name, and inject method manually with a module/class/method dictionary build from your TypeScript project

It's one of my first Python's project, so write in a basic Python way, please fork me or leave comment / issue and help me improve this plugin !

## Installation

### With Package Control:

search for TypescriptCompletion on package control and you will find it ! 

### Manual:

Clone this repository in your sublime package, generally:

    > /Users/yourname/Library/Application Support/Sublime Text 3/Packages/

If you want to check if sublime text correctly load the plugin, you can show the console on view > show console and see a line:

    reloading plugin User.TSCompletion

## Usage

### Auto completion:

Classic Sublime Text auto-completion popup was extend with your own project method. If you are not in a sublime project, you can fill manually a project path to inspect for auto-completion, press:

    cmd+shift+a

Then it's ok for this session ! Sublime text auto completion will work as usual, but extend with your method, so more powerfull for you !!

### Manual auto completion with class choice:

    cmd+shift+a

When you choose a class, then a method, TypescriptCompletion will write for you the method name and it's arguments for you

## ToDo

1. find/read lib.d.ts of typescript to fill auto completion with it
2. add constructor support
3. add interface support
4. detect module of the current file and use it to auto complet static method from other module (not write absolute "path" like root.module1.module2.Static if we are already on module1 but write module2.Static)
5. listen for dot ".", sublime doesn't do it.
6. a lot of idea remaining !
