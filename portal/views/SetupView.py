#!/usr/bin/python
#
# Copyright 2004 Thomas Fogwill (tfogwill@users.sourceforge.net)
#
# This file is part of the translate web portal.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA	02111-1307	USA

from translate.portal.util import Logging
from translate.portal.util.HTTPUtil import *
from translate.portal.database.model import *
from translate.portal.database import dbhelper

"code to setup the view templates for the translate portal"

def setupGlobal(transaction,tmpl):
    "Global setup - applies to all views"
    from time import *
    Logging.debug("Global view setup func setupGlobal() called")
    tmpl.time = asctime(localtime())

def setupTesting(transaction,tmpl):
    from time import *
    Logging.debug("View setup func setupTesting() called")
    tmpl.name = "Tom"
    
def setupFilelist(transaction,tmpl):
    Logging.debug("View setup func setupFilelist() called")
    tmpl.files = dbhelper.retrieve(File, {}, [File.NAME_COL])
    
def setupFiledetail(transaction,tmpl):
    Logging.debug("View setup func setupFiledetail() called")
    tmpl.file = dbhelper.fetchByPK(File, HTTPRequestParameterWrapper(transaction.request()).getInt("file"))
    
def setupStringdetail(transaction,tmpl):
    Logging.debug("View setup func setupStringdetail() called")
    wrapper = HTTPRequestParameterWrapper(transaction.request())
    tmpl.original = dbhelper.fetchByPK(Original, wrapper.getInt("original"))
    tmpl.editing = wrapper.getString("edit",None)
    tmpl.languages = dbhelper.retrieve(Language, {}, [Language.NAME_COL])
    langid = wrapper.getInt("language",0)    
    tmpl.language = dbhelper.fetchByPK(Language,langid)
    tmpl.languageid = langid    
    if langid > 0:
        tmpl.translations = dbhelper.retrieve(Translation, {
            Translation.ORIGINAL_ID_COL:tmpl.original.id,
            Translation.LANGUAGE_ID_COL:langid
        })
    else:
        tmpl.translations = tmpl.original.getTranslations()
    