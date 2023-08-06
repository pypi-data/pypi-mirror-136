'''This script allows to perform a "grep" command that will be applied on files
   content.xml and styles.xml within all ODF files (odt and ods) found within a
   given folder.'''

# ------------------------------------------------------------------------------
from UserList import UserList
import re, sys, os.path, StringIO

from appy import Object as O
from appy.shared.zip import zip, unzip
from appy.shared import utils as sutils

# ------------------------------------------------------------------------------
OPT_C_V  = "Options -c and -v can't be use altogether."
FF_KO    = '%s does not exist.'
S_CLEAN  = '%d styled text part(s) %scleaned.'

# ------------------------------------------------------------------------------
usage = '''Usage: python odfgrep.py [options] keyword file|folder [repl].

 *keyword* is the regular expression (or string if -s) to search within the
           file(s).

 If *file* is given, it is the path to an ODF file (odt or ods). grep will be
 run on this file only.

 If *folder* is given, the grep will be run on all ODF files found in this
 folder and sub-folders.

 If *repl* is given, within matched ODF files, *keyword* will be replaced with
 *repl*.

 OPTIONS

 -v : *v*erbose: dump more info about the find/replace zones (only available if
      option "-c" is not used, see below.

 -d : *d*ry-run: in the context of a replacement, if this option is set, no
      replacement will actually be performed, but output will give info
      (detailed if -v, minimal if not) about what replacements would have been
      performed without this option.

 -c : in *c*ontent. If unset, the find/replace process will only apply to the
      POD-controlled zones of POD template(s): notes and fields. If the option
      is set, it will occur in any part of the template(s).

 -s : by default, *keyword* is interpreted as a regular expression. If you want
      it to be a plain *s*tring instead, set this option.

 IMPORTANT NOTES

 (1) The *repl*acement string may contain references to groups possibly defined
      within the *keyword* regular expression, but only via the "\<nb>"
      notation.

      For example, if *keyword* is cus(tom)_(agenda) and *repl* is \2_\1,
      every match will be replaced with tom_agenda.

 (2) From the command-line, *keyword* and *repl* special chars must be escaped.
     For example, cus(tom)_(agenda) must be written as  cus\(tom\)_\(agenda\)
                  \\2_\\1             must be written as  \\\\2_\\\\1
'''

# ------------------------------------------------------------------------------
class Match:
    '''When a Grep is ran with inContent=False (see class c_Grep), one of its
       outputs is the list of matches within every found ODF document. Every
       match is represented by an instance of class Match.'''

    # Regular expression for parsing elements within an ODF note
    noteRex = re.compile('.*?(<dc:creator>.*?</dc:creator>)?' \
                         '<dc:date>(.*?)</dc:date>(.*)', re.S)

    # Regular expression for parsing paragraphs within a note
    pRex = re.compile('<text:p[^>]*>(.*?)</text:p>')

    def __init__(self, keyword, tag, content, patched=None, dryRun=False):
        # The matched keyword (as a string)
        self.keyword = keyword
        # The precise matched tag
        self.tag = tag
        # The type of tag (= "target") whose content has been (or could be)
        # patched.
        self.target = tag == 'office:annotation' and 'note' or 'field'
        # Note-specific metadata
        self.date = None
        self.creator = None
        self.initials = None
        # The original content of this tag
        self.originalContent = content
        # Within this original content, get the "payload", being the part of the
        # content containing the POD code.
        self.originalPayload = None
        # In the context of a replacement, the version of p_content after
        # replacements were done.
        if patched is not None:
            self.patched = self.parseContent(patched, storeResult=False)
        else:
            self.patched = None
        # Are we in the context of a dry run ?
        self.dryRun = dryRun
        self.parseContent(content, storeResult=True)

    def unescape(self, content):
        '''Unescape special chars from p_content'''
        return content.replace('&apos;', "'")

    def parseNote(self, note):
        '''Parses the raw content of this p_note and return its parts'''
        match = self.noteRex.match(note)
        creator, date, payload = match.groups()
        if creator: creator = creator[12:-13]
        creator = creator or 'unknown'
        # Extract content from every text:p tag
        payload = self.unescape('\n'.join(self.pRex.findall(payload)))
        return creator, date, payload

    def parseField(self, field):
        '''Parses the content of this ODF p_field'''
        # Remove the end of the start tag
        i = field.find('>')
        return self.unescape(field[i+1:])

    def parseContent(self, content, storeResult):
        '''Parses this p_content. If p_storeResult is True, p_content is the
           original content of a POD zone, and this method stores the parsed
           parts on p_self. Else, it parses p_content, does not store anything
           on p_self and returns the p_content's payload.'''
        if self.target == 'note':
            parts = self.parseNote(content)
            r = parts[2]
            if storeResult:
                self.creator, self.date, self.content = parts
        elif self.target == 'field':
            r = self.parseField(content)
            if storeResult:
                self.content = r
        else:
            r = content
            if storeResult:
                self.content = r
        return r

    def __repr__(self, spaces=2, nb=None):
        '''p_self's string representation'''
        sep = ' ' * spaces
        if self.target == 'note':
            part = '\n%sBy %s on %s' % (sep, self.creator, self.date)
        else:
            part = ''
        if self.patched is not None:
            verb = self.dryRun and 'Would have' or 'Has'
            srepl = '\n\n  %s been replaced with:\n\n%s' % (verb, self.patched)
        else:
            srepl = ''
        return '%sMatch::on::%s (tag %s)\n%sKeyword(s): %s%s\n%sOriginal ' \
               'content:\n\n%s%s' % (sep, self.target, self.tag, sep,
                                     self.keyword, part, sep, self.content,
                                     srepl)

