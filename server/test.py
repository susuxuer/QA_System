#! /usr/bin/python
#coding=utf-8
 
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import json
 
from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)
 
class IndexHandler(tornado.web.RequestHandler):
    def post(self):
        greeting = self.request.body
        aaa = json.loads(greeting)
        if "aaa" in aaa.keys():
        	print "!asd!"
 
if __name__ == "__main__":
    app = tornado.web.Application(handlers=[(r"/", IndexHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()