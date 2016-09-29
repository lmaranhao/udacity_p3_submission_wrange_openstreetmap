
# coding: utf-8

OSM_FILE_FULL = "PE_Coast.osm"  # Full OSM File
OSM_FILE_SAMPLE = "PE_Coast_sample.osm"  # Full OSM File
OSM_FILE = OSM_FILE_FULL

# counting tags to get a sense of how many of each tags we have
import xml.etree.cElementTree as ET
import pprint
import codecs
import json

from collections import defaultdict

def count_tags(filename):
    tags = defaultdict(int)
    for event, elem in ET.iterparse(filename):
        tags[elem.tag] += 1
    
    return tags

tags = count_tags(OSM_FILE)
pprint.pprint(tags)

# In Brazil the street type comes first (Avenue, Street, etc)
# This snippet checks all the street names prefixes in teh OSM file to see if there's anything strange or not expected as the street type
# The definition of street is: it's a way tag with a tag with k equals to highway

def check_street_types_counts():
    street_types_counts = defaultdict(int)
    for _, element in ET.iterparse(OSM_FILE):
        if element.tag == "way":
            is_street = False
            street_name = None
            for tag in element.iter("tag"):
                if tag.get("k") == "highway":
                    is_street = True
                elif tag.get("k") == "name":
                    street_name = tag.get("v")
            if is_street and street_name is not None:
                street_type = street_name.split(" ")[0]
                street_types_counts[street_type] += 1

    return street_types_counts

street_types_counts = check_street_types_counts()
pprint.pprint(dict(street_types_counts))

# print the street_types_counts dictionary, only sorted by count
sorted_dict = sorted(street_types_counts.items(), key=lambda x:x[1], reverse = True)

pprint.pprint(sorted_dict)

# map the street prefixes with the respective way ids
# used to manually check some odd results I found at first glance

def check_street_types_way_id():
    street_types_ways = defaultdict(set)
    for _, element in ET.iterparse(OSM_FILE):
        if element.tag == "way":
            way_id = element.get("id")
            is_street = False
            street_name = None
            for tag in element.iter("tag"):
                if tag.get("k") == "highway":
                    is_street = True
                elif tag.get("k") == "name":
                    street_name = tag.get("v")
            if is_street:
                if None == street_name:
                    street_types_ways["None"].add(way_id)
                else:
                    street_type = street_name.split(" ")[0]
                    street_types_ways[street_type].add(way_id)
    return street_types_ways

street_types_ways = check_street_types_way_id()
pprint.pprint(dict(street_types_ways))

# postal codes in Brazil are in the format 12345-123
# below I'll check if the postal_codes fields in the streets are in this format
# I'll print only the ones that doesn't match this format so I can decide what to do to fix them later
import re
postal_code_pattern = '\d{5}-\d{3}'
postal_code_pattern_compiled = re.compile(postal_code_pattern)

def check_postal_codes():
    for _, element in ET.iterparse(OSM_FILE):
        if element.tag == "way":
            way_id = element.get("id")
            is_street = False
            postal_code = None
            street_name = None
            for tag in element.iter("tag"):
                if tag.get("k") == "highway":
                    is_street = True
                elif tag.get("k") == "postal_code":
                    postal_code = tag.get("v")
                elif tag.get("k") == "name":
                    street_name = tag.get("v")
            if is_street and None != postal_code and not postal_code_pattern_compiled.match(postal_code):
                print postal_code + " - " + street_name

check_postal_codes()

# replacement dictionary to be used to clean up the street prefixes
# this dictionary had been built by analyzing the information from the data mungling steps above
prefix_replacement_map = {"travessa": "Travessa",
"Travesa": "Travessa",
"Av.": "Avenida ",
"Av": "Avenida ",
"R.": "Rua",
"rua": "Rua",
"Ria": "Rua",
"rUA": "Rua",
"segunda": "2a",
"Terceira": "3a",
"Quarta": "4a",
u'1\xb0': "1a",
u'2\xb0': "2a",
u'3\xb0': "3a",
u'4\xb0': "4a",
u'5\xb0': "5a",
u'6\xb0': "6a",
u'7\xb0': "7a",
u'8\xb0': "8a",
u"1\xaa": "1a",
u"2\xaa": "2a",
u"3\xaa": "3a",
u"4\xaa": "4a",
u"5\xaa": "5a",
u"6\xaa": "6a",
u"7\xaa": "7a",
u"8\xaa": "8a",
"1": "1a",
"2": "2a",
"3": "3a",
"4": "4a",
"5": "5a",
"6": "6a",
"7": "7a",
"8": "8a",
"Primeira": "1a",
"Segunda": "2a",
"Terceira": "3a",
"Quarta": "4a"}

