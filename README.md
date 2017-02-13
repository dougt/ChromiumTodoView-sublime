ChromiumTodoView-sublime
===========

Overview
--------

ChromiumTodoView is a Sublime Text 3 plugin that displays bug information when you hover over TODO() comments in the chromium source code.

Installation
------------

* via [PackageControl](https://packagecontrol.io/)

or

* clone this repo into your Sublime Text 3 `Packages` directory

Settings
------------

Two settings are required to change before ChromiumTodoView works:

- **depot_tools** is the [depot_tools](https://dev.chromium.org/developers/how-tos/install-depot-tools) directory.
- **python_cmd** is the name of the python bin.  On linux, the value is probably just "python".  On windows, it will be "python276_bin/python.exe".
