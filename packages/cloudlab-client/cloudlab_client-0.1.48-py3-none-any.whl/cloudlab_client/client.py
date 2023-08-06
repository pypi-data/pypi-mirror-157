#!/usr/bin/env python3

import json
import requests
import urllib.parse

from typing import Any, List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def inject_generic_repr(cls):
    """ Injects a generic repr function """
    def generic_repr(that):
        class_items = [f'{k}={v}' for k, v in that.__dict__.items()]
        return f'<{that.__class__.__name__} ' + ', '.join(class_items) + '>'

    cls.__repr__ = generic_repr
    return cls


def assert_nonempty_args(instance: Any, attrs: List[str]):
    for attr in attrs:
        val = getattr(instance, attr, None)
        if not val:
            raise Exception("%s: Attribute %s cannot be %s" %
                            (type(instance).__name__, attr, val))


###############################################################################
# Objects
###############################################################################


@inject_generic_repr
class CloudlabNode(object):

    def __init__(self, name: str, address: str) -> None:
        self.name = name
        self.address = address
        assert_nonempty_args(self, ["name", "address"])


@inject_generic_repr
class CloudlabExperiment(object):

    def __init__(self, name: str, uuid: str, _raw=None) -> None:
        self.name = name
        self.uuid = uuid
        self._raw = _raw
        assert_nonempty_args(self, ["name", "uuid"])


###############################################################################
# Client
###############################################################################


SERVER_AJAX_URL = "https://www.cloudlab.us/server-ajax.php"


@inject_generic_repr
class CloudlabClient(object):
    """Cloudlab client.

    Tries to use the programmatic AJAX APIs as much as possible. Made by
    capturing HTTP requests and replicating them.

    The following methods still use web-scraping:
    - login: Can't get around that for login unfortunately.
    - experiment_list_nodes: Not straightforward how to construct the node URLs
                             from the information returned by the programmatic
                             API.
    """
    def __init__(self, timeout=30, headless_mode=True) -> None:
        options = Options()
        options.headless = headless_mode  # Change to False for debugging
        driver = webdriver.Chrome(options=options)
        self.driver = driver
        self.timeout = timeout

    def _get_auth_cookies(self):
        return {cookie["name"]: cookie["value"]
                for cookie in self.driver.get_cookies()}

    def login(self, username: str, password: str):
        self.driver.get("https://www.cloudlab.us/login.php")
        id_input = self.driver.find_element(by=By.NAME, value="uid")
        id_input.send_keys(username)
        password_input = self.driver.find_element(by=By.NAME, value="password")
        password_input.send_keys(password)
        login_button = self.driver.find_element(
            by=By.ID, value="quickvm_login_modal_button")
        login_button.click()

    def experiment_list(self) -> List[CloudlabExperiment]:
        form_data = {
            "ajax_route": "user-dashboard",
            "ajax_method": "ExperimentList",
            "ajax_args[uid]": "yannisz",
        }
        resp = requests.post(SERVER_AJAX_URL, data=form_data,
                             cookies=self._get_auth_cookies())
        if resp.status_code != 200:
            raise Exception("Experiment list request failed with code %s."
                            % resp.status_code)
        resp_json = json.loads(resp.content)
        if resp_json["code"] != 0:
            raise Exception("Experiment list failed: %s" % resp_json)
        experiments = []
        for exp_name, exp_body in resp_json["value"].get("user_experiments", {}).items():  # noqa: E501
            experiments.append(
                CloudlabExperiment(exp_name.split(":")[-1], exp_body["uuid"],
                                   _raw=exp_body))
        return experiments

    def experiment_get(self, name: str) -> CloudlabExperiment:
        for experiment in self.experiment_list():
            if experiment.name == name:
                return experiment
        raise Exception("Experiment not found!")

    def experiment_list_nodes(self, name: str) -> List[CloudlabNode]:
        nodes = []
        # Get experiment page
        exp = self.experiment_get(name)
        exp_page = "https://www.cloudlab.us/status.php?uuid=%s" % exp.uuid
        self.driver.get(exp_page)
        # Parse node names and addresses
        list_view_table = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table#listview_table")))  # noqa: E501
        WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((By.ID, "listview-row-node0")))
        rows = list_view_table.find_elements(by=By.TAG_NAME, value="tr")
        rows = [row for row in rows
                if row.get_attribute("id").startswith("listview-row-")]
        for row in rows:
            name = (row.find_element(by=By.CSS_SELECTOR,
                                     value="td[name='client_id'")
                       .get_attribute("innerHTML"))
            sshurl = (row.find_element(by=By.CSS_SELECTOR,
                                       value="td[name='sshurl'")
                         .find_element(by=By.TAG_NAME, value="a")
                         .get_attribute("href"))
            address = urllib.parse.urlparse(sshurl).hostname
            nodes.append(CloudlabNode(name, address))
        return nodes

    def experiment_extend(self, name: str, reason: str, hours=144):
        # Apply the same validations as cloudlab.
        MAX_HOURS = 11 * 7 * 24
        if hours > MAX_HOURS:
            raise Exception("Extension cannot be more than %s hours"
                            % MAX_HOURS)
        if hours <= 144 and len(reason) < 120:
            raise Exception("For extension >= 6 days (144 hours), reason must"
                            " be at least 120 characters.")
        elif hours > 144 and len(reason) < 240:
            raise Exception("For extension >= 6 days (144 hours), reason must"
                            " be at least 120 characters.")
        # Get experiment
        experiment = self.experiment_get(name)
        # Request the extension
        form_data = {
            "ajax_route": "status",
            "ajax_method": "RequestExtension",
            "ajax_args[uuid]": experiment.uuid,
            "ajax_args[howlong]": hours,
            "ajax_args[reason]": reason,
            # "ajax_args[maxextension]" <- is this needed???
        }
        # Cookies are our authentication method
        res = requests.post(SERVER_AJAX_URL, data=form_data,
                            cookies=self._get_auth_cookies())
        if res.status_code != 200:
            raise Exception("Experiment extend request failed with code %s."
                            % res.status_code)
        res_json = json.loads(res.content)
        if res_json["code"] != 0:
            raise Exception("Experiment extend request failed: %s" % res_json)

    # TODO:
    # - experiment_create(name=..., num_nodes=..., node_type=...)
