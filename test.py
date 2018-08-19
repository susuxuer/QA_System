#encoding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import jieba
import math
sys.path.append("..")
from KnowledgeGraph.loadModel import loadUserDict
from KnowledgeGraph.auxiliaryFunct import *
loadUserDict()

_result=segment('c语言scanf函数')
for line in _result:
    print line
