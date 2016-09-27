# Wrangle OpenStreetMap Data - A Case Study
## 1. Chosen Area
I'm going to wrangle on the coast of Pernambuco, Brazil openstreetmap data. In this area alone lives roghly 5 million people. It also has some of the most beautiful Brazilian beaches and it is also where I live :).

- File Name: PE_Coast.osm 
- File Size: 99MB
- Mongodb DB Size: 3.6 MB (streets only - json import after wrangling)

## 2. Objective 
The objective here is to work with streets only fixing their prefixes. In Portuguese the streets types such as Street, Avenue, etc comes first and not last as in Engligh so that a street called Silva Street in English is Rua Silva in Portuguese.<br>
A secondary objective is to find what and where other issues at this dataset are and give some options on how those issues could be fixed and the dataset quality improved.

## 3. Definition of a OpenStreetMap Street that will be analized here
We will check the street prefixes of any `way` tag that has a `tag` with its `k` value equals to `highway`. You can see an example below.
```
<way id="204619382" version="2" timestamp="2014-12-14T12:33:15Z" changeset="27456886" uid="230234" user="TrvrHldr">
    <nd ref="2146138187"/>
    <nd ref="2146138185"/>
    <tag k="highway" v="residential"/>
    <tag k="name" v="Rua das Rosas"/>
    <tag k="oneway" v="no"/>
</way>
```

## 4. Problems Found
- Street prefixes not following a clear pattern
- Overabbreviated street prefixes

Below you can see the major issues I found at the code. 
I printed all street prefixes ofund ordered by count.
You can check the full code in the P3_Wrangle_OpenStreetMap_Data_Notebook.py file in this github repository.
```
# print the street_types_counts dictionary, only sorted by count
sorted_dict = sorted(street_types_counts.items(), key=lambda x:x[1], reverse = True)

pprint.pprint(sorted_dict)

[(u'Rua', 13322),
 ('Avenida', 1479),
 ('Travessa', 431),
 ('Estrada', 225),
 (u'Pra\xe7a', 127),
 ('Rodovia', 97),
 (u'Acesso', 60),
 ('Ponte', 59),
 (u'1\xaa', 35),
 ('Alameda', 34),
 ('PE-022', 26),
 (u'2\xaa', 26),
 ....
```

After I checked the dictionary above I was able to manually build the dictionary to be used to fix the bad prefixes.
You can see below the issues found and the fixes proposed.
```
# replacement dictionary to be used to clean up the street prefixes
# this dictionary had been built by analyzing the information from the data mungling steps above
replacement_map = {"travessa": "Travessa",
"Travesa": "Travessa",
"Av.": "Avenida",
"Av": "Avenida",
"R.": "Rua",
"rua": "Rua",
"Ria": "Rua",
"rUA": "Rua",
"segunda": "2a",
"Terceira": "3a",
"Quarta": "4a",
"1°": "1a",
"2°": "2a",
"3°": "3a",
"4°": "4a",
"5°": "5a",
"6°": "6a",
"7°": "7a",
"8°": "8a",
"1ª": "1a",
"2ª": "2a",
"3ª": "3a",
"4ª": "4a",
"5ª": "5a",
"6ª": "6a",
"7ª": "7a",
"8ª": "8a",
"1 Travessa": "1a Travessa",
"2 Travessa": "2a Travessa",
"3 Travessa": "3a Travessa",
"4 Travessa": "4a Travessa",
"5 Travessa": "5a Travessa",
"6 Travessa": "6a Travessa",
"7 Travessa": "7a Travessa",
"8 Travessa": "8a Travessa",
"Primeira": "1a Travessa",
"Segunda": "2a Travessa",
"Terceira": "3a Travessa",
"Quarta": "4a Travessa"}
```

## Applying the dictionary
The code snippet below is responsible for applying the dictionary into the OpenStreetMap file and generate the json file that will be imported into mongodb to be further analized.
```
import codecs
import json

# replaces the bad string prefixes (street types)
def replace_street_prefix(name):
    for key in replacement_map:
        if name.split(" ")[0] == key:
            name.replace(key, replacement_map[key], 1)
            return name.replace(key, replacement_map[key], 1)
        else:
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

        if is_street:
#             pprint.pprint(way["name"])
            if way["name"] is not None:
                way["name"] = replace_street_prefix(way["name"])
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
```

And this is a snippet of the json file produced by the code above:
```
...
{'highway': 'residential',
  'id': '23390018',
  'name': None,
  'timestamp': '2015-08-05T06:44:52Z',
  'uid': '1856060',
  'user': 'patodiez',
  'version': 4},
 {'highway': 'residential',
  'id': '23390020',
  'name': None,
  'timestamp': '2015-08-05T06:44:52Z',
  'uid': '1856060',
  'user': 'patodiez',
  'version': 4},
 {'highway': 'residential',
  'id': '23390023',
  'name': None,
  'timestamp': '2012-12-13T06:26:53Z',
  'uid': '149876',
  'user': 'dbusse',
  'version': 2},
...
```

## 5. Further Analizes With Mongodb
After importing the json produced above into mongodb I was able to performe some queries to get a better sense of the street data inside this dataset.
```
#code to import the json file into mongodb
Leonardos-Air:P3 leo$ mongoimport --db p3_leonardo --collection osm --file /Users/leo/Dropbox/udacity_nanodegree/P3/PE_Coast.osm_processed.json 
2016-09-16T23:02:38.940-0300 connected to: localhost 2016-09-16T23:02:40.581-0300 imported 35330 documents
```

