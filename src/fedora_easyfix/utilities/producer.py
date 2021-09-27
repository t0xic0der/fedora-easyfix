"""
    Copyright (c) 2021 Fedora Websites and Apps

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

import json
import sys
import time

from dotenv import dotenv_values
from fedora_easyfix.__init__ import __version__
from fedora_easyfix.models.github import GitHubRepositories
from fedora_easyfix.models.gitlab import GitLabRepositories
from fedora_easyfix.models.pagure import PagureRepositories
from fedora_easyfix.utilities.composer import StatusDecorator
from urllib3 import PoolManager
from urllib3.exceptions import MaxRetryError, NewConnectionError
from yaml import CLoader, load

httpobjc = PoolManager()
statdcrt = StatusDecorator()


class Producer(object):
    def __init__(self):
        self.envrvars = dotenv_values(".env")
        self.github_username = self.envrvars["GITHUB_USERNAME"]
        self.github_api_key = self.envrvars["GITHUB_API_KEY"]
        self.pagure_api_key = self.envrvars["PAGURE_API_KEY"]
        self.gitlab_api_key = self.envrvars["GITLAB_API_KEY"]
        self.rplist_url = self.envrvars["RPLIST_URL"]
        self.yamldict = load(httpobjc.request("GET", self.rplist_url).data.decode(), Loader=CLoader)
        self.ticket_collection = {
            "forges": {},
            "time_of_retrieval": 0.0
        }

    def check_repolist_version_and_start(self):
        if self.yamldict["repolist_version"] == __version__:
            self.populate_ticket_collection()
            self.ticket_collection["time_of_retrieval"] = time.time()
            self.write_index_to_local_json()
        else:
            statdcrt.failure("Could not index tickets")
            statdcrt.general("Repolist version does not correspond with the Easyfix version")
            sys.exit()

    def populate_ticket_collection(self):
        if "github" in self.yamldict["forges"].keys():
            github_repository_list = self.yamldict["forges"]["github"]["repositories"]
            github_base_url = self.yamldict["forges"]["github"]["url"]
            statdcrt.warning(
                "Found %s repositories on GitHub" %
                len(self.yamldict["forges"]["github"]["repositories"].keys())
            )
            self.ticket_collection["forges"]["github"] = GitHubRepositories(
                github_repository_list,
                github_base_url,
                self.github_api_key,
                self.github_username
            ).return_repository_collection()
        if "pagure" in self.yamldict["forges"].keys():
            pagure_repository_list = self.yamldict["forges"]["pagure"]["repositories"]
            pagure_base_url = self.yamldict["forges"]["pagure"]["url"]
            statdcrt.warning(
                "Found %s repositories on Pagure" %
                len(self.yamldict["forges"]["pagure"]["repositories"].keys())
            )
            self.ticket_collection["forges"]["pagure"] = PagureRepositories(
                pagure_repository_list,
                pagure_base_url,
                self.pagure_api_key
            ).return_repository_collection()
        if "gitlab" in self.yamldict["forges"].keys():
            gitlab_repository_list = self.yamldict["forges"]["gitlab"]["repositories"]
            gitlab_base_url = self.yamldict["forges"]["gitlab"]["url"]
            statdcrt.warning(
                "Found %s repositories on GitLab" %
                len(self.yamldict["forges"]["gitlab"]["repositories"].keys())
            )
            self.ticket_collection["forges"]["gitlab"] = GitLabRepositories(
                gitlab_repository_list,
                gitlab_base_url,
                self.gitlab_api_key
            ).return_repository_collection()

    def write_index_to_local_json(self):
        try:
            tickdata = json.dumps(self.ticket_collection, indent=4)
            with open("tickdata.json", "w") as tickfile:
                tickfile.write(tickdata)
            statdcrt.section("Indexing complete!")
        except PermissionError as expt:
            statdcrt.failure("Could not index tickets")
            statdcrt.general("Please check if appropriate permissions are available to write in the directory")
            sys.exit()


def mainfunc():
    statdcrt.section("Indexing tickets...")
    try:
        prodobjc = Producer()
        prodobjc.check_repolist_version_and_start()
    except KeyError as expt:
        statdcrt.failure("Could not index tickets")
        statdcrt.general("Please check if the environment variables are configured properly")
        sys.exit()
    except NewConnectionError as expt:
        statdcrt.failure("Could not index tickets")
        statdcrt.general("Please check if the repository listing is available in the specified location")
        sys.exit()
    except MaxRetryError as expt:
        statdcrt.failure("Could not index tickets")
        statdcrt.general("Exceeded number of retries while attempting to fetch the repository listing")
        sys.exit()
    except KeyboardInterrupt as expt:
        print("\n", end="")
        statdcrt.failure("Could not index tickets")
        statdcrt.general("Process abortion requested by the user")
        sys.exit()


if __name__ == "__main__":
    mainfunc()
