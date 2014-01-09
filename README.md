# TSCompletion

Sublim Text 3 (ST3) plugin for typescript auto completion (only tested on OSX actually). Inject method with a dynamic library build from your TypeScript project

It's one of my first Python's project, so write in a basic Python way, please fork me or leave comment / issue and help me improve this plugin !

## Installation

### With Package Control:

Not ready yet, need more test on plugin (Windows / Linux platform for example)

### Manually:

1. First way: Clone this repository directly in your sublime package, generally:

    > //Users/yourname/Library/Application Support/Sublime Text 3/Packages/User/

and you can go to the section "Usage".

2. OR Clone this repository anywhere, then fill "dirPath_sublimeText3" in package.json with your sublimeText3 user package path :

    > "dirPath_sublimeText3": "//Users/drouglazet/Library/Application Support/Sublime Text 3/Packages/User/"

then call grunt:

    > grunt

this will copy the plugin in your package user directory, you can use grunt watch to if you want to test some modification

If you want to check if sublime text correctly load the plugin, you can show the console on view > show console and see a line:

    reloading plugin User.TSCompletion

## Usage

If you are in a sublime project, TSCompletion will normally find alone your project path, and check all ts file.
But, if you are not in a project, TSCompletion will ask you to fill a project path to analyse, juste one time for this session, TSCompletion will remember this path unless you quit this sublime window.

When you choose a class, then a method, TSCompletion will write for you the method name and it's arguments for you

### key to run TSCompletion on OSX:

    super+shift+a

## ToDo

1. Test on other platform than OSX
2. add a real auto-completion when we write ".", so key's "super+shift+a" active plugin and listen for a dot "."
3. automatic detection of dot previous object type "object." to pre select class on the quickshearch panel
4. a lot of idea remaining !
