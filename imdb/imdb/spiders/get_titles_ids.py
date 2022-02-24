import scrapy
from dotenv import load_dotenv
import os, os.path
from datetime import datetime

load_dotenv()
datetime_now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


class GetTitlesIdsSpider(scrapy.Spider):
    name = "get_titles_ids"
    allowed_domains = ["https://www.imdb.com"]
    COLLECTION_NAME = "titlesIds"
    BASE_URL = os.getenv("GET_TITLES_IDS_BASE_URL")
    START_URL = ""
    ON_FIRST_PAGE = True

    def save_html_snippet(self, folder, html_page):
        html_snippets_path = "html_snippets/" + self.name + "/"
        if not os.path.exists(html_snippets_path + folder):
         os.mkdir(html_snippets_path + folder)
        elif not os.path.isdir(html_snippets_path + folder):
            print(html_snippets_path + folder, "IS NOT A DIRECTORY !!!")
            return

        write_dest = html_snippets_path + os.path.join(folder, datetime_now + ".html")
        with open(write_dest, "wb+") as f:
            f.write(html_page)

    def start_requests(self):
        # Gets GENRE from "scrapy -a GENRE=comedy"
        self.COLLECTION_NAME += self.GENRE

        self.START_URL = self.BASE_URL + self.GENRE + os.getenv("GET_TITLES_IDS_END_URL") # E.G: imdb.com/search/title/?genres=comedy&sort=release_date,desc
        yield scrapy.Request(url=self.START_URL, callback=self.parse)

    def parse(self, response):
        if self.ON_FIRST_PAGE:
            self.save_html_snippet(self.GENRE, response.body)
        

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
            next_page_url = self.allowed_domains[0] + next_page
            self.ON_FIRST_PAGE = False
            yield scrapy.Request(url=next_page_url, callback=self.parse, dont_filter=True)
        else:
            yield {
                "UPDATED AT": datetime_now,
                "GENRE SCRAPED": self.GENRE,
                "START_URL": self.START_URL,
                "END_URL": response.url
            }
