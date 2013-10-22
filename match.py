#!/usr/bin/env python
#
#
#  match.py
#  Copyright (c) 2007  Yusuke Shinyama <yusuke at cs dot nyu dot edu>
#  
#  Permission is hereby granted, free of charge, to any person
#  obtaining a copy of this software and associated documentation
#  files (the "Software"), to deal in the Software without
#  restriction, including without limitation the rights to use,
#  copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following
#  conditions:
#  
#  The above copyright notice and this permission notice shall be
#  included in all copies or substantial portions of the Software.
#  
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
#  KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
#  WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
#  PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import sys, re
stdout = sys.stdout
stderr = sys.stderr

# scan the logs
def match(charskip, pats, args):
  import fileinput
  for line in fileinput.input(args):
    line = line.strip()
    s = line[charskip:]
    for (pat,name) in pats:
      if pat.search(s): break
    else:
      name = 'unknown'
    print '%s: %s' % (name, line)
  return


def main(argv):
  import getopt
  def usage():
    print 'usage: %s [-c charskip] [-t freq_threshold] patfile [file ...]' % argv[0]
    return 100
  try:
    (opts, args) = getopt.getopt(argv[1:], 'c:t:')
  except getopt.GetoptError:
    return usage()
  charskip = 16
  threshold = 0
  for (k, v) in opts:
    if k == '-c': charskip = int(v)
    elif k == '-t': threshold = int(v)
  if not args: return usage()
  
  patfile = args.pop(0)
  # read the pattern file
  fp = file(patfile)
  pats = []
  for line in fp:
    line = line.strip()
    if not line or line.startswith('#'):
      pass
    elif line.startswith('('):
      (name, freq, pat, _) = eval(line)
      if threshold <= freq:
        pats.append((re.compile(pat), name))
    else:
      print >>stderr, 'Invalid line: %r' % line
  fp.close()
  match(charskip, pats, args)
  return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
