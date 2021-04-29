import scrapy
from scrapy.http import HtmlResponse
from books.items import BooksItem


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/search/?q=%D0%BC%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B0']

    def parse(self, response: HtmlResponse):
        links = response.xpath(
            '//a[@itemprop="name"]/@href'
        ).getall()

        for link in links:
            yield response.follow(link, callback=self.process_item)

        next_page = response.xpath(
            '//a[contains(@class, "_next")]/@href'
        ).get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def process_item(self, response: HtmlResponse):
        item = BooksItem()
        item["_id"] = response.url
        item["title"] = response.xpath('//h1[@class="item-detail__title"]/text()').get().strip()
        item["authors"] = response.xpath('//a[@itemprop = "author"]/text()').getall()
        item["price"] = int(response.xpath('//b[@itemprop = "price"]/text()').get())
        item["rating"] = response.xpath('//div[contains(@class, "rating__rate-value")]/text()').get()
        if item["rating"]:
            item["rating"] = float(item["rating"].strip().replace(",", '.'))

        print()
        yield item