#!/usr/bin/env python
#
#  learn.py
#
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

SIGNIFICANT_TOKEN = re.compile(r'[a-zA-Z]')


# find_lcs
def find_lcs(s1, s2):
  # length table: every element is set to zero.
  m = [ [ 0 for x in s2 ] for y in s1 ]
  # direction table: 1st bit for p1, 2nd bit for p2.
  d = [ [ None for x in s2 ] for y in s1 ]
  for p1 in range(len(s1)):
    for p2 in range(len(s2)):
      if s1[p1] == s2[p2]:
        if p1 and p2:
          m[p1][p2] = m[p1-1][p2-1]+1
        else:
          m[p1][p2] = 1
        d[p1][p2] = 3                   # 11: decr. p1 and p2
      elif m[p1-1][p2] < m[p1][p2-1]:
        # we don't have to do the boundery checking.
        # a negative index always gives an intact zero.
        m[p1][p2] = m[p1][p2-1]
        d[p1][p2] = 2                   # 10: decr. p2 only
      else:                             # m[p1][p2-1] < m[p1-1][p2]
        m[p1][p2] = m[p1-1][p2]
        d[p1][p2] = 1                   # 01: decr. p1 only
  (p1, p2) = (len(s1)-1, len(s2)-1)
  # now we traverse the table in reverse order.
  r = []
  while 1:
    c = d[p1][p2]
    if c == 3: r.append((p1,p2))
    if not (p1 and p2 and m[p1][p2]): break
    if c & 2: p2 -= 1
    if c & 1: p1 -= 1
  r.reverse()
  return r


# find_lcs_len:
# faster version of find_lcs, only for calculating similarities.
def find_lcs_len(s1, s2):
  m = [ [ 0 for x in s2 ] for y in s1 ]
  for p1 in range(len(s1)):
    for p2 in range(len(s2)):
      if s1[p1] == s2[p2]:
        if p1 and p2:
          m[p1][p2] = m[p1-1][p2-1]+1
        else:
          m[p1][p2] = 1
      elif m[p1-1][p2] < m[p1][p2-1]:
        m[p1][p2] = m[p1][p2-1]
      else:                             # m[p1][p2-1] < m[p1-1][p2]
        m[p1][p2] = m[p1-1][p2]
  return m[-1][-1]


# choose a wildcard pattern.
def choose_wildcard(strs):
  s = ''.join(strs)
  if s.isdigit():
    return '[0-9]*'
  elif s.isalpha():
    return '[a-zA-Z_]*'
  elif s.isalnum():
    return '[a-zA-Z_0-9]*'
  else:
    return '.*'


# tokenize a log entry.
TOKEN = re.compile(r'[a-zA-Z0-9_]+|.')
def tokenize(s):
  return tuple(TOKEN.findall(s))


# Read the log entries.
def read_log(files, charskip=16):
  import fileinput
  return ( line[charskip:].strip() for line in fileinput.input(files) )


##  Cluster of log entries
##
class Cluster:

  def __init__(self, name, strs, pat=None):
    self.name = name
    self.strs = strs
    self.pat = pat
    return

  def __len__(self):
    return len(self.strs)

  def add(self, s, tokens1, threshold, maxtries=3):
    if self.pat:
      return self.pat.match(s)
    for (i,tokens2) in enumerate(self.strs):
      common = find_lcs_len(tokens1, tokens2)
      score = 2.0*common / (len(tokens1)+len(tokens2))
      if threshold < score:
        self.strs.append(tokens1)
        return True
      # give up after comparing with n entries.
      if maxtries <= i: break
    return False

  def fuse(self, nents=10):
    if self.pat: return
    keys = self.strs[:nents]
    s1 = keys[0]
    for s2 in keys[1:]:
      s1 = [ s1[p1] for (p1,p2) in find_lcs(s1,s2) ]
    idxs = []
    common = set(s1)
    for s2 in keys:
      common.intersection_update(s2)
      idxs.append([ p2 for (p1,p2) in find_lcs(s1,s2) ])
    common = [ t for t in common if SIGNIFICANT_TOKEN.search(t) ]
    idxs = zip(*idxs)
    r = ['^']
    idx0 = (-1,)*len(keys)
    for (i,idx1) in enumerate(idxs):
      unmatched = []
      for (s,i0,i1) in zip(keys,idx0,idx1):
        if i0+1 < i1:
          unmatched.append(''.join(s[i0+1:i1]))
      if unmatched:
        r.append(choose_wildcard(unmatched))
      r.append(re.escape(s1[i]))
      idx0 = idx1
    pat = ''.join(r)
    self.pat = re.compile(pat)
    print (self.name, len(self.strs), pat, common)
    for tokens in keys:
      if tokens:
        print '# %s' % ''.join(tokens)
    print
    return


