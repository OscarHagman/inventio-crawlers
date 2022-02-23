import scrapy
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
datetime_now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")


class GetTitlesIdsSpider(scrapy.Spider):
    name = "get_titles_ids"
    allowed_domains = ["https://www.imdb.com"]
    COLLECTION_NAME = "titlesIds"
    BASE_URL = os.getenv("GET_TITLES_IDS_BASE_URL")
    HAS_NEXT_PAGE = 0
    START_URL = ""

    def start_requests(self):
        # Gets GENRE from "scrapy -a GENRE=comedy"
        self.START_URL = self.BASE_URL + self.GENRE + os.getenv("GET_TITLES_IDS_END_URL") # E.G: imdb.com/search/title/?genres=comedy&sort=release_date,desc
        yield scrapy.Request(url=self.START_URL, callback=self.parse)

    def parse(self, response):
        page = response.xpath("//div[@class='article']").css("div.lister.list.detail.sub-list")
        titles_list = page.xpath(".//div[@class='lister-list']").css("div.lister-item.mode-advanced")
        
        for title in titles_list:
            imdb_id = title.xpath("string(./div[contains(@class, 'lister-item-image')]/a/img/@data-tconst)").get()
            name = title.xpath("./div[@class='lister-item-content']/h3/a/text()").getall()
            yield {
                "id": imdb_id,
                "name": name
            }
        
        next_page = response.xpath("//div[@class='article']/div[@class='desc']/a[contains(@class, 'next-page')]/@href").get()
        if next_page:
            if self.HAS_NEXT_PAGE <= 1:
                self.HAS_NEXT_PAGE += 1
                next_page_url = self.allowed_domains[0] + next_page
                yield scrapy.Request(url=next_page_url, callback=self.parse, dont_filter=True)
            else:
                yield {
                    "UPDATED AT": datetime_now,
                    "GENRE SCRAPED": self.GENRE,
                    "START_URL": self.START_URL,
                    "END_URL": response.url
                }
