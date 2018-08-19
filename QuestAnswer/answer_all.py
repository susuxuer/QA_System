#encoding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import math
import similarity
sys.path.append("..")
from KnowledgeGraph.loadModel import *
from KnowledgeGraph.dealdata import *
from KnowledgeGraph.auxiliaryFunct import *
from answer_score import *

import KnowledgeGraph.extractTopic as topic
import keywordextract
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

#当找不到节点的attribution内容时，做出的回答
def getInfoNotAttr(node):
    parents=node.get_Parents()
    children=node.get_Inheri()
    strs=''
    if len(parents)!=0:
        strs += str(node)+'是'
        for par in parents:
            strs += str(par) + ','
        strs = strs[:-1]
        strs += '中的子概念。'
    if len(children)!=0:
        if(len(parents)!=0):
            strs+='它也含有'
        else:
            strs+=str(node)+'含有'
        for child in children:
            strs += str(child) + ','
        strs = strs[:-1]
        strs+='等子概念。'
    strs+='如果没有找到您满意的答案，请询问相关的概念。'
    return strs


#根据名字找到具体的节点，返回所有info
def getUsage(graph,relnodes,keys,all_key_set):     # keys：节点关键词组成的list，all_key_set：非节点关键词(除了节点,停用词，支持词后的所有的词)组成的list
    answer = []
    answer_list = []   # 保存所有可能回答的数组
    key_list = []      # 方便返回答案，将节点名存入数组
    # 增加一个nodes列表是为了回答该节点没有信息的情况
    nodes = []
    for name in keys:

        node=getNodeByname(name, graph)
        relnode=getRelNodeByname(name,relnodes)
        usage = {}
        if node==None and relnode!=None:
            usage=relnode.get_Infos()
        elif node!=None and relnode==None:
            usage=node.get_Infos()
            nodes.append(node)

        for item in usage.items():
            if item[1] != '':
                answer_list.append(item)
                key_list.append(name)
    
    
    if len(answer_list) == 0:
        #这里需要对node进行转化，它可能就不是节点
        newNodes=[]
        for node in nodes:
            node=transfer(str(node))
            newNodes.append(getNodeByname(unicode(node), graph))
        nodes=newNodes
        if len(nodes)!=0:
            strs=''
            for node in nodes:
                strs+=getInfoNotAttr(node)+'\n'
            answer.append(strs)
        else:
            answer.append("能力有限，暂时还回答不了")

    else:
        #这一步就是将我们的辅助词进行扩展，主要使用同义词林来扩展
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

#也许所有关键词都不是节点，则用非节点词查到的节点查找答案
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
        answer.append("能力有限，暂时还回答不了")
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
            answer.append("能力有限，暂时还回答不了")

    return answer

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
                return getUsage(graph,relnodes,keys,all_key_set)
        if node!=None and relnode==None:
            definition=node.get_Infos().get(u"定义")
            if str(definition) != "None":
                definitions.append(str(name)+"的定义为："+str(definition))
            else:
                return getUsage(graph,relnodes,keys,all_key_set)
    return definitions

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


#直接回答相同点（在nor_rel）中作答
#参数为一个节点node和剩下的相关节点集合
def getSamePoints(node,nodes,graph):
    answer=''
    nodeRel=node.get_Rela()
    for item in nodeRel:
        _node=str(item[1])
        if _node in nodes:

            rela=item[0]
            if str(rela)=='比较':
                infos=rela.get_Infos().items()
                for ele in infos:
                    if str(ele[0])=='相同点':
                        answer+=str(node)+'和'+str(_node)+'的相同点为：'+ele[1]+'\n'
                        break

    return answer

#得到不同点
#参数同上
def getDifPoints(node, nodes,graph):
    answer = ''
    nodeRel = node.get_Rela()
    for item in nodeRel:
        _node = item[1]
        if str(_node) in nodes:

            rela = item[0]
            if str(rela) == '比较':
                infos = rela.get_Infos().items()
                for ele in infos:
                    if str(ele[0]) == '区别':
                        answer += str(node) + '和' + str(_node) + '的不同点为：' + ele[1] + '\n'
                        break

    return answer

#得到直接的关系，即不是问比较，而是具体问它们之间有什么关系
def getRela(node, nodes,graph):
    answer = ''
    nodeRel = node.get_Rela()
    for item in nodeRel:
        _node = str(item[1])
        if _node in nodes:

            rela = item[0]
            if str(rela) != '比较':
                answer+=str(node)+'和'+str(_node)+'存在'+str(rela)+'的关系。'
                infos = rela.get_Infos().items()
                for ele in infos:
                    answer+=str(rela)+'的'+ele[0]+'为'+ele[1]+';'
                answer=answer[:-1]+'\n'

    return answer





