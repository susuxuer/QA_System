#encoding:utf-8

import main as QA

if __name__ == "__main__":
    keyVec, svm_model = QA.getTrainingData() # 返回特征值组成的向量，和libsvm的训练模板
    test_file = open("../../data/test_out/all_ques.txt", "r")
    test_data = test_file.read().split("\n")
    cnt = 1
    for question in test_data:
    	if cnt > 0:
    	    print("问题"+str(cnt)+":"+question+"\n")
            answer = QA.answerQuestion(question, keyVec, svm_model)
    	    print("回答:\n"+answer+"\n")
    	cnt = cnt+1