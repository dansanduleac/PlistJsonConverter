# About
A plugin for Sublime Text that can convert PLIST XMLs to JSON and vice versa.

# Usage
All commands are accessible via the command palatte.  Comments are not preserved during conversion.

## Plist Json Converter: JSON to PLIST
Command that converts an open JSON file to PLIST.  It will strip C style comments and also try and catch forgotten trailing commas.

## Plist Json Converter: PLIST to JSON
Command that converts an open PLIST file to JSON.

## Plist Json Converter: Save JSON to PLIST
Command that converts an open JSON file to PLIST and saves it to a plist file.  File name is determined by the ```conversion_ext``` setting.  It will strip C style comments and also try and catch forgotten trailing commas.  If the file to convert does not exist on disk, the converted file will not initially either, but it will only be shown in the view buffer until saved manually.

## Plist Json Converter: Save PLIST to JSON
Command that converts an open PLIST file to JSON and saves it to a json file.  File name is determined by the ```conversion_ext``` setting.  If the file to convert does not exist on disk, the converted file will not initially either, but it will only be shown in the view buffer until saved manually.

# Settings
## enable_save_to_file_commands
Allows the disabling of the "save to file" commands in the command palette

## enable_show_in_buffer_commands
Allows the disabling of the "show conversion if view buffer" commands in the command palette

## open_in_new_buffer
When a "show conversion in view buffer" command is executed, this will force the conversion to show up in its own new view buffer.

## conversion_ext
Allows you to provide a mapping from any plist extension to a choosen  json extension and vice versa.  They are evaluated in the order they appear.

## json_language
Allows the selection of a given ST2 language file to be used for the converted buffer or file.

## plist_language
Allows the selection of a given ST2 language file to be used for the converted buffer or file.

# Linux Issues
I have provided a fix for Ubuntu.  Ubuntu requires a full install of Python2.6, but it only comes with a minimal install by default.  You can enter the command below in your linux terminal to get the full install.

```sudo apt-get install python2.6```

I have provided the Python lib path in the settings file so it may be adapted for other distros in needed.

```"linux_python2.6_lib": "/usr/lib/python2.6/lib-dynload"```

# License

Plist Json Converter is released under the MIT license.

Copyright (c) 2012 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Version 0.3.0
- Fix for Linux pyexpat errors
- Fix default JSON.tmLanguage path

# Version 0.2.0
- Add commands to save converted file with specified extension
- For buffer conversion, add setting to open in new buffer
- Allow the turning off of save commands and/or buffer commands

# Version 0.1.0
- First release