### Top 10 contributors to this area
```
pipeline = [
            {"$group" : {"_id" : "$user", "count" : {"$sum" : 1}}},
            {"$sort" : {"count" : -1}},
            {"$limit" : 10}
            ]

run_aggregation(pipeline)

{u'_id': u'TrvrHldr', u'count': 5552}
{u'_id': u'patodiez', u'count': 5415}
{u'_id': u'Usu\xe1rioPar', u'count': 4356}
...
```

### Percentage of each street type
We can see here that residential counts for ~72% of all streets while unclassified is only ~7%
```
db = get_db('p3_leonardo')
total_street_count = db.osm.count()
pipeline = [
            {"$group" : {"_id" : "$highway", "count" : {"$sum" : 1}}},
            {"$sort" : {"count" : -1}},
            {"$project" : {"count" : 1, "percentage" : {"$multiply" : [{"$divide" : [100, total_street_count]}, "$count"]}}}
            ]

run_aggregation(pipeline)

{u'_id': u'residential', u'count': 25564, u'percentage': 72.35776960090574}
{u'_id': u'unclassified', u'count': 2371, u'percentage': 6.711010472686102}
...
```

### Top contributors to the streets in the db in the last 30 days
```
pipeline = [
            {"$group" : {"_id" : "$lit", "count" : {"$sum" : 1}}},
            {"$sort" : {"count" : -1}},
            {"$project" : {"count" : 1, "percentage" : {"$multiply" : [{"$divide" : [100, total_street_count]}, "$count"]}}}
            ]

run_aggregation(pipeline)

{u'_id': None, u'count': 31981, u'percentage': 90.52080384941975}
{u'_id': u'yes', u'count': 3235, u'percentage': 9.156524200396262}
{u'_id': u'no', u'count': 114, u'percentage': 0.3226719501839796}
```

### Percentage of the streeets that doesn't have lit information
~90% of the entries doesn't have information about whether of or not the streets are lit

```
pipeline = [
            {"$group" : {"_id" : "$lit", "count" : {"$sum" : 1}}},
            {"$sort" : {"count" : -1}},
            {"$project" : {"count" : 1, "percentage" : {"$multiply" : [{"$divide" : [100, total_street_count]}, "$count"]}}}
            ]

run_aggregation(pipeline)

{u'_id': None, u'count': 31981, u'percentage': 90.52080384941975}
{u'_id': u'yes', u'count': 3235, u'percentage': 9.156524200396262}
{u'_id': u'no', u'count': 114, u'percentage': 0.3226719501839796}
```

### Percentage of the streeets that doesn't have surface information
~86% of the entries doesn't have information about its surface

```
pipeline = [
            {"$group" : {"_id" : "$surface", "count" : {"$sum" : 1}}},
            {"$sort" : {"count" : -1}},
            {"$project" : {"count" : 1, "percentage" : {"$multiply" : [{"$divide" : [100, total_street_count]}, "$count"]}}}
            ]

run_aggregation(pipeline)

{u'_id': None, u'count': 30489, u'percentage': 86.29776393999433}
{u'_id': u'paved', u'count': 2558, u'percentage': 7.240305689215964}
{u'_id': u'unpaved', u'count': 1018, u'percentage': 2.8814039060288703}
{u'_id': u'asphalt', u'count': 914, u'percentage': 2.5870365128785733}
...
```

### Percentage of the streeets that doesn't have oneway information
~60% of the streets doesn't have information about the flow direction

```
pipeline = [
            {"$group" : {"_id" : "$oneway", "count" : {"$sum" : 1}}},
            {"$sort" : {"count" : -1}},
            {"$project" : {"count" : 1, "percentage" : {"$multiply" : [{"$divide" : [100, total_street_count]}, "$count"]}}}
            ]

run_aggregation(pipeline)

{u'_id': None, u'count': 21215, u'percentage': 60.04811774695725}
{u'_id': u'no', u'count': 9641, u'percentage': 27.288423436173222}
{u'_id': u'yes', u'count': 4474, u'percentage': 12.663458816869515}
```

### Percentage of street without a name
~53% of the streets doesn't have a name in the database

```
pipeline = [
            {"$match" : {"name": None}},
            {"$group" : {"_id" : "$name", "count" : {"$sum" : 1}}},
            {"$sort" : {"count" : -1}},
            {"$project" : {"count" : 1, "percentage" : {"$multiply" : [{"$divide" : [100, total_street_count]}, "$count"]}}}
            ]

run_aggregation(pipeline)

{u'_id': None, u'count': 18867, u'percentage': 53.40220775544862}
```

## 6. Conclusion
The streets related data in this dataset has some obvious gaps like ~53% of the streets miss the name tag which makes it not much attractive for a serious use.
### Some Thoughts on How to Fill This Gap 
I'll list below some ideas on how we could improve this data.

#### Brazilian Data Agencies 
Through the wranging process I noticed that some streets has tags like this one.
```xml
<tag k="note:pt" v="Sem nome no IBGE ou no mapa da Prefeitura do Recife em 17/02/2015"/>
```
IBGE is the Brazilian Institute of Geography and Statistics<br>
Prefeitura do Recife is the Recife City Hall<br>

Data from other agencies such as National Departament of Roads, the State Departament of Roads, Cities agencies, National Postal Service and others could be mungled with he data that is already there.

#### Google Maps
The Google Geolocation API could be used to fill this gap and more. It could be used as well as to confirm some of the existing data such as street names, oneway data and others. This option would come with a cost, though.

#### Final Notes
I'm sure that the ideas proposed here are just a subset of what can be done to improve this dataset. Note that there's no magic bullet and even data used to fix this dataset can be wrong or damaged in someways. <br>
The OpenStreetMap data biggest strenght is the community and maybe using the power of the community is the way to go. Maybe throwing online competitions and/or creating an app (kind of how Waze started out) to help improving the maps while driving would be a more obvious and general approach to this general and global issue.
