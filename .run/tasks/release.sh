# vim: set ft=bash sw=3 ts=3 expandtab:

help_release() {
   echo "- run release: Release a specific version and tag the code"
}

task_release() {
   COPYRIGHT_START=2004 run_command tagrelease "$@"
}

