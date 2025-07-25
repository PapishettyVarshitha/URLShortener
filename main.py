from flask import Flask, request, jsonify, redirect
import string
import random
import threading
from datetime import datetime

app = Flask(__name__)

# In-memory storage for shortened URLs
url_db = {}
lock = threading.Lock()

# Helper function to generate a 6-character short code
def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Helper function to validate input URL
def is_valid_url(url):
    return url.startswith("http://") or url.startswith("https://")

# Endpoint to shorten a URL
@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "Missing 'url' field"}), 400

    long_url = data['url']
    if not is_valid_url(long_url):
        return jsonify({"error": "Invalid URL"}), 400

    short_code = generate_short_code()
    short_url = request.host_url + short_code

    with lock:
        url_db[short_code] = {
            'url': long_url,
            'created_at': datetime.utcnow().isoformat(),
            'clicks': 0
        }

    return jsonify({
        "short_code": short_code,
        "short_url": short_url
    }), 200

# Endpoint to redirect to the original URL
@app.route('/<short_code>', methods=['GET'])
def redirect_to_original(short_code):
    with lock:
        if short_code not in url_db:
            return jsonify({"error": "Short code not found"}), 404

        url_db[short_code]['clicks'] += 1
        original_url = url_db[short_code]['url']

    return redirect(original_url)

# Endpoint to get analytics for a short code
@app.route('/api/stats/<short_code>', methods=['GET'])
def get_stats(short_code):
    with lock:
        if short_code not in url_db:
            return jsonify({"error": "Short code not found"}), 404

        data = url_db[short_code]
        return jsonify({
            "url": data['url'],
            "clicks": data['clicks'],
            "created_at": data['created_at']
        }), 200
