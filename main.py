import os
import threading
import re
from revChatGPT.V1 import Chatbot
from flask import Flask, Response
from flask import request as req
from flask_cors import CORS
from helper import *
import base64
from base64 import b64encode
import pyimgur
app = Flask(__name__)
CORS(app)
chatbot = Chatbot(config={
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1UaEVOVUpHTkVNMVFURTRNMEZCTWpkQ05UZzVNRFUxUlRVd1FVSkRNRU13UmtGRVFrRXpSZyJ9.eyJodHRwczovL2FwaS5vcGVuYWkuY29tL3Byb2ZpbGUiOnsiZW1haWwiOiJha2lrby50ZWNoaUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZX0sImh0dHBzOi8vYXBpLm9wZW5haS5jb20vYXV0aCI6eyJ1c2VyX2lkIjoidXNlci1ZdmFzTXRWNkczV3Q1aVd0UXhYVW5jZ1IifSwiaXNzIjoiaHR0cHM6Ly9hdXRoMC5vcGVuYWkuY29tLyIsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTA5NjAxMDY2NzU4Mzc5MjMwOTM0IiwiYXVkIjpbImh0dHBzOi8vYXBpLm9wZW5haS5jb20vdjEiLCJodHRwczovL29wZW5haS5vcGVuYWkuYXV0aDBhcHAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY5MzQxNTIyMSwiZXhwIjoxNjk0NjI0ODIxLCJhenAiOiJUZEpJY2JlMTZXb1RIdE45NW55eXdoNUU0eU9vNkl0RyIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwgbW9kZWwucmVhZCBtb2RlbC5yZXF1ZXN0IG9yZ2FuaXphdGlvbi5yZWFkIG9yZ2FuaXphdGlvbi53cml0ZSBvZmZsaW5lX2FjY2VzcyJ9.Vo_4IaIiPTM-wD82xCMMfGDssMUzomF3HEvPfdCFyDxAD9bpfgyu3KpF7iyxgOrABkwwqJUfVNRzf8axJgeiuLu18calKYHEOR8R0nZIE6Wcdme1xfwgHYNP0Nb67fqd8xjcVgqxWD8IIAcQwyxcd2Y-XutrGflpzwVUD4MsCMu9uJEOvD-hg0ZgggzP6j6bbXowDyLFQWoeAsC8pzfWhi3BbIUzGopg43gYjgrTJX05ZR8t12rRu4YhJqQeOIbPznLpDVjBBoH78MNRBpPlIZuVfQHXx_KzZyPKF7ghLmBw2R5Jw2zzI08AZQGfVWryWN2UldJz0dw_FYQOcooUDA"
})

from functions import allocate,extract_links,check,mm,ask


def send_req(msg,model):
    global worded 
    worded=""

    if "/" not in msg:
        type_flow=gpt4([{"role": "system", "content": "You are a helpful assistant."},{"role": "user", "content": type_flowchart.format(question=data["message"])}],"gpt-3").lower()
        if "none" not in type_flow:
            if "mindmap" in type_flow or "mind map" in type_flow:
                msg ="/mindmap "+type_flow
            else:
                msg = "/branchchart "+type_flow
        else:
            worded="."
            msg="none"
    print(type_flow)

    if "/mindmap" in msg:
        prompt=mindprompt
        tmap="/mindmap"
    elif "/branchchart" in msg:
        prompt=mermap
        tmap="/branchchart"
    elif "/timeline" in msg:
        prompt=catmap
        tmap="/timeline"

    if "gpt-4" in model and msg!="none":
        for i in range(1,3):
            collect=mm(ask(msg.replace(tmap,''),mermprompt.format(instructions=prompt),api_endpoint))
            if "ERROR in encoding123" not in collect:
                worded=collect
                break
            else:
                worded=""
                print("invalid context")
            if i==3:
                time.sleep(2)
                worded="Failed because max tries exceed!.Try rephrasing Your prompt."
                break
        print("GPT_4")
    elif msg!="none":
        for i in range(1,3):

            collect=mm(gpt4([{"role": "system", "content": f"{prompt}"},{"role": "user", "content": f"{msg.replace(tmap,'')}"}],"gpt-3"))
            if "ERROR in encoding123" not in collect:
                worded=collect
                break
            else:
                worded=""
                print("invalid context")
            if i==3:
                time.sleep(2)
                worded="Failed because max tries exceed!.Try rephrasing Your prompt."
                break
        print("GPT_3")



