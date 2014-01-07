module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        watch: {
            dev:{
                files: ['bin/TSCompletion.py'],
                tasks: ['dev']
            },
            keymap:{
                files: ['bin/*.sublime-keymap'],
                tasks: ['keymap']
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-watch');

    grunt.registerTask('keymap', 'copy keymap to sublime package', function(arg1, arg2){
        grunt.file.copy("./bin/Default (Linux).sublime-keymap", grunt.config("pkg.dirPath_sublimeText3") + "TSCompletion/Default (Linux).sublime-keymap");
        grunt.file.copy("./bin/Default (Windows).sublime-keymap", grunt.config("pkg.dirPath_sublimeText3") + "TSCompletion/Default (Windows).sublime-keymap");
        grunt.file.copy("./bin/Default (OSX).sublime-keymap", grunt.config("pkg.dirPath_sublimeText3") + "TSCompletion/Default (OSX).sublime-keymap");
        grunt.log.writeln('TSCompletion keymap copied to sublime package');
    });

    grunt.registerTask('dev', 'copy plugin to sublime package', function(arg1, arg2){
        grunt.file.copy("./bin/TSCompletion.py", grunt.config("pkg.dirPath_sublimeText3") + "TSCompletion.py");
        grunt.log.writeln('TSCompletion.py copied to sublime package');
    });

    grunt.registerTask('default', 'copy file', function(arg1, arg2){
        grunt.task.run('keymap', 'dev');
        grunt.log.writeln('Update TSCompletion plugin');
    });
};
