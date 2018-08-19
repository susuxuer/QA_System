#encoding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import math
import similarity

sys.path.append("..")
from KnowledgeGraph.dealdata import *
from KnowledgeGraph.auxiliaryFunct import *

import keywordextract
from answer_score import *
import operator
#计算编辑距离的概率

def calPro(word1,word2):
    word1=word1.decode('utf-8')
    word2=word2.decode('utf-8')
    len1=len(word1)
    len2=len(word2)
    len1=(len1+len2)/float(2)
   
    length=similarity.difflib_leven(word1,word2)
    return 1-length/len1

#可能是通过节点的内容找到的节点，比如%s,那么它的回答应该是：节点的定义+节点的该属性
def getDefiniAttr(graph,relnodes,name,keyword):
    node=getNodeByname(name, graph)
    #getInfoFromNode(name)
    relnode=getRelNodeByname(name,relnodes)
    
    info = {}
    if node==None and relnode!=None:
        infos=relnode.get_Infos()
    elif node!=None and relnode==None:
        infos=node.get_Infos()
        if len(infos) == 0:
            answer = "无法找到答案"
            return answer
        for item in infos.items():
            if item[0].find(keyword)!=-1 or item[1].find(keyword)!=-1:
                return str(keyword)+"是"+str(node)+"中的概念， 由"+str(node)+"的"+str(item[0])+"可知："+str(item[1])

#可能是通过节点的内容找到的节点，比如%s,那么它的回答应该是：节点的定义+节点的该属性
def getUsageAttr(graph,relnodes, nodes, keywords):
    answer = []
    answer_list = []   # 保存所有可能回答的数组
    key_list = []      # 方便返回答案，将节点名存入数组
    for i in range(0, len(nodes)):
        node=getNodeByname(nodes[i][0], graph)
        relnode=getRelNodeByname(nodes[i][0],relnodes)
        usage = {}
        if node==None and relnode!=None:
            usage=relnode.get_Infos()
        elif node!=None and relnode==None:
            usage=node.get_Infos()

        for item in usage.items():
            if item[1].count(nodes[i][1]) != 0:
                answer_list.append(item)
                key_list.append(nodes[i][1]+"是"+nodes[i][0]+"中的概念,"+nodes[i][0])
    
    if len(answer_list) == 0:
        answer.append("无法找到答案")
    else:
        tmp_set = set()         # 拷贝一个关键词集
        keywords_set = set(keywords)
        for key in keywords:
            tmp_set.add(key)
        for key in tmp_set:
            similarWord = getCorela(key, graph, relnodes)
            for word in similarWord:
                keywords_set.add(word)
        tmp_answer = getBestAnswer(answer_list, keywords_set, key_list)   # 根据辅助词和非辅助词，获得价值大的答案
        if len(tmp_answer) != 0:
            answer.append(tmp_answer[0])
        else:
            answer.append("无法找到答案")

    return answer

#根据名字找到具体的节点，返回所有info
def getUsage(graph,relnodes,keys,all_key_set):
    answer = []
    answer_list = []   # 保存所有可能回答的数组
    key_list = []      # 方便返回答案，将节点名存入数组
    for name in keys:
        node=getNodeByname(name, graph)
        relnode=getRelNodeByname(name,relnodes)
        usage = {}
        if node==None and relnode!=None:
            usage=relnode.get_Infos()
        elif node!=None and relnode==None:
            usage=node.get_Infos()

        for item in usage.items():
            answer_list.append(item)
            key_list.append(name)
    
    if len(answer_list) == 0:
        answer.append("无法找到答案")
    else:
        tmp_set = set()         # 拷贝一个关键词集
        for key in all_key_set:
            tmp_set.add(key)
        for key in tmp_set:
            similarWord = getCorela(key, graph, relnodes)
            for word in similarWord:
                all_key_set.add(word)
        # 查找非节点词的同义词
        answer = getBestAnswer(answer_list, all_key_set, key_list)
        # 根据辅助词和非辅助词，获得价值大的答案
    return answer

