# encoding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import math
import similarity

sys.path.append("..")
from KnowledgeGraph.dealdata import *
import answer2
from answer_score import *

import keywordextract
import operator

# 计算编辑距离的概率
def calPro(word1, word2):
    word1 = word1.decode('utf-8')
    word2 = word2.decode('utf-8')
    len1 = len(word1)
    len2 = len(word2)
    len1 = (len1 + len2) / float(2)

    length = similarity.difflib_leven(word1, word2)
    return 1 - length / len1

# 可能是通过节点的内容找到的节点，比如%s,那么它的回答应该是：节点的定义+节点的该属性
def getDefiniAttr(graph, relnodes, name, keyword):
    node = getNodeByname(name, graph)
    # getInfoFromNode(name)
    relnode = getRelNodeByname(name, relnodes)

    print node,keyword
    
    if node == None and relnode != None:
        infos = relnode.get_Infos()

        for item in infos.items():
            if item[0].find(keyword) != -1 or item[1].find(keyword) != -1:
                return str(keyword) + "是" + str(relnode) + "中的概念， 由" + str(relnode) + "的" + str(item[0]) + "可知：" + str(
                    item[1])

    if node != None and relnode == None:
        infos = node.get_Infos()

        for item in infos.items():
            if item[0].find(keyword) != -1 or item[1].find(keyword) != -1:
                return str(keyword) + "是" + str(node) + "中的概念， 由" + str(node) + "的" + str(item[0]) + "可知：" + str(
                    item[1])

# 根据所给出的节点回答出比较的情况
def getComparison(graph, relnodes, name, keywords):
    name=unicode(name)
    node = getNodeByname(name, graph)
    # getInfoFromNode(name)
    relnode = getRelNodeByname(name, relnodes)

    comparisions = ''
    if node == None and relnode != None:
        infos = relnode.get_Infos()

        #将各个非节点关键字出现的属性找出来。
        for item in infos.items():
            for keyword in keywords:
                if item[0].find(keyword) != -1 or item[1].find(keyword) != -1:
                    comparisions+="从"+str(relnode)+"的"+item[0]+"可以判断出"+item[1]+"\n"
                    break

    if node != None and relnode == None:
        infos = node.get_Infos()

        # 将各个非节点关键字出现的属性找出来。
        for item in infos.items():
            for keyword in keywords:
                if item[0].find(keyword) != -1 or item[1].find(keyword) != -1:
                    comparisions += "从" + str(node) + "的" + item[0] + "可以判断出" + item[1] + "\n"
                    break
    return comparisions
#回答比较和区别的关系
def getRelations(node,others):
  
    comparisions=''
    rels=node.get_Rela()
    for item in rels:
        if str(item[1]) in others and (str(item[0])==u'比较'):
            relnode=item[0]
            infos=relnode.get_Infos()
            keys=infos.keys()
            if u'1' in keys:
                comparisions+=str(node)+'和'+str(item[1])+'的比较如下：\n'+infos.get(u'1')+'\n'
            else:
                
                comparisions += str(node) + '和' + str(item[1]) + '的比较如下：\n'
                for key in keys:
                     comparisions+='它们的'+key+"是"+infos.get(key)+ '\n'
    return comparisions
#给出所有的节点，回答出它们有相同的属性
#这种情况下，一般是（最差是）可以回答到彼此的定义的
def getCommAttr(nodes):
    interSet = set(nodes[0].get_Infos().keys())
    for j in xrange(1,len(nodes)):
        node=nodes[j]
        curset = set(node.get_Infos().keys())
        if len(curset) != 0:
            interSet &= curset
    comp = ''
    #如果有公共属性，现在将它们全部拿出来
    if len(interSet)!=0:

        for attr in interSet:
            comparison = '它们的' +attr+'不同：\n'
            for node in nodes:
                comparison+=str(node)+'的'+attr+'是'+node.get_Infos().get(attr)+'\n'
            comp+=comparison
    return comp

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

# 回答比较
def ansComp(question):
    # 得到节点和关系节点的集合
    graph, relnodes = preData()
    nodesNames = getAllNodes(graph, relnodes)
    # 得到关键词语
    keywords = keywordextract.keywordExtract(question)
    # keywords=['%s','%d']
    for _key in keywords:
        print _key
    # 满足要求的keywords
    keys = set([])
    all_key_set = set()  # 包含非节点关键词的集合
    support_words = getSupportWord()
    #求的编辑距离
    for keyword in keywords:
        if not if_support(support_words, keyword):         
            records = []  
            
            for word in nodesNames:
                pro = calPro(keyword, word)
                if pro > 0.5:
                    records.append((word, pro))
            # 排序
            records=sorted(records, key=lambda recode: recode[1], reverse=True)
            if len(records)!=0:
                keys.add(records[0][0])
            else:
                all_key_set.add(keyword)

    comparision=[]
    #都是非节点关键字的时候，比如%d%s做出比较
    if len(keys)==0:
        #准备一个交集
        interSet=set(getMaxNode(graph,relnodes,keywords[0]))

        for j in xrange(1,len(keywords)):
            key=keywords[j]
            curset=set(getMaxNode(graph,relnodes,key))
            if len(curset)!=0:
                interSet &=curset

        #如果多个非节点关键字对应一个共同的节点，那么就得出该节点
        if len(interSet)!=0:
            node=list(interSet)[0]
            comparision.append("它们都是"+str(node)+"中的概念。"+getComparison(graph,relnodes,str(node),keywords))
        else:
            for key in keywords:
                node=getMaxNode(graph,relnodes,key)
                if len(node)!=0:
                    node=node[0]
                    
                    comparision.append(getDefiniAttr(graph,relnodes,unicode(node),key))

        return comparision
    #都是节点关键字的情况（这里希望拿到两个节点，但是可能会有更多）
    elif len(keys)!=0:
        #首先判断它们有直接的关系吗
        length=len(keys)
        keys=list(keys)
        for i in xrange(length):
            node=getNodeByname(keys[0],graph)
            relsAndNodes=node.get_Rela()
            adjoints=set([str(item[1]) for item in relsAndNodes])
            others=set([str(keys[j]) for j in xrange(i+1,length)])
            
            others&=adjoints
            comparision.append(getRelations(node,others))
        if len(comparision)!=comparision.count(''):
            return comparision
        #下面是考虑没有直接关系的情况，需要考虑到它们的父亲节点
        else:
            #可能有''，所以删除它们，
            comparision=filter(lambda i:i!='',comparision)
            #先查看节点是否有公共的父亲节点
            
            #所有节点
            nodes=[]
            for item in keys:
                node=getNodeByname(item,graph)
                if len(node.get_Parents())!=0:
                    nodes.append(node)
            interSet=set(nodes[0].get_Parents())        
            for j in xrange(1,len(nodes)):
                node=nodes[j]
                interSet&=set(node.get_Parents())
            
            #如果有公共的父节点
            if len(interSet)!=0:
                #目前这里只考虑一种一个父节点的情况
                parent=list(interSet)[0]
                strs='它们都是'+str(parent)+"中的概念。"
                strs+=getCommAttr(nodes)
                comparision.append(strs)
                return comparision
            #没有公共节点,那么就回答各自的定义
            else:
                comparision = getDefinition(graph,relnodes,keys,all_key_set)
                return comparision





def test():
    # print calPro('整型','整型变量')

    # _dict={}
    # _dict['1']=1
    # print _dict.get('0')

    _list = ansComp("字符指针和字符数组")
    for line in _list:
        print line


if __name__ == "__main__":
    test()

