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
import re
import requests
import wget
import zipfile


DRIVER_HOME = "/usr/local/bin"


def update():
    # Get Chrome application version
    chromereply = os.popen(
        r"/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version"
    ).read()
    chromereply = chromereply.rstrip()
    chromereply = chromereply.lstrip()
    tokens = re.split(r"\s+", chromereply)
    chromefullversion = tokens[2]
    tokens = chromefullversion.split(".")
    chromeversion = tokens[0]

    # Get Chrome driver version
    driverreply = os.popen(r"chromedriver --version").read()
    driverreply = driverreply.rstrip()
    driverreply = driverreply.lstrip()
    tokens = re.split(r"\s+", driverreply)
    driverfullversion = tokens[1]
    tokens = driverfullversion.split(".")
    driverversion = tokens[0]

    # Download and install if driver version does not match application version
    if not driverversion == chromeversion:
        version_number = _get_version(chromeversion)
        download_url = (
            "https://chromedriver.storage.googleapis.com/"
            + version_number
            + "/chromedriver_mac64.zip"
        )
        _download_and_install(download_url)


def _get_version(chromeversion):
    """Get the latest driver for the specifed chrome version
    """
    url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_" + str(
        chromeversion
    )
    response = requests.get(url)
    version_number = response.text
    return version_number


def _download_and_install(download_url):
    # Download the zip file using the url built above
    latest_driver_zip = wget.download(download_url)

    # Extract the zip file into the installation directory
    with zipfile.ZipFile(latest_driver_zip, "r") as zip_ref:
        zip_ref.extractall(path=DRIVER_HOME)

    # Delete the zip file downloaded above
    os.remove(latest_driver_zip)


if __name__ == "__main__":
    update()
