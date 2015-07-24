REM Simple script to grab SVN trunk when Subversion protocol isn't allowed through proxy
REM Set http_proxy to the proxy address, and then place the user/password into the command-line.
set http_proxy=proxy.XXXXXX.com:XXXX
wget --proxy=on --proxy-user=XXXXXX --proxy-passwd=XXXXXXXX -e robots=off -r -np -nH -R index.html -P cedar-backup2 --cut-dirs=4 -I /svn/software/cedar-backup2/trunk -X /svn/software/cedar-backup2/tags http://cedar-solutions.com/svn/software/cedar-backup2/trunk
