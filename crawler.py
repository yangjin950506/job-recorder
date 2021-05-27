from typing import List
import requests
from requests.models import Response
import re
from bs4 import BeautifulSoup
import time
from search_type import SearchType
import os
from multiprocessing import Pool


class Crawler:
    proxy_pool = {"http": "201.69.7.108:9000",
                  "http": "222.92.112.66:8080"}
    # TODO: use proxies

    # TODO: support regex search

    # TODO: support drill down on different sections of interview page

    # TODO: interactive interface to select

    # TODO: remember the last search input

    # TODO: multi thread on the page pulling

    fake_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }

    prefix = "https://www.1point3acres.com/bbs/"

    thread_param = {"class": "s xst"}

    job_seek_page_url_template = None

    interview_experience_url_template = None

    tag = "a"

    pool_size = 20

    job_seek_first_page = "https://www.1point3acres.com/bbs/forum-198-1.html"

    interview_experience_first_page = "https://www.1point3acres.com/bbs/forum-259-1.html"

    page_regex = re.compile("page=.*")

    def __init__(self, use_proxy=False) -> None:
        self.use_proxy = use_proxy
        self.pool = Pool(processes=Crawler.pool_size)

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
            page_column = soup.body.findAll("div", {"class": "pg"})
            if len(page_column) > 0:
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
            page_column = soup.body.findAll("div", {"class": "pg"})
            if len(page_column) > 0:
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
    Args:
        url: the forum page to search
        target_companies: list of companies that user wants to find
    Return:
        List of tuples (Title, Link to Page)
    """

    def find_target_link(self, url, target_companies) -> List:
        resp = self._get_url_content(url)
        soup = BeautifulSoup(resp.content, "lxml")
        print(os.getpid(), " is searching")
        ret = []
        for item in soup.body.findAll(Crawler.tag, Crawler.thread_param):
            for target_company in target_companies:
                if target_company in item.text:
                    ret.append((item.text, Crawler.prefix + item['href']))
        print(os.getpid(), " completes searching")
        return ret

    def find_all_within_pages(self, search_type, target_companies, pages) -> List:
        return self.find_all_with_range(search_type, target_companies, 1, 1 + pages)

    """
    Search all pages within range [from_page, to_page]. The searching on each page within this
    range will be spread among different threads and get aggregated together at the end of this
    function.
    Args:
        search_type: enum type, two categories: job seek or interview
        target_companies: list of companies that user wants to find
        from_page: starting page num
        to_page: ending page num
    Return:
        List of tuples (Title, Link to Page)
    """

    def find_all_with_range(self, search_type, target_companies, from_page, to_page) -> List:
        links = []
        results = []  # used to hold async result objects

        for i in range(from_page, to_page + 1):
            page_url = None

            if search_type is SearchType.JOB_SEEK:
                page_url = self._jump_to_page(i, self._get_job_page_template)
            elif search_type is SearchType.INTERVIEW:
                page_url = self._jump_to_page(i, self._get_interview_page_template)

            result = self.pool.apply_async(self.find_target_link, (page_url, target_companies))
            results.append(result)

        print("Aggregating results...")
        for r in results:
            links.extend(r.get())
        return links

    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['pool']
        return self_dict

    def __setstate__(self, state):
        self.__dict__.update(state)
