from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instagram import settings
from instagram.spiders.instagram_spider import InstagramSpider


if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    users_to_parse = ["drummer_pit", "cheburator404"]
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpider, users_to_parse=users_to_parse)

    process.start()