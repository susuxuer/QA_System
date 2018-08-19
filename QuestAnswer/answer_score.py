#encoding:utf-8

import keywordextract

support_file_path = "../../data/data/support_word" #辅助词路径

#打分的核心功能
def getBestAnswer(answer_list, all_key_set, key_list):     # 根据辅助词和非辅助词，获得价值大的答案
    records = []
    answer = []
    for i in range(0, len(answer_list)):
        keywords = keywordextract.keywordExtract(answer_list[i][1])
        score = 0                                       # 根据权值来选择答案
        for key in all_key_set:
            if key == answer_list[i][0]:
                score = score+3                 # 标志性的词语权值为3,不然为1
            elif key in keywords:
                score = score+1

        tmp_answer = (key_list[i]+"的"+answer_list[i][0],answer_list[i][1])

        records.append((tmp_answer,score))
        
    records = sorted(records,key=lambda recode:recode[1],reverse=True)       # 排序
    max_score = records[0][1]
    for i in range(0, len(records)):
        if records[i][1] == max_score:
            answer_str = records[i][0][0]+"为:"+records[i][0][1]
            answer.append(answer_str)
        else:
            break

    return answer

def getSupportWord():                # 返回辅助词
    support_file = open(support_file_path, "r")
    support_words = (support_file.read()).split("\n")
    support_file.close()
    return support_words


def if_support(support_words, word):    # 判断是否是辅助词
    if word in support_words:
        return True
    return False
