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

from UserAgent import UserAgent


class UserAgentTestCase(unittest.TestCase):
    def setUp(self):
        self.userAgent = UserAgent()

    def test___init__(self):
        self.assertEqual(len(self.userAgent.user_agents), 0)
        self.userAgent.load_user_agents()
        self.assertEqual(len(self.userAgent.user_agents), 3)

    def test_get_random_user_agent(self):
        self.userAgent.load_user_agents()
        n = 0
        ua_a = self.userAgent.get_random_user_agent()
        for i in range(1000):
            ua_b = self.userAgent.get_random_user_agent()
            if ua_a == ua_b:
                n += 1
        self.assertTrue(330 < n and n < 336)

    def tearDown(self):
        self.userAgent = None


if __name__ == "__main__":
    unittest.main()
