import scrapy


class QuotesSpider(scrapy.Spider):
    name = "imdb"
    allowed_domains = ['www.imdb.com']

    def start_requests(self):
        urls = ["https://www.imdb.com/feature/genre"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        genres_page = response.xpath("//*[@id='main']")
        genres_by_images = genres_page.xpath(".//img[contains(@class, 'pri_image')]/../..")

        for genre in genres_by_images:
            genre_link = genre.xpath(".//a/@href").get()
            genre_name = genre.xpath("string(.//a/img/@title)").get()
            print("NAME:", genre_name + "\nLINK:", genre_link)


        # genres_by_text = response.xpath('//*[@id="main"]')


        """
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')
        """