# replacement dictionary to be used to clean up the bad postal codes
postal_code_replacement_map = {"5473550": "54735-500",
"0970-120": "50970-120",
"5475675": "54756-275"}

import codecs
import json

# replaces the bad string prefixes (street types)
def replace_from_map(name, replacement_map):
    for key in replacement_map:
        if name.split(" ")[0] == key:
            name.replace(key, replacement_map[key], 1)
            name = name.replace(key, replacement_map[key], 1)
            break
    return name

# processes each element from the open street map xml file
# returns a dictionary of this element
def process_element(element):
    way = {}
    if element.tag == "way":
        is_street = False
        way["name"] = None
        way_element = element
        for tag in element.iter("tag"):
            if tag.get("k") == "highway":
                is_street = True
                way["highway"] = tag.get("v")
            elif tag.get("k") == "name":
                way["name"] = tag.get("v")
            elif tag.get("k") == "oneway":
                way["oneway"] = tag.get("v")
            elif tag.get("k") == "surface":
                way["surface"] = tag.get("v")
            elif tag.get("k") == "lit":
                way["lit"] = tag.get("v")
            elif tag.get("k") == "access":
                way["access"] = tag.get("v")
            elif tag.get("k") == "emergency":
                way["emergency"] = tag.get("v")
            elif tag.get("k") == "lanes":
                way["lanes"] = int(tag.get("v"))
            elif tag.get("k") == "layer":
                way["layer"] = int(tag.get("v"))
            elif tag.get("k") == "maxspeed":
                way["maxspeed"] = int(tag.get("v"))
            elif tag.get("k") == "bridge":
                way["bridge"] = tag.get("v")
            elif tag.get("k") == "noexit":
                way["noexit"] = tag.get("v")
            elif tag.get("k") == "cycleway" or tag.get("k") == "cycleway:right" or tag.get("k") == "cycleway:left":
                way["cycleway"] = tag.get("v")
            elif tag.get("k") == "sidewalk":
                way["sidewalk"] = tag.get("v")
            elif tag.get("k") == "amenity":
                way["amenity"] = tag.get("v")
            elif tag.get("k") == "postal_code":
                way["postal_code"] = tag.get("v")

        if is_street:
#             pprint.pprint(way["name"])
            if way["name"] is not None:
                way["name"] = replace_from_map(way["name"], prefix_replacement_map)
            if "postal_code" in way:
                way["postal_code"] = replace_from_map(way["postal_code"], postal_code_replacement_map)

            way["id"] = way_element.get("id")
            way["uid"] = way_element.get("uid")
            way["user"] = way_element.get("user")
            way["timestamp"] = way_element.get("timestamp")
            way["version"] = int(way_element.get("version"))
#             pprint.pprint(way["name"])
            return way 
        
    return None

# generates the json file to be imported into mongodb using the mongoimport command
def process_file(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}_processed.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = process_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

process_file(OSM_FILE, True)

# The json file generated above needs to be imported into my local mongodb which is already running. I'll name the database **p3_leonardo**, the collection **osm** and run the command below (if you want to run it in your local machine just change the local path to the PE_Coast.osm_processed.json file):
#
# mongoimport --db p3_leonardo --collection osm --file /Users/leo/Dropbox/udacity_nanodegree/P3/PE_Coast.osm_processed.json
# 
# <output>
# Leonardos-Air:P3 leo$ mongoimport --db p3_leonardo --collection osm --file /Users/leo/Dropbox/udacity_nanodegree/P3/PE_Coast.osm_processed.json
# 2016-09-27T18:19:23.573-0300 connected to: localhost
# 2016-09-27T18:19:24.728-0300 imported 35330 documents
# 
# The functions below will be reused later on when I use some mongodb aggregate functions to analyse the data.
def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db


