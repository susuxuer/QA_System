#-*- coding=utf-8 -*-
import tornado.ioloop
import tornado.web
import tornado.httpserver
import json
import requests
import ConfigParser
import sys
from tornado.options import define, options
sys.path.append("..")
import runcode.main as QA

define("port", default=80, help="run on the given port", type=int)


keyVec, svm_model = QA.getTrainingData() # 返回特征值组成的向量，和libsvm的训练模板
config = ConfigParser.ConfigParser()
config.read("../../data/config/server_config.cfg")
authURL = config.get("global", "authURL")
serverID = config.get("global", "serverID")

# url表示授权服务器的API
# serverId表示授权服务分配给评测系统的serverId
# token表示待验证的token
def verify_token(url, serverId, token):
	return True   # 以后使用接口时，将这一行删除
	sendData = {"serverId":serverId, "token":token}
	response = requests.post(url, sendData)
	jresponse = json.loads(response.text)
	if jresponse["status"] == 1:
		return True
	else:
		return False

#验证token格式是否正确，若不正确，则返回错误信息，否则message is none
def verify_request(task):
	result = {"valid":1, "message":"none"}
	if "token" not in task.keys():
		result = {"valid":0, "message":"missing token..."}
	if "question" not in task.keys():
		result = {"valid":0, "message":"missing submissionType..."}
	return result

#处理web-service发送来的请求,
#body为request时post的数据,
def answer_question_task(body):
	#将body由json格式转化成python字符串格式
	question_task = json.loads(body)
	question = question_task["question"]
	#获取request并验证request是否有效
	request_valid_result = verify_request(question_task)
	print question
	#若request请求格式不正确,则返回错误消息
	if request_valid_result["valid"] == 0:
		response = {"received":"no", "message":request_valid_result["message"]}
	else:
		token = question_task["token"]
		if verify_token(authURL, serverID, token) == True:
			print "token pass"
			if len(question) < 100:
				#问题长度够短，回答问题
				result = QA.answerQuestion(question, keyVec, svm_model)
				response = {"received":"yes", "message":str(result)}
			else:
				response = {"received":"yes", "message":"问题太长了"}
		else:
			response = {"received":"no", "message":"token invalid..."}
	return response

class QuestionAnswerHandler(tornado.web.RequestHandler):
	def post(self):
		#获取问题，进行回答
		response = answer_question_task(self.request.body)
		#响应web服务器
		print response["message"]
		self.write(response)

	def set_default_headers(self):
		self.set_header('Content-type','application/json;charset=utf-8')

if __name__ == "__main__":
    application = tornado.web.Application(handlers=[(r"/", QuestionAnswerHandler)])
    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
    connection.close()
