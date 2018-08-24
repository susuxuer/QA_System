## QA_System
    自动问答系统
    问题分类部分

    文件的解释

    ───┬─ data ───────┬── classifydata ────┬─── filter.txt        judge_code.py识别字符时，无视掉的部分
    │              │                    ├─── keyword           问题分类所需的特征值的集
    │              │                    ├─── dict_nlpir1.txt   pynlpir分词用的词库
    │              │                    ├─── test_question     测试集
    │              │                    ├─── train_question    将五千个问题用judge_code.py过滤后，不含代码的问题
    │              │                    ├─── userdict.txt      结巴分词导入的词库
    │              │                    ├─── filter-question   根据tfidf的值排序后的，中文问题中出现的词
    │              │                    ├─── train             五千个未过滤代码的问题作为训练集
    │              │                    └─── stopword          关键词抽取时用到的停用词集
    │              │  classifydata: 问题分类模块用到的数据
    │              │
    │              ├──── data ──────┬─── attribution            表示节点的属性，包括定义，示例，形式等
    │              │                ├─── con_in                 表示节点之间的继承关系
    │              │                ├─── hgdTest.txt            同义词林(哈工大修订的扩展版)
    │              │                ├─── nor_rel                表示节点之间的关系，其中包含关系的属性
    │              │                ├─── support_word           辅助词
    │              │                └─── transfer               转换词，相当于节点词的同义词林
    │              │
    │              │  data: 这个data主要是用来构建C语言知识图谱的，可以按照各个文件的格式扩充知识图谱。
    │              │ 
    │              ├─ origin
    │              │
    │              │  origin: 这个是创建C语言知识图谱的原始数据，现在不符合格式要求，可以忽略不考虑。
    │              │  
    │              ├─ stanford
    │              │  
    │              │  stanford: 求中心词所使用的java包
    │              │
    │              ├─ testout
    │              │
    │              │  test_out: 用来做参考的输出数据，对程序没影响
    │              │
    │              └─ webCrawler 网络爬虫获得的训练数据，不详细解释了
    │
    │
    └─ src ────────┬── KnowledgeGraph ─┬─── auxiliaryFunct.py
                   │                   ├─── dealdata.py       使用停用词表过滤问题，返回关键词
                   │                   ├─── extractTopic.py   
                   │                   └─── loadModel.py      
                   │
                   │   KnowledgeGraph:
                   │
                   ├── QuestAnswer ────┬─── answer.py                  回答概念类问题
                   │                   ├─── answer_all.py              回答各类问题的整合版
                   │                   ├─── answer_score.py            给多个答案打分
                   │                   ├─── answer_usage_content.py    回答用法类和隶属类问题
                   │                   ├─── answercompare.py           回答比较类问题
                   │                   ├─── keywordextract.py          关键词抽取
                   │                   └─── similarity.py              计算编辑距离
                   │
                   │   QuestAnswer: 
                   │
                   ├── QuestClassify ──┬─── judge_code.py           判断中文问题中是否有太多无法识别的字符
                   │                   ├─── key_word.py             数据预处理，并使用tfidf找出问题分类所需的特征值
                   │                   ├─── main.py                 主函数
                   │                   └─── naive_bayesian_svm.py   使用朴素贝叶斯和svm对问题
                   │ 
                   │  QuestClassify: 问题分类部分代码
                   │ 
                   ├── QuestClassify ────── main.py                 主函数
                   │
                   │
                   │ 
                   └── test.py


    运行方式：
    配置好：1.libsvm 2.NLTK 3.结巴分词 4.tornado 5.numpy 6.requests
    运行 python main.py
