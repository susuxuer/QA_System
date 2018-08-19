#encoding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import operator
import auxiliaryFunct
class Node(object):
    name=''
    #表示继承关系的节点列表
    Inheri_List=[]
    #表示父节点的信息
    Parents_List=[]
    #表示有关系的节点列表，主要存放RelNode
    Rel_List=[]
    #表示节点的基本信息

    info={}
    def __init__(self,name):
        self.name=name
        self.Inheri_List=[]
        self.Parents_List=[]
        self.Rel_List=[]
        self.info={}
    #添加节点的信息
    def add_Info(self,name,info):
        self.info[name]=info
    #添加节点的信息,参数式一个列表的形式
    def add_Infos(self,contents):
        for line in contents:
            start=line.find(':')
            self.info[line[:start].strip()]=line[start+1:].strip()
    #添加继承关系的节点
    def add_Inheri(self,node):
        
        self.Inheri_List.append(node)

    # 添加父节点
    def add_Parents(self, node):
        self.Parents_List.append(node)
    #添加有关系的节点
    def add_Rela(self,rel,node):
        self.Rel_List.append((rel,node))
    #查看继承信息
    def get_Inheri(self):
        return self.Inheri_List

    # 查看父节点
    def get_Parents(self):
        return self.Parents_List
    #查看关系信息
    def get_Rela(self):
        return self.Rel_List
    #查看属性
    def get_Infos(self):
        return self.info
    #表示输出
    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name
    #判断节点是否相等
    def __hash__(self):
        return hash(self.name)
    def __eq__(self,other):
        if isinstance(other,Node):
            return self.name==other.name
        else:
            return False
    #查找某个关键字在这个节点出现的总次数
    def count(self,keyname):
        _count=0
        
        #查看基本信息
        attribution=self.info
        for line in attribution.items():
            count0=line[0].count(keyname)
            count1=line[1].count(keyname)
            _count+=(count0+count1)
        return _count
    

#表示关系的节点
class RelNode(object):
    #两个元素：关系名，关系的介绍（用字典表示）
    
    relName=''
    relProfile={}
    def __init__(self,name):
            self.relName=name
            self.relProfile={}
    def add_Info(self,name,info):
        self.relProfile[name]=info
    def add_Infos(self,contents):
            for line in contents:
                start=line.find(':')
                self.relProfile[line[:start].strip()]=line[start+1:].strip()    
    def get_Infos(self):
        return self.relProfile
    
    def __repr__(self):
            return self.relName
    def __str__(self):
        return self.relName    
    #查找某个关键字在这个关系节点出现的总次数
    def count(self,keyname):
        _count=0
        
        #查看基本信息
        attribution=self.relProfile
        for line in attribution.items():
            count0=line[0].count(keyname)
            count1=line[1].count(keyname)
            _count+=(count0+count1)    
    

