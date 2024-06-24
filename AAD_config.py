from flask import Flask, redirect, request, session, url_for,jsonify,render_template_string,make_response
import msal ,asyncio,requests
from msgraph import GraphServiceClient

from azure.identity import ClientSecretCredential
import uuid,sd_backend.app_config as app_config
import json
app=Flask(__name__)
app.secret_key = 'your_session_secret_key'


@app.route('/get_user',methods=['GET','POST','PATCH'])
def get_user():
    if 'token' not in session:
        return jsonify({'message': 'user not authenticated'}), 401
    else:
        token = session['token']
        get_agrs = request.args
        headers = {"Authorization": f"Bearer {session['token']}"}
        if request.method == 'POST':
            data = request.get_json()
            print(data)
        if request.method == 'PATCH':
            data = request.get_json()
            print(data)
        if request.method == 'GET':
            print("get user info")
            response = requests.get(f"https://graph.microsoft.com/v1.0/users/{get_agrs}", headers=headers)
            if response.status_code == 200:
                user_info = response.json().get('value')
                print("User info:", user_info)
                #property_list = list(user_info.keys())[1:] # 使用 list(item.keys())[0] 获取每个字典的唯一键
                #values_list = list(user_info.values())[1:]
                session['token']=token
                #print("User info:", user_info)
                #print("Property list:", property_list)
                #print("Values list:", values_list)
                #dict_list = [{k: v} for k, v in user_info.items()]
                #print(dict_list)
                return jsonify({'list': user_info}), 200
            else:
                return jsonify({'message': 'Failed to get user info'}), 401