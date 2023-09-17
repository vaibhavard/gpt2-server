import re
from helper import prompt1
import base64
import requests
def mm(graph): 
    graph=graph.replace("mermaid","")
    graph=graph.replace("markdown","")

    pattern = r"```(.+?)```"
    match = re.search(pattern, graph, flags=re.DOTALL)
    if match: 
        graph = match.group(1)
        print(graph)
    else: 
        print("No match found")
        return "Error.Try Again."
    graphbytes = graph.encode("ascii")
    base64_bytes = base64.b64encode(graphbytes)
    base64_string = base64_bytes.decode("ascii")
    return "![]"+"("+"https://mermaid.ink/img/" + base64_string+")"

def extract_links(text):
    # Regular expression pattern to match URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    # Find all matches of the URL pattern in the text
    urls = re.findall(url_pattern, text)
    return urls

def allocate(messages,data,uploaded_image,processed_text,systemp):
    data['message']= messages[-1]['content']
    print(data["message"])
    if systemp:
      data["systemMessage"]=messages[0]["content"]
    else:
      data["systemMessage"]=prompt1

    links = extract_links(data['message'])
    if links!= [] :
      print(links[0])
      data["imageURL"]=links[0]
    elif uploaded_image!="":
      data["imageBase64"]=uploaded_image
      print("UPLOADING IMAGE..")
    elif processed_text !="":
        data["context"]=processed_text

def check(api_endpoint):
    try:
        xx = requests.get(api_endpoint.replace("/conversation",""),timeout=15)
        print(xx.text)
        return "" 
    except :
        return "gpt-3"
        pass