#回答比较和区别的关系
#这里做出修改，如果他们之间有关系，我们也做出相应的回答，就是在回答比较和区别之后，补充回答它们之间的关系
#node是当前节点，others是该问题中与node中的所有rel中的有关系的节点的名词，它们是交集
def getRelations(node,others):
  
    comparisions=''
    rels=node.get_Rela()
    #hasComp表示有比较的属性
    hasComp=False
    for item in rels:
        if str(item[1]) in others and (str(item[0])==u'比较'):
            hasComp=True
            relnode=item[0]
            infos=relnode.get_Infos()
            keys=infos.keys()
            if u'1' in keys:
                comparisions+=str(node)+'和'+str(item[1])+'的比较如下：\n'+infos.get(u'1')+'\n'
            else:
                
                comparisions += str(node) + '和' + str(item[1]) + '的比较如下：\n'
                for key in keys:
                     comparisions+='它们的'+key+"是"+infos.get(key)+ '\n'
    #现在补充回答它们的直接关系

    for item in rels:
        strs = ''
        if hasComp:
            strs+='此外，'

        if str(item[1]) in others and (str(item[0])!=u'比较'):
            strs+=str(node)+'与'+str(item[1])+'有'+str(item[0])+'的关系，'
            relnode=item[0]
            infos=relnode.get_Infos().items()
            for info in infos:
                strs+='它的'+info[0] +'是'+info[1]+';'
            strs=strs[:-1]
    comparisions+='\n'+strs

    return comparisions


#根据名字找到具体的节点，有子节点返回所有子节点，否则返回所有info
def getContent(graph,relnodes,keys,all_key_set):
    contents = []
    key_list = list(keys)
    for name in keys:
        node=getNodeByname(name, graph)
        #getInfoFromNode(name)
        if node!=None:
            contents.append(node.get_Inheri())

    if len(contents) > 0:
        answers = []
        for i in range(0, len(contents)):
            if len(contents[i]) > 1:
                answer = str(key_list[i])+"由 "
                for j in range(0,len(contents[i])):
                    answer = answer+contents[i][j].name
                    if j == len(contents[i])-2:      # 倒数第二个的特殊情况
                        answer = answer+"和"
                    elif j < len(contents[i])-2:
                        answer = answer+","
                    else:
                        answer = answer+" 所组成\n"
                answers.append(answer)

        if len(answers) != 0:
            return answers
        else:
            return getUsage(graph,relnodes,keys,all_key_set)
    else:
        return getUsage(graph,relnodes,keys,all_key_set)  # 如果子节点少于2个，直接当用法问题解决

def editDist(keywords, nodesNames):       # 根据关键词与节点的编辑距离排序，返回节点关键词和非节点关键词的集合
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
        else:
            all_key_set.add(keyword)
    return keys, all_key_set

#这里补充一个transfer函数，就是给定一个函数，查看是否可以转化为我们给定的节点
#若不能则按原来的样子返回
def transfer(keyword):
        new_keywords=[]
        transfer_list = getTransfers()
        mk = 0  # 一个标记，判断关键词是否和同义词匹配
        for transfers in transfer_list:
            for i in range(1, len(transfers)):
                if transfers[i] == keyword:  # 和同义词相同，变成对应的节点词
                    new_keywords.append(transfers[0])
                    mk = 1
                    break
            if mk == 1:
                break
        if mk == 0:
            new_keywords.append(keyword)
        return new_keywords[0]

def getKeySet(keywords, nodesNames, question):         # 获得节点关键词的集合，与非节点关键词的集合，都不含辅助词
    keys, all_key_set = editDist(keywords, nodesNames)

    #这里就是时候没有关键节点
    if len(keys) == 0:                                 # 如果找不到节点，就通过节点的同义词尝试拓展
        transfer_list = getTransfers()
        new_keywords = set()
        for keyword in keywords:
            mk = 0                                     # 一个标记，判断关键词是否和同义词匹配
            for transfers in transfer_list:
                for i in range(1, len(transfers)):
                    if transfers[i] == keyword:        # 和同义词相同，变成对应的节点词
                        new_keywords.add(transfers[0])
                        mk = 1
                        break
                if mk == 1:
                    break
            if mk == 0:
                new_keywords.add(keyword)

        keys, all_key_set = editDist(new_keywords, nodesNames)
        #就是扩展后还是找不到关键词，那么就找中心词扩展
        if len(keys) == 0:                             # 如果还是找不到，将中心词拓展，再重新处理一遍
            new_keywords = topic.extendWord(unicode(question))  
            keys, all_key_set = editDist(new_keywords, nodesNames)
    return keys, all_key_set

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
        print(_key.encode("utf-8"))
    #满足要求的keywords
    
    keys, all_key_set = getKeySet(keywords, nodesNames, question) # 获得节点关键词的集合，与非节点关键词的集合，都不含辅助词

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
                usages.append("能力有限，暂时还回答不了")
            return usages

        else:
            usages.append("能力有限，暂时还回答不了")
            return usages

