import re,tqdm,sys
import subprocess,multiprocessing 

def analyze_sentence(sentence):
    # 创建一个新的子进程来运行 link-parser
    process = subprocess.Popen(['link-parser'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # 通过 stdin 提供句子
    stdout, stderr = process.communicate(sentence)
    # 分析输出（这部分需要你根据你的需求来编写）
    if 'No complete linkages found.' in stdout:
        return False
    return True
def replace_words(text):
    # 将Eq替换为equation
    text = text.replace('Eq', 'equation')
    # 将Fig替换为figure
    text = text.replace('Fig', 'figure')
    text = text.replace('\n', '')
    return text
def replace_percentage(text):
    # 使用正则表达式匹配 xx.xx% 或 xx%
    pattern = r'\d+(\.\d+)?%'
    # 将匹配到的部分替换为 100%
    text = re.sub(pattern, '100%', text)
    return text
def remove_brackets(text):
    # 使用正则表达式匹配 (xxx)，然后替换为空字符串
    result = re.sub(r'\([^)]*\)', '', text)
    return result

def remove_citations(text):
    # 使用正则表达式匹配 \cite{xxx}，然后替换为空字符串
    result = re.sub(r'\\cite\{[^}]*\}', '', text)
    return result
def replace_numbers(text):
    # 使用正则表达式匹配 $xxx$，然后替换为 "The number of dogs"
    result = re.sub(r'\$[^$]*\$', 'Theta', text)
    return result
def process_latex_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    content=replace_percentage(content)
    content=replace_words(content)
    content=remove_citations(content)
    content=replace_numbers(content)
    content=remove_brackets(content)
    
    
    # 匹配所有以大写字母开头，以句号"."结尾的句子
    sentences = re.findall(r'([A-Z][^\\}\{.]*\.\s)', content)

    return sentences
def load_config(file_name):
    
    with open(file_name, 'r') as f:
        # 读取所有行，每一行作为列表的一个元素
        lines = f.readlines()
    line_set=set()
    for line in lines:
        line_set.add(line.strip())  # 使用 strip() 方法移除每行末尾的换行符
        print(line.strip())
    print("所有",file_name,"已经被载入")
    return line_set
def write_config(success_list,file_name):
    succ=""
    for i in success_list:
        succ+=i+"\n"
    with open(file_name, 'w') as f:
        f.write(succ)
def handle_file(file_name):
    # 打开文件
    line_list=load_config("ignore.txt")
    success_list=load_config("success.txt")
    fail_list=load_config("fail.txt")
    # 测试
    sentences = process_latex_file(file_name)
    wrong_number=0
    ans=""
    for sentence in tqdm.tqdm(sentences):
        sentence=sentence[:-1]
        ignore=False
        fails=False
        if(sentence in line_list or sentence in success_list):
            ignore=True
            tqdm.tqdm.write(f'Ignore: {sentence}')
            continue
        if(sentence in fail_list):
            fails=True
        if(fails==True or analyze_sentence(sentence)==False):
            wrong_number+=1
            tqdm.tqdm.write(f'Error in sentence: {sentence}')
            ans+=f'Error in sentence: {sentence}\n'
            fail_list.add(sentence)
        else: #加入到success中去
            success_list.add(sentence)
            
    print("识别的句子总数:",len(sentences),"错误率:",wrong_number/len(sentences))

    with open("Ana_"+file_name+".txt", 'w') as f:
        f.write(ans)
    write_config(list(success_list),"success.txt")
    write_config(list(fail_list),"fail.txt")
processes = []
for i in sys.argv[1:]:
    handle_file(i)
    # new_process = multiprocessing.Process(target=handle_file, args=(i,))
    # new_process.start()
    # processes.append(new_process)
for process in processes:
    process.join()