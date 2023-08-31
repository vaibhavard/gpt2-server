import os
import threading
import re
from revChatGPT.V1 import Chatbot
from flask import Flask, request, Response
from flask_cors import CORS
from helper import *
app = Flask(__name__)
CORS(app)

chatbot = Chatbot(config={
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1UaEVOVUpHTkVNMVFURTRNMEZCTWpkQ05UZzVNRFUxUlRVd1FVSkRNRU13UmtGRVFrRXpSZyJ9.eyJodHRwczovL2FwaS5vcGVuYWkuY29tL3Byb2ZpbGUiOnsiZW1haWwiOiJha2lrby50ZWNoaUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZX0sImh0dHBzOi8vYXBpLm9wZW5haS5jb20vYXV0aCI6eyJ1c2VyX2lkIjoidXNlci1ZdmFzTXRWNkczV3Q1aVd0UXhYVW5jZ1IifSwiaXNzIjoiaHR0cHM6Ly9hdXRoMC5vcGVuYWkuY29tLyIsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTA5NjAxMDY2NzU4Mzc5MjMwOTM0IiwiYXVkIjpbImh0dHBzOi8vYXBpLm9wZW5haS5jb20vdjEiLCJodHRwczovL29wZW5haS5vcGVuYWkuYXV0aDBhcHAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY5MzQxNTIyMSwiZXhwIjoxNjk0NjI0ODIxLCJhenAiOiJUZEpJY2JlMTZXb1RIdE45NW55eXdoNUU0eU9vNkl0RyIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwgbW9kZWwucmVhZCBtb2RlbC5yZXF1ZXN0IG9yZ2FuaXphdGlvbi5yZWFkIG9yZ2FuaXphdGlvbi53cml0ZSBvZmZsaW5lX2FjY2VzcyJ9.Vo_4IaIiPTM-wD82xCMMfGDssMUzomF3HEvPfdCFyDxAD9bpfgyu3KpF7iyxgOrABkwwqJUfVNRzf8axJgeiuLu18calKYHEOR8R0nZIE6Wcdme1xfwgHYNP0Nb67fqd8xjcVgqxWD8IIAcQwyxcd2Y-XutrGflpzwVUD4MsCMu9uJEOvD-hg0ZgggzP6j6bbXowDyLFQWoeAsC8pzfWhi3BbIUzGopg43gYjgrTJX05ZR8t12rRu4YhJqQeOIbPznLpDVjBBoH78MNRBpPlIZuVfQHXx_KzZyPKF7ghLmBw2R5Jw2zzI08AZQGfVWryWN2UldJz0dw_FYQOcooUDA"
})


def extract_links(text):
    # Regular expression pattern to match URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    # Find all matches of the URL pattern in the text
    urls = re.findall(url_pattern, text)
    return urls



def send_req():
    global data
    global nline
    global worded
    ddgd=""
    ee=""
    worded=""
    try:

        with requests.post(api_endpoint, json=data, stream=True) as resp:
            for line in resp.iter_lines():
                if line and "result" not in line.decode() and "conversationId" not in line.decode() and "[DONE]" not in line.decode():
                    line=line.decode()
                    line=line.replace("://","ui34d")

                    try:
                        parsed_data = json.loads("{" + line.replace(":", ": ").replace("data", "\"data\"",1) + "}")
                    except Exception as e:
                        parsed_data={"data":"."}
                        ee=str(e)
                    if parsed_data!={} and parsed_data.get("data") != None:
                        print(parsed_data['data'])
                        msg=parsed_data['data'].replace("ui34d","://")

                        worded=worded+msg
                    time.sleep(0.13)
                elif line and "conversationId"  in line.decode():

                    json_body = line.decode().replace("data: ","")
                    json_body = json.loads(json_body)
                    try:
                        ss = json_body["details"]["adaptiveCards"][0]["body"][1]["text"].replace(")","")
                        links = extract_links(ss)
                        para="\n\n"
                        x=0
                        for lnk in links:
                            x=x+1
                            para=para+f"""[^{x}^]: {lnk}
                            
"""
                        a="Links:"
                        for i in range(1,x+1):
                            a = a + f"""[^{i}^]"""
                        worded=worded+"\n"+a+para
                    except Exception as e:
                        print(e)
                        pass
                    data['parentMessageId'] = json_body['messageId']
                    print("Conversation history saved")

    except Exception as e:
        prev_text = ""

        for query in chatbot.ask(data["message"],):
            reply = query["message"][len(prev_text) :]
            prev_text = query["message"]
            worded=worded+reply
            time.sleep(0.13)

        time.sleep(0.4)
        worded=worded+"\n\n" + ">"+str(e)
        time.sleep(0.1)
        worded=""



    worded=ee
    time.sleep(0.13)
    worded=""



