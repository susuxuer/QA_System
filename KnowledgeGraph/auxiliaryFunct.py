#encoding:utf-8
import sys
import os
import jieba
import operator
import math
import jieba.posseg as seg
import re
reload(sys)
sys.setdefaultencoding('utf-8')

#同义词林
class item:
    def __init__(self):
        self.name= "" # 存词
        self.list= [] # 存词所在的层数

#导入同义词词林hgdTest.txt文件
def loadData():
    file_object= open("../../data/data/hgdTest.txt", "r")
    allLines= file_object.readlines()
    file_object.close()
    itemList= []
    itemListIndex= []
    for line in allLines:
        wordList= line.split()
        temp= item()
        for i in range(0,wordList.__len__()):
            if i== 0:
                temp.name= wordList[i]
                itemListIndex.append(wordList[i])
            else:
                temp.list.append(wordList[i])
        itemList.append(temp)
    itemSet= set(itemListIndex)
    #itemList是item的列表，itemListIndex是名字的列表，itemset是名字的集合
    List= [itemList,itemListIndex,itemSet]
    return List

#求两个词的相似性，主要是依赖同义词词林的5层结构
def newSynSimilarity(word1,word2):

    list1=[word1[0],word1[1],word1[2:4],word1[4],word1[5]+word1[6]]
    list2=[word2[0],word2[1],word2[2:4],word2[4],word2[5]+word2[6]]
    count=0
    for i in range(5):
        if list1[i]==list2[i]:
            count+=1
        else:
            break
    if count==4:
        count=5
    return float(count)/5

#最后一个List就是导入的同义词词林的数据情况
def newSynSimi(word1,word2,List):
    if word1== word2:
        return 1.0
    firstList= []
    secondList= []
    boolFirst= False
    boolSecond= False
    itemList= List[0]
    itemListIndex= List[1]
    itemSet= List[2]

    if word1 in itemSet:
        p= itemListIndex.index(word1)
        firstList= itemList[p].list
        boolFirst= True
    if word2 in itemSet:
        p= itemListIndex.index(word2)
        secondList= itemList[p].list
        boolSecond= True
    if boolFirst== False or boolSecond== False:
        return 0.1
    else:
        max= 0.1
        for mark1 in firstList:
            for mark2 in secondList:
                simi= newSynSimilarity(mark1,mark2)
                if simi > max:
                    max= simi
        return max


#给定一个非辅助关键词，返回一个列表的相关性
#比如给定‘意思’=》[意思，概念，定义]
def getCorela(word,graph,relnodes):

    #得到所有的属性词

    attrs=set([])
    for node in graph.values():
        attrs.update(node.get_Infos().keys())

    for relnode in relnodes.values():
        attrs.update(relnode.get_Infos().keys())
    #另外添加几个词语
    # attrs.add(u'不同')
    # attrs.add(u'区别')
    # attrs.add(u'相同点')
    # attrs.add(u'比较')
    # attrs.add(u'关系')
    _list = loadData()

    # print '*'*90
    # for item in attrs:
    #     print item

    # print '*' * 90

    candidate=[]
    for item in attrs:
        item=str(item.strip())
        if newSynSimi(str(word),item,_list)>0.5:
            candidate.append(item)
    #将word也插入进来，放在了第一位
    candidate.insert(0,word)
    return candidate

#修改词库
def modifDict(path):
    _list=[]
    with open(path,'r') as ropen:
        result=ropen.readlines()
        for item in result:
            item=item.replace('\n','')
            _list.append(item)
    _result=[]
    #添加 n
    for item in _list:
        item+=' '
        item+='n'
        _result.append(item)

    return _result

#将list输入为文档的形式

def output(list,path):
    with open(path,'w') as wopen:
        content=''
        for line in list:
            content+=line+'\n'
            #content+=line
        wopen.writelines(content)





