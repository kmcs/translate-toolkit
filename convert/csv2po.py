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

"""simple script to convert a comma-separated values (.csv) file to a gettext .po localization file 
reads from stdin, currently writes rows to stdout"""

import sys
from translate.misc import quote
from translate.storage import po
from translate.storage import csvl10n

class csv2po:
  def convertstrings(self,thecsv,thepo):
    # currently let's just get the source, msgid and msgstr back
    thepo.sourcecomments = ["#: " + thecsv.source + "\n"]
    thepo.msgid = [quote.quotestr(line) for line in thecsv.msgid.split('\n')]
    thepo.msgstr = [quote.quotestr(line) for line in thecsv.msgstr.split('\n')]

  def convertelement(self,thecsv):
     thepo = po.poelement()
     self.convertstrings(thecsv,thepo)
     return thepo

  def convertfile(self,thecsvfile):
    thepofile = po.pofile()
    for thecsv in thecsvfile.csvelements:
      thepo = self.convertelement(thecsv)
      if thepo is not None:
        thepofile.poelements.append(thepo)
    return thepofile

def convert(fromfileclass,convertorclass):
  """reads in stdin using fromfileclass, converts using convertorclass, writes to stdout"""
  filelines = sys.stdin.readlines()
  fromfile = fromfileclass()
  fromfile.fromlines(filelines)
  convertor = convertorclass()
  tofile = convertor.convertfile(fromfile)
  tolines = tofile.tolines()
  sys.stdout.writelines(tolines)

if __name__ == '__main__':
  convert(csvl10n.csvfile,csv2po)
  

