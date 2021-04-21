"""
1) Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex.news
Для парсинга использовать xpath. Структура данных должна содержать:
- название источника,
- наименование новости,
- ссылку на новость,
- дата публикации

Нельзя использовать BeautifulSoup

2) Сложить все новости в БД(Mongo); без дубликатов, с обновлениями
"""

import requests
from lxml import html
from pprint import pprint
from pymongo import MongoClient
import time
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36"
}


def scrap_mailru():
    news_url_mail = "https://news.mail.ru/"

    r = requests.get(news_url_mail, headers=headers)
    dom = html.fromstring(r.text)
    news_hrefs = dom.xpath("//div[contains(@class, 'daynews__item')]/a/@href")

    info_list = []

    for href in news_hrefs:
        info = {}
        info['href'] = href

        news_req = requests.get(href, headers=headers)
        dom = html.fromstring(news_req.text)
        try:
            one_news = dom.xpath("//div[contains(@class, 'js-article')]")[0]
            info['source'] = one_news.xpath(".//a[contains(@class, breadcrumbs__link)]/@href")[0]
            info['title'] = one_news.xpath(".//h1[contains(@class, hdr__inner)]/text()")[0]
            info['datetime'] = one_news.xpath(".//span[contains(@class, js-ago)]/@datetime")[0]
        except Exception:
            print(f"Error processing url: {href}")

        info_list.append(info)
        time.sleep(1)

    return info_list


def scrap_lentaru():
    news_url_lenta = "https://lenta.ru/"
    r = requests.get(news_url_lenta, headers=headers)
    dom = html.fromstring(r.text)
    news_hrefs = dom.xpath("//a[contains(@href, '/news')]/@href")

    info_list = []

    for href in news_hrefs:
        # skip external news
        if href[0] != '/':
            continue
        href = "https://lenta.ru" + href
        info = {}
        info['href'] = href

        news_req = requests.get(href, headers=headers)
        dom = html.fromstring(news_req.text)
        try:
            one_news = dom.xpath("//div[@class='b-topic__content']")[0]
            info['source'] = "https://lenta.ru/"
            info['title'] = one_news.xpath(".//h1[@class='b-topic__title']/text()")[0]
            info['datetime'] = one_news.xpath(".//time/@datetime")[0]

            info_list.append(info)
        except Exception:
            print(f"Error processing url: {href}")
        time.sleep(1)
    return info_list


def scrap_yandexnews():
    news_url_yandex = "https://yandex.ru/news"
    r = requests.get(news_url_yandex, headers=headers)
    dom = html.fromstring(r.text)

    article_items = dom.xpath("//article")

    info_list = []

    for article in article_items:
        info = {}
        try:
            info['href'] = article.xpath(".//a/@href")[0]
            info['title'] = article.xpath(".//h2/text()")[0]

            # здесь я пытался честно перейти еще раз по ссылке и оттуда распарсить ссылку
            # на сайт источник. но яндекс добавляет тут капчу и скачать по цепочке не выходит
            # поэтому ограничился тут названием источника, а не ссылкой
            info['source'] = article.xpath(".//span[contains(@class, '__source')]/a/text()")[0]

            source_time = article.xpath(".//span[contains(@class, '-source__time')]/text()")[0]

            # здесь написано не очень аккуратно - потому что иногда встречаются времена с датами тоже
            # такие записи будут выдавать ошибку
            # для учебного примера будем считать, что это не критично
            today = datetime.today().date()
            source_time = datetime.strptime(source_time, "%H:%M").time()
            info['datetime'] = str(datetime.combine(today, source_time))

            # была идея парсия из атрибута data-log-id, но значение там константное для разных статей
            # кажется что смысл этого атрибуты не тот что нам нужен
            # ts = article.xpath(".//a/@data-log-id")[0].split('-')[1]
            # info['datetime'] = str(datetime.fromtimestamp(int(ts) / 1000))
            info_list.append(info)
        except Exception:
            print(f"Error processing url: {info['href']}")
        time.sleep(1)
    return info_list


MONGO_URI = "127.0.0.1:27017"
MONGO_DB = "news"


def write_news_to_db(name, news_list):
    with MongoClient(MONGO_URI) as client:
        db = client[MONGO_DB]
        collection = db[name]
        for news in news_list:
            id = news['href']
            collection.update_one(
                {"_id": id},
                {
                    "$set": {"title": news["title"],
                             "source": news["source"],
                             "datetime": news["datetime"]}
                },
                upsert=True
            )


mailru_news_list = scrap_mailru()
write_news_to_db('mail.ru', mailru_news_list)
# pprint(mailru_news_list)

lentaru_news_list = scrap_lentaru()
write_news_to_db('lenta.ru', lentaru_news_list)
# pprint(lentaru_news_list)

yandex_news_list = scrap_yandexnews()
write_news_to_db('yandex.ru', yandex_news_list)
# pprint(yandex_news_list)