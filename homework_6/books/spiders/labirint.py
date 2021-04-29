import scrapy
from scrapy.http import HtmlResponse
from books.items import BooksItem


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7%20%D0%B4%D0%B0%D0%BD%D0%BD%D1%8B%D1%85']

    def parse(self, response: HtmlResponse):
        links = response.xpath(
                '//a[contains(@class, "product-title-link")]/@href'
        ).getall()

        for link in links:
            yield response.follow(link, callback=self.process_item)

        next_page = response.xpath(
            '//div[contains(@class, "pagination-next")]//a/@href'
        ).get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def process_item(self, response: HtmlResponse):
        item = BooksItem()
        item["_id"] = response.url
        item["title"] = response.xpath('//div[@id = "product-title"]/h1/text()').get()
        item["authors"] = response.xpath('//div[contains(@class, "authors")]/a[@data-event-label="author"]/text()').getall()
        try:
            item["price"] = int(response.xpath('//span[contains(@class, "buying-pricenew-val-number")]/text()').get())
        except:
            # если цена со скидкой не найдена - берем обычную цену
            item["price"] = int(response.xpath('//span[contains(@class, "buying-price-val-number")]/text()').get())

        item["rating"] = float(response.xpath('//div[@id="rate"]/text()').get())

        print()
        yield item