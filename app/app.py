from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    now = datetime.now()
    date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    return date_time_str

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)

