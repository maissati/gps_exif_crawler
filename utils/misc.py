import re
import json
import requests
from scrapy import log
from math import radians, cos, sin, asin, sqrt

COUNTRY_GPS = 'ressource/countryCoords.json'
COUNTRY_ISO = 'ressource/countryCodes.json'

def removeTags(url):
  content = ' '.join(re.sub('<[^<]+?>', '', requests.get(url).content).split())
  content = re.sub(' +',' ', content)
  return content

def compareCountry(content, countryCode):
  countries = json.loads(open('ressource/countryCodes.json').read())
  countryNames = [key for key,value in countries.iteritems() if value == countryCode]
  content = content.upper()
  match = False

  for cName in countryNames:
    occ = len(re.findall(r"\b"+cName+r"\b", content))
    log.msg("{0} occurrence(s) for {1}".format(occ, cName), level=log.INFO)
    if occ > 0:
      match = True
  return match

def getCountryCoords(code):
  countries = json.loads(open(COUNTRY_GPS).read())
  return float(countries[code][0]),float(countries[code][1]),

def getCountryCodesFromText(text):
  cCodes = []
  text = text.upper()
  countries = json.loads(open(COUNTRY_ISO).read())
  for name,code in countries.iteritems():
    if re.search(r"\b"+name+r"\b", text):
      cCodes.append(code)
  return cCodes

def sameCity(content, cityName):
  text = content.upper()
  same = False
  #print text
  occ = len(re.findall(r"\b"+cityName.upper()+r"\b", text))
  log.msg("{0} occurrence(s) for {1}".format(occ, cityName), level=log.INFO)
  if occ > 0:
    same = True
  return same

def transformGPS(exifGPSFormat):
  data = exifGPSFormat.translate(None, '[],').split()

  degree = data[0].split('/')
  minute = data[1].split('/')
  second = data[2].split('/')

  degree = float(degree[0] if len(degree) == 1 else float(degree[0])/float(degree[1]))
  minute = float(minute[0] if len(minute) == 1 else float(minute[0])/float(minute[1]))
  second = float(second[0] if len(second) == 1 else float(second[0])/float(second[1]))
  
  return degree + (minute / 60) + (second / 3600)

"""
Calculate the great circle distance between two points 
on the earth (specified in decimal degrees)
@source: http://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
"""
def haversine(lat1, lon1, lat2, lon2):

    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km