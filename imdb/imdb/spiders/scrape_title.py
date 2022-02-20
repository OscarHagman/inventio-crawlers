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
        title_page = response.xpath("//main[@role='main']")

        # TITLE HEADER SECTION
        title_name = title_page.css(".TitleHeader__TitleText-sc-1wu6n3d-0.dxSWFG::text").get()
        
        # RATING SECTION IN TITLE HEADER
        rating_div = title_page.css("div.AggregateRatingButton__ContentWrap-sc-1ll29m0-0.hmJkIS")
        rating = rating_div.css("span.AggregateRatingButton__RatingScore-sc-1ll29m0-1.iTLWoV::text").get()
        num_of_votes = rating_div.css("div.AggregateRatingButton__TotalRatingAmount-sc-1ll29m0-3.jkCVKJ::text").get()

        # MEDIA SECTION
            # Get title image
            # Get title trailer

        # STORYLINE SECTION
        storyline_section = title_page.xpath("//section[@data-testid='Storyline']")
        storyline_text = storyline_section.xpath("//div[@data-testid='storyline-plot-summary']//div/div/text()").get()
        # GENRES SECTION IN STORYLINE
        genres_selector_list = storyline_section.xpath("//li[@data-testid='storyline-genres']//ul[@role='presentation']//li")
        genres = []
        for genre in genres_selector_list:
            genres.append(genre.xpath("./a/text()").get())
        
        # DETAILS SECTION

        #tech_spec_div = scrapy.Selector(title_page).css('.ipc-metadata-list.ipc-metadata-list--dividers-none.ipc-metadata-list--compact.ipc-metadata-list--base')
        #runtime = tech_spec_div.xpath("./div[@class='ipc-metadata-list-item__content-container']/text()").get()

        #//main[@role="main"]//div[@class='Storyline__StorylineWrapper-sc-1b58ttw-0 iywpty']//div[@data-testid="storyline-plot-summary"]//div/div/text()
        # //main[@role="main"] //div[@class="Storyline__StorylineWrapper-sc-1b58ttw-0 iywpty"] //div[@data-testid="storyline-plot-summary"] //div/div/text()
        

        return {
            "id": self.ID, 
            "name": title_name,
            "rating": rating,
            "number of votes": num_of_votes,
            "genres": genres,
            "storyline": storyline_text
        }
