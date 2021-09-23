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

from fedora_easyfix.utilities.composer import StatusDecorator
from urllib3 import PoolManager
from urllib3.exceptions import MaxRetryError, NewConnectionError

httpobjc = PoolManager()
api_base_url = "https://pagure.io/api/0/"
statdcrt = StatusDecorator()


class PagureRepositories():
    def __init__(self, repository_list, base_url, api_key):
        self.repository_list = repository_list
        self.base_url = base_url
        self.api_key = api_key
        self.repository_collection = {}

    def fetch_tickets_from_repository(self, repository_name):
        label = self.repository_list[repository_name]["label"]
        contact = self.repository_list[repository_name]["contact"]
        api_issue_endpoint = "%s%s/issues" % (api_base_url, repository_name)
        respobjc = httpobjc.request(
            "GET",
            api_issue_endpoint,
            fields={
                "per_page": 100,
                "tags": label,
                "status": "Open"
            }
        )
        respdict = json.loads(respobjc.data)
        ticket_count = respdict["total_issues"]
        ticket_list = {}
        for ticket in respdict["issues"]:
            ticket_list[ticket["id"]] = {
                "title": ticket["title"],
                "date_created": ticket["date_created"],
                "last_updated": ticket["last_updated"],
                "creator": {
                    "full_url": ticket["user"]["full_url"],
                    "fullname": ticket["user"]["fullname"],
                    "name": ticket["user"]["name"]
                },
                "url": ticket["full_url"],
                "labels": ticket["tags"]
            }
        api_project_endpoint = "%s%s" % (api_base_url, repository_name)
        respobjc = httpobjc.request(
            "GET",
            api_project_endpoint,
        )
        respdict = json.loads(respobjc.data)
        ticket_dict = {
            "ticket_count": ticket_count,
            "ticket_list": ticket_list,
            "contact": "%s@fedoraproject.org" % contact,
            "url": respdict["full_url"],
            "description": respdict["description"],
            "id": respdict["id"],
            "target_label": label,
            "maintainer": {
                "full_url": respdict["user"]["full_url"],
                "fullname": respdict["user"]["fullname"],
                "name": respdict["user"]["name"]
            },
            "tags": respdict["tags"],
            "date_created": respdict["date_created"]
        }
        return ticket_dict, ticket_count

    def return_repository_collection(self):
        repositories_passed, repositories_failed, repositories_total = 0, 0, 0
        for repository_name in self.repository_list.keys():
            repositories_total += 1
            try:
                self.repository_collection[repository_name], ticket_count = self.fetch_tickets_from_repository(repository_name)
                statdcrt.general("[PASS] %s - Retrieved %s tickets" % (repository_name, ticket_count))
                repositories_passed += 1
            except NewConnectionError as expt:
                statdcrt.general("[FAIL] %s - Failed to retrieve tickets - Could not establish connection" % repository_name)
                repositories_failed += 1
                continue
            except MaxRetryError as expt:
                statdcrt.general("[FAIL] %s - Failed to retrieve tickets - Reached max number of retries" % repository_name)
                repositories_failed += 1
                continue
        statdcrt.success("%s passed, %s failed, %s total" %(repositories_passed, repositories_failed, repositories_total))
        return self.repository_collection
