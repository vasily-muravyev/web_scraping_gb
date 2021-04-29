# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    authors = scrapy.Field()
    price = scrapy.Field()
    rating = scrapy.Field()