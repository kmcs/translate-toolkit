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

"""simple script to convert a gettext .po localization file to a comma-separated values (.csv) file"""

from translate.storage import po
from translate.storage import csvl10n

class po2csv:
  def convertstring(self, postr):
    unquotedstr = po.getunquotedstr(postr)
    if len(unquotedstr) >= 1 and unquotedstr[:1] in "-+'": unquotedstr = "\\" + unquotedstr
    return unquotedstr

  def convertsource(self,thepo):
    sourceparts = []
    for sourcecomment in thepo.sourcecomments:
      sourceparts.append(sourcecomment.replace("#:","",1).strip())
    return " ".join(sourceparts)

  def convertelement(self,thepo):
    thecsv = csvl10n.csvelement()
    if thepo.isheader():
      thecsv.source = "source"
      thecsv.msgid = "original"
      thecsv.msgstr = "translation"
    elif thepo.isblank():
      return None
    else:
      thecsv.source = self.convertsource(thepo)
      thecsv.msgid = self.convertstring(thepo.msgid)
      # avoid plurals
      msgstr = thepo.msgstr
      if isinstance(msgstr, dict):
        msgstr = thepo.msgstr[0]
      thecsv.msgstr = self.convertstring(msgstr)
    return thecsv

  def convertplurals(self,thepo):
    thecsv = csvl10n.csvelement()
    thecsv.source = self.convertsource(thepo)
    thecsv.msgid = self.convertstring(thepo.msgid_plural)
    thecsv.msgstr = self.convertstring(thepo.msgstr[1])
    return thecsv

  def convertfile(self,thepofile):
    thecsvfile = csvl10n.csvfile()
    for thepo in thepofile.poelements:
      thecsv = self.convertelement(thepo)
      if thecsv is not None:
        thecsvfile.csvelements.append(thecsv)
      if thepo.hasplural():
        thecsv = self.convertplurals(thepo)
        if thecsv is not None:
          thecsvfile.csvelements.append(thecsv)
    return thecsvfile

def convertcsv(inputfile, outputfile, templatefile):
  """reads in inputfile using po, converts using po2csv, writes to outputfile"""
  # note that templatefile is not used, but it is required by the converter...
  inputpo = po.pofile(inputfile)
  if inputpo.isempty():
    return 0
  convertor = po2csv()
  outputcsv = convertor.convertfile(inputpo)
  outputcsvlines = outputcsv.tolines()
  outputfile.writelines(outputcsvlines)
  return 1

def main():
  from translate.convert import convert
  formats = {"po":("csv", convertcsv)}
  parser = convert.ConvertOptionParser(formats, usepots=True, description=__doc__)
  parser.run()

