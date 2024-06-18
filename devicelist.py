import pandas as pd
from flask import Flask, request, jsonify

# Path to the CSV file containing the device information
file_path = '/Users/honglang/wechat_backend/host_info.csv'

# Create a new Flask web application instance
devicelist = Flask(__name__)

def get_devices_by_location(file_path, location):
    """
    Function to get devices by location from a CSV file.
    
    Parameters:
    file_path (str): The path to the CSV file containing device information.
    location (str): The location to filter devices by.
    
    Returns:
    list: A list of dictionaries where each dictionary represents a device.
    """
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)
    
    # Filter the DataFrame for devices at the specified location
    location_df = df[df['Location'] == location]
    
    # Convert the filtered DataFrame to a list of dictionaries
    location_data = location_df.to_dict(orient='records')
    
    return location_data

# Print the devices from a specific location for debugging purposes
print(get_devices_by_location(file_path, 'ChengduTreat'))

# Define an endpoint '/devices' that will accept GET requests
@devicelist.route('/devices', methods=['GET'])
def get_devices():
    """
    Endpoint to get devices by location.
    
    Returns:
    JSON response containing the devices or an error message.
    """
    # Get the 'location' query parameter from the request
    location = request.args.get('location')
    
    # If 'location' is not provided, return an error response
    if not location:
        return jsonify({'error': 'Location is required.'}), 400
    
    # Retrieve devices by location from the CSV file
    devices = get_devices_by_location(file_path, location)
    
    # Return the devices as a JSON response
    return jsonify({'devices': devices})

# Run the Flask application on host 0.0.0.0, port 5003 in debug mode
if __name__ == '__main__':
    
    devicelist.run(debug=True, host='0.0.0.0', port=5003)