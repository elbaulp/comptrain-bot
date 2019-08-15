#! python3
import datetime
import logging
import os
from time import sleep

import bs4
import requests
import telegram
import schedule


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def clean_nested(x):
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
    # Replace br with \n
    for br in x.find_all("br"):
        logging.info("Removing br tag %s" % br)
        # br.replace_with('\n')
        br.extract()
    for span in x.find_all("span"):
        logging.info("Removing span tag %s" % span)
        span.unwrap()
    if x.name == "p":
        x.name = "br"
        buff += str(x)
    if x.name == "h2":
        x.string = x.string.upper()
        x.name = "strong"
        x.attrs = {}
        buff += "\n\n{}\n\n".format(x)

    buff = buff.replace("<br>", "")
    buff = buff.replace("</br>", "\n\n")

    return buff


def main():
    # ------------------- E-mail list ------------------------
    token = os.environ["TOKEN"]
    me = os.environ["ME"]
    # --------------------------------------------------------

    # Download page
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"
    }

    getPage = requests.get("https://comptrain.co/free-programming/", headers=headers)
    getPage.raise_for_status()  # if error it will stop the program

    # Parse text for foods
    soup = bs4.BeautifulSoup(getPage.text, "html.parser")
    mydivs = soup.findAll("div", {"class": "vc_gitem-zone-mini"}, limit=2)[1]
    date = mydivs.h4.get_text()  # .find('h4').getText()
    date = "<strong>{}</strong>".format(date.upper())

    a = mydivs.find_all(["p", "h2"])[2:]
    buff = "{}".format(date)
    for item in a:
        if not item.has_attr("style") or item.name == "h2":
            buff = "%s%s" % (buff, clean_html(item))

    bot = telegram.Bot(token=token)

    logging.info("Sending {}\n\n".format(buff))

    bot.send_message(chat_id=me, text=buff, parse_mode="html")

    logging.info("%s" % buff)


if __name__ == "__main__":
    main()
    # logging.info("Starting at %s" % datetime.datetime.now())
    # schedule.every().day.at("03:00:00").do(main)
    # while True:
    #     # logging.info('Time %s' % datetime.datetime.now())
    #     schedule.run_pending()
    #     sleep(30)