def grapher(msg,model):
    global worded
    t=time.time()

    t1 = threading.Thread(target=send_req,args=(msg,model,))
    t1.start()
    sent=False
    while worded=="":
        if 10>time.time()-t>9 and not sent:
            yield 'data: %s\n\n' % json.dumps(streamer(">Please wait."), separators=(',' ':'))
            sent=True
        if sent:
            yield 'data: %s\n\n' % json.dumps(streamer("."), separators=(',' ':'))
            time.sleep(1)
        if 100<time.time():
            break
    

    yield 'data: %s\n\n' % json.dumps(streamer("\n\n"), separators=(',' ':'))
    yield 'data: %s\n\n' % json.dumps(streamer(worded), separators=(',' ':'))

def grapher2():
    global worded
    t=time.time()
    sent=False
    while worded=="":
        if 4>time.time()-t>3 and not sent:
            yield 'data: %s\n\n' % json.dumps(streamer("\n\n"), separators=(',' ':'))
            yield 'data: %s\n\n' % json.dumps(streamer(">Please wait."), separators=(',' ':'))
            sent=True
        if sent:
            yield 'data: %s\n\n' % json.dumps(streamer("."), separators=(',' ':'))
            time.sleep(1)    
        if 100<time.time():
            break

    yield 'data: %s\n\n' % json.dumps(streamer("\n\n"), separators=(',' ':'))
    yield 'data: %s\n\n' % json.dumps(streamer(worded), separators=(',' ':'))

def gpt4(messages,model="gpt-4"):
    global data
    global uploaded_image
    global processed_text
    print(model)


    try:
        xx = requests.get(api_endpoint.replace("/conversation",""),timeout=15)
        print(xx.text)
    except :
        model="gpt-3"
        pass

    if "gpt-4" in model:

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
                            model="gpt-3"
                            print(e)
                            ee=str(e)
                        if parsed_data!={} and parsed_data.get("data") != None:
                            print(parsed_data['data'])
                            msg=parsed_data['data'].replace("ui34d","://")
                            print(msg)
                            
                    elif line and "conversationId"  in line.decode():
                        print("DOCEDED")

                        json_body = line.decode().replace("data: ","")
                        json_body = json.loads(json_body)
                        data['parentMessageId'] = json_body['messageId']
                        return json_body['response']

        except Exception as e:
            model="gpt-3"


    if "gpt-3" in model:

        for provider in providers:
            try:

                response = g4f.ChatCompletion.create(
                    model="gpt-3.5-turbo",provider=provider ,
                    messages=messages,
                    stream=False)
                print(response)
                return response
            except:
                pass



    try:    
        del data["imageURL"]   
    except:
        pass
    try:
        uploaded_image=""
        del data["imageBase64"]
    except:
        pass
    if random.randint(1,4):
        try:
            processed_text=""
            del data["context"]
        except:
            pass

