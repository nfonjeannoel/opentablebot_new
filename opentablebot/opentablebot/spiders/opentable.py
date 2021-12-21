import json

# import requests
import scrapy
from scrapy.crawler import CrawlerProcess

from endpoints import endpoint
from main import getJson, get_ird, get_menu, get_image_list

all_data = []


def save_data():
    with open(f"{file_name}.json", "w") as f:
        f.write(json.dumps(all_data))
    f.close()


def save_resto(data):
    with open("temp_output.json", "a+") as f:
        f.write(json.dumps(data))


class OpentableSpider(scrapy.Spider):
    name = 'opentable'
    print(f"""
            choose 1 for canada
            choose 2 for germany
            choose 3 for mexico
            """)
    choice = int(input("enter choice"))
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

    def parse(self, response):
        hotel_names = response.css("a.rest-row-name::attr(href)").getall()
        for hotel in hotel_names:
            yield response.follow(hotel, callback=self.get_details)

    def get_details(self, response):
        rid = get_ird(response.css("head").get())
        menu_variants = getJson(response.text)
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
            "price_range" : details.get("priceRange", "NA"),
            "restaurant_rating": details.get("aggregateRating", {}),
            "website": details.get("url", "NA"),
            "overview": details.get("description", "NA"),
            "images": details.get("image", []) + image_list,
            "menu": menus,
            "reviews": details.get("review", [])
        }

        global all_data

        save_resto(mydata)
        all_data.append(mydata)


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(OpentableSpider)
    process.start()
    save_data()