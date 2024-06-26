import re,sys,pickle,os
import subprocess,multiprocessing 
import concurrent.futures
from tqdm import tqdm

def analyze_sentence(sentence):
    process = subprocess.Popen(['link-parser'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate(sentence)
    ana=""
    for i in stdout.split("\n"):
        if(i.startswith("LEFT-WALL")):
            ana=i
    # 分析输出（这部分需要你根据你的需求来编写）
    if 'No complete linkages found.' in stdout:
        return sentence,False,ana 
    return sentence,True,ana
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
    if not os.path.exists(file_name):  return set()
    with open(file_name, 'r') as f:
        lines = f.readlines()
    line_set=set()
    for line in lines:
        line_set.add(line.strip())  # 使用 strip() 方法移除每行末尾的换行符
    print("所有",file_name,"已经被载入")
    return line_set
def write_config(success_list,file_name):
    succ=""
    for i in success_list:
        succ+=i+"\n"
    with open(file_name, 'w') as f:
        f.write(succ)
def handle_file(file_name):
    line_list=load_config("ignore.txt")
    success_list=load_config("success.txt")
    if not os.path.exists('fail.pkl'):  fail_dict={}
    else:
        fail_dict = pickle.load(open('fail.pkl', 'rb+') )
    sentences = process_latex_file(file_name)
    wrong_number=0
    ans=""
    needs_calc=[]
    for sentence in sentences:
        sentence=sentence[:-1]
        ignore=False
        fails=False
        if(sentence in line_list or sentence in success_list):
            ignore=True
            continue
        if(sentence in fail_dict):
            ans+=sentence+"\n"+fail_dict[sentence][10:]+"\n\n"
            wrong_number+=1
            fails=True
            continue
        needs_calc.append(sentence)
    if(len(needs_calc)>0):
        with concurrent.futures.ThreadPoolExecutor() as executor, tqdm(total=len(needs_calc)) as pbar:
            future_to_i = {executor.submit(analyze_sentence, i): i for i in needs_calc}
            result_list = []
            for future in concurrent.futures.as_completed(future_to_i):
                i = future_to_i[future]
                result = future.result()
                result_list.append(result)
                pbar.update(1)
        for sentence,flag,info in result_list:
            if(flag==True):
                success_list.add(sentence)
            else:
                wrong_number+=1
                fail_dict[sentence]=info
                ans+=sentence+"\n"+info[10:]+"\n\n"
    print("识别的句子总数:",len(sentences),"错误率:",wrong_number/len(sentences))
    with open("Ana_"+file_name+".txt", 'w') as f:  f.write(ans)
    with open('fail.pkl', 'wb') as file: pickle.dump(fail_dict, file)
    write_config(list(success_list),"success.txt")
if __name__=="__main__":
    processes = []
    for i in sys.argv[1:]:
        handle_file(i)
    for process in processes:
        process.join()   