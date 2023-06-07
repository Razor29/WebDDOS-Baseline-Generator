import random
import requests
import json
import time
import sys
import base64
from os import path

__folder__ = path.abspath(path.dirname(__file__))
session = requests.session()
def to_base64(data):
    return base64.b64encode(data).decode('utf-8')

def split_key_value(single_value_dict):
    key = list(single_value_dict.keys())[0]
    value = single_value_dict[key]
    return key, value

def generate_random_public_ipv4_address():
    first_octet = random.randint(1, 223)

    while True:
        second_octet = random.randint(0, 255)
        third_octet = random.randint(0, 255)

        if (second_octet == 10) or (second_octet == 172 and (third_octet >= 16 and third_octet <= 31)) or (second_octet == 192 and third_octet == 168):
            continue
        break

    fourth_octet = random.randint(1, 100)
    return f"{first_octet}.{second_octet}.{third_octet}.{fourth_octet}"

def build_request(xff, baseURL, user_agent ,ip, request_info):
    if "@num1" in request_info['uri']:
        request_info['uri'] = request_info['uri'].replace("@num1", str(random.randint(1,199)))
    if "@num2" in request_info['uri']:
        request_info['uri'] = request_info['uri'].replace("@num2", str(random.randint(1,40)))
    request_info['headers'] = request_info.get('headers', {})
    request_info['headers']["Host"] = baseURL[baseURL.find('//')+2:]
    request_info['headers']["User-Agent"] = user_agent
    request_info['headers'][xff] = ip
    request_info['url'] = baseURL + request_info['uri']
    return request_info

def session_requests(request_info, body={}, body_json=False ,xff="", ip=""):
    method = request_info['method']
    headers = request_info.get('headers', {})
    auth = request_info.get('auth', None)
    url = request_info['url']

    if not body:
        body = request_info.get('body', None)

    if auth == "api auth basic":
        headers['Authorization'] = "Basic dGVzdF91c2VyOjEyMzQ1Ng=="
        response = session.post(url, headers=headers)
        authorization_token = response.json()["token"]
        session.headers.update({"Authorization": f"Token {authorization_token}"})
        status_code = int(response.status_code)
        return status_code

    elif auth == "web auth form":
        response = session.post(url, headers=headers, data=body)
        session.cookies.update(response.cookies)
        status_code = int(response.status_code)
        return status_code

    else:
        try:
            session.headers.update({xff: ip})
            session.headers.update({"Host": headers['Host']})
            session.headers.update({"User-agent": headers['User-Agent']})

            if body_json:
                response = getattr(session, method.lower())(url, json=body)
            else:
                response = getattr(session, method.lower())(url, data=body)

            status_code = int(response.status_code)
            
            #print(f"Request: {method} {url}")
            #print("Headers:")
            #print(headers)
            #print(f"Body: {body}")
            #print()
            
            #print(f"Response: {status_code} {response.reason}")
            #print("Headers:")
            #print(dict(response.headers))
            #print("Body:")
            #try:
            #    print(response.json())
            #except json.JSONDecodeError:
            #    print(response.text)

            return status_code

        except requests.exceptions.RequestException as e:
            print(e)
            session.close()
        except KeyError as e:
            print(e)
            session.close()

def random_list_item(data_list):
    return data_list[random.randint(0,len(data_list)-1)]

def authenticated_web(data):
    print("authenticated session")
    variables = data['variables'].copy()
    web_traffic = data['web_traffic'].copy()
    ip = generate_random_public_ipv4_address()
    user_agent = random_list_item(variables['user-agents'])
    xff = variables['xff']
    web_list = list(web_traffic.keys())
    session = requests.session()
    req = build_request(xff, variables['url'], user_agent, ip, web_traffic[web_list[0]].copy())
    response_code = session_requests(req, web_traffic[web_list[0]]['body'], xff=xff, ip=ip)

    #print(f"Initial request: {req}")
    print(f"Initial response code: {response_code}")

    web_list = web_list[1:]

    for _ in range(random.randint(2, 30)):
        rand_choice = random.choice(web_list)
        req = build_request(xff, variables['url'], user_agent, ip, web_traffic[rand_choice].copy())
        response_code = session_requests(req, web_traffic[rand_choice]['body'], xff=xff, ip=ip)

        #print(f"Request: {req}")
        print(f"Response code: {response_code}")
        time.sleep(random.randint(2, 15))

    session.close()

def non_authenticated_web(data):
    print("non authenticated session")
    variables = data['variables'].copy()
    web_traffic = data['authenticated_web_traffic'].copy()
    ip = generate_random_public_ipv4_address()
    user_agent = random_list_item(variables['user-agents'])
    xff = variables['xff']
    web_list = list(web_traffic.keys())
    session = requests.session()


    for _ in range(random.randint(1, 30)):
        rand_choice = random.choice(web_list)
        req = build_request(xff, variables['url'], user_agent, ip, web_traffic[rand_choice].copy())
        response_code = session_requests(req, web_traffic[rand_choice]['body'], xff=xff, ip=ip)

        #print(f"Request: {req}")
        print(f"Response code: {response_code}")
        time.sleep(random.randint(2, 15))

    session.close()

if __name__ == "__main__":
    with open(path.join(__folder__, "data.json")) as json_file:
        data = json.load(json_file)
    while True:
        func_list = [non_authenticated_web, authenticated_web]
        
        random.choice(func_list)(data)
        time.sleep(random.randint(10, 400))
