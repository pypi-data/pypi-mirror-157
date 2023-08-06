"""
This project seeks to create a 'retrospective' of Google News top hits.
Copyright (C) Springbok LLC

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from contextlib import contextmanager
from datetime import datetime, timedelta
import logging
import pprint
import re

from bs4 import BeautifulSoup, ResultSet
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.Retrospective.ProxyPool import ProxyPool
from src.Retrospective.ChromeDriver import DRIVER_HOME


GOOGLE_NEWS_BASE_URL = "https://www.google.com/search?tbm=nws"
DRIVER_PATH = f"{DRIVER_HOME}/chromedriver"


logger = logging.getLogger(__name__)


class GoogleNewsDriver:
    def __init__(self):
        self.proxyPool = ProxyPool()
        self.proxyPool.maintain_pool()

    @contextmanager
    def proxied_driver(self, *args, **kwargs):
        options = Options()
        options.headless = True
        options.add_argument("--window-size=1920,1200")
        instance = self.proxyPool.get_random_proxy_instance()
        options.add_argument(
            "--proxy-server={0}:{1}".format(instance.ip_address, "8888")
        )
        driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
        try:
            yield driver
        finally:
            driver.quit()

    def get_google_news_url(
        self,
        query,
        min_date=None,
        max_date=None,
        sorted_by_date=False,
        page_number=1,
        results_per_page=10,
    ):
        """Google News URLs as of May 31, 2021 modified for simpler
        creation.

        Recent, Sorted by relevance (Default)
        https://www.google.com/search?tbm=nws&q=apple&tbs=sbd:0 (p 1)
        https://www.google.com/search?tbm=nws&q=apple&tbs=sbd:0&start=20 (p 2)

        Recent, Sorted by date, Hide Duplicates
        https://www.google.com/search?tbm=nws&q=apple&tbs=sbd:1 (p 1)
        https://www.google.com/search?tbm=nws&q=apple&tbs=sbd:1&start=20 (p 2)

        Custom range... Apr 3, 2020 – May 4, 2021, Sorted by relevance
        https://www.google.com/search?tbm=nws&q=apple&tbs=sbd:0,cdr:1,cd_min:4/3/2020,cd_max:5/4/2021 (pg 1)
        https://www.google.com/search?tbm=nws&q=apple&tbs=sbd:0,cdr:1,cd_min:4/3/2020,cd_max:5/4/2021&start=20 (pg 2)

        Custom range... Apr 3, 2020 – May 4, 2021, Sorted by date (, Hide Duplicates)
        https://www.google.com/search?tbm=nws&q=apple&tbs=sbd:1,cdr:1,cd_min:4/3/2020,cd_max:5/4/2021 (pg 1)
        https://www.google.com/search?tbm=nws&q=apple&tbs=sbd:1,cdr:1,cd_min:4/3/2020,cd_max:5/4/2021&start=20 (pg 2)

        Note that the value of 'start' depends on the Chrome settings of
        the user of this module.
        """
        news_url = GOOGLE_NEWS_BASE_URL + "&q={}".format(query)
        if sorted_by_date:
            news_url += "&tbs=sbd:1"
        else:
            news_url += "&tbs=sbd:0"
        if min_date is not None and max_date is not None:
            news_url += ",cdr:1,cd_min:{0},cd_max:{1}".format(
                min_date.strftime("%m/%d/%Y"), max_date.strftime("%m/%d/%Y"),
            )
        elif min_date is not None or max_date is not None:
            raise Exception("Minimum and maximum date must both be set or None")
        if page_number > 1:
            news_url += "&start={0}".format((page_number - 1) * results_per_page)
        return news_url

    def get_search_result_page_source(self, news_url):
        with self.proxied_driver() as driver:
            driver.get(news_url)
            page_source = driver.page_source
        return page_source

    def parse_search_result_page_source(self, page_source):
        """Selectors are copied from the search results page using
        Chrome Developer Tools by Inspecting Elements and right
        clicking on elements of interest, selecting "Copy >", then
        "Copy selector".
        """
        soup = BeautifulSoup(page_source, "html5lib")
        result_stats = soup.select("#result-stats")
        if result_stats and isinstance(result_stats, ResultSet):
            result_stats = re.search(r"\d+", result_stats[0].text)
            total_count = int(result_stats.group())
            logger.info("Found {0} results".format(total_count))
        else:
            logger.info("No results found")
            return
        g_cards = soup.select("g-card.ftSUBd")
        results = []
        ref_dt = datetime.now()
        if not g_cards:
            return
        for g_card in g_cards:
            # Title
            try:
                # TODO: How do we update these as chrome updates the div classes?
                title = g_card.select("div.mCBkyc.y355M.JQe2Ld.nDgy9d")[
                    0
                ].text
            except Exception as e:
                logger.error("Title not found. Ensure that the div selectors are correct: {0}".format(e))
                title = None
                # Continue, because a lack of a title means that configuration is off
                continue
            # Image
            try:
                image = g_card.select("div.uhHOwf.BYbUcd img")[0].get("src")
            except Exception as e:
                logger.error("Image not found: {0}".format(e))
                image = None
            # Description
            try:
                description = g_card.select("div.GI74Re.nDgy9d")[0].text
            except Exception as e:
                logger.error("Description not found: {0}".format(e))
                description = None
            # Time ago
            try:
                time_ago = g_card.select("div.OSrXXb.ZE0LJd span")[0].text
            except Exception as e:
                logger.error("Time ago not found: {0}".format(e))
                time_ago = None
            # Link
            try:
                link = g_card.select("a[href]")[0].get("href")
            except Exception as e:
                logger.error("Link not found: {0}".format(e))
                link = None
            # Collect results
            date_time = self.time_ago_to_datetime(time_ago, ref_dt=ref_dt) if time_ago else None
            results.append(
                {
                    "title": title,
                    "image": image,
                    "description": description,
                    "time_ago": time_ago,
                    "date_time": date_time,
                    "link": link,
                }
            )
        return results

    def time_ago_to_datetime(self, time_ago, ref_dt=datetime.now()):
        if re.search("ago", time_ago) is not None:
            fields = time_ago.split()
            time_value = int(fields[0])
            time_units = fields[1]
            if re.search("min", time_units):
                ref_dt -= timedelta(minutes=time_value)
            elif re.search("hour", time_units):
                ref_dt -= timedelta(hours=time_value)
            elif re.search("day", time_units):
                ref_dt -= timedelta(days=time_value)
            elif re.search("week", time_units):
                ref_dt -= timedelta(weeks=time_value)
            elif re.search("month", time_units):
                ref_dt -= timedelta(days=time_value * 30)
        else:
            ref_dt = datetime.strptime(time_ago, "%b %d, %Y")
        return ref_dt


if __name__ == "__main__":
    googleNewsDriver = GoogleNewsDriver()
    print(googleNewsDriver.get_google_news_url("apple"))
    # print(googleNewsDriver.get_google_news_url("apple", page_number=2))
    # print(googleNewsDriver.get_google_news_url("apple", sorted_by_date=True))
    # print(googleNewsDriver.get_google_news_url("apple", sorted_by_date=True, page_number=2))
    # print(googleNewsDriver.get_google_news_url("apple", min_date=date.today(), max_date=date.today() + timedelta(days=30)))
    # print(googleNewsDriver.get_google_news_url("apple", min_date=date.today(), max_date=date.today() + timedelta(days=30), page_number=2))
    # print(googleNewsDriver.get_google_news_url("apple", min_date=date.today(), max_date=date.today() + timedelta(days=30), sorted_by_date=True))
    # print(googleNewsDriver.get_google_news_url("apple", min_date=date.today(), max_date=date.today() + timedelta(days=30), sorted_by_date=True, page_number=2))
    news_url = googleNewsDriver.get_google_news_url("cisco")
    page_source = googleNewsDriver.get_search_result_page_source(news_url)
    result = googleNewsDriver.parse_search_result_page_source(page_source)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(result)
