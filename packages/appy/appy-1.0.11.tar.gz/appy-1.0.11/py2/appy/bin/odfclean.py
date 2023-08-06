'''Removes any formatting within notes in an odt or ods document.'''

# ------------------------------------------------------------------------------
import sys, os.path

from appy.bin.odfgrep import Grep

# ------------------------------------------------------------------------------
CLEAN_OK = '%d styled text part(s) unstyled%s'
C_MULTI  = ' on %d file(s).'
CLEAN_NO = 'No styled text part was found within doc statements.'

# ------------------------------------------------------------------------------
usage = '''Usage: python2 odfclean.py file|folder.

 Updates *file|folder*, that must be the absolute path to an odt or ods pod
 template, or a folder. If it is a single template, it removes any formatting
 within its POD notes. If it is a folder, it does it recursively on any pod
 template (odt or ods) recursively found within that folder.
'''

# ------------------------------------------------------------------------------
class Cleaner:
    '''Cleans notes within an ODT or ODS file'''

    def __init__(self, path):
        self.path = path

    def run(self):
        '''Does the job by (mis)using a Grep instance'''
        # Perform a silly find & replace with a Grep instance (replacing a term
        # with itself): it will also have the effect of cleaning the notes with
        # p_self.path, because it is one of the default tasks performed by Grep.
        term = 'do '
        grep = Grep(term, self.path, repl=term, silent=True)
        grep.run()
        # Print a message
        if grep.cleaned:
            isDir = os.path.isdir(self.path)
            if isDir:
                suffix = C_MULTI % len(grep.matches)
            else:
                suffix = '.'
            print CLEAN_OK % (grep.cleaned, suffix)
        else:
            print CLEAN_NO
        return grep.cleaned

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) !=  2:
        print(usage)
        sys.exit(1)
    Cleaner(*sys.argv[1:]).run()
# ------------------------------------------------------------------------------
