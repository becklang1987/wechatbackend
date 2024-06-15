from flask import Flask, redirect, request, session, url_for
import msal
from msgraph.core import GraphClient
import uuid

config = {
  "note": "You configure either the authority setting when you are using Entra ID or External ID, or the oidc_authority setting when you are using External ID with its custom domain. Change the other one to null",
  "authority": "https://login.microsoftonline.com/6c1bada0-4944-497c-95c2-5bbaeaa88ccc",
  "client_id": "993bc9b9-49b0-4aeb-bf9b-4421d22bf65b",
  "scope": [ "https://graph.microsoft.com/.default" ],
  "secret": "MNR8Q~4ZM8XKwjOEVaIs8ifHoXqk5NgG4g8XYaRc",
  "endpoint": "https://graph.microsoft.com/v1.0/users",
  "REDIRECT_URI" :'http://localhost:5000/callback' 
}
msal_app = msal.ConfidentialClientApplication(
    config["client_id"],
    authority=config.get("authority"),  # For Entra ID or External ID,
    client_credential=config["secret"],
    # token_cache=...  # Default cache is in memory only.
                       # You can learn how to use SerializableTokenCache from
                       # https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
    )
result = None

app = Flask(__name__)
app.secret_key = 'your_session_secret_key'

# 配置 Azure AD 应用程序详情
CLIENT_ID = 'your-client-id'
CLIENT_SECRET = 'your-client-secret'
TENANT_ID = 'your-tenant-id'
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
REDIRECT_URI = 'http://localhost:5000/callback'  # 根据实际情况调整
SCOPE = ['User.Read']

# 初始化 MSAL 应用程序
msal_app = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return f'Hello, {session["user"]["name"]}! <a href="/logout">Logout</a>'

@app.route('/login')
def login():
    auth_url = msal_app.get_authorization_request_url(
        SCOPE,
        state=str(uuid.uuid4()),
        redirect_uri=REDIRECT_URI)
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        result = msal_app.acquire_token_by_authorization_code(
            code,
            scopes=SCOPE,
            redirect_uri=REDIRECT_URI)
        if 'access_token' in result:
            session['access_token'] = result['access_token']
            session['user'] = msal_app.get_accounts()[0]  # 获取用户信息
            return redirect(url_for('profile'))
    return 'Could not authenticate', 401

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
    session.clear()
    return redirect(f"{AUTHORITY}/oauth2/v2.0/logout?post_logout_redirect_uri={url_for('index', _external=True)}")

if __name__ == '__main__':
    app.run(port=5000)