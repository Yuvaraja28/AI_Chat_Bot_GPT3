import json, secrets, httpx, sys
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

OPENAI_API_KEY = ""

app = Flask(__name__)
app.secret_key = secrets.token_hex()
sock = SocketIO(app)

try: config_file = json.loads(open("config.json").read())
except: config_file = {}

def verify_password(email, password):
    user = config_file.get('accounts', {'admin': '1234'})
    if (email in user):
        if secrets.compare_digest(user.get(email), password):
            return True
    return False

@app.route('/')
def main():
    return render_template('index.html')

@sock.on('s-message')
def send_msgs(data):
    emit('r-message', json.dumps(OpenAiResp(json.loads(data).get('message'))))

def OpenAiResp(question):
    header = {}
    header["Authorization"] = f"Bearer {OPENAI_API_KEY}" 
    header["Content-Type"] = "application/json"
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": question}] 
    }
    try:
        contents = httpx.post(url="https://api.openai.com/v1/chat/completions", headers=header, data=json.dumps(data), timeout=10).json()
        data = {"question": question, "answer": contents.get('choices', [])[0].get('message', {}).get('content').replace("\n\n", "\n")}
    except:
        data = {"question": question, "answer": "An Error Occured while Generating a Response"}
    return data

try:
    sock.run(app, host="0.0.0.0", port=int(sys.argv[2]))
except IndexError:
    print("USAGE: python3 app.py -p <web-port>")