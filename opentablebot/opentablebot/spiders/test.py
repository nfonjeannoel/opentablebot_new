import requests
from scrapy import Selector

from main import getJson
r = requests.get("https://www.opentable.ca/nova-scotia-new-brunswick-restaurant-listings")
response = Selector(text=r.text)
hotels = response.css(".rest-row-name::attr(href)").getall()
if not hotels:
    hotels = response.css(".rest-row-name::attr(href)").getall()
# print(len(hotels))
print(hotels)
for ind, hotel in enumerate(hotels[0:]):
    nr = requests.get(hotel)
    print(response.css(".schema-json ::text").get())
    print("*"*20)
    print(getJson(r.text))
    break
# print(response.css(".schema-json ::text").get())
# print(getJson(r.text))

