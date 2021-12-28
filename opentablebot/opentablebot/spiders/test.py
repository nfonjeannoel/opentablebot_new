import requests
from scrapy import Selector

from main import getJson
# r = requests.get("https://www.opentable.ca/r/piatto-pizzeria-and-enoteca-charlottetown")
#
# response = Selector(text=r.text)
# print(response.css(".schema-json ::text").get())
# # print(getJson(r.text))


import pathlib
print(str(pathlib.Path(__file__).parent.parent.resolve()).replace("\\", "/"))