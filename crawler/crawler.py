from threading import Thread
from time import sleep

from lxml import html
from requests.exceptions import ConnectionError, HTTPError, Timeout
import requests

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36'
HEADERS = {'User-Agent': USER_AGENT}
LOWEST_SCORE = 25

def stackoverflow_url(pagenum=1, order_by_popular=True):
    suffix = '&tab=popular' if order_by_popular else ''
    return "http://stackoverflow.com/tags?page=%s" % (str(pagenum) + suffix)

def parse_tags_page(text):
    """
    Return each tags represented with (tagname, count),
    and an extra boolean value indicated if we meet a tag smaller than required.
    So we can tell high level function to stop.
    """
    doc = html.fromstring(text)
    tags = doc.get_element_by_id('tags-browser')
    data = []
    for row in tags.findall('tr'):
        for td in row.findall('td'):
            count = int(td.find_class('item-multiplier-count')[0].text_content())
            if count <= LOWEST_SCORE:
                return data, True
            data.append((td.find_class('post-tag')[0].text_content(), count))

    if not len(data):
        print("Parse failed with:")
        print(text)
    return data, False

class Crawler(Thread):
    def __init__(self, start_pagenum, interval):
        super(Crawler, self).__init__()
        if start_pagenum < 1 or int(start_pagenum) != start_pagenum:
            raise ValueError("The start page number should integer greater than 0")
        self.pagenum = start_pagenum
        self.interval = interval
        self.data = []
        self.error = False

    def run(self):
        try:
            while True:
                ok = self.get_tags_from_page()
                if not ok:
                    break
                self.pagenum += self.interval
                sleep(2)
        except (ConnectionError, HTTPError, Timeout):
            self.error = True

    def get_tags_from_page(self):
        url = stackoverflow_url(self.pagenum)
        print("Try to get %s" % url)
        res = requests.get(url, headers=HEADERS)
        if res.status_code in (200, 304):
            data, too_small_tag_met = parse_tags_page(res.text)
            self.data.extend(data)
            if too_small_tag_met:
                print("Crawling stops at %s" % url)
                return False
            return True
        print("Failed with %s : %d" % (url, res.status_code))
        self.error = True
        return False



def crawl_tags_using_threads(thread_num):
    print("Crawl stackoverflow's tags with %d threads" % thread_num)
    if thread_num < 1 :
        raise ValueError('Thread number should be at least 1')
    # If you crawl too fast, stackoverflow will return 503 back
    crawlers = [Crawler(i, thread_num) for i in range(1, thread_num + 1)]
    for crawler in crawlers:
        crawler.start()
    for i, crawler in enumerate(crawlers):
        crawler.join()
    data = []
    for i, crawler in enumerate(crawlers):
        if crawler.error:
            print("Thread %d failed during crawling, try again later" % i)
            return []
        else:
            data.extend(crawler.data)
    return data

