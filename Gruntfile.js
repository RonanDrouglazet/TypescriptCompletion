module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        watch: {
            TSCompletion:{
                files: ['bin/*.py'],
                tasks: ['default']
            }
        },
        bgShell: {
            TSCompletion : {
                cmd: 'cp -R <%= pkg.TSCompletion_directory %>bin/TSCompletion.py <%= pkg.ST3_directory %>TSCompletion.py'
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-bg-shell');

    grunt.registerTask('default', ['bgShell']);
};
