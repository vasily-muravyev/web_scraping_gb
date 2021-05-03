import scrapy
from itemloaders import ItemLoader
from scrapy.http import HtmlResponse
from homework_7.leroymerlin.items import LeroymerlinParserItem


class LmSpider(scrapy.Spider):
    name = 'lm'
    allowed_domains = ['leroymerlin.ru']
    # start_urls = [
    #     "https://leroymerlin.ru/search/?q=%D0%BE%D0%B1%D0%BE%D0%B8&02795=%D0%A2%D0%B5%D0%BA%D1%81%D1%82%D0%B8%D0%BB%D1%8C"
    # ]

    def __init__(self, search):
        super().__init__()
        self.start_urls = [
            f"https://leroymerlin.ru/search/?q={search}"
        ]
        self.search = search

    def parse(self, response: HtmlResponse):

        links = response.xpath('//a[@data-qa = "product-name"]')
        for link in links:
            yield response.follow(link, callback=self.parse_item)

        next_page = response.xpath(
            '//a[@data-qa-pagination-item = "right"]/@href'
        ).get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_item(self, response: HtmlResponse):

        # использую этот селектор для инициализации - иначе почему-то не работает
        # не разобрался до конца почему так
        name = response.xpath('//h1[@slot="title"]')

        loader = ItemLoader(item=LeroymerlinParserItem(), response=response, selector=name)
        loader.add_value("_id", response.url)
        loader.add_xpath("name", '//h1[@slot="title"]/text()')
        loader.add_xpath("price", '//span[@slot="price"]/text()')
        loader.add_xpath("photos", '//picture/img[@itemprop="image" and @alt="product image"]/@src')
        loader.add_xpath("parameters", '//div[@class="def-list__group"]')

        yield loader.load_item()