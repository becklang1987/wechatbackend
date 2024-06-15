from flask import Flask, jsonify, request
from netmiko import ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException
import re

# Create a new Flask web application instance
configAPI = Flask(__name__)

# Define an endpoint '/show' that will accept POST requests
@configAPI.route('/show', methods=['POST'])
def set_config():
    # Get JSON data from the request
    data = request.get_json()
    
    # Define device configuration details using data received from the request
    device_config = {
        'device_type': 'cisco_ios',       # Device type is Cisco IOS
        'host': '192.168.1.45',           # Device IP address
        'username': data.get('username'), # Username from request data
        'password': data.get('password'), # Password from request data
        'port': 22                        # SSH port number
    }
    
    # Fetch the command and config values from the request data
    command = data.get('command')
    config = data.get('config')
    
    # Compile regular expressions to match permitted commands and forbidden configurations
    cmdpattern = re.compile(r'^( *show| *ping| *traceroute| *trace| *sh)', re.IGNORECASE)
    cfgpattern = re.compile(r'(.*res.*|.*reload|.*boot|.*delete|^[0-9])', re.IGNORECASE)
    
    # If a command is provided
    if command:
        # Check if the command matches the permitted command pattern
        if cmdpattern.match(command):
            # Establish SSH connection using Netmiko
            net_connect = ConnectHandler(**device_config)
            # Execute the command and capture the output
            output = net_connect.send_command(command)
            print(command)  # Print the command to the server logs
            print(output)   # Print the output to the server logs
            # Disconnect the SSH session
            net_connect.disconnect()
            # Return the output as a JSON response
            return jsonify({'output': output})
        elif command:
            # If the command is invalid, return an error response
            return jsonify({'output': 'Invalid command'})

    # If a configuration is provided
    elif config:
        # Check if the configuration matches any forbidden patterns
        if cfgpattern.match(config):
            # If the configuration is forbidden, return an error response
            return jsonify({'output': 'Invalid command'})
        elif config:
            # Split the configuration into multiple lines and create a list
            configSet = config.split('\n')
            # Establish SSH connection using Netmiko
            net_connect = ConnectHandler(**device_config)
            # Apply the configuration lines and capture the output
            output = net_connect.send_config_set(configSet)
            print(configSet)  # Print the configuration lines to the server logs
            # Disconnect the SSH session
            net_connect.disconnect()
            # Return the output as a JSON response
            return jsonify({'output': output})
    
    # If neither command nor configuration is provided, return an error response
    elif not config or not command:
            return jsonify({'output': "Empty command or config"})
    
    # Default case, should not be reached, return an error response
    else:
        return jsonify({'output': 'Invalid command or config'})

# Run the Flask application on host 0.0.0.0, port 5010 in debug mode
if __name__ == '__main__': 
    configAPI.run(host='0.0.0.0', port=5010, debug=True)
