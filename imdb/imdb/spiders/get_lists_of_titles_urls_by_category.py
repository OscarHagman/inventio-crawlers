import scrapy
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()


class GetListsOfTitlesURLsByCategorySpider(scrapy.Spider):
    name = "get_lists_of_titles_urls_by_category"
    allowed_domains = ['www.imdb.com']
    COLLECTION_NAME = "ListsOfTitlesByCategory"
    URL = os.getenv("GET_LISTS_OF_TITLES_URLS_BY_CATEGORY_URL")

    def start_requests(self):
        yield scrapy.Request(url=self.URL, callback=self.parse)

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
