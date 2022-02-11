import dotenv
import scrapy
import json
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()


class GetCategoriesURLsSpider(scrapy.Spider):
    name = "get-categories-urls"
    allowed_domains = ['www.imdb.com']
    #ENV = os.getenv("ENV")
    COLLECTION_NAME = "titleCategoryLists"


    def start_requests(self):
        urls = ["https://www.imdb.com/feature/genre"]
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

        # genres_by_text = response.xpath('//*[@id="main"]')
        # print("GENRES:", genres)
        # with open("URLS.json", 'w') as f:
        #     json.dump(genres, f, sort_keys=True, indent=2)
        # self.log(f"Updated URLS at {datetime_now}")
        