def stream_gpt4(messages,model="gpt-4"):
    print(model)
    global data
    global uploaded_image
    global processed_text
    global providers

    ee=""

    if "gpt-3" in check(api_endpoint):
        model="gpt-3"

    if model == "gpt-4":
        t2 = threading.Thread(target=send_req,args=(data["message"],"gpt-3",))
        t2.start()
        if uploaded_image!="":
          yield 'data: %s\n\n' % json.dumps(streamer("Analysing the images..\n\n"), separators=(',' ':'))
        try:
          
            with requests.post(api_endpoint, json=data, stream=True,timeout=1000) as resp:
                for line in resp.iter_lines():
                    if line and "result" not in line.decode() and "conversationId" not in line.decode() and "[DONE]" not in line.decode():
                        line=line.decode()
                        line=line.replace("://","ui34d")

                        try:
                            parsed_data = json.loads("{" + line.replace(":", ": ").replace("data", "\"data\"",1) + "}")
                        except Exception as e:
                            parsed_data={"data":"."}
                            model="gpt-3"
                            print(e)
                            ee=str(e)
                        if parsed_data!={} and parsed_data.get("data") != None:
                            msg=parsed_data['data'].replace("ui34d","://")
                            
                            yield 'data: %s\n\n' % json.dumps(streamer(msg), separators=(',' ':'))

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
                            msg="\n\n\n"+a+para
                            yield 'data: %s\n\n' % json.dumps(streamer(msg), separators=(',' ':'))

                        except Exception as e:
                            print(e)
                            pass
                        if data["context"]!="":
                            data['parentMessageId'] = json_body['messageId']
                            
                        yield from grapher2()

                        print("Conversation history saved")



        except Exception as e:
            print(e)
            yield 'data: %s\n\n' % json.dumps(streamer("> Falling Back to GPT-3:"), separators=(',' ':'))
            yield 'data: %s\n\n' % json.dumps(streamer("\n\n"), separators=(',' ':'))

            prev_text = ""
            try:

                for query in chatbot.ask(data["message"],):
                    reply = query["message"][len(prev_text) :]
                    prev_text = query["message"]
                    yield 'data: %s\n\n' % json.dumps(streamer(reply), separators=(',' ':'))


                yield 'data: %s\n\n' % json.dumps(streamer("\n\n"), separators=(',' ':'))
                yield 'data: %s\n\n' % json.dumps(streamer("> " +str(ee)), separators=(',' ':'))
            except:
                prev_text = ""

                for provider in providers:
                    try:

                        response = g4f.ChatCompletion.create(
                            model="gpt-3.5-turbo",provider=provider ,
                            messages=messages,
                            stream=True,)
                        for message in response:
                            yield 'data: %s\n\n' % json.dumps(streamer(message), separators=(',' ':'))
                        break
                    except:
                        pass



    if model=="gpt-3":
        yield 'data: %s\n\n' % json.dumps(streamer("> GPT-3:"), separators=(',' ':'))
        yield 'data: %s\n\n' % json.dumps(streamer("\n\n"), separators=(',' ':'))

        prev_text = ""
        try:

            for query in chatbot.ask(data["message"],):
                reply = query["message"][len(prev_text) :]
                prev_text = query["message"]
                yield 'data: %s\n\n' % json.dumps(streamer(reply), separators=(',' ':'))


            yield 'data: %s\n\n' % json.dumps(streamer("\n\n"), separators=(',' ':'))
            yield 'data: %s\n\n' % json.dumps(streamer("> " +str(ee)), separators=(',' ':'))
        except:
            prev_text = ""

            for provider in providers:
                try:

                    response = g4f.ChatCompletion.create(
                        model="gpt-3.5-turbo",provider=provider ,
                        messages=messages,
                        stream=True,)
                    for message in response:
                        yield 'data: %s\n\n' % json.dumps(streamer(message), separators=(',' ':'))
                    break
                except:
                    pass







