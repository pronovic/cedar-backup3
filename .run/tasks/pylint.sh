# vim: set ft=bash sw=3 ts=3 expandtab:
# runscript: customized=true

help_pylint() {
   # No help - exists for PyCharm integration
   echo -n ""
}

task_pylint() {
   run_command pylint -t  # ignore the test suite
}

