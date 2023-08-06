#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 Jonathan Schultz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from argrecord import ArgumentRecorder

def parse_arguments(argstring):
    parser = ArgumentRecorder()
    parser.add_argument('-a', '--arg', type = str)
    parser.add_argument('pos', type = str)

    args = parser.parse_args(argstring)
    
    parser.write_comments(args, None)
    return args

def main(argstring=None):
    args = parse_arguments(argstring)

if __name__ == '__main__':
    main()