@app.route("/chat/completions", methods=['POST'])
def chat_completions():
    global data
    global uploaded_image
    global processed_text
    global  systemp
    systemp=True

    streaming = req.json.get('stream', False)
    model = req.json.get('model', 'gpt-4-web')
    messages = req.json.get('messages')
    
    
    allocate(messages,data,uploaded_image,processed_text,systemp,model)


    if "/clear" in data["message"] and "gpt-4" in model :
        del data["parentMessageId"]   
        return 'data: %s\n\n' % json.dumps(streamer('Conversation History Cleared✅'), separators=(',' ':'))
    
    if "/log" in data["message"]  :

        return 'data: %s\n\n' % json.dumps(streamer(str(data)), separators=(',' ':'))

    if "/prompt" in data["message"]  :

        if systemp == False:
            systemp=True
        else:
            systemp=False
        
        return 'data: %s\n\n' % json.dumps(streamer(f"Systemprompt is  {systemp}"), separators=(',' ':'))



    if "/upload" in data["message"] and "gpt-4" in model :
        up="""
<!DOCTYPE html>
<embed src="https://intagpt.up.railway.app/upload" style="width:1000px; height: 500px;">
"""
        return 'data: %s\n\n' % json.dumps(streamer(up), separators=(',' ':'))
    
    # if "/mindmap" in data["message"]  :
    #     yield 'data: %s\n\n' % json.dumps(streamer("> Your request is being processed."), separators=(',' ':'))
    #     yield 'data: %s\n\n' % json.dumps(streamer("\n\n"), separators=(',' ':'))
    #     reply=mm(gpt4([{"role": "system", "content": f"{mindprompt}"},{"role": "user", "content": f"{data['message'].replace('/graph','')}"}],"gpt-3"))
    #     yield 'data: %s\n\n' % json.dumps(streamer(reply), separators=(',' ':'))


    
    if "/context" in data["message"] and "gpt-4" in model :
        cont="""
<!DOCTYPE html>
<embed src="https://intagpt.up.railway.app/context" style="width:1000px; height: 500px;">
"""
        return 'data: %s\n\n' % json.dumps(streamer(cont), separators=(',' ':'))
    
    elif "gpt-4" in model and len(messages) <= 2 and streaming:
        return app.response_class(stream_gpt4(messages,"gpt-3"), mimetype='text/event-stream')

    elif "gpt-4" in model and len(messages) <= 2 and not streaming:
        print("USING GPT_4 NO STREAM")
        k=gpt4(messages)
        print(k)
        return output(k)

    elif "gpt-4" in model and len(messages) > 2 and not streaming:
        print("USING GPT_4 NO STREAM")
        k=gpt4(messages)
        print(k)
        return output(k)
    
    if "gpt-4" in model and len(messages) > 2 and streaming:
        return app.response_class(stream_gpt4(messages), mimetype='text/event-stream')
    elif "gpt-3" in model :
        return app.response_class(stream_gpt4(messages,"gpt-3"), mimetype='text/event-stream')



