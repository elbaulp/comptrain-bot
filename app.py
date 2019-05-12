#! python3
import logging
import os
import datetime

import bs4
import requests
import schedule
import telegram

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


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

    #
    # updater = Updater(token=token)
    # dispatcher = updater.dispatcher

    open = [x for x in workout if 'Open' in x.text][0]
    qualifiers = [x for x in workout if 'Qualifier' in x.text][0]

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

    buff = '%s\n\n\n%s' % (date, extract_wod(x=qualifiers))
    buff = '%s\n%s\n' % (buff, '_' * 50)
    buff = '%s\n\n%s' % (buff, extract_wod(open))

    bot.send_message(chat_id=me,
                     text=buff,
                     parse_mode='html')

    logging.info('%s' % buff)


if __name__ == '__main__':
    logging.info('Starting at %s' % datetime.datetime.now())
    schedule.every().day.at('04:00:00').do(main)
    while True:
        schedule.run_pending()
