import requests
from requests.models import Response
import re
from bs4 import BeautifulSoup
import time

class Crawler:
    proxy_pool = {"http": "201.69.7.108:9000", 
                    "http": "222.92.112.66:8080"}
    # TODO: use proxies

    # TODO: support regex search

    # TODO: support multiple search

    fake_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }

    prefix = "https://www.1point3acres.com/bbs/"

    thread_param = {"class": "s xst"}

    page_url_template = None

    tag = "a"

    job_seek_first_page = "https://www.1point3acres.com/bbs/forum-198-1.html"

    page_regex = re.compile("page=.*")

    def __init__(self, use_proxy=False) -> None:
        self.use_proxy = use_proxy
    
    def _get_url_content(self, url) -> Response:
        if self.use_proxy:
            return requests.get(url=url, headers=Crawler.fake_header, proxies=Crawler.proxy_pool)
        return requests.get(url=url, headers=Crawler.fake_header)
    
    # This is not a thread safe method
    def _get_page_template(self):
        if not Crawler.page_url_template:
            resp = self._get_url_content(Crawler.job_seek_first_page)
            soup = BeautifulSoup(resp.content, "lxml")
            page_column = soup.body.findAll("div", {"class":"pg"})
            if( len(page_column) > 0):
                page_column = page_column[0]
            else:
                raise RuntimeError("page column not found")
            Crawler.page_url_template = Crawler.prefix + page_column.findAll("a", limit=1)[0]['href']
        page = Crawler.page_url_template
        return page

    def _jump_to_page(self, page_num):
        page = self._get_page_template()
        target_page = re.sub(Crawler.page_regex, "page=" + str(page_num), page)
        return target_page

    # def _next_page(self,):
    #     return 

    def find_target_link(self, url, target_company):
        resp = self._get_url_content(url)
        soup = BeautifulSoup(resp.content, "lxml")
        ret = []
        for item in soup.body.findAll(Crawler.tag, Crawler.thread_param):
            if (target_company in item.text):
                ret.append( (item.text, Crawler.prefix + item['href']) )
        return ret

    def find_all_within_pages(self, target_company, pages):
        links = []
        for i in range(1, pages + 1):
            print("Searching in page: ", i)
            page_url = self._jump_to_page(i)
            links.extend(self.find_target_link(page_url, target_company))
            print("page ", i, " searching done")
            # time.sleep(1) # prevent too frequent visits
        print("Aggregating results...")
        return links