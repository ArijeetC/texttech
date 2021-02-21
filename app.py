import requests, os

from flask import Flask, jsonify, request, render_template

QUERY_LIMIT = 1000

app = Flask(__name__)


@app.route("/")
def home():
    """Returns the main webpage of the Flask web app
    """
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)