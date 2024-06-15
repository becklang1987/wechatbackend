import paramiko
import time

def interactive_shell(host, port, username, password):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, port=port, username=username, password=password,look_for_keys=False)
        
        # 打开交互式 shell
        shell = client.invoke_shell()
        
        # 为清晰起见设置 shell 的宽与高
        shell.resize_pty(width=80, height=24)

        # 小暂停以让路由器输出欢迎信息
        time.sleep(1)
        
        # 清除欢迎信息
        if shell.recv_ready():
            output = shell.recv(10000).decode('utf-8')
            print(output, end="")

        # 发送命令的函数，将会打印和接收 shell 输出
        def send_command(command):
            shell.send(command + '\n')
            time.sleep(1)  # 等待命令执行
            while shell.recv_ready():
                output = shell.recv(10000).decode('utf-8')
                print(output, end="")
        
        # 发送并显示命令
        send_command("show version")
        
        # 保持 shell 交互
        while True:
            cmd = input("")
            if cmd.lower() in ["exit", "quit"]:
                break
            send_command(cmd)
            
    except paramiko.AuthenticationException as auth_err:
        print(f"Authentication failed: {auth_err}")
    except paramiko.SSHException as ssh_err:
        print(f"SSH connection error: {ssh_err}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

# 尝试连接到 Cisco 路由器
