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

# 🌐 Flask Main Page
@app.route("/", methods=["GET"])
def index():
    return Response('''
        <html>
            <head><title>Instagram Auto Messenger</title></head>
            <body style="text-align:center; padding:40px;">
                <h2>📤 Instagram Auto DM + Group Messenger</h2>
                <form action="/start" method="POST" enctype="multipart/form-data">
                    <input name="username" placeholder="Username" required><br><br>
                    <input name="password" type="password" placeholder="Password" required><br><br>
                    <input name="receivers" placeholder="Receivers (comma separated)" required><br><br>
                    <input name="delay" type="number" placeholder="Delay in seconds" value="5"><br><br>
                    <input type="file" name="messagefile" required><br><br>
                    <button type="submit">🚀 START</button>
                </form>
                <br><br>
                <form action="/stop" method="POST">
                    <button type="submit" style="background:red;color:white;">🛑 STOP</button>
                </form>
            </body>
        </html>
    ''', mimetype='text/html')

# ▶️ Start Route
@app.route("/start", methods=["POST"])
def start():
    global messaging_active, background_thread

    username = request.form.get("username")
    password = request.form.get("password")
    receivers = request.form.get("receivers").split(",")
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

# ⛔ Stop Route
@app.route("/stop", methods=["POST"])
def stop():
    global messaging_active
    messaging_active = False
    return "<h3>🛑 Messaging stopped. <a href='/'>Go Back</a></h3>"

# Run server on port 5001
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
    