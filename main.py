import os
import time
import json
import random
from revChatGPT.V1 import Chatbot
from flask import Flask, request, Response
from flask_cors import CORS
from helper import *
app = Flask(__name__)
CORS(app)
import threading
chatbot = Chatbot(config={
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1UaEVOVUpHTkVNMVFURTRNMEZCTWpkQ05UZzVNRFUxUlRVd1FVSkRNRU13UmtGRVFrRXpSZyJ9.eyJodHRwczovL2FwaS5vcGVuYWkuY29tL3Byb2ZpbGUiOnsiZW1haWwiOiJha2lrby50ZWNoaUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZX0sImh0dHBzOi8vYXBpLm9wZW5haS5jb20vYXV0aCI6eyJ1c2VyX2lkIjoidXNlci1ZdmFzTXRWNkczV3Q1aVd0UXhYVW5jZ1IifSwiaXNzIjoiaHR0cHM6Ly9hdXRoMC5vcGVuYWkuY29tLyIsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTA5NjAxMDY2NzU4Mzc5MjMwOTM0IiwiYXVkIjpbImh0dHBzOi8vYXBpLm9wZW5haS5jb20vdjEiLCJodHRwczovL29wZW5haS5vcGVuYWkuYXV0aDBhcHAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY5MjE2NjI5MCwiZXhwIjoxNjkzMzc1ODkwLCJhenAiOiJUZEpJY2JlMTZXb1RIdE45NW55eXdoNUU0eU9vNkl0RyIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwgbW9kZWwucmVhZCBtb2RlbC5yZXF1ZXN0IG9yZ2FuaXphdGlvbi5yZWFkIG9yZ2FuaXphdGlvbi53cml0ZSBvZmZsaW5lX2FjY2VzcyJ9.25ze2lN-FxrvB_WUFHkIa1Vh9ZxHCv_uAq6yUoo6un2Gt8TYcpW4jUWO_Ubo5p-V5NMrNUcq8tA3jCtnCkFXBGLlK5t6dIaL_excMKyEhgPpm09GGBwhTVIXA_slsjPOW7iRt77mxjWocXNvF0beghlznVQMWNOSR8q7OwUMsSOTc-dG4xZHlwl7HV6hthiYu3rB7n8whwntbN4yP5ZCixQKEpjVAiGU7oCpQiMD1WgQA9yR175Y8XoLBrMkk8FxkrABn5ojBS5hV1KQ0WtQkuTzXcT9QwGXSzXqNt-XM3rymZ0hZ_LqczhoPdMOwgRK_d6CAh0zrHfg21cNWnimhg"
})

import re
def extract_links(string):
    pattern = r'(https?://\S+)'
    links = re.findall(pattern, string)
    return links


def streamer(tok):
        completion_timestamp = int(time.time())
        completion_id = ''.join(random.choices(
            'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=28))

        completion_data = {
            'id': f'chatcmpl-{completion_id}',
            'object': 'chat.completion.chunk',
            'created': completion_timestamp,
            'model': 'gpt-3.5-turbo-0301',
            'choices': [
                {
                    'delta': {
                        'content':tok
                    },
                    'index': 0,
                    'finish_reason': None
                }
            ]
        }
        return completion_data


@app.route("/v1/chat/completions", methods=['POST'])
def chat_completions():


    streaming = request.json.get('stream', True)
    model = request.json.get('model', 'gpt-3.5-turbo')

    messages = request.json.get('messages')
    data['message']= messages[-1]['content']
    print(data)

    def stream():
        global data
        global nline

        with requests.post(api_endpoint, json=data, stream=True) as resp:
            for line in resp.iter_lines():
                if line and "result" not in line.decode() and "conversationId" not in line.decode() and "[DONE]" not in line.decode():
                    line=line.decode("utf-8")
                    if rf"\n" not in line:
                        if nline:
                            msg = line.replace("data: ","").strip().strip('"')

                            token = " \n\n\n {msg}".format(msg=msg)
                            print("nline used")
                            nline=False
                        else:
                            token = line.replace("data: ","").strip().strip('"')
                    else:
                        msg = line.replace("data: ","").strip().strip('"')
                        print("nline dtected")
                        token=msg.split(rf"\n")[0]

                        nline=True
                    print(token)

                    completion_timestamp = int(time.time())
                    completion_id = ''.join(random.choices(
                        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=28))

                    completion_data = {
                        'id': f'chatcmpl-{completion_id}',
                        'object': 'chat.completion.chunk',
                        'created': completion_timestamp,
                        'model': 'gpt-3.5-turbo-0301',
                        'choices': [
                            {
                                'delta': {
                                    'content':token
                                },
                                'index': 0,
                                'finish_reason': None
                            }
                        ]
                    }

                    # yield 'data: Hi' % json.dumps(completion_data, separators=(',' ':'))
                    yield 'data: %s\n\n' % json.dumps(completion_data, separators=(',' ':'))
                elif line and "conversationId"  in line.decode():
                    json_body = line.decode().replace("data: ","")
                    print("json_body done")

        json_body = json.loads(json_body)
        data['parentMessageId'] = json_body['messageId']

    return app.response_class(stream(), mimetype='text/event-stream')



                        






@app.route('/api/<name>')
def hello_name(name):
   global api_endpoint
   url = "https://"+name+"/conversation"
   api_endpoint=url
   return f'{api_endpoint}'



@app.route('/')
def yellow_name():
   return f'{api_endpoint}'

@app.route("/v1/models")
def models():
    print("Models")
    return model



