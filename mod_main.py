from mod_fct_scraping import choice_list_proxies, main

url = 'https://www.bestbuy.ca/fr-ca/categorie/telephones-deverrouilles/743355?page=1'

"""
                  Inputs for code: Please, read and follow the instructions

output_file_name: Please, write the output file name: example "my_file.csv"
last page       : The code scrape from page 1 to last page(should be > 0).
                  last_page = None. the code will scrape all pages.
list_proxies    : Please, use a list of proxies to scrape data: there is 3 choices
                    1: A given list of proxies (recommended).
                       You can also use your own list by list_proxies = ['x.x.x.x:xxxx']
                    2: The code will get one list of proxies and use it for all the job
                    3: For each scraped page, the code will get a new list of proxies (Unrecommended) 
time_work       : Range of time to work, 
                  If None, random choice for: am: [09h00,12h59]
                                              pm: [16h00,22h59]
"""

output_file_name = "data_phones.csv"
last_page        = 2
list_proxies     = choice_list_proxies(1)  # You can also use your own list by list_proxies = ['x.x.x.x:xxxx']
time_work        = {"am": [ 9, 12, 0, 59],
                    "pm": [16, 22, 0, 59]}

# main(scrap_url=url, file_name=output_file_name)
main(scrap_url=url, file_name=output_file_name, list_proxies=list_proxies, last_page=last_page, time_work=time_work)























