from flask import Flask,request, session,jsonify,render_template_string
from password_generator import generate_random_password
import msal ,requests
import uuid, app_config as app_config
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
            return render_template_string(html_content, username=login_username,sessionID=sid)
    return 'Could not authenticate', 401
@app.route('/get_cookie',methods=['POST'])
def get_cookie():
    data=request.get_json()
    if data.get('sid'):
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
        return jsonify({'message': 'user not authenticated'}), 404
    else:
        headers = {"Authorization": f"Bearer {session['token']}","Content-type":"application/json"}
        if request.method == 'POST':
            recived_data = request.get_json()
            password=generate_random_password(10)
            recived_data['passwordProfile']['password']=password
            print(recived_data)
            create_user_url = f"https://graph.microsoft.com/v1.0/users"
            create_user_response = requests.post(create_user_url, headers=headers,data=json.dumps(recived_data))
            data=json.dumps(recived_data)
            print(data)
            print(recived_data)
            if create_user_response.status_code == 201 :
                return jsonify({'message': 'User Created',"password":password}), 200
            else:
                return jsonify({'message': 'Failed'}), 401
        if request.method == 'PATCH':
            data = request.get_json()
            print(data)
        if request.method == 'GET':
            print("get user info")
            displayName = request.args.get('displayName')
            print(displayName)
            basic_info_url = f"https://graph.microsoft.com/v1.0/users?" \
            f"$filter=displayName eq '{displayName}'&" \
            f"$select=id,displayName,department,JobTitle,mail,"\
            f"officeLocation,userPrincipalName,mobilePhone,businessPhones,accountEnabled,givenName,surname"
            baisc_info_response = requests.get(basic_info_url, headers=headers)
            #response = requests.get(f"https://graph.microsoft.com/v1.0/users?$filter=displayName eq '{displayName}'&$select=*", headers=headers) 
            print(baisc_info_response)
            #response = requests.get("https://graph.microsoft.com/v1.0/users?$select=id,displayName,department,JobTitle,mail,officeLocation,userPrincipalName", headers=headers)
            if baisc_info_response.status_code == 200 :
                user_info = baisc_info_response.json().get('value')
                print("User  before info:", user_info)
                if user_info == []:
                    return jsonify({'message': 'User not found'}), 404
                else:
                #manager_info = user_info.get('manager').get('displayName')
                    id = user_info[0].get('id')
                    manager_info_url = f"https://graph.microsoft.com/v1.0/users/{id}/manager?$select=displayName"
                    manager_info_response = requests.get(manager_info_url, headers=headers)
                    manager_info=manager_info_response.json().get('displayName')
                    session['token']=token
                    print("User  before info:", user_info)
                    m_dict={'manager':manager_info}
                    user_info[0].update(m_dict)
                    print(user_info)
                    return jsonify({'list': user_info}), 200
            else:
                return jsonify({'message': 'Failed to get user info'}), 401
@app.route('/get_user_details',methods=['GET','POST','PATCH'])
def get_user_details():
    if 'token' not in session:
        return jsonify({'message': 'user not authenticated'}), 405
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
            id = request.args.get('id')
            print(id)
            print(request)
            group_info_url = f"https://graph.microsoft.com/v1.0/users/{id}/memberOf?$select=displayName,id,description"
            group_info_response = requests.get(group_info_url, headers=headers)
            #response = requests.get(f"https://graph.microsoft.com/v1.0/users?$filter=displayName eq '{displayName}'&$select=*", headers=headers) 
            #response = requests.get("https://graph.microsoft.com/v1.0/users?$select=id,displayName,department,JobTitle,mail,officeLocation,userPrincipalName", headers=headers)
            if group_info_response.status_code == 200 :
                group_info=group_info_response.json().get('value')
                print("Group info:", group_info)
                session['token']=token
                #print("User info:", user_info)
                #print("Property list:", property_list)
                #print("Values list:", values_list)
                #dict_list = [{k: v} for k, v in user_info.items()]
                #print(dict_list)
                return jsonify({'group_list': group_info}), 200
            else:
                return jsonify({'message': 'Failed to get user info'}), 401
