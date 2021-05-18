from search_type import SearchType
from crawler import Crawler
max_len=1
use_proxy = input("Do you want to enable proxy: (Y/N) ")
use_proxy_flag = not use_proxy and use_proxy == "Y"
input_type = input("Which area do you want to search? (a) JobSeek (b) Interview ")

search_type = SearchType.JOB_SEEK

if input_type == "b":
    search_type = SearchType.INTERVIEW

while True:
    
    target_company_input = input("Please input a company you want to search (separated by space): ")
    target_company_input = target_company_input.strip()
    target_companies = target_company_input.split(" ")

    pages = input("Please input how many pages do you want to search: ")
    pages=int(pages)

    cw = Crawler(use_proxy_flag)
    results = cw.find_all_within_pages(search_type, target_companies, pages)

    for job in results:
        print('{0:<100} 论坛链接：{1:<50}'.format(*job))
        
    if (len(results) == 0):
        print("No result found for ", target_companies)
    conti = input("Continue? (Y/N) ")
    if conti == "Y" or conti == "YES":
        continue
    else:
        break