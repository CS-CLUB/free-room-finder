#!/usr/bin/python2
################################################################################
#
# A script which parses the course entries displayed by the UOIT
# website http://www.uoit.ca/mycampus/avail_courses.html and stores
# each of the rooms, times they are used, and other important information
# in a database.
#
# Copyright (C) 2015, Eric Dube, Jonathan Gillett,
#                     Joseph Heron, and Daniel Smullen
# All rights reserved.
#
# Included files are copyright separately as indicated in their contents.
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


# EXTERNAL IMPORTS
from bs4 import BeautifulSoup as BowlShit
try:
    # Try Python3 import first
    import urllib.request as urllib2
except ImportError:
    # Fallback for Python2
    import urllib2

# INTERNAL IMPORTS
from Parser import Parser
from Parser import PageLoader

import acronyms as acros
import dbinterface, util

# BUILTIN IMPORTS
import logging, sys, pickle, time

class SomethingWentWrong(Exception):
    pass

# ==== Database Storing Methods ====
class FRFStore:
    """Stores course data object (a list) in a database

    This particular storer uses the dbinterface file from the old scraper.
    """
    def __init__(self):
        self.courseData = None
        pass
    def set_course_data(self,courseData,metaData):
        self.courseData = courseData
        self.metaData = metaData
    def setup_default_connection(self):
        usernm = 'jon' # yeah, yeah; I know that's bad.
        passwd = 'test123'
        server = 'localhost'
        schema = 'free_room_finder'
        con = dbinterface.connect_db(usernm,passwd,server,schema)
        if (con == None):
            raise SomethingWentWrong("An error occured while connecting to the database :/")
        else:
            self.con = con
        return con
    def get_connection(self):
        return self.con
    def insert_data_as_offerings(self, debug_offering=0):
        # Choose variables to be used
        courseData = self.courseData
        metaData = self.metaData

        # Make sure everything is okay
        if courseData == None:
            raise SomethingWentWrong("The courseData object was not set -_-")

        debugSoFar = 0
        courseSoFar = 0
        # loop through each course
        for course in courseData:
            for section in course['classes']:
                for classtime in section['times']:

                    # Not very important code - just for debugging
                    debugSoFar += 1
                    if debug_offering != 0:
                        if debugSoFar != debug_offering:
                            continue
                        if debugSoFar > debug_offering:
                            break
                    logging.debug("Offering #"+str(debugSoFar) + ", "+str(section['crn'],)+", "+course['program_code'])


                    # PREPARING DATA FOR DATABASE
                    weekalt = (classtime['week'] == "W1"
                        or classtime['week'] == "W2")
                    weekalt = 1 if weekalt else 0

                    logging.debug("  ~ adding a " + classtime['type'])
                    try:
                        classType = util.reverse_lookup(acros.class_types, classtime['type'])
                    except ValueError:
                        classType = "OTH"

                    start_time  = classtime['start_time']
                    finish_time = classtime['finish_time']
                    start_date  = classtime['start_date']
                    finish_date = classtime['finish_date']

                    # This deals with times/dates that are not available
                    try:
                        start_time  = time.strftime("%H:%M:00", start_time  )
                        finish_time = time.strftime("%H:%M:00", finish_time )
                    except TypeError:
                        start_time = None
                        finish_time = None

                    try:
                        start_date  = time.strftime("%Y-%m-%d", start_date  )
                        finish_date = time.strftime("%Y-%m-%d", finish_date )
                    except TypeError:
                        start_date = None
                        finish_date = None

                    # Determining campus
                    try:
                        campus = util.reverse_lookup(acros.campus_acronyms, section['campus'])
                    except ValueError:
                        campus = acros.make_nan_campus(section['campus'])


                    offering = {
                        'course_name':      course['cname'],
                        'program_code':     course['program_code'],
                        'course_code':      course['course_code'],
                        'crn':              section['crn'],
                        'course_section':   section['section'],
                        'capacity':         section['capacity'],
                        'registered':       section['actual'],
                        'level':            section['level'],
                        'campus':           campus,
                        'teacher_name':     classtime['profs'],
                        'room_number':      classtime['room'], 
                        'day':              classtime['day'],
                        'class_type':       classType,
                        'start_time':       start_time  ,
                        'finish_time':      finish_time ,
                        'start_date':       start_date  ,
                        'finish_date':      finish_date ,
                        'week_alt':         weekalt,

                        'year':             metaData['year'],
                        'semester':         int(acros.semester[metaData['term']])
                    }
                    if (debug_offering != 0):
                        logging.debug(offering)
                    with open('logs/last_offer_dump.txt','w') as f:
                        util.log_anything_prettily(lambda t: f.write(t + "\n"),offering)
                    dbinterface.insert_offering(self.get_connection(), offering)

def main(semester,year):
    # Hardcoded values
    url_base = "http://ssbp.mycampus.ca"
    url_action = "/prod/bwckschd.p_get_crse_unsec"

    # Set metaData (used by database storer)
    metaData = {
        'term': semester,
        'year': year
    }

    # Everything is in catch-all try block
    try:
        # Instantiate objects
        courseData = []
        pageParser = Parser(courseData)

        # === PHASE 1: PARSING ===

        # Set list of faculties to parse
        facsToUse = acros.faculties
        #facsToUse = ["ENGR"]

        # Parse for each faculty
        facSoFar = 0
        for faculty in facsToUse:
            facSoFar += 1
            # Print out which faculty is being parsed
            outta = str(facSoFar)+"/"+str(len(facsToUse))
            logging.info("Parsing faculty: "+outta+" "+faculty+": "+acros.faculties[faculty])

            # Instanciate page loader and get page
            #pageLoader = PageLoader(url_base,url_action,semester,year,faculty)
            #page = pageLoader.get_page(pageLoader.gen_url_and_data());
            with open('last_source.html','r') as f:
                page = ''.join(f.readlines());

            bs = BowlShit(page)
            """
            with open('last_source.html','w') as f:
                f.write(page)
            """

            # Parse page
            pageParser.parse_course_info(page)

        with open('last_object_dump.txt','w') as f:
            util.log_anything_prettily(lambda t: f.write(t + "\n"),courseData)
            #pickle.dump(courseData,f)

        # === PHASE 2: STORING ===
        frf = FRFStore()
        frf.set_course_data(courseData,metaData)
        frf.setup_default_connection()
        frf.insert_data_as_offerings()

    except SomethingWentWrong as e:
        logging.exception("Something terrible(?) happened!!")

if __name__ == "__main__":
    # Set logging to log everything to stderr
    logging.basicConfig(level=logging.DEBUG)
    # Set values from sys arguments
    semester = str(sys.argv[1])
    year = str(sys.argv[2])
    # Do the thing
    main(semester,year)
