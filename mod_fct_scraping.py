import schedule
from mod_class_proxies import GetHtmlRandomProxyRequest
import time
import csv
import sys
import random

# create an object
class_proxy = GetHtmlRandomProxyRequest()


def main(scrap_url, file_name, list_proxies=None, last_page=None, time_work=None):
    """
    Run job tasks
    :param scrap_url: web address for scraping
    :param file_name: output file_name
    :param list_proxies: list of proxies
    :param last_page: number of last page for scraping
    :param time_work: range of time work
    :return:
    """
    if time_work is None:
        time_work = {"am": [ 9, 12, 0, 59],
                     "pm": [16, 22, 0, 59]
                     }
    # am time for starting work
    t_am = time_job(time_work['am'][0], time_work['am'][1], time_work['am'][2], time_work['am'][3])
    # pm time for starting work
    t_pm = time_job(time_work['pm'][0], time_work['pm'][1], time_work['pm'][2], time_work['pm'][3])
    # reference time to close code
    t_ref = time.strftime("%Y-%b-%d %a", time.localtime()) + " " + t_pm
    print("am time work :", t_am)
    print("pm time work :", t_pm)
    # Schedule tasks
    schedule.every().days.at(t_am).do(lambda: job(scrap_url, file_name, list_proxies, last_page, t_ref))
    schedule.every().days.at(t_pm).do(lambda: job(scrap_url, file_name, list_proxies, last_page, t_ref))

    # loop to keep schedule jobs pending
    while True:
        schedule.run_pending()
        time.sleep(1)


def job(scrap_url, file_name, list_proxies, last_page, t_ref):
    """
    Schedule job tasks
    :param scrap_url: web address for scraping
    :param file_name: output file_name
    :param list_proxies: list of proxies
    :param last_page: number of last page for scraping
    :param t_ref: reference time with date format
    :return: None
    """
    print_header()
    list_soups = get_list_soup(scrap_url, list_proxies, last_page)
    phone_data = make_data(list_soups)
    write_in_csv(file_name, phone_data)
    print_end()
    t_close = time.strftime("%Y-%b-%d %a %H:%M", time.localtime(time.time()))
    if t_close > t_ref:
        code_close()


def get_list_soup(scrap_url, list_proxies, last_page=None):
    """
    Get HTML contents and time stamp
    :param scrap_url: web address for scraping
    :param list_proxies: list of proxies
    :param last_page: integer, number of last page for scraping
    :return: List[Tuple[BeautifulSoup, List[Tuple[str, BeautifulSoup]]]]
    """
    if last_page is None:
        last_page = get_num_last_page(scrap_url, list_proxies)
    elif last_page <= 0:
        print(" " * 100)
        print(" " * 40, "Scraping Impossible")
        print(" " * 40, "Number of last page should be superior to \"0\". Please, retry")
        print(" " * 100)
    else:
        # to include last page in range add 1
        last_page += 1

    # initialise counter and list of BeautifulSoup objects for main scraping page
    list_soups = []
    counter = 0

    # loop over pages
    for page_index in range(1, last_page):
        # concatenate url to scroll pages
        url = scrap_url.split("=")[0] + "=" + str(page_index)
        print(url)

        # get BeautifulSoup object from main scraping page
        main_page = class_proxy.get_page(url, list_proxies)

        # get BeautifulSoup object for each item in the main page
        # phones : sub soup of main page
        phones = main_page.find_all('div', attrs={'class': 'col-xs-12_1GBy8 col-sm-4_NwItf col-lg-3_2V2hX '
                                                           'x-productListItem productLine_2N9kG'})
        # initialise list of BeautifulSoup object for each item in main page
        list_details_soup = []
        # loop over items in the main page
        for phone in phones:
            counter += 1
            print("phone number ", counter)

            # find the web address for each item in the main page to get more phone details
            phone_link = main_page.find('link', attrs={'rel': "preconnect"}).get("href") + phone.find('a').get("href")
            page_phone_details = class_proxy.get_page(phone_link, list_proxies)

            # get time stamp
            time_stamp = time.strftime("%Y-%b-%d %a %H:%M:%S", time.localtime())

            # make list of Tuple(time_stamp, BeautifulSoup)
            list_details_soup.append((time_stamp, page_phone_details))

        # make list of Tuple(BeautifulSoup, list_details_soup)
        list_soups.append((main_page, list_details_soup))
    # description list_soup
    # list_soup = [
    #    (soup.page1, [(time_stamp, soup.phone1), (time_stamp, soup.phone2),..., (time_stamp, soup.phone24) ] ),
    #    (soup.page2, [(time_stamp, soup.phone1), (time_stamp, soup.phone2),..., (time_stamp, soup.phone24) ] ),
    #    ... ,
    #    ]
    return list_soups


