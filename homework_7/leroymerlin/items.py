# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from bs4 import BeautifulSoup as bs


def get_price(price):
    return int(price.replace(" ", ""))


def get_parameter(parameter):
    soup = bs(parameter, "html.parser")
    key = soup.find(attrs={"class": "def-list__term"}).text.strip()
    value = soup.find(attrs={"class": "def-list__definition"}).text.strip()
    return {key: value}


class MergeParameters:
    def __call__(self, parameters):
        result = {}
        for param in parameters:
            for key, value in param.items():
                result[key] = value
        return result


class LeroymerlinParserItem(scrapy.Item):
    _id = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    parameters = scrapy.Field(input_processor=MapCompose(get_parameter),
                              output_processor=MergeParameters())
    price = scrapy.Field(input_processor=MapCompose(get_price),
                         output_processor=TakeFirst())