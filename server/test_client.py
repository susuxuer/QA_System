#! /usr/bin/python
#coding=utf-8
import requests
import json

url = "http://mqas.vmatrix.org.cn"
data = {"token":"213123","question":"%d是什么"}
r = requests.post(url, data = json.dumps(data))
# a = json.loads(r)
b = json.loads(r.text)
# print a
print b["message"]
