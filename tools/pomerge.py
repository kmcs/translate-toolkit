#!/usr/bin/env python
# 
# Copyright 2002, 2003 Zuza Software Foundation
# 
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""script that merges .po files and overrides translations"""

import sys
from translate.storage import po
from translate.misc import quote

def readpofile(infile):
  lines = infile.readlines()
  pf = po.pofile()
  pf.fromlines(lines)
  return pf

def writepofile(outfile, pf):
  lines = pf.tolines()
  outfile.writelines(lines)

def mergepofiles(p1, p2, mergeblanks, mergecomments):
  """take any new translations in p2 and write them into p1"""
  for po2 in p2.poelements:
    # there may be more than one entity due to msguniq merge
    entities = []
    for sourcecomment in po2.sourcecomments:
      entities += quote.rstripeol(sourcecomment)[3:].split()
    if len(entities) == 0:
      unquotedid = po.getunquotedstr(po2.msgid)
      po1 = None
      if unquotedid in p1.msgidindex:
        po1 = p1.msgidindex[unquotedid]
      if po1 is None:
        sys.stderr.write("".join(po2.tolines()) + "\n")
      else:
        # finally set the new definition in po1
        po1.merge(po2, overwrite=True)
    for entity in entities:
      po1 = None
      if p1.sourceindex.has_key(entity):
        # now we need to replace the definition of entity with msgstr
        po1 = p1.sourceindex[entity] # find the other po
      # check if this is a duplicate in p2...
      if p2.sourceindex.has_key(entity):
        if p2.sourceindex[entity] is None:
          po1 = None
      # if sourceindex was not unique, use the msgidindex
      if po1 is None:
        unquotedid = po.getunquotedstr(po2.msgid)
        if unquotedid in p1.msgidindex:
          po1 = p1.msgidindex[unquotedid]
      # check if we found a matching po element
      if po1 is None:
        print >>sys.stderr, "# the following po element was not found"
        sys.stderr.write("".join(po2.tolines()) + "\n")
      else:
        if not mergeblanks:
          unquotedstr = po.getunquotedstr(po2.msgstr)
          if len(unquotedstr.strip()) == 0: continue
        # finally set the new definition in po1
        po1.merge(po2, overwrite=True, comments=mergecomments)
  return p1

def str2bool(option):
  option = option.lower()
  if option in ("yes", "true", "1"):
    return True
  elif option in ("no", "false", "0"):
    return False
  else:
    raise ValueError("invalid boolean value: %r" % option)

def mergepo(inputfile, outputfile, templatefile, mergeblanks="no", mergecomments="yes"):
  try:
    mergecomments = str2bool(mergecomments)
  except ValueError:
    raise ValueError("invalid mergecomments value: %r" % mergecomments)
  try:
    mergeblanks = str2bool(mergeblanks)
  except ValueError:
    raise ValueError("invalid mergeblanks value: %r" % mergeblanks)
  inputpo = po.pofile(inputfile)
  if templatefile is None:
    # just merge nothing
    templatepo = po.pofile()
  else:
    templatepo = po.pofile(templatefile)
  templatepo.makeindex()
  inputpo.makeindex()
  outputpo = mergepofiles(templatepo, inputpo, mergeblanks, mergecomments)
  if outputpo.isempty():
    return 0
  outputfile.writelines(outputpo.tolines())
  return 1

def main():
  from translate.convert import convert
  pooutput = ("po", mergepo)
  potoutput = ("pot", mergepo)
  formats = {("po", "po"): pooutput, ("po", "pot"): pooutput, ("pot", "po"): pooutput, ("pot", "pot"): potoutput,
             "po": pooutput, "pot": pooutput}
  mergeblanksoption = convert.optparse.Option("", "--mergeblanks", dest="mergeblanks",
    action="store", default="yes", help="whether to overwrite existing translations with blank translations (yes/no)")
  mergecommentsoption = convert.optparse.Option("", "--mergecomments", dest="mergecomments",
    action="store", default="yes", help="whether to merge comments as well as translations (yes/no)")
  parser = convert.ConvertOptionParser(formats, usetemplates=True, description=__doc__)
  parser.add_option(mergeblanksoption)
  parser.passthrough.append("mergeblanks")
  parser.add_option(mergecommentsoption)
  parser.passthrough.append("mergecomments")
  parser.run()

