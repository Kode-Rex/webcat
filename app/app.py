from flask import Flask, request, jsonify, Response

import requests
from readability.readability import Document

import random
from urllib.robotparser import RobotFileParser

from datetime import datetime

app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    now = datetime.now()
    date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    return date_time_str

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
]

def can_fetch(url):
    rp = RobotFileParser()
    rp.set_url(request.url_root + 'robots.txt')
    rp.read()
    return rp.can_fetch("*", url)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get('url')
    output_format = data.get('output_format', 'JSON').upper()  # Defaults to JSON
    
    if not url:
        error_message = "Error: Missing URL"
        if output_format == 'JSON':
            return jsonify({'error': error_message}), 400
        else:
            return Response(error_message, status=400, mimetype='text/plain')

    if not can_fetch(url):
        error_message = "Error: Access denied by robots.txt"
        if output_format == 'JSON':
            return jsonify({'error': error_message}), 403
        else:
            return Response(error_message, status=403, mimetype='text/plain')

    headers = {'User-Agent': random.choice(USER_AGENTS)}
    try:
        response = requests.get(url, headers=headers)
        doc = Document(response.content)
        content = doc.summary(html_partial=True)
    except Exception as e:
        error_message = f"Error: Failed to scrape the URL - {str(e)}"
        if output_format == 'JSON':
            return jsonify({'error': error_message}), 500
        else:
            return Response(error_message, status=500, mimetype='text/plain')
    
    # Return content based on the requested output format
    if output_format == 'JSON':
        return jsonify({'content': content})
    else:
        return Response(content, mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)

