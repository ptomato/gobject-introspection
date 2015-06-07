# -*- Mode: Python -*-
# GObject-Introspection - a framework for introspecting GObject libraries
# Copyright (C) 2008-2011 Johan Dahlin
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

import os
import optparse

from .docwriter import DocWriter
from .sectionparser import generate_sections_file, write_sections_file
from .transformer import Transformer

FORMATS = ['mallard', 'sections']


def doc_main(args):
    parser = optparse.OptionParser('%prog [options] GIR-file')

    parser.add_option("-o", "--output",
                      action="store", dest="output",
                      help="Directory to write output to")
    parser.add_option("-l", "--language",
                      action="store", dest="language",
                      default="c",
                      help="Output language")
    parser.add_option("-f", "--format",
                      action="store", dest="format",
                      default="mallard",
                      help="Output format [%s]" % ", ".join(FORMATS))
    parser.add_option("", "--add-include-path",
                      action="append", dest="include_paths", default=[],
                      help="include paths for other GIR files")
    parser.add_option("", "--write-sections-file",
                      action="store_const", dest="format", const="sections",
                      help="Backwards-compatible equivalent to '-f sections'")

    options, args = parser.parse_args(args)
    if not options.output:
        raise SystemExit("missing output parameter")

    if len(args) < 2:
        raise SystemExit("Need an input GIR filename")

    if options.format not in FORMATS:
        raise SystemExit("Unknown output format %s (supported: %s)" %
            (options.format, ", ".join(FORMATS)))

    if 'UNINSTALLED_INTROSPECTION_SRCDIR' in os.environ:
        top_srcdir = os.environ['UNINSTALLED_INTROSPECTION_SRCDIR']
        top_builddir = os.environ['UNINSTALLED_INTROSPECTION_BUILDDIR']
        extra_include_dirs = [os.path.join(top_srcdir, 'gir'), top_builddir]
    else:
        extra_include_dirs = []
    extra_include_dirs.extend(options.include_paths)
    transformer = Transformer.parse_from_gir(args[1], extra_include_dirs)

    if options.format == 'sections':
        sections_file = generate_sections_file(transformer)

        fp = open(options.output, 'w')
        write_sections_file(fp, sections_file)
        fp.close()
    else:
        writer = DocWriter(transformer, options.language, options.format)
        writer.write(options.output)

    return 0
