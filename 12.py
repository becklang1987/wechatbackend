from flask import Flask, request, jsonify  
from flask_socketio import SocketIO, emit  
import paramiko  
import uuid  
import threading  
import logging

logging.basicConfig(level=logging.INFO)

  
app = Flask(__name__)  
app.config['SECRET_KEY'] = 'secret!'  
socketio = SocketIO(app, cors_allowed_origins="*",logger=True,engineio_logger=True)
socketio = SocketIO(app)
  
# 存储SSH参数的字典  
ssh_parameters = {}  
# 存储SSH客户端对象的字典  
ssh_shells= {}  
@app.route('/')
def index():
    return 'Hello, this is the Flask-SocketIO server.'
@app.route('/get_websocket_parameter', methods=['POST'])  
def get_parameter():  
    data = request.get_json()  
    username = data.get('username')  
    password = data.get('password')  
    hostname = data.get('hostname')  
    token = str(uuid.uuid4())  
    if not all([username, password, hostname]):  
        return jsonify({'status': 'error', 'message': 'Missing parameters'}), 400  
    ssh_parameters[token] = {'username': username, 'password': password, 'hostname': hostname}
    print(ssh_parameters)
    return jsonify({'token': token}), 200  

@socketio.on('connect')  
def connect():  
    # 客户端连接时不需要立即执行任何操作
    logging.info('连接成功')
    pass  
@socketio.on('start_ssh')  
def start_ssh(data):  
    token = data['token']  
    if token not in ssh_parameters:  
        emit('ssh_error', {'message': 'Invalid token'})  
        return  
      
    ssh_info = ssh_parameters[token]  
    client = paramiko.SSHClient()  
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
    try:  
        client.connect(hostname=ssh_info['hostname'], username=ssh_info['username'], password=ssh_info['password'])  
        shell = client.invoke_shell()  
        ssh_shells[token] = {'client': client, 'shell': shell}  
        emit('ssh_started', {'status': 'SSH connection and shell started'})  
    except Exception as e:  
        emit('ssh_error', {'message': str(e)})  
  
@socketio.on('send_shell_command')  
def send_shell_command(data):  
    token = data['token']  
    command = data['command'] + '\n'  
    if token not in ssh_shells:  
        emit('shell_error', {'message': 'No SSH shell found for the given token'})  
        return  
      
    shell = ssh_shells[token]['shell']  
    shell.send(command)  
    # 这里可以添加代码来读取 shell 的输出并发送给客户端  
  
@socketio.on('disconnect')  
def disconnect():  
    # ...（与之前类似，但关闭 shell 和客户端）  
    for token, shell_info in list(ssh_shells.items()):  
        shell_info['shell'].close()  
        shell_info['client'].close()  
        del ssh_shells[token]  
        print(f"SSH shell and connection for token {token} has been closed.")  
  
# 添加一个后台任务来读取 shell 输出  
def read_shell_output(token):  
    shell = ssh_shells[token]['shell']  
    while True:  
        if token not in ssh_shells:  
            break  
        if shell.recv_ready():  
            output = shell.recv(65535).decode('utf-8')  
            socketio.emit('shell_output', {'output': output, 'token': token})  
  
# 当 SSH shell 启动时，启动一个后台线程来读取输出  
@socketio.on('ssh_started')  
def on_ssh_started(data):  
    token = data.get('token')  
    if token:  
        thread = threading.Thread(target=read_shell_output, args=(token,))  
        thread.daemon = True  
        thread.start()  
  
if __name__ == '__main__':  
    socketio.run(app, debug=True, host='0.0.0.0',port=5005,allow_unsafe_werkzeug=True)

