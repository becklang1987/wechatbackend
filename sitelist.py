from flask import Flask, jsonify, request,session
from validation import validate_token

sitelist=Flask(__name__)
sitelist.secret_key = 'your_session_secret_key'

@sitelist.route('/siteList', methods=['GET'])
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

if __name__ == '__main__':

    sitelist.run(debug=True, port=5002,host='0.0.0.0')