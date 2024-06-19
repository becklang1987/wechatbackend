from flask import Flask, redirect, request, session, url_for,jsonify,render_template_string,make_response
import msal ,asyncio,requests
from msgraph import GraphServiceClient

from azure.identity import ClientSecretCredential
import uuid,app_config
import json
app=Flask(__name__)


@app.route('/',methods=['GET','POST','PATCH'])
def get_user():
    if request.method == 'GET':
        print(request.method)
        print(request.args)
        print(request)
    return jsonify({'code':200,'msg':'success'})

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5030) 