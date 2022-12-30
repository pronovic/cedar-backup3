# vim: set ft=bash sw=3 ts=3 expandtab:
# runscript: customized=true

help_release() {
   echo "- run release: Tag and release the code, triggering GHA to publish artifacts"
}

task_release() {
   COPYRIGHT_START=2004 run_command tagrelease "$@"
}

