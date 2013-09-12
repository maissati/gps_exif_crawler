#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#

import requests
import json
import re
import sqlite3
import misc as Misc
from scrapy import log

WSGeonames_user = 'demo'
DBGeonames = 'ressource/cities15000.sqlite'
TAG_SIZE_MIN = 3

def WSGeonames_Nearby(latitude, longitude):
  url = "http://api.geonames.org/findNearbyPlaceNameJSON?lat="+str(latitude)+"&lng="+str(longitude)+"&maxRows=1&style=short&username="+WSGeonames_user
  log.msg("WSGeonames_Nearby - Calling %s" % url, level=log.DEBUG)
  response = json.loads(requests.get(url).content)
  
  # Since toponymName can also return the subdivision of the city, we remove all numbers (eg. "Lyon 03")
  for line in response['geonames']:
    line['toponymName'] = re.sub("\d+", "", line['toponymName']).lstrip().rstrip()
  
  return response['geonames'] if 'geonames' in response else None

def WSGeonames_CountryCode(latitude, longitude):
  url = "http://api.geonames.org/countryCodeJSON?lat="+str(latitude)+"&lng="+str(longitude)+"&username="+WSGeonames_user
  response = json.loads(requests.get(url).content)
  log.msg("WSGeonames_CountryCode - Calling %s" % url, level=log.INFO)
  return response['countryCode'] if 'countryCode' in response else None

def searchCity(content, exceptCity):

  foundCities = []
  conn = sqlite3.connect(DBGeonames)
  tagsList = list(set(re.compile('\w+').findall(content)))
  for tag in [ word for word in tagsList if len(word) >= TAG_SIZE_MIN ]:
    if tag == exceptCity:
      continue
      
    #print("[*] Searching City Name: %s" % tag)
    # @TODO: City Names like: New York, Etc
    cursor = conn.execute("SELECT name, iso, latitude, longitude from cities where UPPER(name) = ?", [tag.upper()])
    conn.commit()
    for row in cursor.fetchall():
      foundCities.append({
        'Name': row[0],
        'ISO': row[1],
        'Lat': row[2],
        'Long': row[3],
        })
  conn.close()
  return foundCities