def run_aggregation(pipeline):
    db = get_db('p3_leonardo')
    result = db.osm.aggregate(pipeline)
    for r in result:
        pprint.pprint(r)

# Checking if the street prefix and postal code replacement worked
db = get_db('p3_leonardo')

everything_ok = True
for key in prefix_replacement_map:
    from_db = db.osm.find_one({"name": {"$regex": "^" + key + " "}})
    if from_db != None:
        print "a bad street prefix in the database: " + key
        pprint.pprint(from_db)
        print "check the prefix replacement code"
        everything_ok = False
        break
    
for key in postal_code_replacement_map:
    from_db = db.osm.find_one({"name": {"$regex": "^" + key + " "}})
    if from_db != None:
        print "a bad postal code in the database: " + key
        pprint.pprint(from_db)
        print "check the prefix replacement code"       
        everything_ok = False
        break

if everything_ok:
    print "all prefixes and postal codes are good in the database!!"

# find the top 10 contributors to this area
pipeline = [
            {"$group" : {"_id" : "$user", "count" : {"$sum" : 1}}},
            {"$sort" : {"count" : -1}},
            {"$limit" : 10}
            ]

run_aggregation(pipeline)

# find the percentage of each street type
db = get_db('p3_leonardo')
total_street_count = db.osm.count()
pipeline = [
            {"$group" : {"_id" : "$highway", "count" : {"$sum" : 1}}},
            {"$sort" : {"count" : -1}},
            {"$project" : {"count" : 1, "percentage" : {"$multiply" : [{"$divide" : [100, total_street_count]}, "$count"]}}}
            ]

run_aggregation(pipeline)

# find the top contributors to the streets in the db in the last 30 days

from datetime import datetime
from datetime import timedelta

# first convert the timestamp field from string to datetime in the db
all_streets = db.osm.find()
for street in all_streets:
    try:
        date_object = datetime.strptime(street["timestamp"], '%Y-%m-%dT%H:%M:%SZ')
        db.osm.update_one({"_id" : street["_id"]}, {"$set" : {"timestamp" : date_object}})
    except TypeError:
        # db already updated
        pass

thirty_days_ago = datetime.now() + timedelta(days=-30)
        
pipeline = [
            {"$match" : {"timestamp": {"$gte": thirty_days_ago}}},
            {"$group" : {"_id" : "$user", "count" : {"$sum" : 1}}},
            {"$sort" : {"count" : -1}}
            ]

run_aggregation(pipeline)

# find the percentage of the streeets that doesn't have lit information
pipeline = [
            {"$group" : {"_id" : "$lit", "count" : {"$sum" : 1}}},
            {"$sort" : {"count" : -1}},
            {"$project" : {"count" : 1, "percentage" : {"$multiply" : [{"$divide" : [100, total_street_count]}, "$count"]}}}
            ]

run_aggregation(pipeline)

# find the percentage of the streeets that doesn't have surface information
pipeline = [
            {"$group" : {"_id" : "$surface", "count" : {"$sum" : 1}}},
            {"$sort" : {"count" : -1}},
            {"$project" : {"count" : 1, "percentage" : {"$multiply" : [{"$divide" : [100, total_street_count]}, "$count"]}}}
            ]

run_aggregation(pipeline)

# find the percentage of the streeets that doesn't have oneway information
pipeline = [
            {"$group" : {"_id" : "$oneway", "count" : {"$sum" : 1}}},
            {"$sort" : {"count" : -1}},
            {"$project" : {"count" : 1, "percentage" : {"$multiply" : [{"$divide" : [100, total_street_count]}, "$count"]}}}
            ]

run_aggregation(pipeline)

# find the percentage of street without a name
pipeline = [
            {"$match" : {"name": None}},
            {"$group" : {"_id" : "$name", "count" : {"$sum" : 1}}},
            {"$sort" : {"count" : -1}},
            {"$project" : {"count" : 1, "percentage" : {"$multiply" : [{"$divide" : [100, total_street_count]}, "$count"]}}}
            ]

run_aggregation(pipeline)