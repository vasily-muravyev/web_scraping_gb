# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
from homework_8.instagram.items import InstagramUserInfoItem, InstagramUserSubscribersInfo, InstagramUserSubscriptionsInfo

class InstagramPipeline:
    def __init__(self):
        self.client = MongoClient("localhost:27017")
        self.db = self.client["instagram"]

    def process_item(self, item, spider):

        if isinstance(item, InstagramUserInfoItem):
            self.db['user_info'].update_one(
                {"_id": item["_id"]},
                {
                    "$set": {"name": item["name"],
                             "photo_url": item["photo_url"]}
                },
                upsert=True)
        elif isinstance(item, InstagramUserSubscribersInfo):
            self.db['subscribers_info'].update_one(
                {"_id": item["_id"]},
                {
                    "$set": {"name": item["name"],
                             "subscriber_ids": item["subscriber_ids"]}
                },
                upsert=True)
        elif isinstance(item, InstagramUserSubscriptionsInfo):
            self.db['subscriptions_info'].update_one(
                {"_id": item["_id"]},
                {
                    "$set": {"name": item["name"],
                             "subscription_ids": item["subscription_ids"]}
                },
                upsert=True)

        return item

    def close_spider(self, spider):
        self.client.close()