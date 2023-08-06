from typing import *

from commitizen.cz.customize.customize import CustomizeCommitsCz

import threading
import subprocess
import requests
import base64
from tomlkit.items import AoT, Table

import urllib.parse
import sys

api = "rest/api/2/issue/{}"

__all__ = ["Cz_flexivCz"]

cmd = ["git", "rev-parse", "--abbrev-ref", "HEAD"]


class Cz_flexivCz(CustomizeCommitsCz):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jira_issue = ""
        self.jira_summary = ""

        self.flexiv_cz_settings = self.config.settings.get("flexiv_cz", {})

        jira_root_url = self.flexiv_cz_settings.get("jira_root", "")
        assert jira_root_url, sys.exit("error! [jira_root] in [tool.commitizen] is required,please check you config file")
        self.jira_api = urllib.parse.urljoin(jira_root_url, api)

        self.jira_user = self.flexiv_cz_settings.get("jira_user", "")
        assert self.jira_user, sys.exit("error! [jira_user] in [tool.commitizen] is required,please check you config file")

        self.jira_token = self.flexiv_cz_settings.get("jira_token", "")
        assert self.jira_token, sys.exit("error! [jira_token] in [tool.commitizen] is required,please check you config file")

        self.jira_summary_name = self.flexiv_cz_settings.get("jira_summary_name_path",
                                                             "").split(".")[1]
        self.jira_issue_name = self.flexiv_cz_settings.get("jira_issue_name_path",
                                                           "").split(".")[1]

        threading.Thread(target=self.set_jira_info).start()
        # self.set_jira_info()

    def set_jira_info(self) -> str:
        """
        Get Jira issue from branch name
        """
        current_branch = subprocess.check_output(cmd).decode("utf-8").strip()
        jira_issue = current_branch.split("/")[-1]

        headers = {
            "Authorization": f"Basic {base64.b64encode(f'{self.jira_user}:{self.jira_token}'.encode('utf-8')).decode('utf-8')}",
        }

        response = requests.request("GET",
                                    self.jira_api.format(jira_issue),
                                    headers=headers)
        if response.status_code == 200:
            self.jira_summary = response.json()["fields"]["summary"]
            self.jira_issue = jira_issue
        else:
            self.jira_summary = ""
            self.jira_issue = ""

    def questions(self) -> List[Dict[str, Any]]:
        questions = super().questions()
        if isinstance(questions, AoT):
            # AOT is a TOMLKit object
            outer = []
            inner = {}
            questions = questions.body
            for question in questions:
                if isinstance(question, Table):
                    inner = dict(question)
                    if inner["name"] == self.jira_issue_name:
                        inner["default"] = lambda x: self.jira_issue
                    if inner["name"] == self.jira_summary_name:
                        inner["default"] = lambda x: self.jira_summary
                    outer.append(inner)
            return outer
        return questions


discover_this = Cz_flexivCz