def make_data(list_soups):
    """
    Select phones data in list of beautifulSoup objects
    :param list_soups: List[Tuple[BeautifulSoup, List[Tuple[str, BeautifulSoup]]]]
    :return: list[Tuple()]
    """
    # initialise list of phones data
    phone_data = []
    for soup in list_soups:
        # find all phones in the main page
        phones = soup[0].find_all('div', attrs={'class':
                                                'col-xs-8_1VO-Q col-sm-12_1kbJA productItemTextContainer_HocvR'})

        for index, phone in enumerate(phones):
            # get some phones data

            phone_name = phone.find('div', attrs={'class': 'productItemName_3IZ3c'}).text

            phone_evaluation = phone.find('span', attrs={'itemprop': 'ratingCount'}).get_text().strip("()")

            phone_stars = phone.find('meta', attrs={'itemprop': 'ratingValue'}).get('content')

            phone_price = phone.find('div', attrs={'class': 'price_FHDfG medium_za6t1'})
            if phone_price:
                phone_price = phone_price.text
                phone_price_saving = 0.00
            else:
                phone_price = phone.find('div', attrs={'class': 'price_FHDfG medium_za6t1 salePrice_kTFZ3'}).text
                phone_price_saving = phone.find('span', attrs={'class': 'productSaving_3YmNX undefined'}).text

            phone_market = phone.find('span', attrs={'class': 'marketplaceName_1acI5'})
            if phone_market:
                phone_market = phone_market.text
            else:
                phone_market = "N/A"

            # get more phones data
            phones_details = soup[1][index][1]

            discount_end = phones_details.find('time', attrs={'itemprop': 'priceValidUntil'})

            if discount_end:
                discount_end = discount_end.text
            else:
                discount_end = "N/A"

            num_model = phones_details.find('span', attrs={'itemprop': 'model'})
            if num_model:
                num_model = phones_details.find('span', attrs={'itemprop': 'model'}).text
            else:
                num_model = "N/A"

            # recover time stamp
            time_stamp = soup[1][index][0]

            # data for one item
            one_phone = time_stamp, phone_name, phone_evaluation, phone_stars, phone_price, phone_price_saving, \
                        discount_end, phone_market, num_model

            phone_data.append(one_phone)

    return phone_data


def write_in_csv(file_name, phone_data):
    """
    Write data in CSV file
    :param file_name: output file name
    :param phone_data: list of phones data
    :return: None
    """
    with open(file_name, "a+", newline="") as ficout:
        writer = csv.writer(ficout, delimiter="|", quoting=csv.QUOTE_NONNUMERIC)
        # check if file is empty in order to write or not the header
        # move read cursor to the start of file
        ficout.seek(0)
        text = ficout.read(100)
        if len(text) < 1:
            writer.writerow(
                ("Time Stamp", "Phone description", "Evaluation", "Number of Stars", "Sale Price", "Discount",
                 "Dead line of Discount", "Marketplace", "Num of Model"))
            for element in phone_data:
                writer.writerow((element[0], element[1], element[2], element[3], element[4], element[5],
                                 element[6], element[7], element[8]))
        else:
            for element in phone_data:
                writer.writerow((element[0], element[1], element[2], element[3], element[4], element[5],
                                 element[6], element[7], element[8]))