# ------------------------------------------------------------------------------
class Matches(UserList):
    '''List of Match instances found in a given file'''

    def __init__(self, fileName, *args, **kwargs):
        UserList.__init__(self, *args, **kwargs)
        self.fileName = fileName

    def __repr__(self):
        '''p_self's string representation'''
        if len(self) == 1:
            prefix = '1 match'
        else:
            prefix = '%d matches' % len(self)
        r = [':: %s for %s ::' % (prefix, self.fileName)]
        i = 0
        for match in self:
            i += 1
            r.append(match.__repr__(nb=i))
        return '%s\n' % '\n\n'.join(r)

# ------------------------------------------------------------------------------
class Grep:
    toGrep = ('content.xml', 'styles.xml')
    toUnzip = ('.ods', '.odt')

    # Messages ~{ b_replace: { b_match: s_message }}~
    messageTexts = { True:  {True:  '%s: %d replacement(s) done.',
                             False: 'No replacement was made.'},
                     False: {True:  '%s matches %d time(s).',
                             False: 'No match found.'}}

    # ODF tags used by POD statements or expressions
    podTags = ('office:annotation', 'text:conditional-text', 'text:text-input')

    # Regex used to remove formatting possibly found in notes
    spanRex = re.compile('<text:span[^>]*>(.*?)</text:span>')

    # Regex allowing to detect mentions, in the replacement string, to groups
    # defined in the keywords regex.
    groupsRex = re.compile('\\\(\d)+')

    def __init__(self, keyword, fileOrFolder, repl=None, inContent=False,
                 silent=None, verbose=False, dryRun=False, asString=False):
        # Create a regex from the passed p_keyword
        self.skeyword = keyword
        if asString:
            # Keyword must be interpreted as a raw string and not a regex
            keyword = re.escape(keyword)
        self.keyword = re.compile(keyword, re.S)
        # The file or folder where to find POD templates
        self.fileOrFolder = fileOrFolder
        # A temp folder where to unzip the POD templates
        self.tempFolder = sutils.getOsTempFolder()
        # (optional) The replacement text
        self.repl = repl
        # (optional) Find/replace p_keyword in raw ODF content, or in POD-
        #            controlled zones (fields, statements) ?
        self.zoneRex = self.getZoneRex(inContent)
        # Must lists of matches be built for every found ODF document ?
        if not inContent:
            # Yes
            self.matches = {} # ~{s_filePath:[Match]}~
        # If called programmatically, we don't want any output on stdout
        self.silent = silent
        if silent:
            self.messages = []
        # When replacing, count the number of styled text parts whose style was
        # removed (see m_cleanNote).
        self.cleaned = 0
        # Verbose output ?
        self.verbose = verbose
        # In dry-run mode, a replacement is not truly done: output indicates
        # what replacement(s) would have been performed.
        self.dryRun = dryRun

    def getZoneRex(self, inContent):
        '''Return, if p_inContent is False, the regex representing pod zones
           within content|styles.xml.'''
        if inContent: return
        # Build the regex
        tags = []
        for tag in self.podTags:
            tags.append('(?:%s)' % tag)
        tags = '|'.join(tags)
        # Negative lookahead assertion (?!-) is used to prevent matching tag
        # "office:annotation-end".
        return re.compile('<(?P<tag>%s)(?!-)(.*?)</(?P=tag)>' % tags, re.S)

    def dump(self, message, raiseError=False):
        '''Dumps a p_message, either on stdout or in self.messages if we run in
           silent mode.'''
        # Raise an exception if requested
        if raiseError: raise Exception(message)
        # Log or store the p_message, depending on p_silent
        if self.silent:
            self.messages.append(message)
        else:
            print(message)

    def getMessage(self):
        '''Returns self.messages, concatenated in a single string'''
        messages = getattr(self, 'messages', None)
        if not messages: return ''
        return '\n'.join(messages)

    def getReplacement(self, match, counts=None):
        '''In the context of a replacement, this method returns p_self.repl,
           that will replace the matched p_self.keyword. In the context of a
           simple grep, the method returns the matched content, left untouched.
           In both contexts, p_counts about matches are updated.'''
        if counts is not None:
            counts.inXml += 1
        if self.repl:
            fun = lambda m: match.group(int(m.group(1)))
            r = self.groupsRex.sub(fun, self.repl)
        else:
            # The replacement has just been triggered to build self.matches.
            # Return the matched zone unchanged.
            r = match.group(0)
        return r

    def cleanStyle(self, match):
        '''A styled text part has been found in p_match. Clean it and update the
           count in p_self.cleaned.'''
        if self.repl:
            self.cleaned += 1
        return match.group(1)

    def cleanNote(self, note):
        '''Returns the content of this p_note, where any formatting has been
           removed.'''
        return self.spanRex.sub(self.cleanStyle, note)

    def addMatch(self, fileName, imatch):
        '''Adds this p_imatch concerning this p_fileName among p_self.matches'''
        matches = self.matches
        if fileName in matches:
            matches[fileName].append(imatch)
        else:
            matches[fileName] = Matches(fileName, [imatch])
        
    def findIn(self, fileName, match, counts):
        '''A POD zone has been found, in m_match, in a file whose name is
           p_fileName. Perform replacements within this zone.'''
        # Remember the current count of matches
        initialCount = counts.inXml
        initialCleaned = self.cleaned
        originalContent = match.group(0)
        tag = match.group(1)
        content = match.group(2)
        if tag == 'office:annotation':
            # Ensure there is no formatting in the note before applying the
            # replacement.
            content = self.cleanNote(content)
        r = self.keyword.sub(lambda m: self.getReplacement(m, counts), content)
        if counts.inXml > initialCount:
            # self.keyword has matched. Create a Match instance.
            if self.repl:
                patched = r # A true replacement was done
            else:
                patched = None # There was a match, but v_r repeats v_content,
                               # because we are not in the context of a
                               # replacement.
            self.addMatch(fileName, Match(self.skeyword, tag, content,
                                          patched, self.dryRun))
            # Count the number of match instead of the number of individual
            # replacements.
            counts.inXml = initialCount + 1
        else:
            # Cleaning for this file will finally not be applied, so set the
            # count to the one that existed before managing this file.
            self.cleaned = initialCleaned
        return '<%s%s</%s>' % (tag, r, tag)

    def grepFileContent(self, fileName, tempFolder, contents):
        '''Finds self.keyword among p_tempFolder/content.xml and
           p_tempFolder/styles.xml, whose content is in p_contents and was
           extracted from p_fileName, and return the number of matches. If
           Match objects must be built, p_self.matches are updated accordingly.

           If self.repl is there, and if there is at least one match, the method
           replaces self.keyword by self.repl for all matches, re-zips the ODF
           file whose parts are in p_tempFolder and overwrites the original file
           in p_fileName.'''
        # Initialise counts
        counts = O(
          inXml  = 0, # The number of matches within the currently analysed XML
                      # file (content.xml or styles.xml), within p_fileName.
          inFile = 0, # The number of matches within p_fileName (sums all inner
                      # counts from content.xml and styles.xml)
        )
        zoneRex = self.zoneRex
        for name in self.toGrep:
            # Get the file content
            content = contents[name]
            # Step #1: find (and potentially replace) matches in the content of
            #          the file as loaded in a string, in v_content...
            if not zoneRex:
                # ... either in the full document ...
                found = self.keyword.findall(content)
                if not found: continue
                counts.inXml = len(found)
                if self.repl:
                    # Make the replacement
                    fun = lambda match: self.getReplacement()
                    content = self.keyword.sub(fun, content)
            else:
                # ... or within every POD expression or statement
                counts.inXml = 0 # Reinitialise the XML count
                fun = lambda match: self.findIn(fileName, match, counts)
                content = self.zoneRex.sub(fun, content)
                if not counts.inXml: continue
            counts.inFile += counts.inXml
            # Step #2: actually perform replacements on the file on disk, if a
            #          p_self.repl(acement) is required and if at least one
            #          replacement can be performed.
            if counts.inXml and self.repl and not self.dryRun:
                # Overwrite the file on disk
                tempFileName = os.path.join(tempFolder, name)
                f = open(tempFileName, 'w')
                f.write(content)
                f.close()
        # Re-zip the result when relevant
        if counts.inFile and self.repl:
            zip(fileName, tempFolder, odf=True)
        return counts.inFile

    def grepFile(self, fileName):
        '''Unzip the .xml files from file named p_fileName and perform a grep on
           it.'''
        # Unzip the file in the temp folder
        tempFolder = sutils.getOsTempFolder(sub=True)
        # Unzip the file in its entirety
        contents = unzip(fileName, tempFolder, odf=True)
        nb = self.grepFileContent(fileName, tempFolder, contents)
        if nb and not self.verbose:
            # If verbose, Match instances will all be dumped at the end
            msg = self.messageTexts[bool(self.repl)][bool(nb)] % (fileName, nb)
            self.dump(msg)
        # Delete the temp folder
        sutils.FolderDeleter.delete(tempFolder)
        return nb

    def run(self):
        '''Performs the "grep" on self.fileOrFolder. If called by RamGrep, it
           outputs messages on stdout. Else, it dumps it in self.messages.'''
        nb = 0
        if os.path.isfile(self.fileOrFolder):
            nb += self.grepFile(self.fileOrFolder)
        elif os.path.isdir(self.fileOrFolder):
            # Grep on all files found in this folder
            for dir, dirnames, filenames in os.walk(self.fileOrFolder):
                for name in filenames:
                    if os.path.splitext(name)[1] in self.toUnzip:
                        nb += self.grepFile(os.path.join(dir, name))
        else:
            self.dump(FF_KO % self.fileOrFolder)
        if not nb:
            self.dump(self.messageTexts[bool(self.repl)][False])
        elif self.verbose:
            # Dump the match instances
            for match in self.matches.itervalues():
                self.dump(repr(match))
        if self.cleaned:
            verb = self.dryRun and 'would have been ' or ''
            self.dump(S_CLEAN % (self.cleaned, verb))
        return nb

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    # Get options
    args = sys.argv
    options = {}
    if '-c' in args: # Find/replace in content or in POD zones ?
        args.remove('-c')
        options['inContent'] = True
    if '-v' in args: # verbose
        args.remove('-v')
        options['verbose'] = True
    if '-d' in args: # Dry-run (replace)
        args.remove('-d')
        options['dryRun'] = True
    if '-s' in args: # Keyword is interpreted as a string and not a regex
        args.remove('-s')
        options['asString'] = True
    # Check args validity
    if len(sys.argv) not in (3, 4, 5):
        print(usage)
        sys.exit()
    if 'verbose' in options and 'inContent' in options:
        print OPT_C_V
        sys.exit()
    Grep(*sys.argv[1:], **options).run()
# ------------------------------------------------------------------------------
