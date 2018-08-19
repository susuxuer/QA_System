#coding=utf-8
import jieba.posseg as pseg
import sys
sys.path.append("..")
import KnowledgeGraph.loadModel as PRE
from KnowledgeGraph.auxiliaryFunct import *
import re
def stopwordFilter(question_vec):                  # 使用停用词表过滤,返回为过滤后的问题向量
    stopword_vec = PRE.getStops()
    no_stopword_question_vec = [] # 没有停用词的问题向量

    for word in question_vec:
        if word not in stopword_vec:
            no_stopword_question_vec.append(word)

    return no_stopword_question_vec

# def exchange_space_to_comma(ques):      # pynlpir分词，如果问题里面有空格直接段错误，所以空格怎么办
#该函数就是对question进行分词，然后过滤掉停用词等
def keywordExtract(question): # 输入为中文问题，返回关键词
    split_word_vec = []
    #因为你这里没有涉及倒词性，我就简单使用分词，如果需要词性稍微百度即可
    #splitWord = pseg.cut(question)
    #splitWord = pynlpir.segment(question,pos_tagging=False)
    split_word_vec=segment(question)
    i = 0

        
    # for word in splitWord:
    #     # if word.flag == "n" or word.flag == "eng" or word.flag == "x":        # 词性需要是名词
    #     split_word_vec.append((word.word).encode('utf-8'))
    #     #split_word_vec.append(word.encode('utf-8'))

    word_vec = []                      # 将特殊情况处理后的词语向量
    #简单来说就是过滤一下，使得分完的词更加干净
    for i in range(0,len(split_word_vec)):                 # 处理特殊情况
        if split_word_vec[i] != " " and split_word_vec[i] != "\n":   # 忽略掉空格和换行
            word_vec.append(split_word_vec[i])



    keyword_vec = stopwordFilter(word_vec)
    keyword_set = set(keyword_vec)
    keyword_vec = list(keyword_set)


    return keyword_vec

def getTfidf(word, filepath): #输入一个词和tfidf结果的路径，返回tfidf的值，没有这个词返回0
    fileIn = open(filepath, "r")
    data = fileIn.read()
    word_and_idf_vec = data.split("\n")
    word_vec = []
    idf_vec = []
    for word_and_idf in word_and_idf_vec:
        tmp = word_and_idf.split()
        if len(tmp) > 1:
            word_vec.append(tmp[0])
            idf_vec.append(tmp[1])

    if word in word_vec:                                   # 在结果中进行查找
        return idf_vec[word_vec.index(word)]
    else:
        return 0

if __name__ == "__main__":
    PRE.loadUserDict()               # 为结巴分词导入词库
    # PRE.loadPynlpIR()

    while(raw_input()!='stop'):
        print("选择功能：\n1. 抽出一个问题的关键词\n2. 得到一个词的tfidf值\n")
        choice = raw_input("选择：")
        if choice == "1":
            question = raw_input("输入问题：")
            keyword_vec = keywordExtract(question)      # 进行朴素贝叶斯和svm结合的测试
            for keyword in keyword_vec:
                print(keyword+" ")
            print("\n")
        elif choice == "2":
            word = raw_input("输入词语：")
            classNum = getTfidf(word, "../../data/classifydata/filter-question")
            print("值: "+str(classNum))