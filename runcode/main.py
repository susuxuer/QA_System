#encoding:utf-8

import sys
sys.path.append("..")
import QuestClassify.main as QC
import QuestAnswer.answer_all as QA
import KnowledgeGraph.loadModel as PRE

def getTrainingData():
    PRE.loadUserDict()               # 为结巴分词导入词库
    keyVec, svm_model = QC.data_processing_training() # 返回特征值组成的向量，和libsvm的训练模板
    return keyVec, svm_model

def answerQuestion(question, keyVec, svm_model):
    question_class = QC.nbs.predict_question(question, keyVec, svm_model)
    answer = ""
    _list = ["看懂了，但是这个没办法回答"]
    if question_class == "概念":
        _list = QA.ansDef(question)
    elif question_class == "用法" or question_class == "原因":
        _list = QA.ansUsage(question)
    elif question_class == "比较":
        _list = QA.ansComp(question)
    elif question_class == "隶属":
        _list = QA.ansContent(question)
    elif question_class == "内含代码":
        _list = ["这问题确实看不懂"]
    if len(_list) != 0:
        for line in _list:
            answer = answer+line+"\n"
    else:
        answer = "看懂了，但是这个没办法回答"

    return answer

if __name__ == "__main__":

    keyVec, svm_model = getTrainingData()

    # ------------- 以上是数据预处理，和训练的部分----------------
    # ------------- 以下是测试的部分 ---------------------------

    while (1):
        question = raw_input("输入中文问题：")
        answer = answerQuestion(question, keyVec, svm_model)
        print ("\n回答：\n"+answer)

