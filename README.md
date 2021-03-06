# Wrangle OpenStreetMap Data - A Case Study
## 1. Chosen Area
I'm going to wrangle on the coast of Pernambuco, Brazil openstreetmap data. In this area alone lives roghly 5 million people. It also has some of the most beautiful Brazilian beaches and it is also where I live :).

- File Name: PE_Coast.osm 
- File Size: 99MB
- Mongodb DB Size: 3.6 MB (streets only - json import after wrangling)

## 2. Objective 
The objective here is to work with streets only fixing their prefixes and postal codes. In Portuguese the streets types such as Street, Avenue, etc comes first and not last as in Engligh so that a street called Silva Street in English is Rua Silva in Portuguese.<br>
A secondary objective is to find what and where other issues at this dataset are and give some options on how those issues could be fixed and the dataset quality improved.

### 2.1.Code
If you feel like following the code step by step you can choose between [html](https://github.com/lmaranhao/udacity_p3_submission_wrange_openstreetmap/blob/master/P3_Wrangle_OpenStreetMap_Data_Notebook.html), [a python notebook](https://github.com/lmaranhao/udacity_p3_submission_wrange_openstreetmap/blob/master/P3_Wrangle_OpenStreetMap_Data_Notebook.ipynb) or a [pure python file](https://github.com/lmaranhao/udacity_p3_submission_wrange_openstreetmap/blob/master/P3_Wrangle_OpenStreetMap_Data.py).

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
- Overabbreviated and wronglyabbreviated street prefixes
- A few Postal codes are inconsistent

### 4.1. Some bad prefixes found [\[Code\]](https://github.com/lmaranhao/udacity_p3_submission_wrange_openstreetmap/blob/master/P3_Wrangle_OpenStreetMap_Data.py#L107)
`Av, Av., R., R, Ria, rUA, ...`
After manually checking the full list of prefixes I created a dictionary that maps the bad or wrong street name prefixes found to the right ones. 

### 4.2. The bad postal codes found [\[Code\]](https://github.com/lmaranhao/udacity_p3_submission_wrange_openstreetmap/blob/master/P3_Wrangle_OpenStreetMap_Data.py#L81)
`5473550, 0970-120, 5475675`
For the postal codes, since it's just 4 bad entries, I've manually searched for the postal codes in google maps and created the postal code replacement map below. If we had more bad entries an automated way of doing this would be the way to go.

[\[Code\]](https://github.com/lmaranhao/udacity_p3_submission_wrange_openstreetmap/blob/master/P3_Wrangle_OpenStreetMap_Data.py#L149)
```
# replacement dictionary to be used to clean up the bad postal codes
postal_code_replacement_map = {"5473550": "54735-500",
"0970-120": "50970-120",
"5475675": "54756-275"}
```

## 5. Fixing the isues: Applying the dictionary [\[Code\]](https://github.com/lmaranhao/udacity_p3_submission_wrange_openstreetmap/blob/master/P3_Wrangle_OpenStreetMap_Data.py#L154)
After the dictionaries have been created it's time to apply them to the raw data and create the json file to be imported into mongodb.

And this is a snippet of the json file produced by the code above:
```
{
  "uid": "149876",
  "timestamp": "2016-03-05T22:22:09Z",
  "version": 1,
  "postal_code": "54786-390",
  "user": "dbusse",
  "id": "401858042",
  "highway": "residential",
  "name": "Rua Monte Horeb"
}
```

## 6. Further Analizes With Mongodb
After importing the json produced above into mongodb I was able to performe some queries to get a better sense of the street data inside this dataset.
```
#code to import the json file into mongodb
Leonardos-Air:P3 leo$ mongoimport --db p3_leonardo --collection osm --file /Users/leo/Dropbox/udacity_nanodegree/P3/PE_Coast.osm_processed.json 
2016-09-16T23:02:38.940-0300 connected to: localhost 2016-09-16T23:02:40.581-0300 imported 35330 documents
```

### Checking if the street prefix and postal code replacement worked [\[Code\]](https://github.com/lmaranhao/udacity_p3_submission_wrange_openstreetmap/blob/master/P3_Wrangle_OpenStreetMap_Data.py#L267)
Before moving any further I ran some code that searched for any of the bad prefixes and bad postal codes in the database. It found nothing :)!!


### Top contributors to this area [\[Code\]](https://github.com/lmaranhao/udacity_p3_submission_wrange_openstreetmap/blob/master/P3_Wrangle_OpenStreetMap_Data.py#L292)
```
{u'_id': u'TrvrHldr', u'count': 5552}
{u'_id': u'patodiez', u'count': 5415}
{u'_id': u'Usu\xe1rioPar', u'count': 4356}
...
```

### Percentage of each street type [\[Code\]](https://github.com/lmaranhao/udacity_p3_submission_wrange_openstreetmap/blob/master/P3_Wrangle_OpenStreetMap_Data.py#L301)
We can see here that residential counts for ~72% of all streets while unclassified is only ~7%
```
{u'_id': u'residential', u'count': 25564, u'percentage': 72.35776960090574}
{u'_id': u'unclassified', u'count': 2371, u'percentage': 6.711010472686102}
```

### Top contributors to the streets in the db in the last 30 days [\[Code\]](https://github.com/lmaranhao/udacity_p3_submission_wrange_openstreetmap/blob/master/P3_Wrangle_OpenStreetMap_Data.py#L312)
```
{u'_id': None, u'count': 31981, u'percentage': 90.52080384941975}
{u'_id': u'yes', u'count': 3235, u'percentage': 9.156524200396262}
{u'_id': u'no', u'count': 114, u'percentage': 0.3226719501839796}
```

### Percentage of the streeets that doesn't have lit information [\[Code\]](https://github.com/lmaranhao/udacity_p3_submission_wrange_openstreetmap/blob/master/P3_Wrangle_OpenStreetMap_Data.py#L337)
~90% of the entries doesn't have information about whether of or not the streets are lit
```
{u'_id': None, u'count': 31981, u'percentage': 90.52080384941975}
{u'_id': u'yes', u'count': 3235, u'percentage': 9.156524200396262}
{u'_id': u'no', u'count': 114, u'percentage': 0.3226719501839796}
```

### Percentage of the streeets that doesn't have surface information [\[Code\]](https://github.com/lmaranhao/udacity_p3_submission_wrange_openstreetmap/blob/master/P3_Wrangle_OpenStreetMap_Data.py#L346)
~86% of the entries doesn't have information about its surface
```
{u'_id': None, u'count': 30489, u'percentage': 86.29776393999433}
{u'_id': u'paved', u'count': 2558, u'percentage': 7.240305689215964}
{u'_id': u'unpaved', u'count': 1018, u'percentage': 2.8814039060288703}
{u'_id': u'asphalt', u'count': 914, u'percentage': 2.5870365128785733}
```

### Percentage of the streeets that doesn't have direction (oneway) information [\[Code\]](https://github.com/lmaranhao/udacity_p3_submission_wrange_openstreetmap/blob/master/P3_Wrangle_OpenStreetMap_Data.py#L355)
~60% of the streets doesn't have information about the flow direction
```
{u'_id': None, u'count': 21215, u'percentage': 60.04811774695725}
{u'_id': u'no', u'count': 9641, u'percentage': 27.288423436173222}
{u'_id': u'yes', u'count': 4474, u'percentage': 12.663458816869515}
```

### Percentage of street without a name [\[Code\]](https://github.com/lmaranhao/udacity_p3_submission_wrange_openstreetmap/blob/master/P3_Wrangle_OpenStreetMap_Data.py#L364)
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

## 7. Conclusion
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
The Google Geolocation API could be used to fill this gap and more. It could be used as well as to confirm some of the existing data such as street names, postal codes, oneway data and others. This option would come with a cost, though. As of today the Google Geolocation API has a 2,500 requests free daily quota + $0.50 per 1000 excess requests (in U.S. dollars).

#### Final Notes
I'm sure that the ideas proposed here are just a subset of what can be done to improve this dataset. Note that there's no magic bullet and even data used to fix this dataset can be wrong or damaged in someways. <br>
The OpenStreetMap data biggest strenght is the community and maybe using the power of the community is the way to go. Maybe throwing online competitions and/or creating an app (kind of how Waze started out) to help improving the maps while driving would be a more obvious and general approach to this general and global issue.
