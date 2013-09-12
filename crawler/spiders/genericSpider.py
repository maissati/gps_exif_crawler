from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.item import Item
from crawler.items import CrawlerItem
from scrapy import signals
from scrapy import log
from scrapy.xlib.pydispatch import dispatcher
import requests
import utils.exif as Exif
import StringIO
import pprint
import simplejson
import json
import utils.ws_geonames as WSGeonames
import utils.misc as Misc
import utils.plugins as Plugins
import gpscrawling.analysis as GPSCrawling
import datetime

class genericSpider(CrawlSpider):
    name = 'genericSpider'
    allowed_domains = ['www.tumbleweed-studio.net']
    start_urls = ['http://www.tumbleweed-studio.net/~aissat_m/scrapy/wordpress/']
    rules = (
        Rule(SgmlLinkExtractor(
            #allow = ()
            #deny = ('\?tag=', '/tag/','/tags/', '/feed/', '/category/', '#comment', 'replytocom')
            ),
            callback='parse_item',
            follow=True),
        )

    def __init__(self, *a, **kw):
        super(genericSpider, self).__init__(*a, **kw)
        self._items = {}
        self._items['genericSpider'] = []
        dispatcher.connect(self.post_process, signals.spider_closed)


    def post_process(self, spider):
        log.msg('Starting post_process function...', level=log.INFO)
        self.processMismatch()


    def CALLBACK_processImage(self, url, item):

        img = Plugins.pluginImageDownloader(url)
        stream = StringIO.StringIO(img)
        data = Exif.process_file(stream)
        if not data:
            self.log('No EXIF data for %s ' % url)
            item['exif'] = 'no'
            return item
        self.log('EXIF data found for %s' % url)
        item['exif'] = 'yes'

        if ('GPS GPSLatitude' in data) and ('GPS GPSLongitude' in data):
            self.log('EXIF GPSLatitude: %s' % data['GPS GPSLatitude'])
            self.log('EXIF GPSLongitude: %s' % data['GPS GPSLongitude'])
            item['latitude'] = Misc.transformGPS(data['GPS GPSLatitude'].printable)
            item['longitude'] = Misc.transformGPS(data['GPS GPSLongitude'].printable)
            log.msg("{0} has GPS data (origin: {1}).".format(url, item['page']), level=log.INFO)
            self._items['genericSpider'].append(dict(item))

        return item

    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        items = []

        # extract urls from the src attribute of img tags
        # Example: <img src="http://url"> will extract http://url
        images = hxs.select('//img')
        for image in images:
            item = CrawlerItem()
            item['page'] = response.url
            item['picture'] = image.select('@src').extract()[0]
            item = self.CALLBACK_processImage(item['picture'], item)
            items.append(item)

        urls = hxs.select('//a')
        for url in urls:
            if url.select('img'):
                item = CrawlerItem()
                item['page'] = response.url
                item['picture'] = url.select('img/@src').extract()[0]
                item['picture_destination'] = url.select('@href').extract()[0]
                item = self.CALLBACK_processImage(item['picture_destination'], item)
                items.append(item)

        #if len(items):
        log.msg('%s images were found.' % len(items), level=log.INFO)
        return items

    
    def processMismatch(self):

        try:
            for item in self._items['genericSpider']:
                if item['page'].find('/page/') > 0 or item['page'] == self.start_urls[0]:
                    log.msg(' Found main page, skipping {0}'.format(item['page']), level=log.INFO)
                    continue
                picture = item['picture_destination'] if 'picture_destination' in item else item['picture']
                log.msg("___________", level=log.INFO)
                log.msg("[*] URL: %s" % item['page'], level=log.INFO)
                log.msg("IMG => %s" % picture, level=log.INFO)

                content = Misc.removeTags(item['page'])
                codes = Misc.getCountryCodesFromText(content)
                country = WSGeonames.WSGeonames_CountryCode(item['latitude'], item['longitude'])
                city= WSGeonames.WSGeonames_Nearby(item['latitude'], item['longitude'])

                try :
                    item['results'] = {}

                    item['gps_country'] = country
                    item['gps_city'] = city[0]['toponymName']
                    
                    item['results']['match_country'] = GPSCrawling.matchCountry(content, country)
                    item['results']['match_city'] = GPSCrawling.matchCity(content, city)
                    item['results']['mismatch_country'] = GPSCrawling.mismatchCountry(item, codes, country)
                    item['results']['mismatch_city'] = GPSCrawling.mismatchCity(item, content, item['gps_city'])
                except Exception,e:
                    print e
        except Exception, e:
            print e
        finally:
            now = datetime.datetime.now()
            filename = "dumps/stats_"+now.strftime("%Y.%m.%d_%H-%M")+".json"
            with open(filename, 'w') as outfile:
                json.dump(self._items, outfile, sort_keys=True, indent=4)

