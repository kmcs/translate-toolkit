#!/usr/bin/env python

from jToolkit.widgets import widgets
from jToolkit.widgets import table
from translate.pootle import pagelayout

class TranslatePage(pagelayout.PootlePage):
  """the page which lets people edit translations"""
  def __init__(self, project, session, argdict, dirfilter=None):
    self.argdict = argdict
    self.dirfilter = dirfilter
    self.project = project
    self.matchnames = self.getmatchnames(self.project.checker)
    self.searchtext = self.argdict.get("searchtext", "")
    # TODO: fix this in jToolkit
    if isinstance(self.searchtext, unicode):
      self.searchtext = self.searchtext.encode("utf8")
    self.translationsession = self.project.gettranslationsession(session)
    self.instance = session.instance
    self.pofilename = None
    self.lastitem = None
    self.receivetranslations()
    self.viewmode = self.argdict.get("view", 0)
    self.finditem()
    translations = self.gettranslations()
    self.maketable(translations)
    searchcontextinfo = widgets.HiddenFieldList({"searchtext": self.searchtext})
    contextinfo = widgets.HiddenFieldList({"pofilename": self.pofilename})
    translateform = widgets.Form([self.transtable, searchcontextinfo, contextinfo], {"name": "translate", "action":""})
    title = "Pootle: translating %s into %s: %s" % (self.project.projectname, self.project.languagename, self.pofilename)
    if self.viewmode:
      pagelinks = []
      if self.firstitem > 0:
        linkitem = max(self.firstitem - 10, 0)
        pagelinks.append(widgets.Link("?translate=1&view=1&item=%d" % linkitem, "Previous %d" % (self.firstitem - linkitem)))
      if self.firstitem + len(translations) < self.project.getpofilelen(self.pofilename):
        linkitem = self.firstitem + 10
        itemcount = min(self.project.getpofilelen(self.pofilename) - linkitem, 10)
        pagelinks.append(widgets.Link("?translate=1&view=1&item=%d" % linkitem, "Next %d" % itemcount))
      pagelinks = pagelayout.IntroText(pagelinks)
    else:
      pagelinks = []
    translatediv = pagelayout.TranslateForm([pagelinks, translateform])
    pagelayout.PootlePage.__init__(self, title, translatediv, session, bannerheight=81)
    self.addfilelinks(self.pofilename, self.matchnames)
    if dirfilter and dirfilter.endswith(".po"):
      currentfolder = "/".join(dirfilter.split("/")[:-1])
    else:
      currentfolder = dirfilter
    self.addfolderlinks("current folder", currentfolder, "index.html")
    autoexpandscript = widgets.Script('text/javascript', '', newattribs={'src': self.instance.baseurl + 'js/autoexpand.js'})
    self.headerwidgets.append(autoexpandscript)

  def addfilelinks(self, pofilename, matchnames):
    """adds a section on the current file, including any checks happening"""
    searchcontextinfo = widgets.HiddenFieldList({"pofilename": self.pofilename})
    self.addsearchbox(self.searchtext, searchcontextinfo)
    self.links.addcontents(pagelayout.SidebarTitle("current file"))
    self.links.addcontents(pagelayout.SidebarText(pofilename))
    if matchnames:
      checknames = [matchname.replace("check-", "", 1) for matchname in matchnames]
      self.links.addcontents(pagelayout.SidebarText("checking %s" % ", ".join(checknames)))
    postats = self.project.getpostats(self.pofilename)
    blank, fuzzy = postats["blank"], postats["fuzzy"]
    translated, total = postats["translated"], postats["total"]
    self.links.addcontents(pagelayout.SidebarText("%d/%d translated\n(%d blank, %d fuzzy)" % (translated, total, blank, fuzzy)))

  def receivetranslations(self):
    """receive any translations submitted by the user"""
    skip = "skip" in self.argdict
    for key, value in self.argdict.iteritems():
      if key.startswith("trans"):
        try:
          item = int(key.replace("trans",""))
        except:
          continue
        # submit the actual translation back to the project...
        self.pofilename = self.argdict["pofilename"]
	if skip:
          self.translationsession.skiptranslation(self.pofilename, item)
	else:
          self.translationsession.receivetranslation(self.pofilename, item, value)
        self.lastitem = item

  def getmatchnames(self, checker): 
    """returns any checker filters the user has asked to match..."""
    matchnames = []
    for checkname in self.argdict:
      if checkname in ["fuzzy", "blank", "translated"]:
        matchnames.append(checkname)
      elif checkname in checker.getfilters():
        matchnames.append("check-" + checkname)
    matchnames.sort()
    return matchnames

  def addtransrow(self, rownum, origcell, transcell):
    self.transtable.setcell(rownum, 0, origcell)
    self.transtable.setcell(rownum, 1, transcell)

  def maketable(self, translations):
    self.transtable = table.TableLayout({"class":"translate-table", "cellpadding":10})
    origtitle = table.TableCell("original", {"class":"translate-table-title"})
    transtitle = table.TableCell("translation", {"class":"translate-table-title"})
    self.addtransrow(-1, origtitle, transtitle)
    translations = self.gettranslations()
    self.textcolors = ["#000000", "#000060"]
    for row, (orig, trans) in enumerate(translations):
      thisitem = self.firstitem + row
      self.addtranslationrow(thisitem, orig, trans, thisitem in self.editable)
    self.transtable.shrinkrange()
    return self.transtable

  def finditem(self):
    """finds the focussed item for this page, searching as neccessary"""
    item = self.argdict.get("item", None)
    if item is None:
      try:
        self.pofilename, self.item = self.project.searchpoitems(self.pofilename, self.lastitem, self.matchnames, self.dirfilter, self.searchtext).next()
      except StopIteration:
        if self.translationsession.lastitem is None:
          raise StopIteration("There are no items matching that search")
        else:
          raise StopIteration("You have finished going through the items you selected")
    else:
      if not item.isdigit():
        raise ValueError("Invalid item given")
      self.item = int(item)
      self.pofilename = self.argdict.get("pofilename", self.dirfilter)

  def gettranslations(self):
    """gets the list of translations desired for the view, and sets editable and firstitem parameters"""
    if self.viewmode:
      self.editable = []
      self.firstitem = self.item
      return self.project.getitems(self.pofilename, self.item, self.item+10)
    else:
      self.editable = [self.item]
      self.firstitem = max(self.item - 3, 0)
      return self.project.getitems(self.pofilename, self.item-3, self.item+4)

  def getorigcell(self, row, orig, editable):
    origclass = "translate-original "
    if editable:
      origclass += "translate-original-focus "
    else:
      origclass += "autoexpand "
    origdiv = widgets.Division([], "orig%d" % row, cls=origclass)
    origtext = widgets.Font(orig, {"color":self.textcolors[row % 2]})
    origdiv.addcontents(origtext)
    return table.TableCell(origdiv, {"class":"translate-original"})

  def gettranscell(self, row, trans, editable):
    transclass = "translate-translation "
    if not editable:
      transclass += "autoexpand "
    transdiv = widgets.Division([], "trans%d" % row, cls=transclass)
    if editable:
      if isinstance(trans, str):
        trans = trans.decode("utf8")
      textarea = widgets.TextArea({"name":"trans%d" % row, "rows":3, "cols":40}, contents=trans)
      skipbutton = widgets.Input({"type":"submit", "name":"skip", "value":"skip"}, "skip")
      submitbutton = widgets.Input({"type":"submit", "name":"submit", "value":"submit"}, "submit")
      contents = [textarea, skipbutton, submitbutton]
    else:
      text = pagelayout.TranslationText(widgets.Font(trans, {"color":self.textcolors[row % 2]}))
      editlink = pagelayout.TranslateActionLink("?translate=1&item=%d&pofilename=%s" % (row, self.pofilename), "Edit", "editlink%d" % row)
      contents = [text, editlink]
    transdiv.addcontents(contents)
    return table.TableCell(transdiv, {"class":"translate-translation"})

  def addtranslationrow(self, row, orig, trans, editable=False):
    """returns an origcell and a transcell for displaying a translation"""
    origcell = self.getorigcell(row, orig, editable)
    transcell = self.gettranscell(row, trans, editable)
    self.addtransrow(row, origcell, transcell)

