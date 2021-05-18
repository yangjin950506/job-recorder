from typing import List
import requests
from requests.models import Response
import re
from bs4 import BeautifulSoup
import time
from search_type import SearchType

class Crawler:
    proxy_pool = {"http": "201.69.7.108:9000", 
                    "http": "222.92.112.66:8080"}
    # TODO: use proxies

    # TODO: support regex search

    # TODO: multi thread on the page pulling

    fake_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }

    prefix = "https://www.1point3acres.com/bbs/"

    thread_param = {"class": "s xst"}

    job_seek_page_url_template = None

    interview_experience_url_template = None

    tag = "a"

    job_seek_first_page = "https://www.1point3acres.com/bbs/forum-198-1.html"

    interview_experience_first_page = "https://www.1point3acres.com/bbs/forum-145-1.html"

    page_regex = re.compile("page=.*")

    def __init__(self, use_proxy=False) -> None:
        self.use_proxy = use_proxy
    
    """
    Generic method to get the content(HTML) of a url
    """
    def _get_url_content(self, url) -> Response:
        if self.use_proxy:
            return requests.get(url=url, headers=Crawler.fake_header, proxies=Crawler.proxy_pool)
        return requests.get(url=url, headers=Crawler.fake_header)
    

    """
    Get the job seek page template to do pagination
    """
    # This is not a thread safe method
    def _get_job_page_template(self) -> str:
        if not Crawler.job_seek_page_url_template:
            resp = self._get_url_content(Crawler.job_seek_first_page)
            soup = BeautifulSoup(resp.content, "lxml")
            page_column = soup.body.findAll("div", {"class":"pg"})
            if( len(page_column) > 0):
                page_column = page_column[0]
            else:
                raise RuntimeError("page column not found")
            Crawler.job_seek_page_url_template = Crawler.prefix + page_column.findAll("a", limit=1)[0]['href']
        page = Crawler.job_seek_page_url_template
        return page

    """
    Get the interview experience page template to do pagination
    """
    def _get_interview_page_template(self) -> str:
        # if not set already, then set the template
        if not Crawler.interview_experience_url_template:
            resp = self._get_url_content(Crawler.interview_experience_first_page)
            soup = BeautifulSoup(resp.content, "lxml")
            page_column = soup.body.findAll("div", {"class":"pg"})
            if( len(page_column) > 0):
                page_column = page_column[0]
            else:
                raise RuntimeError("page column not found")
            Crawler.interview_experience_url_template = Crawler.prefix + page_column.findAll("a", limit=1)[0]['href']
        page = Crawler.interview_experience_url_template
        return page

    """
    This is a generic jump page function, the input is
    page_num : the destination page num starting from 1
    get_page_func : which page is jump here. Only two options : job seek and interview experience
    """
    def _jump_to_page(self, page_num, get_page_func) -> str:
        page = get_page_func()
        target_page = re.sub(Crawler.page_regex, "page=" + str(page_num), page)
        return target_page

    """
    Generic method to find target company related posts in a given url/page
    Return the post name and its hyper link
    """
    def find_target_link(self, url, target_companies) -> List:
        resp = self._get_url_content(url)
        soup = BeautifulSoup(resp.content, "lxml")
        ret = []
        for item in soup.body.findAll(Crawler.tag, Crawler.thread_param):
            for target_company in target_companies:
                if target_company in item.text:
                    ret.append( (item.text, Crawler.prefix + item['href']) )
        return ret


    def find_all_within_pages(self, search_type, target_companies, pages) -> List:
        links = []
        for i in range(1, pages + 1):
            print("Searching in page: ", i)
            page_url = None
            if search_type is SearchType.JOB_SEEK:
                page_url = self._jump_to_page(i, self._get_job_page_template)
            elif search_type is SearchType.INTERVIEW:
                page_url = self._jump_to_page(i, self._get_interview_page_template)
            links.extend(self.find_target_link(page_url, target_companies))
            print("page ", i, " searching done")
            # time.sleep(1) # prevent too frequent visits
        print("Aggregating results...")
        return links