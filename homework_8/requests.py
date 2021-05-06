from pymongo import MongoClient

client = MongoClient("localhost:27017")
db = client['instagram']


def get_user_subscriptions(db, username):
    record = db["subscriptions_info"].find_one({"name": username})
    return record["subscription_ids"]


def get_user_subscribers(db, username):
    record = db["subscribers_info"].find_one({"name": username})
    return record["subscriber_ids"]


subscriptions = get_user_subscriptions(db, "drummer_pit")
subscribers = get_user_subscribers(db, "cheburator404")
print(len(subscriptions), subscriptions)
print(len(subscribers), subscribers)