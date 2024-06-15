import asyncio
import websockets
import paramiko
from io import StringIO

# SSH 服务器配置信息


async def handle_client(websocket, path):
    # 初始化 SSH 客户端
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 连接 SSH 服务器
        ssh.connect(hostname=hostname, port=22, username=username, password=password,look_for_keys=False)
        chan = ssh.invoke_shell()
        
        async def send_data():
            # 持续接收来自 SSH 的数据并发送给客户端
            while True:
                if chan.recv_ready():
                    data = chan.recv(1024).decode('utf-8')
                    await websocket.send(data)
                await asyncio.sleep(0.1)
        
        # 启动一个任务来发送数据
        asyncio.create_task(send_data())
        
        async for message in websocket:
            chan.send(message + '\n')  # 将来自客户端的消息发送到 SSH Shell
        
    except Exception as e:
        print(f"SSH connection error: {e}")
    finally:
        ssh.close()

start_server = websockets.serve(handle_client, "localhost", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()