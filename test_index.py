"""
Simple test to verify Flask app works on Vercel.
This is a minimal version without database or routes to isolate the issue.
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Vercel! Flask is working."

@app.route('/test')
def test():
    import sys
    import os
    return f"""
    <h1>Environment Test</h1>
    <p>Python Version: {sys.version}</p>
    <p>Current Directory: {os.getcwd()}</p>
    <p>Environment: {os.environ.get('VERCEL', 'Not Vercel')}</p>
    <p>Writable /tmp: {os.access('/tmp', os.W_OK)}</p>
    """

if __name__ == '__main__':
    app.run(debug=True)