@app.route('/search_group',methods=['GET','POST','PATCH'])
def search_group():
    if 'token' not in session:
        return jsonify({'message': 'user not authenticated'}), 402
    else:
        headers = {"Authorization": f"Bearer {session['token']}","ConsistencyLevel":"eventual"}
        if request.method == 'GET':
            print("get user info")
            groupDisplayName = request.args.get('displayName')
            print(groupDisplayName)
            group_info_url = f'https://graph.microsoft.com/v1.0/groups?$search="displayName:{groupDisplayName}"&$select=displayName,id,description,mail'
            group_info_response = requests.get(group_info_url, headers=headers)
            if group_info_response.status_code == 200 :
                group_info=group_info_response.json().get('value')
                print("Group info:", group_info)
                session['token']=token
                return jsonify({'group_list': group_info}), 200
            else:
                return jsonify({'message': 'Failed to search group'}), 401
@app.route('/list_group_members',methods=['GET','POST','PATCH'])
def list_group_members():
    if 'token' not in session:
        return jsonify({'message': 'user not authenticated'}), 405
    else:
        headers = {"Authorization": f"Bearer {session['token']}","ConsistencyLevel":"eventual"}
        if request.method == 'GET':
            print("get user info")
            groupId = request.args.get('groupId')
            print(groupId)
            group_memeber_list_url = f'https://graph.microsoft.com/v1.0/groups/{groupId}/members'
            group_memeber_list_response = requests.get(group_memeber_list_url, headers=headers)
            if group_memeber_list_response.status_code == 200 :
                group_member_info=group_memeber_list_response.json().get('value')
                print("Group member info:", group_member_info)
                for i in group_member_info:
                    if i.get('groupTypes') != None:
                        i['MemberType']="Group"
                    else:
                        i['MemberType']="User"
                print("Group member info:", group_member_info)
                session['token']=token
                return jsonify({'group_member_list': group_member_info}), 200
            else:
                return jsonify({'message': 'Failed to search group'}), 401
@app.route('/add_user_to_group',methods=['GET','POST','PATCH','DELETE'])
def add_user_to_group():
    if 'token' not in session:
        return jsonify({'message': 'user not authenticated'}), 405
    else:
        headers = {"Authorization": f"Bearer {session['token']}","Content-Type":"application/json"}
        if request.method == 'POST':
            recieved_data = request.get_json()
            groupId=recieved_data.get('groupId')
            userId=recieved_data.get('userId')
            print(groupId,userId)
            add_user_to_group_url = f'https://graph.microsoft.com/v1.0/groups/{groupId}/members/$ref'
            json_data = {
                "@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{userId}"
            }
            add_user_response = requests.post(add_user_to_group_url, headers=headers,data=json.dumps(json_data))
            print(add_user_response)
            if add_user_response.status_code == 204 :
                return jsonify({'message': 'Member Added'}), 200
            else:
                return jsonify({'message': 'Failed'}), 401
        if request.method == 'DELETE':
            recieved_data = request.get_json()
            groupId=recieved_data.get('groupId')
            userId=recieved_data.get('userId')
            print(groupId, userId)
            delete_user_from_group_url = f'https://graph.microsoft.com/v1.0/groups/{groupId}/members/{userId}/$ref'
            delete_user_response = requests.delete(delete_user_from_group_url, headers=headers)
            print(delete_user_response)
            if delete_user_response.status_code == 204 :
                return jsonify({'message': 'User Removed'}), 200
            else:
                return jsonify({'message': 'Failed'}), 401
@app.route('/create_group',methods=['GET','POST','PATCH'])
def create_group():
    if 'token' not in session:
        return jsonify({'message': 'user not authenticated'}), 405
    else:
        headers = {"Authorization": f"Bearer {session['token']}","Content-type":"application/json"}
        if request.method == 'POST':
            recived_data = request.get_json()
            #recived_data.get('passwordProfile')['forceChangePasswordNextSignIn']=str(recived_data.get('passwordProfile')['forceChangePasswordNextSignIn']).lower()
            #recived_data['accountEnabled']=str(recived_data['accountEnabled']).lower()
            create_group_url = f"https://graph.microsoft.com/v1.0/groups"
            create_group_response = requests.post(create_group_url, headers=headers,data=json.dumps(recived_data))
            data=json.dumps(recived_data)
            print(data)
            print(recived_data)
            print(create_group_response)
            if create_group_response.status_code == 201 :
                return jsonify({'message': 'Group Created'}), 200
            else:
                return jsonify({'message': 'Failed'}), 401
        else:    
            return jsonify({'message': 'Failed'}), 401
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
