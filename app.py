from flask import Flask, request, jsonify
import time

# Define a local user pool with predefined usernames, passwords, and digits
local_user_pool = {
    'honglang': {'password': 'honglang', 'digits': 50, 'counter': 0, 'lock_time': None, 'is_locked': False},
    'oliver': {'password': 'oliver', 'digits': 60, 'counter': 0, 'lock_time': None, 'is_locked': False}
}

# Create a new Flask web application instance
app = Flask(__name__)

def reset_counter(username):
    user = local_user_pool[username]
    user['counter'] = 0
    user['lock_time'] = None
    user['is_locked'] = False

@app.route('/', methods=['POST'])
def receive_data():
    """
    Endpoint to receive and process JSON data for user authentication.
    
    Returns:
    JSON response with success or error message.
    """
    # Get JSON data from the request
    data = request.get_json()
    
    # Process the received data (for debugging purposes, print the data)
    print(data)
    
    # Extract the relevant information from the received data
    username = data.get('username')
    password = data.get('password') 
    digits = data.get('digits')  
    
    # Check if the username exists in the local user pool
    if username in local_user_pool:
        user = local_user_pool[username]
        
        # Check if the user is locked
        if user['is_locked']:
            current_time = time.time()
            if current_time - user['lock_time'] >= 10800:  # 10800 seconds = 3 hours
                reset_counter(username)
            else:
                remaining_lock_time = 10800 - (current_time - user['lock_time'])
                return jsonify({'message': f'User {username} is currently locked. Try again in {int(remaining_lock_time//60)} minutes.'}), 403
        
        # Verify if the provided password and digits match the stored values
        if password == user['password'] and digits == user['digits']:
            reset_counter(username)
            # If both match, return a success response
            return jsonify({'message': 'Authentication successful'}), 200
        else:
            user["counter"] += 1
            counter = user["counter"]
            # Check for multiple failed attempts
            if counter < 3:
                chance = 3 - counter
                return jsonify({'message': f'Authentication failed (wrong password or digits). {chance} chances left.'}), 401
            else:
                user['is_locked'] = True
                user['lock_time'] = time.time()
                return jsonify({'message': f'User {username} locked out due to multiple failed attempts'}), 403
    else:
        # If the username is not found in the user pool, return a user not found response
        return jsonify({'message': 'User not found'}), 404

# Run the Flask application on host 0.0.0.0, port 5001 in debug mode
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)