'''
Plist Json Converter
Licensed under MIT
Copyright (c) 2012 Isaac Muse <isaacmuse@gmail.com>
'''

import sublime
import sublime_plugin
import json
from io import StringIO
import sys
import re
from os.path import exists, splitext, basename
import codecs

PACKAGE_SETTINGS = "plist_json_convert.sublime-settings"

# if sublime.platform() == "linux":
#     # Try and load Linux Python2.6 lib.  Default path is for Ubuntu.
#     linux_lib = sublime.load_settings(PACKAGE_SETTINGS).get("linux_python2.6_lib", "/usr/lib/python2.6/lib-dynload")
#     if not linux_lib in sys.path and exists(linux_lib):
#         sys.path.append(linux_lib)
from plistlib import readPlistFromBytes, writePlistToBytes

from PlistJsonConverter.PlistJsonConverterLib.file_strip.json import sanitize_json

ERRORS = {
    "view2plist": "Could not read view buffer as PLIST!\nPlease see console for more info.",
    "plist2json": "Could not convert PLIST to JSON!\nPlease see console for more info.",
    "view2json": "Could not read view buffer as JSON!\nPlease see console for more info.",
    "json2plist": "Could not convert JSON to PLIST!\nPlease see console for more info.",
    "filewrite": "Could not write file!\nPlease see console for more info.",
    "bufferwrite": "Could not write view buffer!\nPlease see console for more info."
}


def error_msg(msg, e=None):
    sublime.error_message(msg)
    if e != None:
        print("Plist Json Converter Exception:")
        print(e)


class LanguageConverter(sublime_plugin.TextCommand):
    lang = None
    default_lang = "Packages/Text/Plain text.tmLanguage"
    settings = None

    def __set_syntax(self):
        if self.output_view != None:
            # Get syntax language and set it
            syntax = sublime.load_settings(self.settings).get(self.lang, self.default_lang) if self.lang != None else self.default_lang
            self.output_view.set_syntax_file(syntax)

    def __write_file(self, edit):
        errors = False
        # Get current view's filename
        filename = self.view.file_name()
        save_filename = self.get_output_file(filename) if filename != None and exists(filename) else None

        if save_filename != None:
            # Save content to UTF file
            try:
                with codecs.open(save_filename, "w", "utf-8") as f:
                    f.write(self.output)
                self.output_view = self.view.window().open_file(save_filename)
            except Exception as e:
                errors = True
                error_msg(ERRORS["filewrite"], e)
            if not errors:
                self.__set_syntax()
        else:
            # Could not acquire a name that exists on disk
            # Fallback to buffer write
            self.__write_buffer(edit, force_new_buffer=True)

    def __write_buffer(self, edit, force_new_buffer=False):
        errors = False
        new_buffer = bool(sublime.load_settings(self.settings).get("open_in_new_buffer", False))

        # Save content to view buffer
        try:
            self.output_view = self.view.window().new_file() if new_buffer or force_new_buffer else self.view
            self.output_view.replace(
                edit,
                sublime.Region(0, self.view.size()),
                self.output.decode('utf-8')
            )
        except Exception as e:
            errors = True
            error_msg(ERRORS["bufferwrite"], e)

        if not errors:
            if new_buffer or force_new_buffer:
                # If a name can be acquired from the original view, give buffer a modified derivative of the name
                filename = self.view.file_name()
                buffer_name = basename(self.get_output_file(filename)) if filename != None else None
                if buffer_name != None:
                    self.output_view.set_name(buffer_name)
            self.__set_syntax()

    def is_enabled(self, save_to_file=False):
        enabled = True
        if save_to_file and not bool(sublime.load_settings(self.settings).get("enable_save_to_file_commands", False)):
            enabled = False
        elif not save_to_file and not bool(sublime.load_settings(self.settings).get("enable_show_in_buffer_commands", False)):
            enabled = False
        return enabled

    def get_output_file(self, filename):
        return self.view

    def read_buffer(self):
        return False

    def convert(self, edit):
        return False

    def run(self, edit, save_to_file=False):
        if not self.read_buffer():
            if not self.convert(edit):
                if save_to_file:
                    self.__write_file(edit)
                else:
                    self.__write_buffer(edit)


class PlistToJsonCommand(LanguageConverter):
    lang = "json_language"
    default_lang = "Packages/Javascript/JSON.tmLanguage"
    settings = PACKAGE_SETTINGS

    def get_output_file(self, filename):
        name = None

        # Try and find file ext in the ext table
        ext_tbl = sublime.load_settings(self.settings).get("conversion_ext", [])
        for ext in ext_tbl:
            m = re.match("^(.*)\\." + ext["plist"] + "$", filename, re.IGNORECASE)
            if m != None:
                name = m.group(1) + "." + ext["json"]
                break

        # Could not find ext in table, replace current extension with default
        if name == None:
            name = splitext(filename)[0] + ".JSON"
        return name

    def read_buffer(self):
        errors = False
        try:
            # Ensure view buffer is in a UTF8 format.
            # Wrap string in a file structure so it can be accessed by readPlist
            # Read view buffer as PLIST and dump to Python dict
            self.plist = readPlistFromBytes(
                self.view.substr(
                    sublime.Region(0, self.view.size())
                ).encode('utf8')
            )
        except Exception as e:
            errors = True
            error_msg(ERRORS["view2plist"], e)
        return errors

    def convert(self, edit):
        errors = False
        try:
            if not errors:
                # Convert Python dict to JSON buffer.
                self.output = json.dumps(self.plist, sort_keys=True, indent=4, separators=(',', ': ')).encode('utf-8').decode('raw_unicode_escape')
        except Exception as e:
            errors = True
            error_msg(ERRORS["plist2json"], e)
        return errors


class JsonToPlistCommand(LanguageConverter):
    lang = "plist_language"
    default_lang = "Packages/XML/XML.tmLanguage"
    settings = PACKAGE_SETTINGS

    def get_output_file(self, filename):
        name = None

        # Try and find file ext in the ext table
        ext_tbl = sublime.load_settings(self.settings).get("conversion_ext", [])
        for ext in ext_tbl:
            m = re.match("^(.*)\\." + ext["json"] + "$", filename, re.IGNORECASE)
            if m != None:
                name = m.group(1) + "." + ext["plist"]
                break

        # Could not find ext in table, replace current extension with default
        if name == None:
            name = splitext(filename)[0] + ".plist"
        return name

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

        except Exception as e:
            errors = True
            error_msg(ERRORS["view2json"], e)
        return errors

    def convert(self, edit):
        errors = False
        try:
            # Convert Python dict to PLIST buffer
            self.output = writePlistToBytes(self.json)
        except Exception as e:
            errors = True
            error_msg(ERRORS["json2plist"], e)
        return errors
