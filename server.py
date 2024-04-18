import socket
import threading
from test import *
lock = threading.Lock()
line_list=load_config("ignore.txt") #先把这些都加载进来
success_list=load_config("success.txt")
if not os.path.exists('fail.pkl'):  fail_dict={}
else:
    fail_dict = pickle.load(open('fail.pkl', 'rb+') ) 
def handle(sentence):
    sentences=sentence.split("\n")
    needs_calc=[]
    ans=""
    for sentence in sentences:
        sentence=sentence.strip()
        if(sentence in line_list or sentence in success_list):
            continue
        if(sentence in fail_dict):
            ans+=sentence+"\n"+fail_dict[sentence][10:]+"\n\n"
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
            lock.acquire()
            if(flag==True):
                success_list.add(sentence)
            else:
                fail_dict[sentence]=info
                ans+=sentence+"\n"+info[10:]+"\n\n"
            lock.release()
    return ans

def handle_client(client):
    data = client.recv(1024).decode('utf-8').strip('\0')
    print('Received data:', data)
    result = handle(data)
    client.send(result.encode('utf-8'))
    client.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 1234))
server.listen(1)

try:
    while True:
        client, addr = server.accept()
        print('Received connection from', addr)
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()
    
except KeyboardInterrupt:
    print("Ctrl+C pressed, exiting...")
finally:
    # This code will be executed no matter what
    print("Cleaning up resources...")
    server.close()
    with open('fail.pkl', 'wb') as file: pickle.dump(fail_dict, file) #结束之后保存
    write_config(list(success_list),"success.txt")