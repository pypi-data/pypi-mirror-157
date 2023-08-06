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


import os
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class UserAgent:
    def __init__(
        self,
        data_path=os.path.join(
            BASE_DIR, "Retrospective", "user-agents", "user-agents.txt",
        ),
    ):
        self.data_path = data_path
        self.user_agents = []

    def load_user_agents(self):
        with open(self.data_path, "r") as f:
            self.user_agents = f.readlines()

    def get_random_user_agent(self):
        ua = random.choice(self.user_agents)
        self.user_agents.remove(ua)
        if len(self.user_agents) == 0:
            self.load_user_agents()
        return ua.strip()


def main():
    pass


if __name__ == "__main__":
    main()