@app.route("/v1/chat/completions", methods=['POST'])
def chat_completions2():
    global data
    global uploaded_image
    global processed_text
    global     systemp

    streaming = req.json.get('stream', True)
    model = req.json.get('model', 'gpt-4-web')
    messages = req.json.get('messages')
    print(model)
    
    
    allocate(messages,data,uploaded_image,processed_text,systemp,model)


    if "/clear" in data["message"] and "gpt-4" in model :
        icon="()"
        del data["systemMessage"]   


        try:
            del data["parentMessageId"]   
            icon=icon+"(history)"
        except:
            pass
        try:
            processed_text=""
            del data["context"]
            icon=icon+"(context)"
        except:
            pass
        try:
            uploaded_image=""
            del data["imageBase64"]
            icon=icon+"(image)"

        except:
            pass
        try:
            del data["imageURL"]
            icon=icon+"(imageurl)"
        except:
            pass
        return 'data: %s\n\n' % json.dumps(streamer('Cleared✅ '+icon), separators=(',' ':'))
    
    if "/log" in data["message"]  :

        return 'data: %s\n\n' % json.dumps(streamer(str(data)), separators=(',' ':'))

    if "/prompt" in data["message"]  :

        if systemp == False:
            systemp=True
        else:
            systemp=False
        
        return 'data: %s\n\n' % json.dumps(streamer(f"Systemprompt is  {systemp}"), separators=(',' ':'))

    if "/help" in data["message"]  :
        return 'data: %s\n\n' % json.dumps(streamer("""
>Developer Options:
**/log  /prompt  /clear  /upload  /context /image**
                                                    
>Graphs
**/mindmap  /flowchart  /complexchart  /linechart  /branchchart**"""), separators=(',' ':'))
    
    if "/upload" in data["message"] and "gpt-4" in model :
        up="""<!DOCTYPE html>
<embed src="https://intagpt.up.railway.app/upload" style="width:1000px; height: 500px;">
"""
        return 'data: %s\n\n' % json.dumps(streamer(up), separators=(',' ':'))
    if "/context" in data["message"] and "gpt-4" in model :
        cont="""<!DOCTYPE html>
<embed src="https://intagpt.up.railway.app/context" style="width:1000px; height: 500px;">
"""
        return 'data: %s\n\n' % json.dumps(streamer(cont), separators=(',' ':'))
    if "/mindmap" in data["message"] or "/branchchart" in data["message"] or "/timeline" in data["message"] :
        return app.response_class(grapher(data["message"],model), mimetype='text/event-stream')
    
    elif "/flowchart" in data["message"] or "/complexchart" in data["message"] or  "/linechart" in data["message"] :
        if "gpt-3" in model:
            if "/flowchart" in  data["message"]:
                return app.response_class(stream_gpt4([{"role": "system", "content": f"{flowchat}"},{"role": "user", "content": f"{data['message'].replace('/flowchart','')}"}],"gpt-3"), mimetype='text/event-stream')
            if "/complexchart" in  data["message"]:
                return app.response_class(stream_gpt4([{"role": "system", "content": f"{complexchat}"},{"role": "user", "content": f"{data['message'].replace('/complexchart','')}"}],"gpt-3"), mimetype='text/event-stream')
            if "/linechart" in  data["message"]:
                return app.response_class(stream_gpt4([{"role": "system", "content": f"{linechat}"},{"role": "user", "content": f"{data['message'].replace('/linechat','')}"}],"gpt-3"), mimetype='text/event-stream')
        elif "gpt-4" in model:

            if "/flowchart" in  data["message"]:
                data["message"]=data["message"].replace("/flowchart","")
                data["systemMessage"]=mermprompt.format(instructions=flowchat)
            if "/complexchart" in  data["message"]:
                data["message"]=data["message"].replace("/complexchart","")
                data["systemMessage"]=mermprompt.format(instructions=complexchat)

            if "/linechart" in  data["message"]:
                data["message"]=data["message"].replace("/linechart","")
                data["systemMessage"]=mermprompt.format(instructions=linechat)

            return app.response_class(stream_gpt4(messages,"gpt-4"), mimetype='text/event-stream')



    elif "gpt-4" in model and len(messages) <= 2 and streaming:
        return app.response_class(stream_gpt4(messages,"gpt-3"), mimetype='text/event-stream')

    elif "gpt-4" in model and len(messages) <= 2 and not streaming:
        print("USING GPT_4 NO STREAM")
        k=gpt4(messages,"gpt-3")
        print(k)
        return output(k)

    elif "gpt-4" in model and len(messages) > 2 and not streaming:
        print("USING GPT_4 NO STREAM")
        k=gpt4(messages)
        print(k)
        return output(k)
    
    if "gpt-4" in model and len(messages) > 2 and streaming:
        return app.response_class(stream_gpt4(messages), mimetype='text/event-stream')
    elif "gpt-3" in model :
        return app.response_class(stream_gpt4(messages,"gpt-3"), mimetype='text/event-stream')
        # return 'data: %s\n\n' % json.dumps(streamer(str(messages)), separators=(',' ':'))






@app.route('/api/<name>')
def hello_name(name):
   global api_endpoint
   url = "https://"+name+"/conversation"
   api_endpoint=url
   return f'{api_endpoint}'

@app.route('/context', methods=['POST'])
def my_form_post():
    global processed_text
    text = req.form['text']
    processed_text = text
    return "The context has been added."

@app.route('/context')
def my_form():
    return '''
<form method="POST">
    <textarea name="text"></textarea>
    <input type="submit">
</form>
'''

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global uploaded_image
    if req.method == 'POST': 
        if 'file1' not in req.files: 
            return 'there is no file1 in form!'
        file1 = req.files['file1']
        content = file1.read()
        data = b64encode(content)
        client = pyimgur.Imgur("47bb97a5e0f539c")
        r = client._send_request('https://api.imgur.com/3/image', method='POST', params={'image': data})
        uploaded_image=r['link']
        return f"Image has been uploaded and your question can now be asked. ({r['link']})"

    return '''
    <h1>Upload new Image</h1>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="file1">
      <input type="submit">
    </form>
    '''


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
