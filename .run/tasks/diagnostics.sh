# vim: set ft=bash sw=3 ts=3 expandtab:

help_diagnostics() {
   echo "- run diagnostics: Print CedarBackup runtime diagnostics"
}

task_diagnostics() {
   cat << EOF > "$WORKING_DIR/diagnostics.py"
from CedarBackup3.util import Diagnostics
Diagnostics().printDiagnostics(prefix="*** ")
EOF

   run_command latestcode
   poetry_run python "$WORKING_DIR/diagnostics.py" "$@"
}

