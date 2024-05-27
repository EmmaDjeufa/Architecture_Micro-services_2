from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_url_path='')

@app.route('/')
def index():
    return send_from_directory('frontend', 'accueil.html')

@app.route('/<path:path>')
def static_file(path):
    return send_from_directory('frontend', path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
