# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import hashlib
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from scrapy.utils.python import to_bytes

class LeroymerlinPipeline:

    def __init__(self):
        self.client = MongoClient("localhost:27017")
        self.db = self.client["leroymerlin"]

    def process_item(self, item, spider):
        self.db[spider.search].update_one(
            {"_id": item["_id"]},
            {
                "$set": {"name": item["name"],
                         "photos": item["photos"],
                         "parameters": item["parameters"],
                         "price": item["price"]}
            },
            upsert=True)

        return item

    def close_spider(self, spider):
        self.client.close()


class LeroymerlinImagesPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f'{info.spider.search}/{image_guid}.jpg'

    def get_media_requests(self, item, info):
        if item["photos"]:
            for photo_url in item['photos']:
                try:
                    yield scrapy.Request(photo_url)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item["photos"] = [itm[1] for itm in results if itm[0]]
        return item