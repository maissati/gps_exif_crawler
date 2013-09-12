import json
import utils.ws_geonames as WSGeonames
import utils.misc as Misc
from scrapy import log

def matchCountry(content, country):
        log.msg(' -- BEGIN PASS (1) - MATCH EXIF GPS -> COUNTRY TAG ', level=log.INFO)
       
        match = Misc.compareCountry(content, country)
        if match:
            log.msg("   [+] Picture location (Country: %s) and Country tag from text match !" % country, level=log.INFO)
        else:
            log.msg("   [-] Picture location (Country: %s) not found in text." % country, level=log.INFO)
        log.msg(' -- END PASS (1)', level=log.INFO)
        return  match

def matchCity(content, cities):
    log.msg(' -- BEGIN PASS (2) - MATCH EXIF GPS -> CITY TAG ', level=log.INFO)

    match = False
    for city in cities:
        cityName = city['toponymName']
        if Misc.sameCity(content, cityName):
            log.msg("   [+] Picture location (City: %s) and City tag from text match !" % cityName, level=log.INFO)
            match = True
            break
        else:
            log.msg("   [-] Picture location (City: %s) not found in text." % cityName, level=log.INFO)
    log.msg(' -- END PASS (2)', level=log.INFO)
    return match

def mismatchCountry(item, countries, exceptCountry):
    log.msg(' -- BEGIN PASS (3) - MISMATCH COUNTRY TAGS -> EXIF GPS ', level=log.INFO)

    results = []
    for country in countries:
        if country == exceptCountry:
            continue
        lat, lon = Misc.getCountryCoords(country)
        distance = Misc.haversine(item['latitude'], item['longitude'], lat, lon)
        c_mismatch = {}
        c_mismatch['country'] = country
        c_mismatch['distance'] = distance
        results.append(c_mismatch)
        log.msg("  [?] Potential Mismatch: Country: {0}, DISTANCE = {1} km".format(country, distance), level=log.INFO)
    log.msg(' -- END PASS (3)', level=log.INFO)
    return results


def mismatchCity(item, content, exceptCity):
    log.msg(' -- BEGIN PASS (4) - MISMATCH CITY TAGS -> EXIF GPS ', level=log.INFO)
    citiesTags = WSGeonames.searchCity(content, exceptCity)

    results = []
    for city in citiesTags:
        distance = Misc.haversine(item['latitude'], item['longitude'], city['Lat'], city['Long'])
        c_mismatch = {}
        c_mismatch['city'] = city['Name']
        c_mismatch['distance'] = distance
        log.msg("  [?] Potential Mismatch: City: {0}, ISO: {1}, Lat: {2}, Long: {3}. DISTANCE = {4} km".format(city['Name'], city['ISO'], city['Lat'], city['Long'], distance), level=log.INFO)
        if distance < 5:
            log.msg("      -> False-Positive (distance < 5 km)", level=log.INFO)
        c_mismatch['false_alarm'] = True if distance < 5 else False
        results.append(c_mismatch)
    log.msg(' -- END PASS (4)', level=log.INFO)
    return results