##  "Greedy" clustering algorithm.
##
def cluster_log(clusters, token2clusters, entries, threshold=0.7, nents=10, verbose=0):
  if verbose == 0:
    stderr.write('Clustering.'); stderr.flush()
  for line in entries:
    tokens = tokenize(line)
    if not tokens: continue
    sig_tokens = [ t for t in tokens if SIGNIFICANT_TOKEN.search(t) ]
    cset = set()
    for t in sig_tokens:
      if t in token2clusters:
        cset.update(token2clusters[t])
    i = 0
    for c in sorted(cset, key=len, reverse=True):
      if c.add(line, tokens, threshold):
        if 0 < verbose:
          print >>stderr, '+%s: %s' % (c.name, line)
        elif verbose == 0:
          stderr.write('.'); stderr.flush()
        if len(c) == nents:
          c.fuse(nents)
        break
    else:
      c = Cluster('type-%d' % len(clusters), [tokens])
      clusters.append(c)
      cset.add(c)
      if 0 < verbose:
        print >>stderr, '!%s: %s' % (c.name, line)
      elif verbose == 0:
        stderr.write('+'); stderr.flush()
    for t in sig_tokens:
      token2clusters[t] = cset
  if 0 <= verbose:
    stderr.write('\n'); stderr.flush()
  return clusters


##  read_clusters
##
def read_clusters(clusters, token2clusters, fname):
  fp = file(fname)
  for line in fp:
    line = line.strip()
    if not line or line.startswith('#'):
      pass
    elif line.startswith('('):
      (name, freq, pat, tokens) = eval(line)
      c = Cluster(name, [None]*freq, re.compile(pat))
      for t in tokens:
        if t not in token2clusters:
          token2clusters[t] = set()
        token2clusters[t].add(c)
      clusters.append(c)
    else:
      print >>stderr, 'Invalid line: %r' % line
  fp.close()
  return


# main
def main(argv):
  import getopt
  def usage():
    print 'usage: %s [-v|-q] [-c charskip] [-n num_entries] [-t similarity_threshold] [-p pattern_file] [file ...]' % argv[0]
    return 100
  try:
    (opts, args) = getopt.getopt(argv[1:], 'vqc:n:t:p:')
  except getopt.GetoptError:
    return usage()
  verbose = 0
  nents = 10
  charskip = 16
  threshold = 0.7
  clusters = []
  token2clusters = {}
  for (k, v) in opts:
    if k == '-v': verbose += 1
    elif k == '-q': verbose -= 1
    elif k == '-c': charskip = int(v)
    elif k == '-n': nents = int(v)
    elif k == '-t': threshold = float(v)
    elif k == '-p': read_clusters(clusters, token2clusters, v)
  entries = read_log(args, charskip)
  clusters = cluster_log(clusters, token2clusters, entries, threshold, nents, verbose)
  for c in sorted(clusters, key=len, reverse=True):
    c.fuse(nents)
  return 0

if __name__ == '__main__': sys.exit(main(sys.argv))

