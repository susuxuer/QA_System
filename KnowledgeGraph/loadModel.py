#encoding:utf-8
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')
from nltk.parse.stanford import StanfordDependencyParser
import jieba
#导入jieba的词库
def loadUserDict():
    jieba.load_userdict("../../data/classifydata/userdict.txt")
#导入pynlpir的词库
# def loadPynlpIR():
#     nlpir.Init(nlpir.PACKAGE_DIR, nlpir.UTF8_CODE, None)
#     nlpir.SetPOSmap(nlpir.ICT_POS_MAP_FIRST)
#     nlpir.ImportUserDict(b'../data/classifydata/dict_nlpir.txt')
#得到停用词
def getStops():
    stops = set([])
    with open('../../data/classifydata/stopword', 'r') as ropen:
        result = ropen.readlines()
        for line in result:
            line = str(line.strip())
            if line != '' and line != ' ':
                stops.add(line)
    return list(stops)

#得到节点的同义词表
def getTransfers():
    transfer_file = open("../../data/data/transfer", "r")
    whole_file = transfer_file.read()
    transfer_file.close()
    transfer_lines = whole_file.split("\n")
    transfers = [[] for i in range(len(transfer_lines))]
    for i in range(0, len(transfer_lines)):
        if len(transfer_lines[i]) != 0:
            front = 0
            rear = 0
            block_mk = 0      # 是否有个词语有空格被中括号包起来了
            tmp_word = ""
            for j in range(0, len(transfer_lines[i])):
                if transfer_lines[i][j] == '[':
                    block_mk = 1
                    front = front+1
                elif transfer_lines[i][j] == ']':
                    block_mk = 0
                    rear = j
                elif transfer_lines[i][j] == ' ' and block_mk == 0:
                    tmp_word = transfer_lines[i][front:rear]
                    front = j+1
                    transfers[i].append(tmp_word)
                else:
                    rear = j+1
            transfers[i].append(transfer_lines[i][front:rear])

    return transfers

#导入依赖关系的model
def getDepenParser():
    path_to_jar = '../../data/stanford/stanford-parser.jar'
    path_to_models_jar = '../../data/stanford/stanford-parser-3.5.2-models.jar'
    # path_to_models_jar = '../../data/standord/stanford-chinese-corenlp-2016-01-19-models.jar'
    model_path = '../../data/stanford/chinesePCFG.ser.gz'
    dependency_parser = StanfordDependencyParser(path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar,
                                                 model_path=model_path)

    return dependency_parser


if __name__=="__main__":
    a = getTransfers()
    for b in a:
        for c in b:
            print(c+" ")
        print("\n")

    # loadPynlpIR()
    # _list=pynlpir.segment("你 是谁",pos_tagging=False)
    # for line in _list:
    #     print line