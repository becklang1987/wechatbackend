import json
file_path="./sd_backend/data.json"
with open(file_path,"r") as f:
    data=json.load(f)
    for i in data:
        print(i.get('id'))