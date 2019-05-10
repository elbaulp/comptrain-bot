#! python3
import bs4
import requests
import telegram
import os

# ------------------- E-mail list ------------------------
token = os.environ['TOKEN']
channel-id = os.environ['ME']
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
        br.replace_with('\n')
    for i in x.children:
        i = str(i)
        i = i.replace('<p>', '')
        i = i.replace('</p>', '\n\n')
        buff += str(i)
    return buff


buff = '%s\n\n\n%s' % (date, extract_wod(x=qualifiers))
buff = '%s\n\n%s' % (buff, extract_wod(open))

bot.send_message(chat_id=channel-id,
                 text=buff,
                 parse_mode='html')
