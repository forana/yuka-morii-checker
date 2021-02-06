import os
import redis
import requests
from bs4 import BeautifulSoup as bs

PAGE_URL = "https://bulbapedia.bulbagarden.net/wiki/Category:Illus._by_Yuka_Morii"

if __name__ == "__main__":
    print("Scraping...")
    resp = requests.get(PAGE_URL)
    if not resp.ok:
        resp.raise_for_status()
    soup = bs(resp.content, "html.parser")
    groups = soup.find_all("div", class_="mw-category-group")
    cards = []
    for group in groups:
        items = group.find_all("a")
        for item in items:
            cards.append((item.get("title"), item.get("href")))
    print("Checking against known cards")
    r = redis.from_url(os.environ["REDIS_URL"])
    new_cards = []
    for title, url in cards:
        if r.get(title) is None:
            print(f"Found new: {title}")
            new_cards.append(card)
