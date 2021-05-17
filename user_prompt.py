from crawler import Crawler
max_len=1
use_proxy = input("Do you want to enable proxy: (Y/N) ")
use_proxy_flag = not use_proxy and use_proxy == "Y"

while True:
    
    target_company = input("Please input a company you want to search: ")
    pages = input("Please input how many pages do you want to search: ")
    pages=int(pages)
    cw = Crawler(use_proxy_flag)
    results = cw.find_all_within_pages(target_company, pages)
    # max_len = max([r[0] for r in results])
    for job in results:
        print('{0:<100} 论坛链接：{1:<100}'.format(*job))

    conti = input("Continue? (Y/N)")
    if conti == "Y" or conti == "YES":
        continue
    else:
        break