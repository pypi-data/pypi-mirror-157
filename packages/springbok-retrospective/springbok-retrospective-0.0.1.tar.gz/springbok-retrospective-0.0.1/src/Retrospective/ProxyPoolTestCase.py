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

from ProxyPool import ProxyPool


class ProxyPoolTestCase(unittest.TestCase):
    def setUp(self):
        self.proxyPool = ProxyPool()

    def test_maintain_pool(self):
        self.assertEqual(len(self.proxyPool.instances), 0)
        self.proxyPool.maintain_pool()
        self.assertEqual(len(self.proxyPool.instances), self.proxyPool.target_count)

        self.proxyPool.maintain_pool()
        self.assertEqual(len(self.proxyPool.instances), self.proxyPool.target_count)

    def test_add_to_pool(self):
        self.proxyPool.maintain_pool()

        self.proxyPool.add_to_pool(1)
        self.assertEqual(len(self.proxyPool.instances), self.proxyPool.target_count + 1)

        self.proxyPool.maintain_pool()
        self.assertEqual(len(self.proxyPool.instances), self.proxyPool.target_count)

    def test_remove_from_pool(self):
        self.proxyPool.maintain_pool()

        self.proxyPool.remove_from_pool(1)
        self.assertEqual(len(self.proxyPool.instances), self.proxyPool.target_count - 1)

        self.proxyPool.maintain_pool()
        self.assertEqual(len(self.proxyPool.instances), self.proxyPool.target_count)

    def test_restart_pool(self):
        self.proxyPool.maintain_pool()

        ip_a = set([i.ip_address for i in self.proxyPool.instances])
        self.proxyPool.restart_pool()
        ip_b = set([i.ip_address for i in self.proxyPool.instances])
        self.assertEqual(len(ip_a.intersection(ip_b)), 0)

    def test_terminate_pool(self):
        self.proxyPool.maintain_pool()

        self.proxyPool.terminate_pool()
        self.assertEqual(len(self.proxyPool.instances), 0)

    def tearDown(self):
        self.proxyPool.terminate_pool()


if __name__ == "__main__":
    unittest.main()
