import scrapy
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()


class GetTitleCategoryListsURLsSpider(scrapy.Spider):
    name = "get_title_category_urls"
    allowed_domains = ['www.imdb.com']
    COLLECTION_NAME = "titleCategoryLists"
    URL = os.getenv("GET_TITLE_CATEGORY_LISTS_URLS_SPIDER_URL")

    def start_requests(self):
        urls = [self.URL]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        genres_page = response.xpath("//*[@id='main']")
        genres_by_images = genres_page.xpath(".//img[contains(@class, 'pri_image')]/../..")

        genres = []
        datetime_now = datetime.now()
        genres.append({"UPDATED AT": datetime_now.strftime("%m/%d/%Y %H:%M:%S")})

        for genre in genres_by_images:
            genre_url = genre.xpath(".//a/@href").get()
            genre_name = genre.xpath("string(.//a/img/@title)").get()

            genres.append({"genre": genre_name, "url": genre_url})
        
        return genres        
