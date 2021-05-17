import requests
from requests.models import Response
import re
from bs4 import BeautifulSoup

class Crawler:
    
    # TODO: use proxies

    fake_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }

    prefix = "https://www.1point3acres.com/bbs/"

    thread_param = {"class": "s xst"}

    page_url_template = None

    tag = "a"

    job_seek_first_page = "https://www.1point3acres.com/bbs/forum-198-1.html"

    page_regex = re.compile("page=.*")

    def __init__(self) -> None:
        pass
    
    def _get_url_content(self, url) -> Response:
        return requests.get(url=url, headers=Crawler.fake_header)
    
    # This is not a thread safe method
    def _get_page(self, target_page):
        if not Crawler.page_url_template:
            resp = self._get_url_content(Crawler.job_seek_first_page)
            soup = BeautifulSoup(resp.content, "lxml")
            page_column = soup.body.findAll("div", {"class":"pg"})
            if( len(page_column) > 0):
                page_column = page_column[0]
            else:
                raise RuntimeError("page column not found")
            Crawler.page_url_template = page_column.findAll("a", limit=1)['href']
        return 

    def _jump_to_page(self, page_num):
        page = Crawler.page_url_template
        page = re.sub(Crawler.page_regex, "page=" + str(page_num), string)
        return page

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
        
        return links

url = "https://www.1point3acres.com/bbs/forum-198-1.html"
res = requests.get(url=url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    })

string = "forum.php?mod=forumdisplay&amp;fid=198&amp;sortid=192&amp;%1=&amp;sortid=192&amp;page=2"
print()
soup = BeautifulSoup(res.content, "lxml")
# print(soup.body.findAll("tbody", {"id":re.compile("normalthread.*")}))
# print(soup.body.findAll("a", {"class":"s xst"}))

prefix = "https://www.1point3acres.com/bbs/"
target = "LinkedIn"

# for item in soup.body.findAll("a", {"class":"s xst"}):
#     if (target in item.text):
#         print (prefix + item['href'])

# for item in soup.body.findAll("div", {"class":"pg"}):
#     print(item.findAll("a", limit=1))


