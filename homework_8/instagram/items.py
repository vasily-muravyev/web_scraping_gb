# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


# для простоты реализации учебной задачи будем просто хранить списки подписок и подписчиков
# в отдельных коллекциях и еще в одной коллекции информацию о пользователях

class InstagramUserInfoItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    photo_url = scrapy.Field()


class InstagramUserSubscribersInfo(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    subscriber_ids = scrapy.Field()


class InstagramUserSubscriptionsInfo(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    subscription_ids = scrapy.Field()