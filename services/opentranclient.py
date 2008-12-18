#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of Translate.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import os
import xmlrpclib
import pycurl

from translate.services import restclient
from translate.lang import data

class OpenTranClient(restclient.RESTClient):
    """CRUD operations for TM units and stores"""
    
    def __init__(self, url, target_lang, source_lang="en"):
        restclient.RESTClient.__init__(self)
        self.url = url
        self.target_lang = target_lang
        #detect supported language
        self._issupported(target_lang)

        self.source_lang = source_lang
        
    def translate_unit(self, unit_source, callback=None):
        print "target lang", self.target_lang
        if isinstance(unit_source, unicode):
            unit_source = unit_source.encode("utf-8")

        request_body = xmlrpclib.dumps(
            (unit_source, self.source_lang, self.target_lang), "suggest2")
        request = restclient.RESTClient.Request(
                self.url, unit_source, "POST", request_body)
        request.curl.setopt(pycurl.VERBOSE, 1)
        request.curl.setopt(pycurl.URL, self.url)
        self.add(request)
        if callback:
            request.connect("REST-success", 
                            lambda widget, id, response: callback(widget, id, self.format_suggestions(response)))


    def _handle_language(self, request, language, response):
        (result,), fish = xmlrpclib.loads(response)
        print "result", result
        if result:
            print "found the language", language
            self.target_lang = language
        else:
            lang = data.simplercode(language)
            print language, "failed moving on to", lang
            if lang:
                self._issupported(lang)
        
    def _issupported(self, language):
        print "language", language
        request_body = xmlrpclib.dumps((language,), "supported")
        request = restclient.RESTClient.Request(
            self.url, language, "POST", request_body)
        request.curl.setopt(pycurl.URL, self.url)
        request.curl.setopt(pycurl.VERBOSE, 1)
        self.add(request)
        request.connect("REST-success", self._handle_language)

    def format_suggestions(self, suggestions):
        """clean up open tran suggestion and use the same format as tmserver"""
        (suggestions,), fish = xmlrpclib.loads(suggestions)
        results = []
        for suggestion in suggestions:
            result = {}
            result['target'] = suggestion['text']
            result['source'] = suggestion['projects'][0]['orig_phrase']
            results.append(result)
        return results