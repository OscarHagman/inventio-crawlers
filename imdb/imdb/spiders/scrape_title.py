import scrapy


class ScrapeTitleSpider(scrapy.Spider):
    name = 'scrape_title'
    allowed_domains = ['imdb.com']
    start_urls = ['http://imdb.com/']

    def parse(self, response):
        pass