def get_num_last_page(scrap_url, list_proxies):
    """
    Get number of last page for scraping
    :param scrap_url: web address for scraping
    :param list_proxies: list of proxies
    :return: integer
    """
    # get number of last page
    print("Get number of last page")

    # get soup
    page = class_proxy.get_page(scrap_url, list_proxies)

    # get number of phones in all pages
    max_phones = page.find('span', attrs={'class': 'materialOverride_STCNx toolbarTitle_2lgWp'})
    max_phones = max_phones.get_text().split("r")[0]
    max_phones = max_phones.replace(u'\xa0', u'')

    # get number of phones in one page
    numb_phones = page.find_all('div', attrs={'class': 'col-xs-12_1GBy8 col-sm-4_NwItf col-lg-3_2V2hX '
                                                       'x-productListItem productLine_2N9kG'})

    last_page = round((int(max_phones) / len(numb_phones)))
    print("There is {} items at all and {} items in one page".format(int(max_phones), len(numb_phones)))
    print("So, number of pages for scraping = ", last_page)

    # to include last page in range add + 1
    return last_page + 1


def choice_list_proxies(num):
    """
    Choose the list of proxies to use
    :param num: integer can be 1, 2 or 3
    :return: list
    """
    if num == 1:
        list_proxies = ['78.140.7.239:33943', '164.163.73.66:999', '212.24.148.234:36087', '190.152.213.126:435',
                        '85.117.61.186:49929', '79.137.254.51:60779', '159.224.44.19:33789', '103.216.51.210:8191',
                        '61.9.82.34:32280', '222.165.214.98:45801', '181.112.40.114:33509', '80.188.239.106:39271',
                        '103.21.163.76:6666', '181.118.167.104:80', '31.173.94.93:43539', '86.125.112.230:57373',
                        '13.75.114.68:25222', '36.91.44.243:37927', '34.217.82.196:8888', '167.99.177.76:8080']

    elif num == 2:
        list_proxies = class_proxy.get_list_proxies()
    elif num == 3:
        list_proxies = None
    else:
        sys.exit("the choice can be only 1, 2 or 3! Please retry")
    return list_proxies


def print_header():
    """
    Print on screen
    :return: None
    """
    print("=" * 100)
    print(" " * 20, "Téléphones déverrouillés : Best Buy Mobile | Best Buy Canada")
    print(" " * 47, "Start Scraping")
    print("=" * 100)


def print_end():
    """
    Print on screen
    :return:  None
    """
    print("=" * 100)
    print(" " * 35, time.strftime("%Y-%b-%d %a %H:%M:%S", time.localtime()), "End job")
    print("=" * 100)


def time_job(h_str, h_end, m_str, m_end):
    """
    Get "time" by random choice
    :param h_str: hour start
    :param h_end: hour end
    :param m_str: minutes start
    :param m_end: minutes end
    :return: str
    """
    h = random.randint(h_str, h_end)
    if h >= 24:
        h = h - 24
    m = random.randint(m_str, m_end)
    t = "{:02d}".format(h) + ":" + "{:02d}".format(m)
    return t


def code_close():
    """
    Close the code to release cpu
    :return: None
    """
    print(" " * 35, time.strftime("%Y-%b-%d %a %H:%M:%S", time.localtime()), "Exit Code")
    sys.exit()


if __name__ == '__main__':
    main(scrap_url='https://www.bestbuy.ca/fr-ca/categorie/telephones-deverrouilles/743355?page=1',
         file_name='data_phones.csv',
         list_proxies=choice_list_proxies(1),
         last_page=2,
         time_work={"am": [ 9, 12, 0, 59],
                    "pm": [16, 22, 0, 59]
                    }
         )
