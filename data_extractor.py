import os
import csv
import json
import requests
import random
import pprint as pp
import pandas as pd
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path

data_path = Path("data")
if not data_path.exists():
    data_path.mkdir(parents=True)

# Total pages: 3
def coinmarketcap(pages, target):
    print("Started Coinmarketcap extraction")
    session = requests.Session()
    for page in range(pages):
        print("Extracting page: ", page)
        r = requests.get(
            "https://api.coinmarketcap.com/data-api/v3/headlines/alexandria/articles?slug=bitcoin&page="
            + str(page)
            + "&size=1000",
        )
        try:
            for i in r.json()["data"]:
                target["title"].append(i["title"])
                target["date"].append(i["publishedOn"])
        except:
            print("Error in request")
            print("Status: ", r.status_code)
    return 0


# Total pages: 40
def blockcrypto(pages, target):
    print("Started Blockcrypto extraction")
    session = requests.Session()
    for page in range(1, pages):
        print("Extracting page: ", page)
        r = requests.get(
            "https://www.theblockcrypto.com/wp-json/v1/posts/?post_type=&page="
            + str(page)
            + "&s=bitcoin&category=&tag=&author=&posts_per_page=100&sticky=false",
        )
        try:
            for i in r.json()["posts"]:
                target["title"].append(i["title"])
                target["date"].append(i["published"])
        except:
            print("Error in request")
            print("Status: ", r.status_code)
    return 0


def cointelegraph(pages, target):
    url = "https://cointelegraph.com/tags/bitcoin"
    print("Started Cointelegraph extraction")
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    for page in range(pages):
        print("Clicking on page: ", page)

        # Agregamos un delay random
        delay_s = random.randint(1, 5)
        delay_ms = random.random()
        time.sleep(delay_s + delay_ms)  # No se si reduce el riesgo de baneo IP
        next_page = driver.find_element_by_class_name("posts-listing__more-btn")
        driver.execute_script("arguments[0].click();", next_page)

    titles = driver.find_elements_by_class_name("post-card-inline__title")
    dates = driver.find_elements_by_class_name("post-card-inline__date")
    for title, date in zip(titles, dates):
        target["title"].append(title.get_attribute("innerHTML"))
        target["date"].append(date.get_attribute("datetime"))

    driver.close()
    return 0


if __name__ == "__main__":
    data_dict = {"title": [], "date": []}
    coinmarketcap(3, data_dict)  # año-mes-dia
    blockcrypto(40, data_dict)  # año-mes-dia
    cointelegraph(250, data_dict)  # año-mes-dia
    print("Extracted:  " + str(len(data_dict["title"])) + " titles")
    print("Extracted:  " + str(len(data_dict["date"])) + " dates")

    test = pd.read_csv(
        os.path.join(data_path, "test.csv"),
        sep="|",
        parse_dates=["date"],
        date_parser=lambda col: pd.to_datetime(col, utc=True),
        infer_datetime_format=True,
    )

    df = pd.DataFrame(data_dict)

    output_file = open("test2.csv", "w")
    final = pd.concat([test, df])
    final.drop_duplicates(inplace=True)
    final.sort_values(by=["date"], inplace=True)
    final.to_csv("final_test.csv", sep="|", index=False)
    output_file.close()
