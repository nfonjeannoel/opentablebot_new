import datetime
import json

# import requests
import os
import pathlib
from random import randint

import scrapy
from scrapy.crawler import CrawlerProcess

from endpoints import endpoint
from main import getJson, get_ird, get_menu, get_image_list


def get_week():
    return str(datetime.datetime.utcnow().isocalendar()[0]) + '-' + str(datetime.datetime.utcnow().isocalendar()[1])


week = ""
site_name = "opentable"

all_data = []
file_name = ""


def save_data():
    with open(f"{file_name}.json", "w") as f:
        f.write(json.dumps(all_data))
    f.close()


def save_resto(data):
    save_path = str(pathlib.Path(__file__).parent.resolve()).replace("\\",
                                                                     "/") + f"/{site_name}/{file_name}/{week}/{data.get('rid', 'fake-' + str(randint(10000, 90000)))}.json"
    with open(save_path, "w") as f:
        f.write(json.dumps(data))
        print(f"saved {data['hotel_name']}")


def create_path_section():
    global week
    week = get_week()
    parent_dir = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/")
    path = os.path.join(parent_dir, f"{site_name}/{file_name}/{week}")

    try:
        os.makedirs(path, exist_ok=True)
        print("sub Directory '%s' created successfully" % file_name)

    except OSError as error:
        print("sub Directory '%s' can not be created" % file_name)


class OpentableSpider(scrapy.Spider):
    name = 'opentable'
    print(f"""
            choose 1 for canada
            choose 2 for germany
            choose 3 for mexico
            """)
    choice = int(input("enter choice:- "))
    # check main,py for start urls for various countries
    # change filename to the name of the city
    global file_name
    if choice == 1:
        start_urls = endpoint[1]
        file_name = "canada"
    if choice == 2:
        start_urls = endpoint[2]
        file_name = "germany"
    if choice == 3:
        start_urls = endpoint[3]
        file_name = "mexico"
    else:
        print("*" * 20)

    create_path_section()

    def parse(self, response):
        # print(response.css("h6::text").getall())
        hotel_names = response.css("a.rest-row-name::attr(href)").getall()
        if not hotel_names:
            hotel_names = response.css("a._1e9PcCDb012hY4BcGfraQB::attr(href)").getall()
        # print(hotel_names)
        for hotel in hotel_names:
            yield response.follow(hotel, callback=self.get_details)
            # print(hotel)
        #     handle pagination
        max_pages = response.css("li.pagination-li span span::text").getall()
        print(max_pages)
        if len(max_pages) > 0:
            max_pages = max_pages[-1]
        else:
            max_pages = response.css('[data-test="pagination-link"] a::text').getall()
            if len(max_pages) > 0:
                max_pages = max_pages[-1]
            else:
                max_pages = None
        if max_pages is None:
            print("no pagination, none")
        else:
            print(max_pages)
            try:
                max_pages = int(max_pages)
            except:
                print("no pagination")
                max_pages = 1
            if max_pages != 1:
                for i in range(2, max_pages + 1):
                    if '?' in response.url:
                        url = f"{response.url}&sort=Popularity&page={i}"
                    else:
                        url = f"{response.url}?sort=Popularity&from={max_pages}00"
                    yield scrapy.Request(url=url, callback=self.parse_pagination_products)
                    print(f"scraping about {max_pages + 1 * 100} data")

    def parse_pagination_products(self, response):
        hotel_names = response.css("a.rest-row-name::attr(href)").getall()
        for hotel in hotel_names:
            yield response.follow(hotel, callback=self.get_details)

    def get_details(self, response):
        rid = get_ird(response.css("head").get())
        menu_variants = getJson(response.text)
        # print(type(menu_variants))
        # return
        # if type(menu_variants != dict):
        #     print(f"not json for {response.css('._4a4e7a6a::text').get()}")
        #     return
        menus = get_menu(menu_variants)
        details = json.loads(response.css(".schema-json ::text").get())
        tags = response.css("a.d302396e::text").extract()
        image = response.css("div._5fc02aaa").extract()
        image_list = get_image_list(image)
        mydata = {
            "hotel_name": details.get("name", "NA"),
            "url": response.url,
            "tags": tags,
            "rid": str(rid),
            "opening_hours": details.get("openingHours", "NA"),
            "phone_number": details.get("telephone", "NA"),
            "location": details.get("address", {}),
            "price_range": details.get("priceRange", "NA"),
            "restaurant_rating": details.get("aggregateRating", {}),
            "website": details.get("url", "NA"),
            "overview": details.get("description", "NA"),
            "images": details.get("image", []) + image_list,
            "menu": menus,
            "reviews": details.get("review", [])
        }

        # global all_data

        save_resto(mydata)
        # all_data.append(mydata)


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(OpentableSpider)
    process.start()
    # save_data()
