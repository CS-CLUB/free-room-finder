#!/bin/bash

read -p "Enter year (ex: 2015): " year
echo "Running scraper on winter semester (check logs for details)"
python2 scraper.py winter $year &> logs/test.log
echo "Running scraper on fall semester (check logs for details)"
python2 scraper.py fall $year &> logs/test.log
