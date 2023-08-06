# coding=utf-8
"""
CLI Implementation of the parac module. This module provides the interface and
commands for utilising the Para Compiler using the command line.

This is not intended for direct code usage, since the module is structured to
be used from a single function call of `cli_entry()`. This means the module
itself will handle exiting the program, as well as managing the command-line
arguments.

If '__main__' is run directly this module will run on default the CLI and parse
the command line arguments.

Copyright (C) 2021 Luna Klatzer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

__title__ = "paralang_cli"
__description__ = "Command Line Interface Implementation for the Para " \
                  "programming compiler"
__url__ = "https://github.com/Para-Lang/Para-CLI/"
__author__ = "Luna Klatzer"
__author_email__ = "luna.klatzer@gmail.com"
__license__ = "GNU GENERAL PUBLIC LICENSE v3.0"
__version__ = "v0.1.dev7"
__code_name__ = ""
__release__ = f"{__code_name__} {__version__}"
__copyright__ = "Luna Klatzer"

from .__main__ import *
from .logging import *
from . import scripts
