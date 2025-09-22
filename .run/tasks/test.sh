# vim: set ft=bash sw=3 ts=3 expandtab:
# runscript: customized=true

# The logic below mostly replicates what was available in util/test.py prior to
# converting to the more standard unittest discovery process.  Since Cedar
# Backup is the only code of mine that still uses unittest, there's no point in
# pulling this into a shared command.

help_test() {
   echo "- run test: Run the unit tests (use --help to see other options)"
}

task_test() {

   local OPTIND OPTARG option coverage html pattern verbose

   coverage="no"
   html="no"
   pattern=""
   verbose=""

   while getopts ":ch" option; do
     case $option in
       c) 
         coverage="yes"
         ;;
       h) 
         html="yes"
         ;;
       *) 
         echo "run test [-c] [-ch] [full] [verbose] [name]"
         echo "  -c       run coverage"
         echo "  -ch      run coverage and generate the HTML report"
         echo "  full     run the full integration test suite (useful on Ken's home network)"
         echo "  verbose  enable (very) verbose test output"
         echo "  name     execute the test with name only; i.e. 'util' executes test_util.py"
         exit 1
         ;;
     esac
   done

   shift $((OPTIND -1))  # pop off the options consumed by getopts

   while [ $# -gt 0 ]; do
     case $1 in
       full) 
         sudo -v
         export PEERTESTS_FULL="Y"
         export WRITERSUTILTESTS_FULL="Y"
         export ENCRYPTTESTS_FULL="Y"
         export SPLITTESTS_FULL="Y"  
         ;;
       verbose) 
         verbose="-v"
         export FULL_LOGGING="Y"
         ;;
      *)
         pattern="-p test_$1.py"
     esac
     shift
   done

   if [ $coverage == "yes" ]; then
      run_command uvrun coverage run -m unittest discover -s tests -t tests $verbose $pattern
      run_command uvrun coverage report
      run_command uvrun coverage lcov -o .coverage.lcov
      if [ $html == "yes" ]; then
         run_command uvrun coverage html -d .htmlcov
         run_command openfile .htmlcov/index.html
      fi
   else
      run_command uvrun python -m unittest discover -s tests -t tests $verbose $pattern
   fi

}