#回答定义
def ansDef(question):
    #得到节点和关系节点的集合
    graph,relnodes=preData()
    nodesNames=getAllNodes(graph, relnodes)
    #得到关键词语
    keywords=keywordextract.keywordExtract(question)
    for keyword in keywords:
        print(keyword.encode("utf-8"))
    #满足要求的keywords
    keys, all_key_set = getKeySet(keywords, nodesNames, question) # 获得节点关键词的集合，与非节点关键词的集合，都不含辅助词
    #如果keys中有，表示识别到节点，若是没有那么就开始找节点内部的信息
    length=len(keys)
   
    definitions=[]
    #找到节点的情况
    if length>0:
        definitions = getDefinition(graph, relnodes, keys, all_key_set)
        return definitions
    
    #没有找到节点的情况,直接和用法类的问题一样处理
    else:
        return ansUsage(question)
                    

# 回答比较
#这里将比较又划分为：相同点，不同点(区别)，比较，关系
def ansComp(question):
    # 得到节点和关系节点的集合
    graph, relnodes = preData()
    nodesNames = getAllNodes(graph, relnodes)
    # 得到关键词语
    keywords = keywordextract.keywordExtract(question)


    keys, all_key_set = getKeySet(keywords, nodesNames, question) # 获得节点关键词的集合，与非节点关键词的集合，都不含辅助词

    # #在回答比较的时候，现在为非节点支持词进行同义词词林扩展，主要是找到“区别”，“相同点”，“比较”，“关系”等词
    # extend=[]
    #
    # for word in all_key_set:
    #     extend.extend(getCorela(word,graph,relnodes))
    # 先初始化：“区别”，“相同点”，“比较”，“关系”都为false
    # 0001 0010 0100 1000
    mark = 0
    if u'区别' in all_key_set:
        mark = 1
    elif u'相同点' in all_key_set:
        mark = 2
    elif u'比较' in all_key_set:
        mark = 4
    elif u'关系' in all_key_set:
        mark = 8

    for item in keys:
        print(item)
    print '*********************'
    for item in all_key_set:
        print(item)

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
    #在这里我们开始讨论节点关键字，然后修改为将相同点和非相同点区别开来回答。
    elif len(keys)!=0:


        #首先判断它们有直接的关系吗,即是否为nor_rel中的相关节点
        #若有，然后直接看是否可以找到相同点，区别，比较，关系的作答
        length=len(keys)
        #如果不关键词的长度不超过2，就不能进行比较
        if length<2:

            comparision = getDefinition(graph, relnodes, keys, all_key_set)
            comparision.insert(0,'对不起，我只找到了一个概念，您可以说的我更加懂你。')
            return comparision
        else:
            keys=list(keys)
            for i in xrange(length):
                node=getNodeByname(unicode(keys[i]),graph)
                if node == None:
                    continue

                relsAndNodes=node.get_Rela()
                adjoints=set([str(item[1]) for item in relsAndNodes])
                others=set([str(keys[j]) for j in xrange(i+1,length)])

                others&=adjoints

                if mark==1:
                    comparision.append(getDifPoints(node,others,graph))
                elif mark==2:
                    comparision.append(getSamePoints(node, others,graph))
                elif mark==4:
                    comparision.append(getSamePoints(node, others,graph))
                    comparision.append(getDifPoints(node, others,graph))

                elif mark==8:
                    comparision.append(getRela(node,others,graph))


            if len(comparision)!=comparision.count(''):
                return comparision
            #下面是考虑没有直接关系的情况,即不能直接作答，需要考虑到它们的父亲节点
            else:
                #可能有''，所以删除它们，
                comparision=filter(lambda i:i!='',comparision)
                #先查看节点是否有公共的父亲节点

                #所有节点
                nodes=[]
                for item in keys:
                    item=transfer(item)
                    node=getNodeByname(unicode(item),graph)
                    if node == None:
                        continue
                    if len(node.get_Parents())!=0:
                        nodes.append(node)
                interSet=set(nodes[0].get_Parents())
                for j in xrange(1,len(nodes)):
                    node=nodes[j]
                    interSet&=set(node.get_Parents())

                #注意从这里开始并没有将相同点，区别和比较进行划分
                #如果有公共的父节点,然后回答
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



#回答隶属
def ansContent(question):
    #得到节点和关系节点的集合
    graph,relnodes=preData()
    nodesNames=getAllNodes(graph, relnodes)
    #得到关键词语
    keywords=keywordextract.keywordExtract(question)
    for _key in keywords:
        print(_key.encode("utf-8"))
    #满足要求的keywords

    keys, all_key_set = getKeySet(keywords, nodesNames, question) # 获得节点关键词的集合，与非节点关键词的集合，都不含辅助词
            
    #如果keys中有，表示识别到节点，若是没有那么就开始找节点内部的信息
    length=len(keys)
    contents=[]
    #找到节点的情况
    if length>0:
        contents=getContent(graph, relnodes, keys, all_key_set)
        return contents
    
    #没有找到节点的情况,直接和用法类的问题一样处理
    else:
        return ansUsage(question)

def test():
    #print calPro('整型','整型变量')
    
    #_dict={}
    #_dict['1']=1
    #print _dict.get('0')
    #loadPynlpIR()
    loadUserDict()
    #_list=ansDef("C语言怎么用？")
    _list = ansComp("指针数组和数组有什么比较。")
    for line in _list:
        print line
    
    
    
if __name__=="__main__":
    test()

