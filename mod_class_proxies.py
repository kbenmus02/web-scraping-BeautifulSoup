import requests
from bs4 import BeautifulSoup
import random
import time


class GetHtmlRandomProxyRequest:

    def __init__(self, url_proxies='https://www.sslproxies.org/'):
        """
        :param url_proxies: address to scrap in order to get a list of proxies
        """
        self.url = url_proxies

        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64); AppleWebKit/537.36 (KHTML, like Gecko) '
                                      'Chrome/84.0.4147 Safari/537.36'}

        # initialise list of proxies
        self.list_proxies = []

    def get_list_proxies(self):
        """
        Get list of proxies
        :return: list proxies
        """
        # get html page content
        page = requests.get(url=self.url, headers=self.headers)
        soup = BeautifulSoup(page.content, 'html.parser')

        # find section's tag to get ip address and the number of port
        section = soup.find('section', attrs={"id": "list"})

        # make a list of proxies
        for ip, port in zip(section.find_all('td')[::8], section.find_all('td')[1::8]):
            self.list_proxies.append(ip.text + ':' + port.text)

        print("scraping {} to get a list of proxies".format(self.url))
        return self.list_proxies

    def get_page(self, scraping_url, list_proxies=None):
        """
        Get Html page content using a list of proxies and if applicable, my proxy
        :param scraping_url: web address for scraping
        :param list_proxies: list proxies
        :return: BeautifulSoup object
        """

        if list_proxies is None:
            list_proxies = self.get_list_proxies()

        # initialise counter and limit of connexion retries
        c_try = 0
        limit_try = 10
        while True:
            try:
                # choose a random address
                address = random.choice(list_proxies)
                proxy = {'https': address}

                page = requests.get(scraping_url, headers=self.headers, proxies=proxy, timeout=12)
                if page.status_code == 200:
                    print("         Using proxy {} --> Success, status code = {}".format(proxy, page))
                    break
            except:
                print("Using proxy {} --> Unsuccessful! Trying with another one".format(proxy))
                c_try += 1
                if c_try > limit_try:
                    print(" {} tries, over limit go to my proxy".format(c_try))
                    break

        if c_try <= limit_try:
            soup = BeautifulSoup(page.content, 'html.parser')
        else:
            soup = self.get_page_my_proxy(scraping_url)

        return soup

    def get_page_my_proxy(self, scraping_url):
        """
        Get Html page content
        :param scraping_url: web address for scraping
        :return: BeautifulSoup object
        """
        while True:
            try:
                page = requests.get(scraping_url, headers=self.headers, timeout=12)
                if page.status_code == 200:
                    print("     Success, status code = {}".format(page))
                    self.random_time_sleep()
                    break
            except:
                print("Unsuccessful! Retry")
                time.sleep(10)

        soup = BeautifulSoup(page.content, 'html.parser')
        return soup

    @staticmethod
    def random_time_sleep():
        """
        Get random time sleep
        :return:float
        """
        time_sleep = random.uniform(1, 3)
        print("sleep {0:5.2f} minutes".format(time_sleep))
        time.sleep(time_sleep * 60)

