#encoding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import math
import similarity

sys.path.append("..")
from KnowledgeGraph.dealdata import *
from answer_score import *

import keywordextract
import operator
import answer2
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
    
    if node==None and relnode!=None:
        infos=relnode.get_Infos()
        
        for item in infos.items():
            if item[0].find(keyword)!=-1 or item[1].find(keyword)!=-1:
                return str(keyword)+"是"+str(relnode)+"中的概念， 由"+str(relnode)+"的"+str(item[0])+"可知："+str(item[1])
       
    if node!=None and relnode==None:
        infos=node.get_Infos()
        
        for item in infos.items():
            if item[0].find(keyword)!=-1 or item[1].find(keyword)!=-1:
                return str(keyword)+"是"+str(node)+"中的概念， 由"+str(node)+"的"+str(item[0])+"可知："+str(item[1])

#根据名字找到具体的节点，并做出回答,这里是对节点的直接回答
def getDefinition(graph,relnodes,keys,all_key_set):
    definitions = []
    for name in keys:
        node=getNodeByname(name, graph)
        relnode=getRelNodeByname(name,relnodes)
        if node==None and relnode!=None:
            definition=relnode.get_Infos().get(u"定义")
            if str(definition) != "None":
                definitions.append(str(name)+"的定义为："+str(definition))
            else:
                return answer2.getUsage(graph,relnodes,keys,all_key_set)
        if node!=None and relnode==None:
            definition=node.get_Infos().get(u"定义")
            if str(definition) != "None":
                definitions.append(str(name)+"的定义为："+str(definition))
            else:
                return answer2.getUsage(graph,relnodes,keys,all_key_set)
    return definitions
 
    
#回答定义
def ansDef(question):
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
   
    definitions=[]
    #找到节点的情况
    if length>0:
        definitions = getDefinition(graph, relnodes, keys, all_key_set)
        return definitions
    
    #没有找到节点的情况,直接和用法类的问题一样处理
    else:
        return answer2.ansUsage(question)
                    
  
def test():
    #print calPro('整型','整型变量')
    
    #_dict={}
    #_dict['1']=1
    #print _dict.get('0')
    
    _list=ansDef("什么是%d？")
    for line in _list:
        print line
    
    
    
if __name__=="__main__":
    test()

