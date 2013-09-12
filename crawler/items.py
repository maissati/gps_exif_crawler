# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class CrawlerItem(Item):
	
	page = Field()
	picture = Field()
	picture_destination = Field()
	exif = Field()
	latitude = Field()
	longitude = Field()
