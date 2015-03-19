################################################################################
#
# A module containing the functions for interfacing with MySQL databases
#
# A script which parses the course entries displayed by the UOIT
# website http://www.uoit.ca/mycampus/avail_courses.html and stores
# each of the rooms, times they are used, and other important information
# in a database.
#
# Copyright (C) 2013, Eric A. Dube, Jonathan Gillett,
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

# INTERNAL IMPORTS [not sure if needed yet]
import acronyms as acros
#import util

# EXTERNAL IMPORTS
try:
    # Try Python3 import first
    import urllib.request as urllib2
except ImportError:
    # Fallback for Python2
    import urllib2
from bs4 import BeautifulSoup as BowlShit

# BUILTIN IMPORTS
import time
import logging

import util

class PostData:
    def __init__(self):
        self.items = []
    def add_item(self,name,value):
        self.items.append([name,value])
    def get_string(self):
        # Python for the win! Love one-lining this stuff! - EAD
        res = '&'.join([item[0] + "=" + item[1] for item in self.items])
        return res

class TableParser:
    """A class which parses a table using BS4 and calls the given functions while parsing

    The purpose of this class is to provide a foolproof method for parsing tables
    that can be used multiple times without cluttering the rest of the parse code.

    This could later provide comprehensive logging of all parsing of tables.
    """
    def __init__(self):
        pass
    def parse_with(self,soup):
        for tableElement in soup.children:

            logging.debug("Parsing tableElement: " + str(tableElement.name))

            # if there is a tbody element, that's where we need to be
            if tableElement.name == "tbody":
                self.parse_with(tableElement)
            # if it is a table row
            elif tableElement.name == "tr":
                self.parse_with(tableElement)
            # if it is a table header
            elif tableElement.name == "th":
                logging.debug("TABLE HEADER")
                self.parse_header(tableElement)
            # if a loose table cell (this shouldn't happen)
            elif tableElement.name == "td":
                self.parse_cell(tableElement)
    # Set the triggers
    def on_parse_header(self,func):
        self.parse_header = func
    def on_parse_cell(self,func):
        self.parse_cell = func
    # default empty functions
    def parse_header(self,soup):
        print("Oops!")
    def parse_cell(self,soup):
        print("Oops!")


