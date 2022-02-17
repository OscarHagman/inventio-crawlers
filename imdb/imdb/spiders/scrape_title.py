import scrapy
from dotenv import load_dotenv
import os

load_dotenv()


class ScrapeTitleSpider(scrapy.Spider):
    name = 'scrape_title'
    allowed_domains = ['imdb.com']
    COLLECTION_NAME = "titles"
    BASE_URL = os.getenv("SCRAPE_TITLE")

    def start_requests(self):
        URL = self.BASE_URL + self.ID + "/" # Gets ID from "scrapy -a ID=tt1234567..."
        yield scrapy.Request(url=URL, callback=self.parse)

    def parse(self, response):
        title_page = response.xpath("//div[@id='ipc-wrap-background-id']")

        name = title_page.xpath("//h1[contains(@class, 'TitleHeader__TitleText-sc-1wu6n3d-0 dxSWFG')]/text()").get()
        
        rating_div = title_page.xpath("//div[contains(@class, 'AggregateRatingButton__ContentWrap-sc-1ll29m0-0')]")
        rating = rating_div.xpath("//span[contains(@class, 'AggregateRatingButton__RatingScore-sc-1ll29m0-1 iTLWoV')]/text()").get()

        tech_spec_div = scrapy.Selector(title_page).css('.ipc-metadata-list ipc-metadata-list--dividers-none ipc-metadata-list--compact ipc-metadata-list--base')
        

        return {
            "id": self.ID, 
            "name": name,
            "rating": rating
        }
