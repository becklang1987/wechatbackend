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

import requests

#TENANT_ID = 'your-tenant-id'
#CLIENT_ID = 'your-client-id'
#CLIENT_SECRET = 'your-client-secret'
#USERNAME = 'user@example.com'
#PASSWORD = 'user-password'
#SCOPE = 'https://graph.microsoft.com/.default'

TOKEN_URL = f'https://login.microsoftonline.com/{config["authority"]}/oauth2/v2.0/token'

'''
data = {
    'grant_type': 'password',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'username': USERNAME,
    'password': PASSWORD,
    'scope': SCOPE
}
'''
response = requests.post(TOKEN_URL, data=config)
response_data = response.json()

if 'access_token' in response_data:
    access_token = response_data['access_token']
    print(f"Access Token: {access_token}")

    # 使用访问令牌调用 Microsoft Graph API 示例
    graph_url = 'https://graph.microsoft.com/v1.0/me'
    headers = {'Authorization': f'Bearer {access_token}'}
    graph_response = requests.get(graph_url, headers=headers)
    print(graph_response.json())
else:
    print(f"Error: {response_data.get('error_description', 'Unknown error')}")