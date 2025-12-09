from flask import Flask, jsonify, request
app = Flask(__name__)

SIM_STATE = {"status":"idle", "ticks":0}

@app.route("/status")
def status():
    return jsonify(SIM_STATE)

@app.route("/step", methods=["POST"])
def step():
    SIM_STATE["ticks"] += 1
    SIM_STATE["status"] = "running"
    return jsonify({"ok": True, "ticks": SIM_STATE["ticks"]})

@app.route("/command", methods=["POST"])
def command():
    payload = request.json or {}
    # payload e.g. {"action":"inject_resource","planet":"GCPia","amount":100}
    return jsonify({"received": payload})
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