#准备数据，遍历文档，填充上面的信
#返回图的节点信息，关系节点信息
def preData():
    graph={}
    RelNodes={}
    #获取所有节点的继承关系
    
    _list=loadFile('../../data/data/con_in')
    for line in _list:
        line=line.strip()
        #line=re.split(r'\s+',line)
        #first_node=get_Object(graph,line[0].strip())
        #second_node=get_Object(graph,line[1].strip())
        index=line.find(' ')
        first_node=get_Object(graph,line[:index].strip())
        second_node=get_Object(graph,line[index+1:].strip())
        first_node.add_Inheri(second_node)
        second_node.add_Parents(first_node)
    #测试
    #for key in graph.keys():
        #_list=graph[key].get_Inheri()
        #for line in _list:
            #print key,'---',line
            
    #获取所有节点之间的正常关系
    _list=loadFile('../../data/data/nor_rel')
    for p in xrange(len(_list)):
        line=_list[p].strip()
        _list.append(line)
    #     print line
    # print len(_list)
    #这里有一个bug不知道为什么会读两遍，内容是一边的内容，但是长度却是2倍
    i=0
    while i<len(_list)/2:
        line=_list[i]
        #得到关系中的第一个节点
        #firstNode=re.match(r'(.*?) ',line)
        #firstNode=firstNode.group(1)
        blank_index=line.find(' ')
        firstNode=line[:blank_index].strip()
        #print firstNode
        firstNode=get_Object(graph,firstNode.strip())
        
        #获得关系中的关系
        relation=re.search(r'\s(.*?)<',line)
        relation=relation.group(1)
        #print relation
        relation=RelNode(relation.strip())
        
        #获取关系中的内容
        contents=[]
        cur_line=get_contentRel(_list,i,contents,'',[])
        relation.add_Infos(contents)
        RelNodes[str(relation)]=relation
        
        
        #for _line in contents:
            #print _line
        
        #获取关系中的另一个节点
        #现在添加另一个节点
        dealLine=_list[cur_line]
        index=dealLine.rfind('>')
        anotherNode=dealLine[index+1:].strip()
        #print anotherNode
        #这行代码表示添加
        anotherNode=get_Object(graph,anotherNode)

        #添加节点之间的正常关系,正常关系式相互添加的
        firstNode.add_Rela(relation,anotherNode)
        anotherNode.add_Rela(relation,firstNode)

        #这样就可以进行下一轮循环
        i=(cur_line+1)              

    #获取所有节点的属性
    _list=loadFile('../../data/data/attribution')
   
    for p in xrange(len(_list)):
        line=_list[p].strip()
        _list.append(line)
        #print line
    i=0
    while i<len(_list):
    #for i in xrange(len(_list)):
        #判断总的起始，即属性中的节点
        total_mark=True
        total_node=''
        if total_mark:
            result=re.match(r'(.*?)<',_list[i].strip())
            if result==None:
                continue
            else:
                total_node=result.group(1)
                #print 'current node',total_node
                total_mark=False        
        contents=[]
        cur_line=get_contentAttr(_list,i,contents,'')
        #for line in contents:
            #print line
        #那么可以直接在attribution后面添加进行扩充而不一定需要定位到那个节点扩充
        #print total_node
        try:
            cur_node=graph[total_node.strip()]
        except KeyError,e:
            print 'missing:',cur_node
        cur_node.add_Infos(contents)
                    
        
        #这样就可以进行下一轮循环
        i=(cur_line+1)
        
        
    #测试
    #test_node=graph[u'for循环']
    #attribution=test_node.get_Info()
    #for line in attribution.items():
        #print line[0],'---',line[1]


          
        
    return graph,RelNodes

    
                

#提取属性的内容
#hasEnd表示出现了最后一个和'<'匹配的'>'
#prefix前一次处理留下是内容
#返回处理完后的行号，就可以进行下一轮的查找
def get_contentAttr(lines,curline,contents,prefix):
    
        
    line=unicode(lines[curline]).strip()
    length=len(line)
    #print line
    if len(prefix)!=0:
        end=line.find('>')
        if end!=-1:
            prefix+=line[:end]
            contents.append(prefix)
            #print prefix
            mark=end+1
            if mark==length:
                return curline
        else:
            prefix+=(line+'\n')
            curline=get_contentAttr(lines,curline+1,contents,prefix)
            return curline
        
    
    
    start=line.find('<')
    content=''
    
    
    i=(start+1)
    while i<length:
    #for i in xrange(start+1,length):
        if line[i]!='>':
            content+=line[i]
            
        else:
            #表示结束
            if i==(length-1):
                contents.append(content)
                #print content
                return curline
            else:
                contents.append(content)
                #print content
                #重新置空
                content=''
                #进入下一个<
                for k in xrange(i,length):
                    if line[k]=='<':
                        i=k
                        break
        i+=1
    
    if not line.endswith('>'):
        curline=get_contentAttr(lines, curline+1, contents, content)
        return curline

#提取关系的属性,和上面的不同，是一个全新的算法
def get_contentRel(lines,curline,contents,prefix,symbols):
    
    line=unicode(lines[curline]).strip()
    #判断是否为单独的一行
    left=line.find('<')
    right=line.find('>')
    length=len(line)
    #
    isComplete=False
    
    content=prefix
    i=0
    while i<length:
        if '<' in symbols:
            content+=line[i]
            if i==(length-1) and left==-1 and right==-1:
                content+='\n'
                    
        if line[i]=='<' and '<' not in symbols:
            symbols.append('<')
            content=''
            isComplete=False
        if line[i]=='>' and '<' in symbols:
            content=content[:-1]
            contents.append(content)
            symbols.remove('<')
            content=''
            isComplete=True
       
        i+=1
    if not isComplete:
        curline=get_contentRel(lines,curline+1,contents,content,symbols)
    return curline
  

#主要用于通过名字取出对象，如果对象存在就直接拿出来，如果不存在，存放后，再取出来
def get_Object(_dict,name):
    keys=_dict.keys()
    if name not in keys:
        _dict[name]=Node(name)
    return _dict[name]
        
        