#抽取5000文档中的问句
def extractDocs():
    allQues=[]
    dir='/home/suxiaoheng517/output/'
    for name in os.listdir(dir):
        file_name=dir+name;
        with open(file_name,'r') as ropen:
            result=ropen.readlines()
            allQues.append(result[1].replace('\n',''))
    output(allQues,'../../data/classifydata/all_ques.txt')

#对这个文档进行分词，然后提取出频率最高的词语，作为候选停用词
#得到领域的高频词
def getDomainStops(path):
    #存放最终的结果
    count={}
    jieba.load_userdict("../../data/classifydata/userdict.txt")
    #加入已有的通俗的听用词
    stops=set([])
    with open('../../data/classifydata/stopword','r') as ropen:
        result=ropen.readlines()
        for line in result:
            line=str(line.strip())
            stops.add(line)

    result=[]
    punct =set(['；',';',',','，','.','。','?','？','!','！','(','（',')','）','{','{','}','}','/','',' '])
    with open(path,'r') as ropen:
        result=ropen.readlines()
    for line in result:
        line=jieba.cut(line)
        for item in line:
            item=str(item.strip())
            if item not in punct and item not in stops:
                count[item]=count.get(item,0)+1
    #讲count排一下序,那么返回的就是一个列表啦
    count=sorted(count.iteritems(),key=operator.itemgetter(1),reverse=True)
    #现在只返回大于阈值的词语
    words=[line[0] for line in count if line[1]>=50]
    #然后计算这些词的信息熵
    entro={}
    for word in words:
        res=countEntro(word,result)
        entro[word]=res

    return entro

#计算每个词语的信息熵
#主要是论文中的三个公式,第一个参数是一个要查询的词，第二个是所有的文档
def countEntro(word,result):
    punct = set(
        ['；', ';', ',', '，', '.', '。', '?', '？', '!', '！', '(', '（', ')', '）', '{', '{', '}', '}', '/', '', ' '])
    sum=float(0)
    for line in result:
        line=jieba.cut(line)
        _line=[]
        for item in line:
            if item not in punct:
                item=str(item.strip())
                _line.append(item)
        num=float(_line.count(word))
        pro=num/len(_line)
        if pro==0:
            qw=0
        else:
            qw=pro*math.log(pro)
        sum+=qw

    final=1+(1/(math.log(5000)))*sum
    return final

#每个节点的一个属性作为一个文档
#用一行输出
def getDocu(graph,relnodes):
    _list=[]
    for node in graph.values():
        infos=node.get_Infos()
        for info in infos.items():
            _list.append(str(node)+'的'+info[0]+'为'+info[1])
    for node in relnodes.values():
        infos = node.get_Infos()
        for info in infos.items():
            _list.append(str(node) + '的' + info[0] + '为' + info[1])
    output(_list,'../../data/classifydata/all_doc')
    return _list

#得到support的值
def getSupport(_list):
    count = {}
    jieba.load_userdict("../../data/classifydata/userdict.txt")
    #添加userdict中的词
    user_dict=[]
    with open('../../data/classifydata/userdict.txt', 'r') as ropen:
        result = ropen.readlines()
        for line in result:
            line = str(line.strip()).split()[0].strip()
            user_dict.append(line)
    # 加入已有的通俗的停用词
    stops = set([])
    with open('../../data/classifydata/stopword', 'r') as ropen:
        result = ropen.readlines()
        for line in result:
            line = str(line.strip())
            stops.add(line)


    punct = set(
        ['；', ';', ',', '，', '.', '。', '?', '？', '!', '！', '(', '（', ')', '）', '{', '{', '}', '}', '/', '', ' '])

    for line in _list:
        line = seg.cut(line)
        line=[item.word for item in line if item.flag=='n']
        for item in line:
            item = str(item.strip())
            if item not in punct and item not in stops and item not in user_dict:
                count[item] = count.get(item, 0) + 1
    count = sorted(count.iteritems(), key=operator.itemgetter(1), reverse=True)
    #下面是来计算熵
    words = [line[0] for line in count if line[1] >= 5]
    # 然后计算这些词的信息熵
    entro = {}
    for word in words:
        res = countEntro(word, _list)
        entro[word] = res

    entro=sorted(entro.iteritems(),key=operator.itemgetter(1),reverse=True)
    return entro

