from flask import Flask, redirect, request, session, url_for,jsonify,render_template_string,make_response
import msal ,asyncio,requests
from msgraph import GraphServiceClient

from azure.identity import ClientSecretCredential
import uuid,app_config
import json


msal_app = msal.ConfidentialClientApplication(
    app_config.config.get("client_id"),
    authority=app_config.config.get("authority"),  # For Entra ID or External ID,
    client_credential=app_config.config.get("secret"),
    # token_cache=...  # Default cache is in memory only.
                       # You can learn how to use SerializableTokenCache from
                       # https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
    )
result = None
sid=None
token=None
Credentials=ClientSecretCredential(app_config.config.get("tenant_id"), app_config.config.get("client_id"), app_config.config.get("secret"))
app = Flask(__name__)
app.secret_key = 'your_session_secret_key'
# 配置 Azure AD 应用程序详情

# 初始化 MSAL 应用程序
current_session_id=None
current_session_username=None
@app.route('/')
def index():
    global current_session_id
    print("123")
    #if 'user' not in session:
        #return redirect(url_for('login'))
    session['id']=str(uuid.uuid4())
    current_session_id=session['id']
    return f'Hello, {session["id"]}!'
@app.route('/login')
def login():
    auth_url = msal_app.get_authorization_request_url(
        app_config.config.get("scope"),
        state=str(uuid.uuid4()),
        redirect_uri=app_config.config.get("REDIRECT_URI"),
        prompt='login')
    print(auth_url)
    print(session)
    #return f"Hello agin,{session['id']}"
    if "id" in session and session['id']==current_session_id:
        print('sid is:'+session['id'],'csid is:'+current_session_id)
        return auth_url,200
    else:
        return jsonify({'message': 'user not exist or sid error'}), 401

@app.route('/callback')
def callback():
    global result,sid,token
    code = request.args.get('code')
    print("received code")
    if code:
        result = msal_app.acquire_token_by_authorization_code(
            code,
            scopes=app_config.config.get("scope"),
            redirect_uri=app_config.config.get("REDIRECT_URI"))
        if 'access_token' in result:
            token = result['access_token']
            login_username= msal_app.get_accounts()[0]['username'] 
            sid=str(uuid.uuid4())
            print(login_username)# 用户信息'
            #return jsonify ({'message': 'Authentication successful'}), 200
            html_content ="""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Callback</title>
                    <script src="https://res.wx.qq.com/open/js/jweixin-1.3.2.js"></script>
                    <script type="text/javascript">
                        window.onload = function() {
                            // 检查当前环境是否在小程序中
                            if (typeof wx !== 'undefined' && wx.miniProgram) {
                                wx.miniProgram.postMessage({ data: { 
                                    message: "Authentication successful", 
                                    username: "{{username}}", 
                                    sid: "{{sessionID}}"
                                }});

                                // 使用 wx.miniProgram.navigateBack 或 wx.miniProgram.redirectTo 返回小程序页面
                                wx.miniProgram.switchTab({ url: '/pages/home/home' });
                            }
                        }
                    </script>
                </head>
                <body>
                </body>
                </html>
            """ 
            #render_template_string(html_content, user_info=session['user'],session_id=sessionID)
            #response = make_response(render_template_string(html_content, username=login_username, sessionID=sid))
            #response.set_cookie('username', login_username, httponly=True, secure=True)
            #response.set_cookie('sid', sid, httponly=True, secure=True)
            #return response
            return render_template_string(html_content, username=login_username,sessionID=sid)
            #return jsonify({f'message': 'Authentication successful', 'Logged In As User': session['user']['username']})
    return 'Could not authenticate', 401
@app.route('/get_cookie',methods=['POST'])
def get_cookie():
    data=request.get_json()
    if data.get('sid') and data.get('sid')==sid:
        session['sid']=data.get('sid')
        session['token']=token
        return jsonify({'message': 'Cookie set successfully'}), 200
    else:
        return jsonify({'message': 'Cookie not set or sid error'}), 401
@app.route('/validation',methods=['POST'])
def validation():
    data=request.get_json()
    print(data)
    user=data.get('user')
    sid=data.get('sid')
    username=data.get('username')
    #username=session.get('user')['username']
    print('user is :',username)
    if username and sid:
        print("user and sid exist")
        print(username,sid,current_session_username,current_session_id)
        if username==current_session_username and sid==current_session_id:
            return jsonify({'message': 'user authencated'}), 200
        return jsonify({'message': 'session id or username do not match'}), 401
    else:
        print("user or sid not exist")
        return jsonify({'message': 'user not exist or sid error'}), 401
@app.route('/get_user',methods=['GET','POST','PATCH'])
def get_user():
    if 'token' not in session:
        return jsonify({'message': 'user not authenticated'}), 401
    else:
        headers = {"Authorization": f"Bearer {session['token']}"}
        if request.method == 'POST':
            data = request.get_json()
            print(data)
        if request.method == 'PATCH':
            data = request.get_json()
            print(data)
        if request.method == 'GET':
            print("get user info")
            response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
            if response.status_code == 200:
                user_info = response.json()
                property_list = list(user_info.keys())  # 使用 list(item.keys())[0] 获取每个字典的唯一键
                values_list = list(user_info.values()) 
                session['token']=token
                print("User info:", user_info)
                print("Property list:", property_list)
                print("Values list:", values_list)
                dict_list = [{k: v} for k, v in user_info.items()]
                print(dict_list)
                return jsonify({'plist':property_list,'vlist':values_list}), 200
            else:
                return jsonify({'message': 'Failed to get user info'}), 401

        #graph_client = GraphServiceClient(credentials=Credentials,scopes=app_config.config.get("scope"))
        #async def get_user_info():
            #user_info = await graph_client.me.get()
        #return asyncio.run(get_user_info())
'''
@app.route('/profile')
def profile():
    if 'access_token' not in session:
        return redirect(url_for('login'))
    access_token = session['access_token']
    graph_client = GraphClient(credential=access_token)
    user_info = graph_client.get('/me').json()
    return f'User Profile: {user_info} <br><a href="/">Home</a>'

@app.route('/logout')
def logout():
    print(session)
    session.clear()
    print(session)
    return f"{config['authority']}/oauth2/v2.0/logout?post_logout_redirect_uri={url_for('index', _external=True)}"
'''
if __name__ == '__main__':
    app.run(port=5020,debug=True,host='0.0.0.0')#ssl_context=('server.crt', 'server.key'))

#