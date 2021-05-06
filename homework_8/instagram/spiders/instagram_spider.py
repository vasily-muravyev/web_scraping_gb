import scrapy
from scrapy.http import HtmlResponse
import re
import json
from pprint import pprint
from urllib.parse import quote
from copy import deepcopy
from homework_8.instagram.items import InstagramUserInfoItem, InstagramUserSubscribersInfo, InstagramUserSubscriptionsInfo


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    username = "bazil.mur"
    enc_password = "#PWD_INSTAGRAM_BROWSER:10:1620294983:AdNQADfroU5t+dSj9bHIcCj7pvFKNGg+JTMxMqhS0oP3SnorSkjuldzeukbf0MS64U05RGYrQ+BBsVeGdsypvTWfH5N9hbNcNj8XzxPen6CzsCkOD6Jf8eFHjnUM5cNkhUwsFoeiA+70OeYFPw=="
    user_to_parse_url_template = "/%s"
    subscriptions_query_hash = "3dec7e2c57367ef3da3d987d89f9dbc8"
    subscribers_query_hash = "5aefa9893005572d237da5068082d8d5"
    graphql_url = "https://www.instagram.com/graphql/query/?"

    def __init__(self, users_to_parse):
        super().__init__()
        self.users_to_parse = users_to_parse

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.login_url,
            method="POST",
            callback=self.user_login,
            formdata={
                "username": self.username,
                "enc_password": self.enc_password
            },
            headers={
                'x-csrftoken': csrf_token
            }
        )

    def user_login(self, response: HtmlResponse):
        data = response.json()
        if data['authenticated']:
            for user_to_parse in self.users_to_parse:
                yield response.follow(
                    self.user_to_parse_url_template % user_to_parse,
                    callback=self.user_data_parse,
                    cb_kwargs={
                        "username": user_to_parse,
                    }
                )

    def make_str_variables(self, variables):
        str_variables = quote(
            str(variables).replace(" ", "").replace("'", '"')
        )
        return str_variables

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {
            'first': 12,
            'id': user_id,
            'name': username
        }

        str_variables = self.make_str_variables(variables)
        url_subscribers = f"{self.graphql_url}query_hash={self.subscribers_query_hash}&variables={str_variables}"
        url_subscriptions = f"{self.graphql_url}query_hash={self.subscriptions_query_hash}&variables={str_variables}"

        yield response.follow(
            url_subscribers,
            callback=self.user_subscribers_parse,
            cb_kwargs={
                "variables": deepcopy(variables),
            }
        )
        yield response.follow(
            url_subscriptions,
            callback=self.user_subscriptions_parse,
            cb_kwargs={
                "variables": deepcopy(variables),
            }
        )

    def user_subscribers_parse(self, response: HtmlResponse, variables):
        data = response.json()
        info = data["data"]["user"]['edge_followed_by']
        subscribers = info['edges']

        if "subscriber_ids" not in variables:
            variables["subscriber_ids"] = []

        for subscriber in subscribers:
            subscriber_id = int(subscriber["node"]["id"])
            variables["subscriber_ids"].append(subscriber_id)

            user_info_item = InstagramUserInfoItem()
            user_info_item["_id"] = subscriber_id
            user_info_item["name"] = subscriber["node"]["username"]
            user_info_item["photo_url"] = subscriber["node"]["profile_pic_url"]
            yield user_info_item

        page_info = info['page_info']
        if page_info['has_next_page']:
            variables['after'] = page_info['end_cursor']
            str_variables = self.make_str_variables(variables)
            url_subscribers = f"{self.graphql_url}query_hash={self.subscribers_query_hash}&variables={str_variables}"

            yield response.follow(
                url_subscribers,
                callback=self.user_subscribers_parse,
                cb_kwargs={
                    "variables": variables,
                }
            )
        else:
            user_subscribers_item = InstagramUserSubscribersInfo()
            user_subscribers_item["_id"] = variables["id"]
            user_subscribers_item["name"] = variables["name"]
            user_subscribers_item["subscriber_ids"] = variables["subscriber_ids"]
            yield user_subscribers_item

    def user_subscriptions_parse(self, response: HtmlResponse, variables):
        data = response.json()
        info = data["data"]["user"]['edge_follow']
        subscriptions = info['edges']
        variables["first"] = 24

        if "subscription_ids" not in variables:
            variables["subscription_ids"] = []

        for subscription in subscriptions:
            subscription_id = int(subscription["node"]["id"])
            variables["subscription_ids"].append(subscription_id)

            user_info_item = InstagramUserInfoItem()
            user_info_item["_id"] = subscription_id
            user_info_item["name"] = subscription["node"]["username"]
            user_info_item["photo_url"] = subscription["node"]["profile_pic_url"]
            yield user_info_item

        page_info = info['page_info']
        if page_info['has_next_page']:
            variables['after'] = page_info['end_cursor']
            str_variables = self.make_str_variables(variables)
            url_subscriptions = f"{self.graphql_url}query_hash={self.subscriptions_query_hash}&variables={str_variables}"

            yield response.follow(
                url_subscriptions,
                callback=self.user_subscriptions_parse,
                cb_kwargs={
                    "variables": variables,
                }
            )
        else:
            user_subscription_item = InstagramUserSubscriptionsInfo()
            user_subscription_item["_id"] = variables["id"]
            user_subscription_item["name"] = variables["name"]
            user_subscription_item["subscription_ids"] = variables["subscription_ids"]
            yield user_subscription_item

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')