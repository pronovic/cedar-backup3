# vim: set ft=bash sw=3 ts=3 expandtab:
# runscript: customized=true

help_checks() {
   echo "- run checks: Run the code checkers"
}

task_checks() {
   echo ""
   run_command checktabs
   echo ""
   run_command ruffformat --check
   echo ""
   run_command rufflint
}

