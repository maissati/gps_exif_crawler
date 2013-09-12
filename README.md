Scrapy EXIF Crawler (GPS Analysis)
=========

Scrapy EXIF Crawler is a python template which uses [The Scrapy Framework](http://scrapy.org) to automatically crawl all pages from a given URL and extract EXIF information from any scraped picture. The following project (GPS Analysis) is a proof of concept using the Scrapy EXIF Crawler to extract all GPS information and search for any mismatch with the text surrounding the picture. 

It uses [Geonames](http://geonames.org) free web service and databases. The EXIF parser is a slightly modified version of [Gene Cash and Ianaré Sévi](https://github.com/ianare/exif-py) project. I also used the [geoname-to-sqlite script](https://github.com/robotamer/geonames-to-sqlite) to convert [Geonames databases](http://download.geonames.org/export/dump/) into sqlite databases.


The project in general is part of the thesis of my diploma Msc. Computer Science (Univeristy of Kent) :
> Crawling the Internet for EXIF data and contextual mismatches.

Requirements
-----------

To be able to run the project, you will need:

* [Python v 2.6-2.7.5] - version 2.7.5 is recommended (scrapy is not compatible python 3 !)
* [Scrapy v 1.6.5] - The project has been tested only with this version. It might be compatible with newer versions


Installation
--------------

No installation, just extract the folder where you want =)

Configure
-----------

##### The project cannot be used without configuring it.

First, you need to create a free account from Geonames website and activate it to use the Web Service. When it is done, edit the value "WSGeonames_user" from the file "utils/ws_geonames.py" to your username.

```python
WSGeonames_user = 'username'
```

Then download the database cities15000.zip (http://download.geonames.org/export/dump/cities15000.zip) and extract it to the folder "scripts/". Launch the sqlite converter with the command:
```sh
cd scripts && php worldcities2sql.php && cp cities15000.sqlite ../ressource/ && cd ..
```
*Note: you can download larger databases such as cities5000 or cities1000. Just don't forget to change the filename in scripts/wordcities2sql.php and in utils/ws_geonames.py (global variable DBGeonames)*


Use
----------

Edit the file "crawler/spiders/genericSpider.py" and change the value of the variables:

```python
    allowed_domains = ['www.domain.net']
    start_urls = ['http://www.domain.net/site']
```

You can also edit the file crawler/settings.py for scrapy settings.

When you are ready, just run one of the following command:
```sh
  scrapy crawl genericSpider
  scrapy crawl genericSpider -o dump/full.json -t json
```

*Note: check [Scrapy Documentation](http://doc.scrapy.org/en/0.16/) for all settings and customization.*

Results
----------
The program will always dump the results to "dump/stats_{%timestamp}.json".
Here is an example of the content of the file:

```json
{
    "genericSpider": [

        {
            "exif": "yes",
            "gps_city": "Lyon",
            "gps_country": "FR",
            "latitude": 45.761000000000003,
            "longitude": 4.8546666666666667,
            "page": "http://example.net/blog/exemple-of-mismatch-1/",
            "picture": "http://www.example.net/blog/wp-content/uploads/2013/06/ice_cream-300x224.jpg",
            "picture_destination": "http://www.example.net/blog/wp-content/uploads/2013/06/ice_cream.jpg",
            "results": {
                "match_city": false,
                "match_country": false,
                "mismatch_city": [],
                "mismatch_country": [
                    {
                        "country": "ES",
                        "distance": 963.1623484533053
                    }
                ]
            }
        },
        (...)
        // more results
    ]
}
```

License
-
MIT

*Mohamed Amine AISSATI - https://github.com/maissati*

  

    