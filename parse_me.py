#!/usr/bin/env python

from datetime import datetime
from inspect import stack as inspect_stack
from logging import getLogger
import re

def parse(filename):
    with open(filename, "r") as f:
        return real_parser(f)

def real_parser(iostream):
    """Receipt parser. This could use a little work.
    """
    l = getLogger("{}".format(inspect_stack()[1][3]))
    r = dict()
    line = iostream.readline()
    findAddress = False
   
    while line:
        l.debug("read: %r", line)
        m = re.match(r"Store #(?P<store>\d+) +(?:eat|tko|tkc) +(?P<month>\d\d)/(?P<day>\d\d)/(?P<year>\d+) (?P<hour>\d\d):(?P<minute>\d\d):(?P<second>\d\d) *\n", line)
        storeName = re.search(r'Subway' ,line)
        zipcode = re.search('([0-9]{5})',line)
        phoneNumber = re.search('[0-9]\d{2}-\d{3}-\d{4}', line)

        if m:
        	l.debug("match: %r", m.groups())
        	store, month, day, year, hour, minute, second = [int(x) for x in m.groups()]
        	r["store_number"] = store
        	r["date"] = datetime(2000+year,month, day, hour, minute, second).isoformat(sep=" ")
        else:
        	l.debug("no match")

        if(storeName and not r.get("store name")):
      		r["store name"] = line[:-1]
      		findAddress = True
      	elif(findAddress):
      		address = re.search(r'(\d+)', line)
      		if(address):
      			r["address"] = line[:-1]
      			findAddress = False

      	if(zipcode and not r.get("zipcode")):
      		if(not(int(store) == int(zipcode.group())) ):
      			r["zipcode"] = zipcode.group()

      	if(phoneNumber and not r.get("phone_number")):
      		r["phone_number"] = phoneNumber.group()     

        line = iostream.readline()
    # I should probably parse a little more of the receipt...
    return r

if "__main__" == __name__:
    from argparse import ArgumentParser
    from logging import basicConfig, CRITICAL, ERROR, WARNING, INFO, DEBUG

    parser = ArgumentParser(description="Parse a receipt file.")
    parser.add_argument("-v", "--verbose", action="count")
    parser.add_argument("-q", "--quiet", action="count")
    parser.add_argument("file_name", metavar="file_name")

    arguments = parser.parse_args()

    raw_log_level = 2 + (arguments.verbose or 0) - (arguments.quiet or 0)
    if   raw_log_level <= 0: log_level = CRITICAL
    elif raw_log_level == 1: log_level = ERROR
    elif raw_log_level == 2: log_level = WARNING    # default
    elif raw_log_level == 3: log_level = INFO
    else:                    log_level = DEBUG
    basicConfig(level=log_level)

    l = getLogger("{}".format(__name__))
    l.debug("Parsing file: %s", arguments.file_name)

    from pprint import pprint
    pprint(parse(arguments.file_name))
