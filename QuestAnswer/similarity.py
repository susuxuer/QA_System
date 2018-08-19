#coding:utf-8
__author__= '1'
import math
import difflib

def difflib_leven(str1, str2):
    str1=str1.decode('utf-8')
    str2=str2.decode('utf-8')
    leven_cost = 0
    s = difflib.SequenceMatcher(None, str1, str2)
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        #print('{:7} a[{}: {}] --> b[{}: {}] {} --> {}'.format(tag, i1, i2, j1, j2, str1[i1: i2], str2[j1: j2]))

        if tag == 'replace':
            leven_cost += max(i2-i1, j2-j1)
        elif tag == 'insert':
            leven_cost += (j2-j1)
        elif tag == 'delete':
            leven_cost += (i2-i1)
    return leven_cost

class similarity():
    def __init__(self):
        pass
    def levenshtein(self,first,second): #计算编辑距离
        if len(first)== 0:
            return 0.1
        if len(second)== 0:
            return 0.1
        if len(first)>len(second):
            first,second= second,first # 交换两个数
        first_length= math.ceil(len(first)/ 3.0).__int__() # 只判断中文（3个字节），但是防止有英文出现，故除以3取上界
        second_length= math.ceil(len(second)/ 3.0).__int__()
        distance_matrix = [range(second_length) for x in range(first_length)] # 动态规划记录数据的矩阵，无初始值则为0
        for i in range(1,first_length):
            for j in range(1,second_length):
                deletion = distance_matrix[i-1][j] + 1 # 删除操作，距离+1
                insertion = distance_matrix[i][j-1] + 1 # 插入操作，距离+1
                substitution = distance_matrix[i-1][j-1] # 替换操作，即将第二个的词的第i个字与第一个词的第i-1个字
                #汉字是3个字节，所以以3个字节为整体判断
                if first[3*(i- 1): 3* i]!= second[3*(j- 1): 3* j]: #第二个的词的第i个字与第一个词的第i-1个字不相同，则替换+1
                    substitution += 1
                distance_matrix[i][j] = min(insertion,deletion,substitution) # 判断这次对比到底是采取什么操作，取最小值
        temp= distance_matrix[first_length-1][second_length-1]
        # simi= float(0)
        # simi= (second_length-temp)/(second_length.__float__())
        return temp

if __name__== "__main__":
    
    print difflib_leven('整型', '整型变量')
    firstWord= raw_input('input the first word:')
    
    secondWord= raw_input('input the second word:')
    
    length= similarity()
    
    # 计算相似度
    simi= length.levenshtein(firstWord,secondWord)
    print simi
    
    

