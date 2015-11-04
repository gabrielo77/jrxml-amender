#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#    Amender script that amends Jaspersoft Studio files to get backward
#    compatibility.
#    Copyright (C) Gabriel Davini. (<https://github.com/gabrielo77>).
#
#    This file is a part of Amender
#
#    Amender is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Amender is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from __future__ import print_function

import logging
import os
import re
import sys

from pyinotify import IN_CLOSE_WRITE, Notifier, ProcessEvent, WatchManager


def amend_file(filename, prefix):
    try:
        with open(filename) as report:
            directory, name = os.path.split(filename)
            amended_name = prefix + name
            amended_filename = os.path.join(directory, amended_name)
            with open(amended_filename, "w") as amended:
                total_lines = []
                paragraphs = 0
                properties = 0
                uuids = 0
                for line in report.readlines():
                    if 'paragraph' in line:
                        paragraphs += 1
                        continue  # don't include 'paragraph' lines
                    elif 'com.jaspersoft.studio.unit.height' in line:
                        properties += 1
                        continue  # don't include 'property' lines
                    new_line = line
                    if 'uuid' in line:
                        uuids += 1
                        # remove 'uuid' tags
                        new_line = re.sub('\suuid\=\"[0-9a-zA-Z\-]+\"', '', line)
                    total_lines.append(new_line)
                amended.writelines(total_lines)
                info_msg = ("Remove {} paragraphs and {} properties lines, clean {} uuid tags from"
                            " {} lines")
                logger.info(info_msg.format(paragraphs, properties, uuids, len(total_lines)))
    except Exception as e:
        logger.critical(repr(e))
        return False
    finally:
        logger.info("Succesfully created: %s" % amended_filename)
        return True


class EventHandler(ProcessEvent):
    """
    Handle IN_CLOSE_WRITE events
    """

    def my_init(self, prefix=''):
        self.prefix = prefix

    def process_IN_CLOSE_WRITE(self, event):
        filename = event.pathname
        if filename.endswith('jrxml') and self.prefix not in filename:
            logger.info("File writen: %s" % filename)
            amend_file(filename, self.prefix)

    def process_default(self, event):
        print(event.paragraph)

if __name__ == '__main__':
    from argparse import ArgumentParser

    current_file = sys.argv[0]
    parser = ArgumentParser(prog=current_file)
    parser.add_argument("-d", "--dir2watch", help="Directory with the .jrxml files. Default: '.'",
                        default='.')
    parser.add_argument("-p", "--prefix", default="amended-",
                        help="Prefix for the amended file. This is not sanitized so be sure you do"
                             " not overwrite the orignal file. Default: amended-")
    parser.add_argument("-r", "--rec", action='store_true', default=False,
                        help="Watch directory recursively. Default: False")
    parser.add_argument("-v", "--version", help="Print version and exit.", action='version',
                        version="%(prog)s 0.1")
    options = parser.parse_args()
    logger = logging.getLogger(current_file)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
    streamH = logging.StreamHandler(sys.stdout)
    streamH.setFormatter(formatter)
    logger.addHandler(streamH)
    logger.info("Started, hit Ctrl+C to quit")
    if not os.path.isdir(options.dir2watch):
        logger.error("No such a directory: %s" % options.dir2watch)
        exit(1)
    masks = IN_CLOSE_WRITE
    wm = WatchManager()
    wm.add_watch(options.dir2watch, masks, rec=options.rec)
    handler = EventHandler(prefix=options.prefix)
    notifier = Notifier(wm, handler)
    logger.info("Watching dir: %s" % os.path.abspath(options.dir2watch))
    notifier.loop()
