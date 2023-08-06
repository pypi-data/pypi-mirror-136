import base64
from gevent import monkey

from miniweb.request import HttpRequest
monkey.patch_all()

import os
import json

import unittest
import requests
from fastutils import fsutils
from gevent import pywsgi

from .example import application

def get_simple_server(port):
    port = 18181
    backlog = 4096
    server = pywsgi.WSGIServer(("0.0.0.0", 18181), application, backlog=backlog)
    server.start()
    server_url = f"http://127.0.0.1:{port}"
    return server, server_url

class TestMiniweb(unittest.TestCase):

    def setUp(self):
        self.server, self.server_url = get_simple_server(18801)

    def tearDown(self):
        self.server.stop()
    
    def test01(self):
        response = requests.get(self.server_url + "/plain/ping")
        assert response.status_code == 200
        assert response.text == "pong"

    def test02(self):
        response = requests.post(self.server_url + "/plain/echo", data={"msg": "hello"})
        assert response.status_code == 200
        assert response.text == "hello"

    def test03(self):
        response = requests.get(self.server_url + "/plain/redirect")
        assert response.status_code == 200
        assert response.text == "pong"
        assert response.url == self.server_url + "/plain/ping"

    def test04(self):
        response = requests.get(self.server_url + "/json/ping")
        response_data = json.loads(response.content)
        assert response.status_code == 200
        assert response_data["data"] == "pong"

    def test05(self):
        response = requests.get(self.server_url + "/json/echo", params={"msg": "hello"})
        response_data = json.loads(response.content)
        assert response.status_code == 200
        assert response_data["data"] == "hello"

    def test06(self):
        response = requests.get(self.server_url + "/json/redirect")
        response_data = json.loads(response.content)
        assert response.status_code == 200
        assert response_data["data"] == "pong"
        assert response.url == self.server_url + "/json/ping"

    def test07(self):
        response = requests.get(self.server_url + "/simplejson/ping")
        response_data = json.loads(response.content)
        assert response.status_code == 200
        assert response_data["result"] == "pong"

    def test08(self):
        response = requests.get(self.server_url + "/simplejson/echo", params={"msg": "hello"})
        response_data = json.loads(response.content)
        assert response.status_code == 200
        assert response_data["result"] == "hello"

    def test09(self):
        response = requests.get(self.server_url + "/simplejson/redirect")
        response_data = json.loads(response.content)
        assert response.status_code == 200
        assert response_data["result"] == "pong"
        assert response.url == self.server_url + "/simplejson/ping"

    def test10(self):
        response = requests.get(self.server_url + "/plain/ping2")
        assert response.status_code == 404
    
    def test11(self):
        response = requests.put(self.server_url + "/plain/ping")
        assert response.status_code == 405
    
    def test12(self):
        response = requests.get(self.server_url + "/plain/cookie")
        cookies = response.cookies.get_dict()
        assert cookies["sessionid"] == "session01"
        assert cookies["appid"] == "app01"
        assert cookies["username"] == "username01"
    
    def test13(self):
        response = requests.get(self.server_url + "/simplejson/div", params={"a": 5, "b": 1})
        response_data = json.loads(response.content)
        assert response_data["result"] == 5

        response = requests.get(self.server_url + "/simplejson/div", params={"a": 5, "b": 0})
        response_data = json.loads(response.content)
        assert response_data["error"]["message"] == "division by zero"

    def test14(self):
        cookies = {
            "msg": "hello"
        }
        response = requests.get(self.server_url + "/plain/echo/cookie", cookies=cookies)
        assert response.text == "hello"

    def test15(self):
        response = requests.post(self.server_url + "/plain/echo/payload", json={"msg": "hello"})
        assert response.text == "hello"

    def test16(self):
        response = requests.get(self.server_url + "/plain/addflag")
        assert response.text == "1,2,3,4"

    def test17(self):
        data = {
            "msg": "a" * (1024*1024*3),
        }
        response = requests.post(self.server_url + "/plain/echo", data=data)
        assert response.status_code == 413

    def test18(self):
        tmpfc1 = "tmpf1"
        tmpfc2 = ""
        tmpfc3 = os.urandom(1024)
        tmpf1 = fsutils.TemporaryFile(tmpfc1)
        tmpf2 = fsutils.TemporaryFile(tmpfc2)
        tmpf3 = fsutils.TemporaryFile(tmpfc3)
        files = {
            "f1": tmpf1.open("rb"),
            "f2": tmpf2.open("rb"),
            "f3": tmpf3.open("rb"),
        }
        data = {
            "msg": "hello world",
            "name": "test name",
        }
        response = requests.post(self.server_url + "/plain/upload", data=data, files=files)
        response_data = json.loads(response.content)
        assert response_data["msg"] == "hello world"
        assert response_data["name"] == "test name"
        assert response_data["boundary"]
        assert response_data["f1"] == tmpfc1
        assert response_data["f2"] == tmpfc2
        assert response_data["f3"] == base64.encodebytes(tmpfc3).decode("utf-8")