class Parser:
    def __init__(self, course_data):
        self.course_data = course_data # object

        self.curr_course = None
        self.curr_class = None
    def parse_course_info(self, raw_html):
        """A function which parses all the course information on a given page (HTML string)

        Arguments:
            raw_html -> HTML string containing the page
        """
        course_content = BowlShit(raw_html)

        with open('test_dump.txt','w') as f:
            f.write(course_content.prettify())

        # Parses all the course information in the first table.
        #for course_table in course_content.findAll('table', {'class': "datadisplaytable", 'summary': 
        #                            "This layout table is used to present the sections found"}):

        tableParser = TableParser()

        tableParser.on_parse_header(self.parse_section_header)
        tableParser.on_parse_cell(self.parse_section_datum)

        # Parses all the course information in the course table
        # i.e. afaik this for loop only goes through a single table
        for course_table in course_content.find_all('table', {'class': "datadisplaytable", 'summary': 
                                    "This layout table is used to present the sections found"}):
            tableParser.parse_with(course_table)

            """ Old cluttery parsing code
            self.curr_course = None # holds current course object (dict) being edited
            self.curr_class = None # holds current class object (dict) being edited
            print("A")
            for tElem in course_table.children:
                print("B: "+str(tElem.name))
                if tElem.name == "th":
                    self.parse_section_header(tElem)
                elif tElem.name == "tr":
                    # Look through every table cell in this row
                    for td in tElem.children:
                        if td.name == "td":
                            # Look through every child in every table cell of this row
                            for datum in td.children:
                                self.parse_section_datum(datum)
            """


    def parse_section_header(self, tElem):
        """Parses a header identifying a particular CRN

        TODO: rewrite this docstring so it's more accurate/informative

        Arguments:
            tElem -> BeautifulSoup object to parse (TH element from page)
            course_data -> object to enter new course data into
            curr_course -> object to modify with new course information
            curr_class -> object to modify with new class information
        """
        logging.debug("data:section_header:" + tElem.get_text())

        txtParts = tElem.get_text().split(' - ')

        # Fix for potential dash in class name:
        # Take CRN value as first numeric value
        # Done by calling int(val) until ValueError not thrown
        howMany = 0 # will rep how many parts belong to course name
        while True:
            try:
                testInt = int(txtParts[howMany])
                txtParts[howMany] = testInt
                break
            except ValueError:
                pass
            howMany += 1
        cname = ' - '.join(txtParts[0:howMany])
        crn   =            txtParts[howMany+0] # converted to int by above loop
        ccode =            txtParts[howMany+1]
        secNo =            txtParts[howMany+2]

        # Select the relavent course
        for course in self.course_data:
            if course['ccode'] == ccode:
                self.curr_course = course
                break
        # If loop did not break (we didn't find the course)
        else:
            # create a new course
            self.curr_course = {'ccode': ccode, 'cname': cname, 'classes': []}
            # split up the course code
            program_code, course_code = self.curr_course['ccode'].split(' ')
            self.curr_course['program_code'] = program_code
            self.curr_course['course_code'] = course_code
            # push new course onto course_data list
            self.course_data.append(self.curr_course)

        self.curr_class = {'crn': crn, 'section': secNo, 'times': []}
        self.curr_course['classes'].append(self.curr_class)

    def parse_section_datum(self, datum):
        for element in datum.children:
            logging.debug("data:section_datum_elem:" + str(element.name))
            if element.name == "table":
                logging.debug("data:element_table:" + element.caption.get_text())
                if element.caption.get_text() == "Scheduled Meeting Times":
                    self.parse_section_timetable(element)
                elif element.caption.get_text() == "Registration Availability":
                    self.parse_section_avail(element)
            if element.name == "span":
                name = element.get_text().encode('ascii', 'ignore').strip()
                val = element.next_sibling.encode('ascii', 'ignore').strip()
                name_and_key_associations = {
                    "Associated Term:": 'term',
                    "Levels:": 'level',
                    "": 'campus'
                }

                for nameToTest in name_and_key_associations:
                    if name == nameToTest:
                        key = name_and_key_associations[nameToTest]
                        self.curr_class[key] = val;
    def parse_section_timetable(self, table):
        for row in table.children:
            logging.debug(row.name)
            if row.name == "tbody":
                self.parse_section_timetable(row)
            elif row.name == "tr": # in case of inconsistancies
                rowData = []
                # Collect row data by storing each TD value
                for cell in row.children:
                    if cell.name == "td":
                        rowData.append(cell)
                # Set data to corresponding variable
                week     = rowData[0].get_text().encode('ascii', 'ignore').strip()
                times     = rowData[2].get_text().encode('ascii', 'ignore').strip()
                day     = rowData[3].get_text().encode('ascii', 'ignore').strip()
                room     = rowData[4].get_text().encode('ascii', 'ignore').strip()
                dates     = rowData[5].get_text().encode('ascii', 'ignore').strip()
                ctype     = rowData[6].get_text().encode('ascii', 'ignore').strip()
                profs     = rowData[7].get_text().encode('ascii', 'ignore').strip()


                # === PROBLEM ===

                # It never gets these... but why?

                if week == '':
                    week = "ALL"

                # Make sure this is an actual contents row
                if week == "Week" or times == "Time":
                    # This means this is just the row of headings
                    continue # Go to next iteration
                if (times == "TBA"):
                    startTime = None
                    endTime = None
                else:
                    startTime, endTime = times.split(' - ')
                    startTime = time.strptime(startTime, "%I:%M %p")
                    endTime = time.strptime(endTime, "%I:%M %p")

                if (dates == "TBA"):
                    startDate = None
                    endDate = None
                else:
                    startDate, endDate = dates.split(' - ')
                    startDate = time.strptime(startDate, "%b %d, %Y")
                    endDate = time.strptime(endDate, "%b %d, %Y")

                self.curr_class['times'].append({
                        'week': week,
                        'start_time': startTime,
                        'finish_time': endTime,
                        'start_date': startDate,
                        'finish_date': endDate,
                        'room': room,
                        'profs': profs,
                        'type': ctype,
                        'day': day
                    })
    def parse_section_avail(self, table):
        for row in table.children:
            logging.debug(row.name)
            if row.name == "tbody":
                self.parse_section_avail(row)
            elif row.name == "tr": # in case of inconsistancies
                rowData = []
                # Collect row data by storing each TD value
                for cell in row.children:
                    if cell.name == "td":
                        rowData.append(cell)
                # Set data to corresponding variable
                capacity     = rowData[1].get_text().encode('ascii', 'ignore').strip()
                actual         = rowData[2].get_text().encode('ascii', 'ignore').strip()
                remaining     = rowData[3].get_text().encode('ascii', 'ignore').strip()


                # Make sure this is an actual contents row
                if capacity == "Capacity" or actual == "Actual":
                    # This means this is just the row of headings
                    continue # Go to next iteration

                self.curr_class['capacity'] = int(capacity)
                self.curr_class['actual'] = int(actual)
                self.curr_class['remaining'] = int(remaining)





class PageLoader:
    def __init__(self,url_base,url_action,semester,year,subj):
        self.actionURL = url_base + url_action

        self.set_term(semester,year)
        self.set_subj(subj)
        
    def set_term(self,semester,year):
        self.term_in = str(year) + str(acros.semester[semester])
    def set_subj(self,subj):
        self.subj = subj

    def get_page(self,page):
        url, data = page
        req = urllib2.Request(url, data=data)
        """
        print("=== Headers ===")
        print(req.headers)
        print("=== Data ===")
        print(req.data)
        """
        response = urllib2.urlopen(req)
        pageContents = response.read()
        

        return pageContents
    def gen_url_and_data(self):
        url = self.actionURL

        term_in = self.term_in
        subj = self.subj

        vals = PostData()
        vals.add_item('TRM'                , "U")
        vals.add_item('term_in'            , term_in)        # OVER HERE
        vals.add_item('sel_subj'        , "dummy")
        vals.add_item('sel_day'            , "dummy")
        vals.add_item('sel_schd'        , "dummy")
        vals.add_item('sel_insm'        , "dummy")
        vals.add_item('sel_camp'        , "dummy")
        vals.add_item('sel_levl'        , "dummy")
        vals.add_item('sel_sess'        , "dummy")
        vals.add_item('sel_instr'        , "dummy")
        vals.add_item('sel_ptrm'        , "dummy")
        vals.add_item('sel_attr'        , "dummy")
        vals.add_item('sel_subj'        , subj)        # OVER HERE
        vals.add_item('sel_crse'        , "")
        vals.add_item('sel_title'        , "")
        vals.add_item('sel_schd'        , "%")
        vals.add_item('sel_insm'        , "%")
        vals.add_item('sel_from_cred'    , "")
        vals.add_item('sel_to_cred'        , "")
        vals.add_item('sel_camp'        , "%")
        vals.add_item('begin_hh'        , "0")
        vals.add_item('begin_mi'        , "0")
        vals.add_item('begin_ap'        , "a")
        vals.add_item('end_hh'            , "0")
        vals.add_item('end_mi'            , "0")
        vals.add_item('end_ap'            , "a")

        data = vals.get_string()

        return (url,data)