#导入文件,自动去掉空格的处理
def loadFile(fileName):
    _list=[]
    with open(fileName,'r') as ropen:
        results=ropen.readlines()
        for line in results:
            if not line.strip()=='':
                _list.append(line.decode('utf-8'))
    return _list
            
#写入文件
def writeFile(fileName,_list):
    content=''
    with open(fileName,'w') as wopen:
        for line in _list:
            content+=line
        wopen.writelines(content)
        
            
#查找节点的信息
def getInfoFromNode(name):
    graph,relnodes=preData()
    node=graph[name]
    #查看节点的子节点
    children=node.get_Inheri()
    for line in children:
        print 'Child:',line
    #查看基本信息
    attribution=node.get_Infos()
    for line in attribution.items():
        print 'Basic information:',line[0],'---',line[1]
    #查看有关系的节点信息
    arcInfo=node.get_Rela()
    for line in arcInfo:
        rel=line[0]
        anotherNode=line[1]
        print 'anotherNode:',anotherNode
        for info in rel.get_Infos().items():
            print rel,'---',info[0],'---',info[1]
        
#返回所有的节点,包括节点和关系节点
def getAllNodes(graph,relnodes):
    #graph,relnodes=preData()
    _list=set([])
    for item in graph.keys():
        _list.add(item)
    for item in relnodes.keys():
        _list.add(item)
    return list(_list)
    

#通过名字确定是节点还是关系节点
def getNodeByname(name,graph):
    return graph.get(name)
def getRelNodeByname(name,relnodes):
    return relnodes.get(name)
    
 
#计算关键子在那个节点出现的次数最多
def getMaxNode(graph,relnodes,keyname):
    _dict={}
    nodes=graph.values()
    for node in nodes:
        _dict[node]=node.count(keyname)
    for relnode in relnodes.values():
        _dict[relnode]=relnode.count(keyname)
    #排序
    result=sorted(_dict.iteritems(),key=operator.itemgetter(1),reverse=True)
    #print result
    _list=[]
    for item in result:
        if item[1]>0:
            _list.append(item[0])
        elif item[1]==0:
            break
    
    #返回的这个node需要判断式Node还是RelNode
    return _list 

#返回关键词在那些节点出现过的集合
def getExistNode(graph,relnodes,keynames):
    max_count = 0                      #  选择出现次数最多的
    j = 1
    nodes=graph.values()
    node_list = [[] for i in range(len(nodes)+len(relnodes))]

    for node in nodes:
        for keyname in keynames:
            if node.count(keyname) > max_count:
                max_count = node.count(keyname)
                j = j+1
                node_list[j].append((str(node).decode("utf-8"),keyname.decode("utf-8")))
            elif node.count(keyname) == max_count:
                node_list[j].append((str(node).decode("utf-8"),keyname.decode("utf-8")))

    for relnode in relnodes.values():
        for keyname in keynames:
            if relnode.count(keyname) > max_count:
                max_count = relnode.count(keyname)
                j = j+1
                node_list[j].append((str(relnode).decode("utf-8"),keyname.decode("utf-8")))
            elif relnode.count(keyname) == max_count:
                node_list[j].append((str(relnode).decode("utf-8"),keyname.decode("utf-8")))

    #返回的这个node_set需要判断式Node还是RelNode
    return node_list[j]

    

def test():
    # _list=loadFile('../data/origin/attribution')
    # writeFile('../data/attr', _list)
    # print 'success'

    # preData()

    #getInfoFromNode(u'数据类型')

    # graph,relnodes=preData()
    # _list=auxiliaryFunct.getCorela('样式',graph,relnodes)
    # for item in _list:
    #     print item

    # graph,relnodes=preData()
    # _list=getAllNodes(graph,relnodes)
    # for item in _list:
    #     print item

    # graph,relnodes=preData()

    # node=getMaxNode(graph,relnodes,u'%d')
    # print node

    # graph,relnodes=preData()
    # result=getAllNodes(graph, relnodes)
    # for item in result:
    # print item
    init=['defiNE','%d','flOat','static','%c']
    graph,relnodes=preData()
    nodes=getAllNodes(graph,relnodes)
    result=auxiliaryFunct.changeNodeEx(init,nodes)
    for item in result:
        print item

    # graph, relnodes = preData()
    # _list = auxiliaryFunct.getDocu(graph, relnodes)
    # count = auxiliaryFunct.getSupport(_list)
    # for item in count:
    #     print item[0]
if __name__=='__main__':
    test()
