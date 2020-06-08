import csv
import os
import requests
from bs4 import BeautifulSoup


class ParserAvtoria():

    def __init__(self):
        self.HEADERS = {'user-agent':
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/81.0.4044.138 Safari/537.36',
                        'accept': '*/*'}
        self.HOST = 'https://auto.ria.com'
        self.FILE = 'cars.csv'

    def getHtml(self, url, params=None):
        req = requests.get(url, headers=self.HEADERS, params=params)
        return req

    def getPagesCount(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        pagination = soup.find_all('span', class_='mhide')
        if pagination:
            return int(pagination[-1].get_text())
        else:
            return 1

    def getContent(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', class_='proposition')

        cars = []
        for item in items:
            uah_price = item.find('span', class_='grey size13',)
            if uah_price:
                uah_price = uah_price.get_text().replace(' • ', '')
            else:
                uah_price = 'Specify the price'
            cars.append({
                'title': item.find(
                    'div', class_='proposition_title').get_text(strip=True),
                'link': self.HOST + item.find(
                    'h3', class_='proposition_name').find_next('a').get('href'),
                'usd_price': item.find(
                    'span', class_='green').get_text(),
                'uah_price': uah_price,
                'city': item.find(
                    'svg', class_='svg svg-i16_pin').find_next('strong').get_text(),
            })
        return cars

    def saveFile(self, items, path):
        with open(path, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(
                ['Сar brand', 'Link', 'USD price', 'UAH price', 'City'])
            for item in items:
                writer.writerow([item['title'],
                                 item['link'],
                                 item['usd_price'],
                                 item['uah_price'],
                                 item['city']])

    def creationLink(self):
        brend = input('Enter the brand: ').lower()
        while brend == '':
            brend = input('Enter the brand: ').lower()
            if brend != '':
                break

        if brend != '':
            model = input('Enter the model: ').lower()
            year = input('Enter the year: ').lower()
            u = brend + '/model-' + model + '/year-' + year + '/'

            return self.HOST + '/newauto/marka-' + u

    def parse(self):
        URL = self.creationLink()
        URL = URL.strip()
        self.html = self.getHtml(URL)
        if self.html.status_code == 200:
            cars = []
            pages_count = self.getPagesCount(self.html.text)
            for page in range(1, pages_count + 1):
                print(f'Parsing the page {page} of {pages_count}...')
                html = self.getHtml(URL, params={'page': page})
                cars.extend(self.getContent(html.text))
            self.saveFile(cars, self.FILE)
            print(f'Received {len (cars)} cars')
            os.startfile(self.FILE)
        else:
            print('Error')


a = ParserAvtoria()
a.parse()
