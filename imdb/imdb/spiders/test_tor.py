import scrapy


class TestSpider(scrapy.Spider):
    name = 'get-user-agent'
    start_urls = ['https://www.whatismybrowser.com/detect/what-is-my-user-agent/']
    COLLECTION_NAME = "UA"

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse, dont_filter=True, headers={
            "User-Agent": self.USER_AGENT
        })

    def parse(self, response):
        return {"UA": response.xpath("/html/body/div/section[2]/div/div[1]/div/div/a/text()").get()}