# vim: set ft=bash ts=3 sw=3 expandtab:
# Run the Pylint code checker

# We generate relative paths in the output to make integration with Pycharm work better

command_pylint() {
   TESTS="tests"

   while getopts "t" option; do
     case $option in
       t)
         TESTS=""  # -t means to ignore the tests
         ;;
       ?)
         echo "invalid option -$OPTARG"
         exit 1
         ;;
     esac
   done

   shift $((OPTIND -1))  # pop off the options consumed by getopts

   echo "Running pylint checks..."
   TEMPLATE="{path}:{line}:{column} - {C} - ({symbol}) - {msg}"
   poetry_run pylint --msg-template="$TEMPLATE" -j 0 "$@" $(ls -d src/*) $TESTS
   echo "done"
}
