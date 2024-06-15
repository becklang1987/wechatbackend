from netmiko import ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException
import time
# 定义设备连接信息
CR01_device_config = {
    'device_type': 'cisco_ios',
    'host': host,
    'username': usernmae,
    'password': password,
    'port': 22
}

def execute_cli_commands(device_config, commands):
    try:
        print(f"Connecting to {device_config['host']} on port {device_config['port']} with username {device_config['username']}")

        # 连接到设备
        net_connect = ConnectHandler(**device_config)

        # 进入配置模式并执行配置命令
        output = net_connect.send_config_set(commands)
        
        print(f"Command output: {output}")

        obj = time.gmtime()
        time_str = time.asctime(obj)
        # 保存配置
        save_output = net_connect.save_config()
        print(f"Save output: {save_output}")
        with open('output_file', 'a') as file:
            file.write(f"####Alert triggered ,automatically deploy PBR to CR01, starting at:{time_str}###\n")
            file.write(f"Command output for {device_config['host']}:\n")
            file.write(output + "\n")
            file.write(f"#######")

        # 断开连接
        net_connect.disconnect()

    except NetMikoAuthenticationException as auth_error:
        print(f"Authentication failed: {auth_error}")
    except NetMikoTimeoutException as timeout_error:
        print(f"Connection timed out: {timeout_error}")
    except Exception as e:
        print(f"An error occurred: {e}")

# 示例 CLI 命令列表
cli_command_set1 = [
    "access-list 110 permit ip 192.168.100.0 0.0.0.255 host 1.1.1.1",
    "route-map pbr01 permit 10",
    "match ip address 110",
    "set ip next-hop 10.139.255.127"
]
cli_command_set2 = [
    "no route-map pbr01 permit 10"