@app.route("/v1/chat/completions", methods=['POST'])
def chat_completions():
    global data


    streaming = request.json.get('stream', True)
    model = request.json.get('model', 'gpt-4-web')


    messages = request.json.get('messages')
    if len(messages) <= 2:
        print("no con detected")

    data['message']= messages[-1]['content']
    print(data["message"])
    links = extract_links(data['message'])
    if links!= [] :
      print(links[0])
      data["imageURL"]=links[0]

    def stream_gpt4():
        global worded
        global data
        prev_word=""
        t1 = threading.Thread(target=send_req)
        t1.start()
        t=time.time()
        sent = False
        sent2=False
        sent3=False
        pattern = r'https:\s+//'


        while worded == "":
            if sent2:
              yield 'data: %s\n\n' % json.dumps(streamer("🔃"), separators=(',' ':'))
              time.sleep(1)

            if 10>time.time()-t>9 and not sent:
                yield 'data: %s\n\n' % json.dumps(streamer("> Please Wait."), separators=(',' ':'))
                yield 'data: %s\n\n' % json.dumps(streamer("\n\n\n"), separators=(',' ':'))
                sent=True
            elif 20>time.time()-t>19 and not sent2:
                yield 'data: %s\n\n' % json.dumps(streamer("> Server had gone to sleep becuase of inactivity.Server is booting.."), separators=(',' ':'))
                sent2=True
                yield 'data: %s\n\n' % json.dumps(streamer("\n\n"), separators=(',' ':'))

                yield 'data: %s\n\n' % json.dumps(streamer("> GPT-3 Response"), separators=(',' ':'))
                yield 'data: %s\n\n' % json.dumps(streamer("\n\n"), separators=(',' ':'))

                global data
                prev_text = ""

                for query in chatbot.ask(messages[-1]['content'],):
                    reply = query["message"][len(prev_text) :]
                    prev_text = query["message"]
                    print(reply)
                    yield 'data: %s\n\n' % json.dumps(streamer(reply), separators=(',' ':'))
                    
                yield 'data: %s\n\n' % json.dumps(streamer("\n\n"), separators=(',' ':'))
                yield 'data: %s\n\n' % json.dumps(streamer("> GPT-4 Response"), separators=(',' ':'))
                yield 'data: %s\n\n' % json.dumps(streamer("\n\n"), separators=(',' ':'))


            elif 60>time.time()-t>59 and not sent3:
                yield 'data: %s\n\n' % json.dumps(streamer("> Server Has been restarted because of overload.Now you can ask your question."), separators=(',' ':'))
                yield 'data: %s\n\n' % json.dumps(streamer("\n"), separators=(',' ':'))
                sent3=False
                break

            pass

        yield 'data: %s\n\n' % json.dumps(streamer("\n\n\n"), separators=(',' ':'))

        while worded!="":


            if prev_word!=worded:
                message = worded[len(prev_word) :]
                yield 'data: %s\n\n' % json.dumps(streamer(message), separators=(',' ':'))


                prev_word=worded
                try:
                    worded = re.sub(pattern, 'https://', worded)
                except:
                    pass
                  
            if 350>time.time()-t>340 :
              worded=""
              break
        try:    
          del data["imageURL"]   
        except:
          pass

            







                    # yield 'data: Hi' % json.dumps(completion_data, separators=(',' ':'))
                # elif line and "conversationId"  in line.decode():
                #     json_body = line.decode().replace("data: ","")
                #     json_body = json.loads(json_body)
                #     data['parentMessageId'] = json_body['messageId']
                #     print("Conversation history saved")

    def stream_gpt3():
        global data
        prev_text = ""

        for query in chatbot.ask(messages[-1]['content'],):
            reply = query["message"][len(prev_text) :]
            prev_text = query["message"]
            print(reply)
            yield 'data: %s\n\n' % json.dumps(streamer(reply), separators=(',' ':'))
        yield 'data: %s\n\n' % json.dumps(streamer("\n\n"), separators=(',' ':'))

    if "/clear" in data["message"] and "gpt-4" in model :
        data=backup
        return 'data: %s\n\n' % json.dumps(streamer('Conversation History Cleared✅'), separators=(',' ':'))
    elif "gpt-4" in model and len(messages) =< 2:
        return 'data: %s\n\n' % json.dumps(streamer('Conversation History Cleared✅'), separators=(',' ':'))


    if "gpt-4" in model and len(messages) > 2:
        return app.response_class(stream_gpt4(), mimetype='text/event-stream')
    elif "gpt-3.5" in model :
        return app.response_class(stream_gpt3(), mimetype='text/event-stream')







@app.route('/api/<name>')
def hello_name(name):
   global api_endpoint
   url = "https://"+name+"/conversation"
   api_endpoint=url
   return f'{api_endpoint}'



@app.route('/')
def yellow_name():
   return f'Server 1 is OK and server 2 check: {api_endpoint}'

@app.route("/v1/models")
def models():
    print("Models")
    return model



if __name__ == '__main__':
    config = {
        'host': '0.0.0.0',
        'port': 1337,
        'debug': True
    }

    app.run(**config)
