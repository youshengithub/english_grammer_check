首先执行  apt install link-grammar
然后执行 python test.py file_name1 file_name2 其中file_name就是你想要分析的文件，支持多个文件 用空格隔开
结果回保存在Ana_file_name里面，[单词] 这里面就是错误的地方
对于每一个句子，分析结果都会被记录下来，方便下一次快速的进行查找
注意到file_name文件里面的句子必须以大写字母开头 并且以点号和一个空格结尾 例如 "I like dogs. ",只有满足这样的句子才会被送入语法分析