#检查是否为其中的
def check(word,_list):
    word = unicode(word)
    if word in _list:
        return word,True
    for item in _list:
        if word in item:
            return item,True
    return word,False

#修改关键词，尽量让其变成我们的节点中的词
def changeNode(iniWords,allNode):
    result=[]
    for word in iniWords:
        result1=check(word,allNode)
        if result1[1]==True:
            result.append(result1[0])
        else:
            match=False
            for comp in allNode:

                word=unicode(word)
                comp = unicode(comp)

                set1=set(unicode(word))
                set2=set(unicode(comp))

                length=len(set1)-1
                set1&=set2

                if len(set1)>length:
                    result.append(comp)
                    match=True
                    break
            if match==False:
                result.append(word)

    return result

#词典去重
def removeDup(path,outpath):
    _set=set([])
    with open(path, 'r') as ropen:
        results = ropen.readlines()
        for line in results:
            line=line.strip().replace('\n','')
            if line.strip() != '' and  line!=' ':
                _set.add(line)
    strs=''
    for line in _set:
        strs+=line+' key\n'
    #print strs
    with open(outpath,'w') as wopen:
        wopen.writelines(strs)


#这里重写写一个jieba分词，主要是用来处理%d之类的情况
#目前还没有包含词性
def segment(sentence):
    sens=jieba.cut(sentence)
    _list=[]
    for word in sens:
        _list.append(word)

    length=len(_list)
    result=[]
    specil=['x','X','e','E','s','S','l','L','d','D','o','O','u','U','f','F','g','G','e','E','=']
    i=0
    mark=False
    while(i<length-1):

        char=_list[i]
        if char=='%' and _list[i+1] in specil:
            result.append(char+_list[i+1])
            if i==length-2:
                mark=True
            i += 2
        else:
            result.append(char)
            i+=1
    if mark==False:
        result.append(_list[-1])

    return result

#给一个字符串，将其中的所有含有字母的都转换为小写字母
def switchWord(word):
    newWord=''
    length=len(word)
    i=0

    while i<length:
        char=word[i]
        if char.isalpha() and char.isupper():
            char=char.lower()
        newWord+=char

        i+=1
    return newWord

#为了解决大小写的问题，这里对changeNode进行包装
#下面是扩充版本
def changeNodeEx(iniWords,allNode):
    #转换
    switchWords=[]
    for word in iniWords:
        switchWords.append(switchWord(word))

    #用一个nodes集合表示转换后的nodes
    switchNodes=[]
    for word in allNode:
        switchNodes.append(switchWord(word))
    #这里显示的是最新的转换后的节点
    modify=changeNode(switchWords,switchNodes)
    #找出变换的节点，然后还原倒allNode的节点关键字
    length=len(iniWords)
    i=0
    while i<length:
        if modify[i]!=switchWords[i]:
            changWord=modify[i]
            index=switchNodes.index(changWord)
            modify[i]=allNode[index]
        i+=1
    return modify



def test():
    _list=loadData()
    print newSynSimi('不同','不同之处',_list)

    # _list=modifDict('../../data/classifydata/test')
    # output(_list,'../../data/classifydata/userdict1.txt')

    # extractDocs()

    # _list=getDomainStops('../../data/classifydata/all_ques.txt')
    # for line in _list.items():
    #     print line[0],'---',line[1]

    #removeDup('../../data/classifydata/dict_nlpir.txt','../../data/classifydata/dict_nlpir1.txt')

    # _list=segment('指针和数组有什么不同之处')
    # for line in _list:
    #     print line

    # print switchWord('abDSrFF你好')


if __name__=="__main__":
    test()

    print 'success'

