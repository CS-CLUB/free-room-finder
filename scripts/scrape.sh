#!/bin/bash
################################################################################
#
# A script to simplify executing db-generate-room.py to parse an
# available semester.
#
# Copyright (C) 2015, Jonathan Gillett, Joseph Heron
# All rights reserved.
#
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
#
###############################################################################

read -p "Enter year (ex: 2015): " year
echo "Running scraper on winter semester (check logs for details)"
python2 scraper.py winter $year &> logs/test.log
echo "Running scraper on fall semester (check logs for details)"
python2 scraper.py fall $year &> logs/test.log
