#encoding:utf-8
import sys
import re
import jieba
import loadModel
import auxiliaryFunct
import dealdata
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..")
from QuestAnswer.keywordextract import keywordExtract
from KnowledgeGraph.auxiliaryFunct import *
from QuestAnswer.answer_score import getSupportWord
#建立依赖关系的类
class Word(object):
    name=''
    partOfSpeech=''
    #和这个词相关的所有依赖关系
    depens=[]
    def __init__(self,name):
        self.name=name
        self.partOfSpeech=''
        self.depens=[]
    def addPart(self,part):
        self.partOfSpeech=part
    #添加依赖关系
    def addDepen(self,rel,den):
        self.depens.append((rel,den))

    def getDepen(self):
        return self.depens

    def getPart(self):
        return self.partOfSpeech

    # 表示输出
    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

#将句子处理为单句
#方法比较low，就是将最长的分句来出来
def getSingSen(sentence):
    sentence=re.split(r'[,，]',sentence)
    maxSence=''
    maxlen=0
    for line in sentence:
        line=line.strip()
        if len(line)>maxlen:
            maxlen=len(line)
            maxSence=line
    return str(maxSence)


#将句子分词
def tagSen(sentence):
    str=''
    _list=segment(sentence)
    #_list = pynlpir.segment(sentence,pos_tagging=False)
    for item in _list:
        str+=(item+' ')
    str=str[:-1]
    return str

#得到句子的依赖关系
#输入一个字符串，然后得到这个句子的依赖关系：这个字符串需要分好词
def depenRela(string,dependency_parser):

    #如果报错返回None
    haserror=False
    try:
        result = dependency_parser.raw_parse(string.decode('utf-8','ignore'))
    except UnicodeDecodeError:
        haserror=True
    if not haserror:
        words = {}
        #默认第一个是中心词
        result = result.next()
        try:
            result=list(result.triples())
        except TypeError:
            return None,None
        for line in result:
            print(line[0][0]+" "+line[0][1]+" "+line[1]+" "+line[2][0]+" "+line[2][1])

        for parser in result:
            gov=parser[0]
            rel=parser[1]
            dep=parser[2]
            name=gov[0]
            part=gov[1]

            govWord=getObject(name,words)
            govWord.addPart(part)
            depName=dep[0]
            depPart=dep[1]
            depWord=getObject(depName,words)
            depWord.addPart(depPart)
            govWord.addDepen(rel,depWord)

            words[name]=govWord
            words[depName]=depWord

        if len(result) != 0:
            coreWord=result[0][0][0]
            #返回的是一个核心词和一个词字典
            return coreWord,words
        else:
            return None,None
    #编码出错就返回None
    else:
        return None,None

#给定一个Word节点，然后对此进行扩充，找到相关的nn,dep,det,conj,且它们都不是stop
def findMore(word,extension,stops,supports):
    for depen in word.getDepen():
            if depen[0] == u'det' and str(depen[1]) not in stops and str(depen[1]) not in supports :
                extension.append(str(depen[1]))
            elif depen[0] == u'nn' and str(depen[1]) not in stops and str(depen[1]) not in supports:
                extension.append(str(depen[1]))
            elif depen[0] == u'dep' and str(depen[1]) not in stops and str(depen[1]) not in supports:
                extension.append(str(depen[1]))
            elif depen[0] == u'conj' and str(depen[1]) not in stops and str(depen[1]) not in supports:
                extension.append(str(depen[1]))

#正式处理，对中心词,subj,obj,中心词的限定词，进行扩展
#返回关键词列表
def extendWord(sentence):
    sentence=getSingSen(sentence)
    # print sentence
    tags=tagSen(sentence)
    # print tags
    dependency_parser=loadModel.getDepenParser()
    coreWord, words=depenRela(tags,dependency_parser)
    #如果编码没错就继续，否则知识简单的扩展关键词
    if coreWord!=None:
        #停用词
        stops=loadModel.getStops()
        # 支持词
        supports = getSupportWord()
        #需要进行扩展的节点
        extension=[]
        #得到核心词的节点
        word=getObject(coreWord,words)
        extension.append(str(word))
        #我们首先过滤中心词的所有情况
        #然后考虑如果有nsubj和dobj我们也进行扩展
        nsubj=None
        dobj=None
        for depen in word.getDepen():
            if depen[0]==u'det' and str(depen[1]) not in stops and str(depen[1]) not in supports:
                extension.append(str(depen[1]))
                findMore(depen[1],extension,stops,supports)
            elif depen[0]==u'dep' and str(depen[1]) not in stops and str(depen[1]) not in supports:
                extension.append(str(depen[1]))
                findMore(depen[1], extension, stops,supports)
            elif depen[0]==u'nsubj' and str(depen[1]) not in stops and str(depen[1]) not in supports:
                nsubj=depen[1]
                extension.append(str(depen[1]))
                findMore(depen[1], extension, stops,supports)
            elif depen[0]==u'dobj' and str(depen[1]) not in stops and str(depen[1]) not in supports:
                dobj = depen[1]
                extension.append(str(depen[1]))
                findMore(depen[1], extension, stops,supports)
            elif depen[0]==u'nn' and str(depen[1]) not in stops and str(depen[1]) not in supports:
                extension.append(str(depen[1]))
                findMore(depen[1], extension, stops,supports)


        # for line in extension:
        #     print line
        origin=keywordExtract(sentence)
        set1=set(origin)
        # print 'extension'
        # for item in extension:
        #     print item
        set2=set(extension)
        set3=set1&set2
        # print 'intersection'
        # for item in set3:
        #     print item
        ext=list(set3)

        #接下来就是正式地扩展
        graph, relnodes = dealdata.preData()
        nodes = dealdata.getAllNodes(graph, relnodes)
        result = auxiliaryFunct.changeNodeEx(ext, nodes)
        result.extend(list(set1-set3))
        return result

    #编码出错
    else:

        origin = keywordExtract(sentence)
        ext = set(origin)


        # 接下来就是正式地扩展
        graph, relnodes = dealdata.preData()
        nodes = dealdata.getAllNodes(graph, relnodes)
        result = auxiliaryFunct.changeNodeEx(ext, nodes)

        return result



#根据名字来获取word
def getObject(name,words):
    word=words.get(name,None)
    if word==None:
        return Word(name)
    else:
        return word

def test():
    result=extendWord(u"static和auto有什么区别")
    print '*'*90
    for line in result:
        print line

if __name__=="__main__":
    test()