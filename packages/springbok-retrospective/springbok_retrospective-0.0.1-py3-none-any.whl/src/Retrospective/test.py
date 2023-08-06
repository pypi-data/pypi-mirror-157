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


import unittest
import src.Retrospective.ChromeDriver as ChromeDriver

from src.Retrospective.Retrospective import Retrospective


class TestGoogleNewsDriver(unittest.TestCase):
    def setUp(self):
        self.retrospective = Retrospective()
        ChromeDriver.update()
        self.news_url = self.retrospective.googleNewsDriver.get_google_news_url("cisco")
        self.page_source = self.retrospective.googleNewsDriver.get_search_result_page_source(
            self.news_url
        )
        self.results = self.retrospective.googleNewsDriver.parse_search_result_page_source(
            self.page_source
        )

    def test_get_google_news_url(self):
        self.assertEqual(
            self.news_url, "https://www.google.com/search?tbm=nws&q=cisco&tbs=sbd:0", "Should be 'https://www.google.com/search?tbm=nws&q=cisco&tbs=sbd:0'")

    def test_get_search_result_page_source(self):
        self.assertIsNotNone(
            self.page_source, "Should not be None")

    def test_parse_search_result_page_source(self):
        self.assertIsNotNone(
            self.results, "No results returned from parser")
        self.assertTrue(
            "title" in self.results[0])
        self.assertTrue(
            "description" in self.results[0])
        self.assertTrue(
            "link" in self.results[0])
        self.assertTrue(
            "time_ago" in self.results[0])

if __name__ == '__main__':
    unittest.main()