#! python3
import datetime
import logging
import os
from time import sleep

import bs4
import requests
import schedule
import telegram

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def clean_nested(x):
    for i in x.em.find_all('strong'):
        i.parent.unwrap()
    for i in x.strong.find_all('em'):
        i.parent.unwrap()
    return x


def extract_wod(x):
    x.div.unwrap()
    x.div.unwrap()
    buff = ''
    athletes = x.h2
    athletes.string = athletes.string.upper()
    athletes.extract()
    # athletes.span.unwrap()
    athletes.name = 'strong'
    athletes.attrs = None

    buff += '%s\n\n' % athletes

    # Replace br with \n
    for br in x.find_all('br'):
        logging.info('Removing br tag %s' % br)
        br.replace_with('\n')
    for span in x.find_all('span'):
        logging.info('Removing span tag %s' % span)
        span.unwrap()
    for i in x.children:
        i = str(i)
        i = i.replace('<p>', '')
        i = i.replace('</p>', '\n\n')
        buff += str(i)
    return buff


def main():
    # ------------------- E-mail list ------------------------
    token = os.environ['TOKEN']
    me = os.environ['ME']
    # --------------------------------------------------------

    # Download page
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
    }

    getPage = requests.get('https://comptrain.co/free-programming/', headers=headers)
    getPage.raise_for_status()  # if error it will stop the program

    # Parse text for foods
    soup = bs4.BeautifulSoup(getPage.text, 'html.parser')
    # mydivs = menu.find("div", {"class": "vc_gitem-zone-mini"})
    mydivs = soup.findAll("div", {"class": "vc_gitem-zone-mini"}, limit=10)[1]
    date = mydivs.h4.get_text()  # .find('h4').getText()
    date = '<strong>%s</strong>' % date.upper()
    workout = mydivs.findChildren('div', {'class': 'wpb_wrapper'})

    bot = telegram.Bot(token=token)

    open = [clean_nested(x) for x in workout if 'Open' in x.text][0]
    qualifiers = [clean_nested(x) for x in workout if 'Qualifier' in x.text][0]

    buff = '%s\n\n\n%s' % (date, extract_wod(x=qualifiers))
    buff = '%s\n%s\n' % (buff, '_' * 50)
    buff = '%s\n\n%s' % (buff, extract_wod(open))

    logging.info('Sending %s\n\n' % buff)

    bot.send_message(chat_id=me,
                     text=buff,
                     parse_mode='html')

    logging.info('%s' % buff)


if __name__ == '__main__':
    logging.info('Starting at %s' % datetime.datetime.now())
    schedule.every().day.at('04:00:00').do(main)
    while True:
        logging.info('Time %s' % datetime.datetime.now())
        schedule.run_pending()
        sleep(30)
