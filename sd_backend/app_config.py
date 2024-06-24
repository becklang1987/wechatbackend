config = {
  "note": "Yo configure either the authority setting when you are using Entra ID or External ID, or the oidc_authority setting when you are using External ID with its custom domain. Change the other one to null",
  "authority": "https://login.microsoftonline.com/6c1bada0-4944-497c-95c2-5bbaeaa88ccc",
  "tenant_id": "6c1bada0-4944-497c-95c2-5bbaeaa88ccc",
  "client_id":"3122bdef-d615-4d3d-a59c-0d0edcc2a0a7",
  #"client_id": "993bc9b9-49b0-4aeb-bf9b-4421d22bf65b",#lab_app_appid
  "scope": [ "https://graph.microsoft.com/.default" ],
  "endpoint": "https://graph.microsoft.com/v1.0/users",
  "REDIRECT_URI" :'https://b6a0-240e-39a-edf-bc80-bd26-acca-49dd-3bb2.ngrok-free.app/callback'
}
