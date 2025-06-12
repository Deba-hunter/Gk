from flask import Flask, request, Response, redirect
from threading import Thread
from instagrapi import Client
import time

app = Flask(__name__)
client = Client()

# Global variables
messaging_active = False
background_thread = None

# 🔁 Message sending function
def send_messages(receivers, messages, delay):
    global messaging_active
    while messaging_active:
        for msg in messages:
            if not messaging_active:
                break
            for user in receivers:
                try:
                    client.direct_send(msg, [user])
                    print(f"Sent to {user}: {msg}")
                except Exception as e:
                    print(f"Error sending to {user}: {e}")
            time.sleep(delay)

# 🌐 Main Page
@app.route("/", methods=["GET"])
def index():
    return Response('''
        <html>
            <head>
                <title>Instagram Auto Messenger</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #f1f1f1;
                        padding: 20px;
                        text-align: center;
                    }
                    h2 {
                        color: #333;
                    }
                    form {
                        background: white;
                        padding: 20px;
                        margin: auto;
                        border-radius: 10px;
                        max-width: 350px;
                        box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
                    }
                    input, button {
                        width: 100%;
                        padding: 10px;
                        margin-top: 10px;
                        border-radius: 8px;
                        border: 1px solid #ccc;
                        font-size: 16px;
                    }
                    button {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                    }
                    button:hover {
                        background-color: #45a049;
                    }
                    .stop-button {
                        background-color: #e60000;
                        margin-top: 20px;
                    }
                </style>
            </head>
            <body>
                <h2>📤 Instagram Auto DM + Group Messenger</h2>
                <form action="/start" method="POST" enctype="multipart/form-data">
                    <input name="username" placeholder="Instagram Username" required>
                    <input name="password" type="password" placeholder="Instagram Password" required>
                    <input name="receivers" placeholder="Receivers (space ya comma se alag karein)" required>
                    <input name="delay" type="number" placeholder="Delay in seconds" value="5">
                    <input type="file" name="messagefile" required>
                    <button type="submit">🚀 START</button>
                </form>
                <form action="/stop" method="POST">
                    <button type="submit" class="stop-button">🛑 STOP</button>
                </form>
            </body>
        </html>
    ''', mimetype='text/html')

# ▶️ Start messaging
@app.route("/start", methods=["POST"])
def start():
    global messaging_active, background_thread

    username = request.form.get("username")
    password = request.form.get("password")
    raw_input = request.form.get("receivers")
    receivers = [r.strip() for r in raw_input.replace(",", " ").split() if r.strip()]
    delay = int(request.form.get("delay", 5))
    file = request.files["messagefile"]
    messages = file.read().decode("utf-8").splitlines()

    try:
        client.login(username, password)
    except Exception as e:
        return f"<h3>Login failed: {e}</h3>"

    messaging_active = True
    background_thread = Thread(target=send_messages, args=(receivers, messages, delay))
    background_thread.start()

    return redirect("/")

# ⛔ Stop messaging
@app.route("/stop", methods=["POST"])
def stop():
    global messaging_active
    messaging_active = False
    return "<h3>🛑 Messaging stopped. <a href='/'>Go Back</a></h3>"

# 🚀 Run on port 5001
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
                    
