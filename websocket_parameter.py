from flask import Flask, request, jsonify

import param

app = Flask(__name__)
# 全局变量存储参数
ssh_parameters = {}

@app.route('/parameter', methods=['POST'])
def get_parameter():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    hostname = data.get('hostname')
    command = data.get('command')
    if not (username and password and hostname):
        return jsonify({'status': 'error', 'message': 'Missing parameters'}), 400
    #param.interactive_shell(username, password, hostname).send_command(command)
    print(username, password, hostname, command)
    return jsonify({'status': 'success', 'message': 'Command executed successfully'}), 200

if __name__ == '__main__': 
    app.run(debug=True,host='0.0.0.0',port=5005)

