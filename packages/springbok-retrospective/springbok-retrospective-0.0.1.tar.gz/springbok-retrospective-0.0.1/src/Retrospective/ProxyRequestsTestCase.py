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

from bs4 import BeautifulSoup as Soup

from ProxyRequests import ProxyRequests


class ProxyRequestTestCase(unittest.TestCase):
    def setUp(self):
        self.proxyRequests = ProxyRequests()

    def test___init__(self):
        self.assertEqual(len(self.proxyRequests.proxy_pool.instances), 3)
        self.assertEqual(len(self.proxyRequests.user_agent.user_agents), 3)

    def test_get_random_user_agent(self):
        url = "https://www.google.com"
        response = self.proxyRequests.get(url)
        soup = Soup(response.content, "html.parser")
        input = soup.find_all("input", attrs={"class": "gLFyf gsfi"})
        self.assertEqual(len(input), 1)

    def tearDown(self):
        self.proxyRequest = None


if __name__ == "__main__":
    unittest.main()
