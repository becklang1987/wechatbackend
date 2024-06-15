from flask import Flask, jsonify, request

sitelist=Flask(__name__)

@sitelist.route('/siteList', methods=['GET'])
def get_sitelist():
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

if __name__ == '__main__':
    sitelist.run(debug=True, port=5002,host='0.0.0.0')