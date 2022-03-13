from platform import release
import scrapy
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# String manipulation start and end "words"
img_str_start = "._V1_"
img_str_end = ".jpg"
name_id_start = "/name/"
name_id_end = "?ref"
title_id_start = "/title/"
title_id_end = "/?ref"
company_id_start = "/company/"
company_id_end = "?ref"


class ScrapeTitleSpider(scrapy.Spider):
    name = 'scrape_title'
    allowed_domains = ['imdb.com']
    BASE_DOMAIN_URL = "https://www.imdb.com"
    TABLE_NAME = os.getenv("SCRAPE_TITLE_TABLE_NAME")
    BASE_URL = os.getenv("SCRAPE_TITLE_BASE_URL")

    def start_requests(self):
        URL = self.BASE_URL + self.ID + "/" # Gets ID from "scrapy -a ID=tt1234567..."
        yield scrapy.Request(url=URL, callback=self.parse)

    def parse(self, response):
        title_page = response.xpath("//main[@role='main']")

        # TITLE HEADER SECTION
        title_name = title_page.xpath(".//h1[@data-testid='hero-title-block__title']//text()").get()
        try:
            original_title = title_page.xpath('//div[@data-testid="hero-title-block__original-title"]/text()').get()
            original_title = original_title.replace("Original title: ", "")
        except Exception as e:
            pass
        
        # RATING SECTION IN TITLE HEADER
        rating_div = title_page.css("div.AggregateRatingButton__ContentWrap-sc-1ll29m0-0.hmJkIS")
        rating = rating_div.css("span.AggregateRatingButton__RatingScore-sc-1ll29m0-1.iTLWoV::text").get()
        num_of_votes = rating_div.css("div.AggregateRatingButton__TotalRatingAmount-sc-1ll29m0-3.jkCVKJ::text").get()
        meta_score = title_page.xpath("//ul[@data-testid='reviewContent-all-reviews']//span[@class='score-meta']//text()").get()

        # MEDIA SECTION
        img_src = title_page.xpath(".//div[@data-testid='hero-media__poster']//img[@class='ipc-image']//@src").get()
        img_src = self.chars_between_two_strings(img_src, img_str_start, img_str_end, "-")
        trailer_src = title_page.xpath(".//div[@data-testid='hero-media__slate']//a/@href").get()
        #trailer_src = self.get_video_url(trailer_src)
        
        # CAST SECTION
        cast_section = title_page.xpath(".//section[@data-testid='title-cast']")
        top_cast_section = cast_section.xpath(".//div[@data-testid='shoveler-items-container']//div[@data-testid='title-cast-item']")
        top_cast = self.get_top_cast(top_cast_section)

        crew_section = cast_section.css(".ipc-metadata-list.ipc-metadata-list--dividers-all.ipc-metadata-list--base")
        crew = self.get_crew(crew_section)
        
        # MORE LIKE THIS SECTION
        more_like_this_section = title_page.xpath(".//section[@data-testid='MoreLikeThis']//div[@data-testid='shoveler-items-container']")
        more_like_this_section_list = more_like_this_section.xpath(".//div[@class='ipc-poster-card ipc-poster-card--base ipc-poster-card--dynamic-width ipc-sub-grid-item ipc-sub-grid-item--span-2']")
        more_like_this = self.get_more_like_this(more_like_this_section_list)

        # STORYLINE SECTION
        storyline_section = title_page.xpath(".//section[@data-testid='Storyline']")
        storyline_text = storyline_section.xpath(".//div[@data-testid='storyline-plot-summary']//div/div/text()").get()
        # GENRES SECTION IN STORYLINE
        genres_selector_list = storyline_section.xpath(".//li[@data-testid='storyline-genres']//ul[@role='presentation']//li")
        genres = []
        for genre in genres_selector_list:
            genres.append(genre.xpath("./a/text()").get())
        
        certificate = title_page.xpath(".//li[@data-testid='storyline-certificate']//li[@class='ipc-inline-list__item']/span/text()").get()
        
        # DETAILS SECTION
        details_section = title_page.xpath(".//div[@data-testid='title-details-section']")
        details = self.get_details(details_section)
        
        # BOX OFFICE SECTION
        box_office_section = title_page.xpath(".//div[@data-testid='title-boxoffice-section']")
        box_office = self.get_box_office(box_office_section)

        # TECH SPEC SECTIONS
        tech_specs_section = title_page.xpath(".//div[@data-testid='title-techspecs-section']")
        tech_specs = self.get_tech_specs(tech_specs_section)
        
        return {
            "title_id": self.ID, 
            "UPDATED_AT": datetime_now,
            "URL": response.url,
            "title_name": title_name,
            "original_title": original_title,
            "imdb_rating": rating,
            "number_of_votes": num_of_votes,
            "meta_score": meta_score,
            "image": img_src,
            "trailer": trailer_src,
            "top_cast": top_cast,
            "crew": crew,
            "more_like_this": more_like_this,
            "genres": genres,
            "certificate": certificate,
            "storyline": storyline_text,
            "details": details,
            "box_office": box_office,
            "technical_specs": tech_specs
        }

    def get_video_url():
        # Use splash to load webpage in docker container
        # follow trailer link and get the src from //*[@id="imdb-jw-video-1"]//div[@class="jw-media jw-reset"]//video/@src
        pass

    def chars_between_two_strings(self, main_str, start_str, end_str, get_or_rm):
        try:
            start_id = main_str.find(start_str) + len(start_str)
            end_id = main_str.find(end_str)
        except AttributeError:
            return None
        except Exception as e:
            print("\n\nCHARS_BETWEEN_TWO_STRINGS:")
            print("SOMETHING UNEXPECTED HAPPENED\n\n", e)

        if get_or_rm == "+":
            new_str = main_str[start_id:end_id]
        elif get_or_rm == "-":
            new_str = main_str[:start_id] + main_str[end_id:]
        else:
            print('\n>>> NEED TO USE "+" OR "-" TO DETERMINE IF IT IS TO GET OR REMOVE CHARS FROM A STRING BETWEEN TWO "WORDS"\n')
            return

        return new_str
    
    def list_to_str(self, list):
        result = ""
        for item in list:
            result += item
        return result
    
    def list_to_str_with_space(self, list):
        result = ""
        if len(list) > 1:
            for item in list:
                result += item + " "
        elif list == []:
            return None
        else:
            return list[0]
        return result[:-1]
    
    def get_top_cast(self, top_cast_section):
        if top_cast_section is None or top_cast_section == []:
            return None

        top_cast = []
        for cast in top_cast_section:
            cast_href = cast.xpath(".//a[@data-testid='title-cast-item__actor']//@href").get()
            cast_id = self.chars_between_two_strings(cast_href, name_id_start, name_id_end, "+")
            cast_img_src = cast.xpath(".//img[@class='ipc-image']//@src").get()
            cast_image = self.chars_between_two_strings(cast_img_src, img_str_start, img_str_end, "-")
            cast_name = cast.xpath(".//a[@data-testid='title-cast-item__actor']/text()").get()
            try:
                cast_as = cast.xpath(".//span[@data-testid='cast-item-characters-with-as']/text()").get()[3:]
            except TypeError:
                cast_as = None
            except Exception as e:
                print("\nSOMETHING UNEXPECTED HAPPENED IN get_top_cast():\n", e)

            top_cast.append({
                "cast_id": cast_id,
                "cast_image": cast_image,
                "cast_name": cast_name,
                "as": cast_as
                })        
        return top_cast

    def get_crew(self, crew_section):
        if crew_section is None or crew_section == []:
            return None

        crew = []
        # Gets all the rows, each row is a crew type
        crew_rows = crew_section.xpath(".//li[@class='ipc-metadata-list__item']")
        # Loops through each row, getting each column (row = crew type, column = crew individual)
        for crew_type in crew_rows:
            cast_type = crew_type.xpath(".//span[@class='ipc-metadata-list-item__label']/text()").get()
            cast_columns = crew_type.xpath(".//li[@class='ipc-inline-list__item']")
            crew_individuals = []
            for crew_individual in cast_columns:
                crew_href = crew_individual.xpath(".//a/@href").get()
                crew_id = self.chars_between_two_strings(crew_href, name_id_start, name_id_end, "+")
                crew_name = crew_individual.xpath(".//a/text()").get()
                crew_individuals.append({"cast_id": crew_id, "cast_name": crew_name})

            crew.append({cast_type: crew_individuals})        
        return crew
    
    def get_more_like_this(self, more_like_this_section):
        if more_like_this_section is None or more_like_this_section == []:
            return None

        more_like_this = []
        for title in more_like_this_section:
            title_href = title.xpath(".//span[@data-testid='title']/../@href").get()
            title_id = self.chars_between_two_strings(title_href, title_id_start, title_id_end, "+")
            name = title.xpath(".//span[@data-testid='title']/text()").get()
            rating = title.xpath(".//span[@class='ipc-rating-star ipc-rating-star--base ipc-rating-star--imdb']/text()").get()
            more_like_this.append({"title_id": title_id, "title_name": name, "rating": rating})
        return more_like_this
    
    def get_details(self, details_section):
        if details_section is None or details_section == []:
            return None

        details_rows_selector = details_section.xpath(".//li[contains(@class, 'ipc-metadata-list__item')][not(@data-testid='title-details-companycredits')]")

        # Gets all the rows, each row is a details type
        # Loops through each row, getting each column (row = details type, column = detail)
        result = []
        for details_row in details_rows_selector:
            details_type = details_row.xpath(".//a[@class='ipc-metadata-list-item__label ipc-metadata-list-item__label--link']/text()").get()
            # if details_type is None, there weren't an a tag to scrape and the details type value is just plain text in a span tag
            if details_type is None:
                details_type = details_row.xpath(".//span[@class='ipc-metadata-list-item__label']/text()").get()

            details_columns = details_row.xpath(".//li[@class='ipc-inline-list__item']")
            details = []
            for details_column in details_columns:
                detail = details_column.xpath(".//a/text()").get()
                detail_href = details_column.xpath(".//a/@href").get()
                # if detail is not none, there is an a tag, else the coulmn value is plain text in a span tag
                if detail is not None:
                    # checks that the href is linking to an external webpage, if true add it, otherwise its not interesting
                    if "https://" in detail_href or "http://" in detail_href:
                        details.append({detail: detail_href})
                    # if the a tags href contains "/company/", get the company id and name
                    elif company_id_start in detail_href:
                        company_id = self.chars_between_two_strings(detail_href, company_id_start, company_id_end, "+")
                        details.append({"company_id": company_id, "company": detail})
                    else:
                        details.append(detail)
                else:
                    detail = details_column.xpath(".//span/text()").get()
                    details.append(detail)

            result.append({details_type: details})        
        return result
    
    def get_box_office(self, box_office_section):
        if box_office_section is None or box_office_section == []:
            return None

        box_office_list_items = box_office_section.xpath(".//li[contains(@class, 'ipc-metadata-list__item')]")
        result = []
        for box_office_list_item in box_office_list_items:
            box_office_type = box_office_list_item.xpath(".//span[@class='ipc-metadata-list-item__label']/text()").get()
            box_office_item = box_office_list_item.xpath(".//span[@class='ipc-metadata-list-item__list-content-item']/text()").getall()
            box_office_item = self.list_to_str_with_space(box_office_item)
            result.append({box_office_type: box_office_item})
        
        return result
    
    def get_tech_specs(self, tech_specs_section):
        if tech_specs_section is None or tech_specs_section == []:
            return None

        runtime = tech_specs_section.xpath(".//li[@data-testid='title-techspec_runtime']/div/text()").getall()
        runtime = self.list_to_str(runtime)
        result = [{"runtime": runtime}]

        tech_specs_list_items = tech_specs_section.xpath(".//li[@class='ipc-metadata-list__item'][not(@data-testid='title-techspec_runtime')]")
        for tech_spec in tech_specs_list_items:
            tech_spec_type = tech_spec.xpath(".//span[@class='ipc-metadata-list-item__label']/text()").get()
            tech_spec_item = tech_spec.xpath(".//a[@class='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link']/text()").getall()
            # if tech_spec_item is empty list, there weren't an a tag to scrape and the data is in a span tag instead
            if tech_spec_item == []:
                tech_spec_item = tech_spec.xpath(".//span[@class='ipc-metadata-list-item__list-content-item']/text()").get()

            result.append({tech_spec_type: tech_spec_item})

        return result
