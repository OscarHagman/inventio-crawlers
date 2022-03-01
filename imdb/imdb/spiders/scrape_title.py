import scrapy
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ScrapeTitleSpider(scrapy.Spider):
    name = 'scrape_title'
    allowed_domains = ['imdb.com']
    COLLECTION_NAME = "titles"
    BASE_URL = os.getenv("SCRAPE_TITLE")

    def start_requests(self):
        URL = self.BASE_URL + self.ID + "/" # Gets ID from "scrapy -a ID=tt1234567..."
        yield scrapy.Request(url=URL, callback=self.parse)

    def parse(self, response):
        title_page = response.xpath("//main[@role='main']")

        # TITLE HEADER SECTION
        title_name = title_page.xpath(".//h1[@data-testid='hero-title-block__title']//text()").get()
        
        # RATING SECTION IN TITLE HEADER
        rating_div = title_page.css("div.AggregateRatingButton__ContentWrap-sc-1ll29m0-0.hmJkIS")
        rating = rating_div.css("span.AggregateRatingButton__RatingScore-sc-1ll29m0-1.iTLWoV::text").get()
        num_of_votes = rating_div.css("div.AggregateRatingButton__TotalRatingAmount-sc-1ll29m0-3.jkCVKJ::text").get()
        meta_score = title_page.xpath("//ul[@data-testid='reviewContent-all-reviews']//span[@class='score-meta']//text()").get()

        # MEDIA SECTION
        img_src = title_page.xpath(".//div[@data-testid='hero-media__poster']//img[@class='ipc-image']//@src").get()
        img_src = self.get_img_full_res(img_src)
        trailer_src = title_page.xpath(".//div[@data-testid='hero-media__slate']//a/@href").get()
        # div.hero-media__slate a::attr(href)
        #trailer_src = self.get_video_url(trailer_src)
        
        # CAST SECTION
            # Get top cast
            # Get directors
            # Get writers
        
        # MORE LIKE THIS SECTION
            # Get id, name and rating

        # STORYLINE SECTION
        storyline_section = title_page.xpath(".//section[@data-testid='Storyline']")
        storyline_text = storyline_section.xpath(".//div[@data-testid='storyline-plot-summary']//div/div/text()").get()
        # GENRES SECTION IN STORYLINE
        genres_selector_list = storyline_section.xpath(".//li[@data-testid='storyline-genres']//ul[@role='presentation']//li")
        genres = []
        for genre in genres_selector_list:
            genres.append(genre.xpath("./a/text()").get())
        
        # Get Certificate (18, PG, 16 etc)
        
        # DETAILS SECTION
            # Get release date
            # Get Country of origin
            # Get Official Sites
            # Get Languages
            # Get production companies
        
        # BOX OFFICE SECTION
            # Get Budget
            # Get Gross US & Canada
            # Get Opening weekend US & Canada
            # Get Gross worldwide

        # TECH SPEC SECTIONS
            # Get runtime
            # Get Color
            # Get aspect ratio
        
        # Test

        return {
            "UPDATED_AT": datetime_now,
            "URL": response.url,
            "id": self.ID, 
            "name": title_name,
            "imdb_rating": rating,
            "number_of_votes": num_of_votes,
            "meta_score": meta_score,
            "image": img_src,
            "trailer": "https://www.imdb.com" + trailer_src,
            "genres": genres,
            "storyline": storyline_text
        }

    def get_video_url():
        # Use splash to load webpage in docker container
        # follow trailer link and get the src from //*[@id="imdb-jw-video-1"]//div[@class="jw-media jw-reset"]//video/@src
        pass

    def get_img_full_res(self, img_src):
        #remove the last part of the string up to "V1_" but keep the ".jpg"
        pass