#根据名字找到具体的节点，有子节点返回所有子节点，否则返回所有info
def getContent(graph,relnodes,name,all_key_set):
    
    node=getNodeByname(name, graph)
    #getInfoFromNode(name)
    relnode=getRelNodeByname(name,relnodes)
    contents = []
    if node==None and relnode!=None:
        contents=relnode.get_Inheri()
    elif node!=None and relnode==None:
        contents=node.get_Inheri()

    if len(contents) > 1:
        answer = str(name)+"由 "
        for i in range(0,len(contents)):
            answer = answer+contents[i].name
            if i == len(contents)-2:      # 倒数第二个的特殊情况
                answer = answer+"和"
            elif i < len(contents)-2:
                answer = answer+","
            else:
                answer = answer+" 所组成\n"
        return answer
    else:
        keys = set()
        keys.add(name)
        return getUsage(graph,relnodes,keys,all_key_set)  # 如果子节点少于2个，直接当用法问题解决

#回答用法
def ansUsage(question):
    #得到节点和关系节点的集合
    graph,relnodes=preData()
    nodesNames=getAllNodes(graph, relnodes)
    #得到关键词语
    keywords=keywordextract.keywordExtract(question)
    support_words = getSupportWord()
    # keywords = changeNode(keywords,nodesNames)
    for _key in keywords:
        print _key
    #满足要求的keywords
    keys=set([])
    all_key_set = set()  # 包含非节点关键词的集合
    #求的编辑距离
    for keyword in keywords:
        if not if_support(support_words, keyword):
            records=[]
            for word in nodesNames:
                pro=calPro(keyword,word)
                if pro>0.5:
                    records.append((word,pro))

            #排序
        
            records=sorted(records,key=lambda recode:recode[1],reverse=True)
            if len(records)!=0:
                keys.add(records[0][0])
            else:
                all_key_set.add(keyword)
    #如果keys中有，表示识别到节点，若是没有那么就开始找节点内部的信息
    usages=[]
    #找到节点的情况
    if len(keys) != 0:
        usages=getUsage(graph, relnodes, keys, all_key_set)
        return usages
    
    #没有找到节点的情况
    else:
        no_support_words = []  # 不含辅助词的集合
        for keyword in keywords:
            if not if_support(support_words, keyword):
                no_support_words.append(keyword)
        
        #keywords=list(keys)
        #关键字处理,关键字可能得不到我们要的节点
        if len(no_support_words) != 0:
            nodes=getExistNode(graph, relnodes, no_support_words)
            if len(nodes)!=0:
                usages = getUsageAttr(graph, relnodes, nodes, keywords)
            else:
                usages.append("无法找到答案")
            return usages

        else:
            usages.append("无法找到答案")
            return usages

#回答隶属
def ansContent(question):
    #得到节点和关系节点的集合
    graph,relnodes=preData()
    nodesNames=getAllNodes(graph, relnodes)
    #得到关键词语
    keywords=keywordextract.keywordExtract(question)
    for _key in keywords:
        print _key
    #满足要求的keywords
    keys=set([])
    all_key_set = set()  # 包含非节点关键词的集合
    support_words = getSupportWord()
    #求的编辑距离
    for keyword in keywords:
        if not if_support(support_words, keyword):
            records=[]
            for word in nodesNames:
                pro=calPro(keyword,word)
                if pro>0.5:
                    records.append((word,pro))
            #排序
        
            records=sorted(records,key=lambda recode:recode[1],reverse=True)
            if len(records)!=0:
                keys.add(records[0][0])
            else:
                all_key_set.add(keyword)
        
            
    #如果keys中有，表示识别到节点，若是没有那么就开始找节点内部的信息
    length=len(keys)
    contents=[]
    #找到节点的情况
    if length>0:
        for name in keys:
            content=getContent(graph, relnodes, name, all_key_set)
            contents = content
        return contents
    
    #没有找到节点的情况,直接和用法类的问题一样处理
    else:
        return ansUsage(question)

def test():
    #print calPro('整型','整型变量')
    
    #_dict={}
    #_dict['1']=1
    #print _dict.get('0')
    
    _list=ansContent("什么是%d")
    for line in _list:
        print line
    
    
    
if __name__=="__main__":
    test()

