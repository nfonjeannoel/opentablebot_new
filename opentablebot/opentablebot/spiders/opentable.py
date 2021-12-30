import datetime
import json
from time import sleep

import requests
from requests import request
import keyboard as keyboard
from playwright.sync_api import sync_playwright
# import requests
import os
import pathlib
from random import randint

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.shell import inspect_response
from scrapy.utils.response import open_in_browser

from endpoints import endpoint
from main import getJson, get_ird, get_menu, get_api_images


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


def get_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        for i in range(40):
            page.press(selector='html', key="PageDown")
        page.wait_for_timeout(timeout=10000)
        # html.send_keys(Keys.HOME)
        html = page.content()
        browser.close()
        parent_dir = str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/")
        with open(f"{parent_dir}/page_html.html", "w") as f:
            f.write(html)


class OpentableSpider(scrapy.Spider):
    name = 'opentable'

    def start_requests(self):
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

        for url in start_urls:
            if "?" in url:
                print(f"fetching {url} with headless browser")
                get_html(url)
                parent_dir = "file:///" + str(pathlib.Path(__file__).parent.resolve()).replace("\\", "/")
                # print(f"{parent_dir}/page_html")
                r = scrapy.Request(url=f"{parent_dir}/page_html.html", callback=self.parse)
            else:
                print(f"fetching {url} with scrapy")
                r = scrapy.Request(url, callback=self.parse)
            yield r

    def parse(self, response):

        hotels = response.css("._2WscsV4-12URxWrPI0TvSI a::attr(href)").getall()
        print(hotels)
        for hotel in hotels:
            yield response.follow(hotel, callback=self.get_details)
        # #     handle pagination
        max_pages = response.css("li.pagination-li span span::text").getall()
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
                for i in range(2, max_pages):
                    if "?" in response.url:
                        url = f"{response.url}&sort=Popularity&page={i}"
                    else:
                        url = f"{response.url}?sort=Popularity&from={i}00"
                    print(url)
                    # yield scrapy.Request(url=url, callback=self.parse_pagination_products)
                print(f"scraping about {max_pages * 100} data")

    def parse_pagination_products(self, response):
        hotel_names = response.css("._2WscsV4-12URxWrPI0TvSI a::attr(href)").getall()
        for hotel in hotel_names:
            yield response.follow(hotel, callback=self.get_details)

    def get_details(self, response):
        rid = get_ird(response.css("head").get())
        # rid = response.url.split("corrid=")[-1].split("&")[0]
        menu_variants = getJson(response.text)
        # get_images_from_api(response.text, rid)
        # return
        if type(menu_variants) == list:
            menus = get_menu(menu_variants)
        elif type(menu_variants) == dict:
            print(menu_variants)
            temp_menu_variants = menu_variants['menuData']
            if temp_menu_variants or temp_menu_variants is not None:
                menus = get_menu(temp_menu_variants)
            else:
                menus = menu_variants['menuInfo']['url']
        else:
            print(f"menu for {response.url} not available on website ")
            menus = response.css("a._3GP4hokChzyxZ_vA2sI6yU::attr(href)").get()

        tags = response.css("a.d302396e::text").extract()
        images = get_api_images(rid)
        details_str = response.css(".schema-json ::text").get(default="")
        if details_str == "" or details_str is None:
            details_str = response.css("#mainContent script ::text").get(default="")
        if details_str is not None or details_str != "":
            try:
                details = json.loads(details_str)
            except:
                mydata = {
                    "hotel_name": response.css("._1E11-nyyWnndSSOElGuAVa::text").get(),
                    "url": response.url,
                    "tags": tags,
                    "rid": str(rid),
                    "images" : images
                }
                save_resto(mydata)
                return
        else:
            details = {}

        # print(details)
        # return

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
            "images": images,
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
