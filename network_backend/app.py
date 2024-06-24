from flask import Flask, jsonify, request,session
from validation import validate_token
import pandas as pd
from netmiko import ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException
import re

# Path to the CSV file containing the device information
file_path = '/Users/honglang/wechat_backend/host_info.csv'

app=Flask(__name__)
app.secret_key = 'your_session_secret_key'

@app.route('/siteList', methods=['GET'])
def get_sitelist():
    print(session)
    if 'sid' in session and 'token' in session:
        data=request.args.to_dict()
        print(data)
        if data.get('region')  == 'APAC':
            siteList=['Singapore', 'Tokyo', 'Sydney', 'Melbourne', 'Brisbane', 'Auckland','ChengduTreat','ChengduCommercial']
        elif data.get('region') == 'EMEA':
            siteList=['Frankfurt', 'Munich', 'Paris', 'Amsterdam', 'London', 'Dublin']
        elif data.get('region') == 'NA':
            siteList=['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia']
        else:
            siteList=['Chengdu', 'Shanghai', 'Beijing', 'Guangzhou', 'Shenzhen', 'Xian']
        return jsonify({'siteList': siteList})
    else:
        return jsonify({'error': 'Unauthorized access'}), 401
import pandas as pd
from flask import Flask, request, jsonify,session

# Path to the CSV file containing the device information
file_path = '/Users/honglang/wechat_backend/host_info.csv'

# Create a new Flask web application instance


def get_devices_by_location(file_path, location):
    """
    Function to get devices by location from a CSV file.
    
    Parameters:
    file_path (str): The path to the CSV file containing device information.
    location (str): The location to filter devices by.
    
    Returns:
    list: A list of dictionaries where each dictionary represents a device.
    """
  
    df = pd.read_csv(file_path)
    
    # Filter the DataFrame for devices at the specified location
    location_df = df[df['Location'] == location]
    
    # Convert the filtered DataFrame to a list of dictionaries
    location_data = location_df.to_dict(orient='records')
    
    return location_data


# Print the devices from a specific location for debugging purposes
print(get_devices_by_location(file_path, 'ChengduTreat'))

# Define an endpoint '/devices' that will accept GET requests
@app.route('/devices', methods=['GET'])
def get_devices():
    """
    Endpoint to get devices by location.
    
    Returns:
    JSON response containing the devices or an error message.
    """
    if 'sid' in session and 'token' in session:
    # Get the 'location' query parameter from the request
        location = request.args.get('location')
    
    # If 'location' is not provided, return an error response
        if not location:
            return jsonify({'error': 'Location is required.'}), 400
    
    # Retrieve devices by location from the CSV file
        devices = get_devices_by_location(file_path, location)
    
    # Return the devices as a JSON response
        return jsonify({'devices': devices})
    else:
        return jsonify({'error': 'Please login first.'}), 401


# Create a new Flask web application instance

# Define an endpoint '/show' that will accept POST requests
@app.route('/show', methods=['POST'])
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

if __name__ == '__main__':

    app.run(debug=True, port=5002,host='0.0.0.0')