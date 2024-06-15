import asyncio
import websockets
import paramiko
import uuid
from flask import Flask, request, jsonify
import threading
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# 存储SSH参数的字典
ssh_parameters = {}
# 存储SSH客户端对象的字典
ssh_shells = {}
# 存储WebSocket连接的字典
ws_connections = {}


@app.route('/')
def index():
    return 'Hello, this is the WebSocket server.'


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


async def handle_client(websocket, path):
    logging.info('WebSocket连接成功')

    async for message in websocket:
        data = json.loads(message)
        event = data['event']

        if event == 'start_ssh':
            token = data['token']
            await start_ssh(websocket, token)
        elif event == 'send_shell_command':
            token = data['token']
            command = data['command']
            await send_shell_command(websocket, token, command)
        elif event == 'disconnect':
            await disconnect(websocket)


async def start_ssh(websocket, token):
    if token not in ssh_parameters:
        await websocket.send(json.dumps({'event': 'ssh_error', 'message': 'Invalid token'}))
        return

    ssh_info = ssh_parameters[token]
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ssh_info['hostname'], username=ssh_info['username'], password=ssh_info['password'])
        shell = client.invoke_shell()
        ssh_shells[token] = {'client': client, 'shell': shell}
        ws_connections[token] = websocket
        await websocket.send(json.dumps({'event': 'ssh_started', 'status': 'SSH connection and shell started'}))

        threading.Thread(target=read_shell_output, args=(token,), daemon=True).start()
    except Exception as e:
        await websocket.send(json.dumps({'event': 'ssh_error', 'message': str(e)}))


async def send_shell_command(websocket, token, command):
    if token not in ssh_shells:
        await websocket.send(json.dumps({'event': 'shell_error', 'message': 'No SSH shell found for the given token'}))
        return

    shell = ssh_shells[token]['shell']
    shell.send(command + '\n')


async def disconnect(websocket):
    tokens_to_remove = [token for token, ws in ws_connections.items() if ws == websocket]
    for token in tokens_to_remove:
        if token in ssh_shells:
            ssh_shells[token]['shell'].close()
            ssh_shells[token]['client'].close()
            del ssh_shells[token]
        del ws_connections[token]
        print(f"SSH shell and connection for token {token} has been closed.")


def read_shell_output(token):
    shell = ssh_shells[token]['shell']
    websocket = ws_connections[token]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while token in ssh_shells and websocket.open:
        if shell.recv_ready():
            output = shell.recv(65535).decode('utf-8')
            coroutine = websocket.send(json.dumps({'event': 'shell_output', 'output': output, 'token': token}))
            future = asyncio.run_coroutine_threadsafe(coroutine, loop)
            future.result()


def run_websocket_server():
    start_server = websockets.serve(handle_client, "0.0.0.0", 5005)
    asyncio.get_event_loop().run_until_complete(start_server)
    logging.info(f"WebSocket Server started on ws://0.0.0.0:5005")
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    threading.Thread(target=run_websocket_server, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5010)