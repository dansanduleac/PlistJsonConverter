'''
Plist Json Converter
Licensed under MIT
Copyright (c) 2012 Isaac Muse <isaacmuse@gmail.com>
'''

import sublime
import sublime_plugin
import json
import StringIO
import sys
from os.path import join
from plistlib import readPlist, writePlistToString

lib = join(sublime.packages_path(), 'PlistJsonConverter')
if not lib in sys.path:
    sys.path.append(lib)
from lib.file_strip.json import sanitize_json

ERRORS = {
    "view2plist": "Could not read view buffer as PLIST!\nPlease see console for more info.",
    "plist2json": "Could not convert PLIST to JSON!\nPlease see console for more info.",
    "view2json": "Could not read view buffer as JSON!\nPlease see console for more info.",
    "json2plist": "Could not convert JSON to PLIST!\nPlease see console for more info."
}


def error_msg(msg, e=None):
    sublime.error_message(msg)
    if e != None:
        print "Plist Json Converter Exception:"
        print e


class LanguageConverter(sublime_plugin.TextCommand):
    lang = None
    default_lang = "Packages/Text/Plain text.tmLanguage"
    settings = None

    def __set_syntax(self):
        syntax = sublime.load_settings(self.settings).get(self.lang, self.default_lang) if self.lang != None else self.default_lang
        self.view.set_syntax_file(syntax)

    def read_buffer(self):
        return False

    def convert(self, edit):
        return False

    def run(self, edit):
        if not self.read_buffer():
            if not self.convert(edit):
                self.__set_syntax()


class PlistToJsonCommand(LanguageConverter):
    lang = "json_language"
    default_lang = "Packages/Javascript/JSON.tmLanguage"
    settings = "plist_json_convert.sublime-settings"

    def read_buffer(self):
        errors = False
        try:
            # Ensure view buffer is in a UTF8 format.
            # Wrap string in a file structure so it can be accessed by readPlist
            # Read view buffer as PLIST and dump to Python dict
            self.plist = readPlist(
                StringIO.StringIO(
                    self.view.substr(
                        sublime.Region(0, self.view.size())
                    ).encode('utf8')
                )
            )
        except Exception, e:
            errors = True
            error_msg(ERRORS["view2plist"], e)
        return errors

    def convert(self, edit):
        errors = False
        try:
            if not errors:
                # Convert Python dict to JSON buffer.
                # Replace view with JSON buffer
                self.view.replace(
                    edit,
                    sublime.Region(0, self.view.size()),
                    json.dumps(self.plist, sort_keys=True, indent=4, separators=(',', ': ')).decode('raw_unicode_escape')
                )
        except Exception, e:
            errors = True
            error_msg(ERRORS["plist2json"], e)
        return errors


class JsonToPlistCommand(LanguageConverter):
    lang = "plist_language"
    default_lang = "Packages/XML/XML.tmLanguage"
    settings = "plist_json_convert.sublime-settings"

    def read_buffer(self):
        errors = False
        try:
            # Strip comments and dangling commas from view buffer
            # Read view buffer as JSON
            # Dump data to Python dict
            self.json = json.loads(
                sanitize_json(
                    self.view.substr(
                        sublime.Region(0, self.view.size())
                    ),
                    True
                )
            )

        except Exception, e:
            errors = True
            error_msg(ERRORS["view2json"], e)
        return errors

    def convert(self, edit):
        errors = False
        try:
            # Convert Python dict to PLIST
            # Replace view buffer with PLIST buffer
            self.view.replace(
                edit,
                sublime.Region(0, self.view.size()),
                writePlistToString(self.json).decode('utf8')
            )
        except Exception, e:
            errors = True
            error_msg(ERRORS["json2plist"], e)
        return errors
