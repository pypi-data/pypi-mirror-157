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


import requests

from ProxyPool import ProxyPool
from UserAgent import UserAgent


class ProxyRequests:
    def __init__(self, target_count=3, max_attempts=3):
        self.target_count = target_count
        self.max_attempts = max_attempts
        self.proxy_pool = ProxyPool()
        self.proxy_pool.maintain_pool()
        self.user_agent = UserAgent()
        self.user_agent.load_user_agents()

    def get(self, url, headers={}):
        attempts = 0
        while attempts < self.max_attempts:
            instance = self.proxy_pool.get_random_proxy_instance()
            proxies = {
                "http": "http://" + instance.ip_address + ":8888",
                "https": "http://" + instance.ip_address + ":8888",
            }
            if not headers:
                headers = {
                    "user-agent": self.user_agent.get_random_user_agent(),
                    # "referer": "https://www.google.com/",
                    # "accept": "*/*",
                    # "accept-encoding": "gzip, deflate, br",
                    # "accept-language": "en-US,en;q=0.9",
                    # "content-length": "0",
                    # "content-type": "text/plain;charset=UTF-8",
                    # "dnt": "1",
                    # "origin": "https://www.google.com",
                    # "sec-fetch-dest": "empty",
                    # "sec-fetch-mode": "no-cors",
                    # "sec-fetch-site": "same-origin",
                }
            response = requests.get(url, proxies=proxies, headers=headers)
            if not response.ok:
                instance.terminate()
                self.proxy_pool.maintain_pool()
            else:
                break
        return response


def main():
    pass


if __name__ == "__main__":
    main()
