import os
import requests
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
from typing import List, Dict, Tuple

PAGE_URL = "https://bulbapedia.bulbagarden.net/wiki/Category:Illus._by_Yuka_Morii"
MAILGUN_API_KEY = os.environ["MAILGUN_API_KEY"]
MAILGUN_DOMAIN = os.environ["MAILGUN_DOMAIN"]
EMAIL_TO = os.environ["MAILGUN_TARGET"]
EMAIL_FROM = f"yuka-morii-checker@{MAILGUN_DOMAIN}"
client = MongoClient(os.environ["MONGO_URL"])


def scrape_cards() -> List[Tuple[str, str]]:
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
    print(f" -> Found {len(cards)} cards")
    return cards


def get_known_cards() -> Dict[str, str]:
    return {c["title"]: c["url"] for c in client.ymc.cards.find(projection=["title", "url"])}


def filter_new_cards(cards: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    print("Checking against known cards")
    known_cards = get_known_cards()
    print(f" -> {len(known_cards.keys())} cards known")
    new_cards = [c for c in cards if not c[0] in known_cards]
    for title, _ in new_cards:
        print(f" -> Found new: {title}")
    return new_cards


def save_cards(cards: List[Tuple[str, str]]):
    print("Saving cards")
    for title, url in cards:
        client.ymc.cards.insert_one({"title": title, "url": url})


def email_message(cards: List[Tuple[str, str]]):
    card_lines = []
    for card in cards:
        card_lines.append(f"{card[0]} https://bulbapedia.bulbagarden.net{card[1]}")
    return f"yuka-morii-checker has found {len(cards)} new cards:\n\n" + "\n".join(card_lines)


def send_email(message: str):
    print("Sending email notification")
    requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={"from": EMAIL_FROM, "to": EMAIL_TO, "subject": "yuka morii alert!", "text": message},
    )


if __name__ == "__main__":
    cards = scrape_cards()
    new_cards = filter_new_cards(cards)
    print(f"{len(new_cards)} new cards found")
    if len(new_cards) > 0:
        send_email(email_message(new_cards))
        save_cards(new_cards)
