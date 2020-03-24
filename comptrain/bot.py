""""""
import datetime
import logging
import os
from time import sleep

import bs4
import requests
import schedule
import telegram

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)


def clean_nested(x):
    """"""
    if x.em:
        for i in x.em.find_all("strong"):
            i.parent.unwrap()
    if x.strong:
        for i in x.strong.find_all("em"):
            i.parent.unwrap()

    return x


def clean_html(x):
    x = clean_nested(x)

    buff = ""
    for element in x(text=lambda text: isinstance(text, bs4.Comment)):
        element.extract()
    # Replace br with \n
    for br in x.find_all("br"):
        logging.debug("Removing br tag %s" % br)
        br.extract()
    for span in x.find_all("span"):
        logging.debug("Removing span tag %s" % span)
        span.unwrap()
    if x.name == "p":
        x.name = "br"
        x.attrs = {}
        buff += str(x)
    if x.name == "h2":
        x.string = x.string.upper()
        x.name = "strong"
        x.attrs = {}
        buff += f"\n\n{x}\n\n"

    buff = buff.replace("<br>", "")
    buff = buff.replace("</br>", "\n\n")

    return buff


def parse_page(url: str, headers: dict) -> str:
    getPage = requests.get(url, headers=headers)
    getPage.raise_for_status()  # if error it will stop the program

    # Parse text for foods
    soup = bs4.BeautifulSoup(getPage.text, "html.parser")
    mydivs = soup.findAll("div", {"class": "wod-info"}, limit=1)[0]
    date = soup.findAll("div", {"class": "wod-date"}, limit=1)[0].h5.get_text()
    date = f"<strong>{date.upper()}</strong>\n\n"

    a = mydivs.find_all(["p", "h2"])

    buff = f"{date}"
    for item in a:
        if not item.has_attr("style") or item.name == "h2":
            buff = "%s%s" % (buff, clean_html(item))

    return buff


def send_message(*args: str):
    token = os.environ["TOKEN"]
    me = os.environ["ME"]

    bot = telegram.Bot(token=token)

    for msg in args:
        bot.send_message(
            chat_id=me, text=msg, parse_mode="html", disable_notification=True
        )
        logging.info(f"Sending msg:\n{msg}\n\n\n")


def main():

    # Download page
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"
    }

    wod = parse_page("https://comptrain.co/wod/", headers)
    home_wod = parse_page("https://comptrain.co/home-gym/", headers)
    send_message(wod, home_wod)


if __name__ == "__main__":
    logging.info("Starting at %s" % datetime.datetime.now())
    schedule.every().day.at("03:00:00").do(main)
    while True:
        logging.info("Time %s" % datetime.datetime.now())
        schedule.run_pending()
        sleep(30)
