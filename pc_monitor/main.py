from flask import Flask, request, Response
import json
try:
    from .util import Util
except Exception:
    from util import Util

app = Flask("pc_monitor_server")
util = Util()

@app.route("/", methods=["POST", "GET"])
def home():
    info = util.all()
    return Response(json.dumps(info, ensure_ascii=False), mimetype="application/json")

def main(addr, port):
    app.run(addr, port= port)

if __name__ == "__main__":
    addr = "0.0.0.0"
    port = 9999
    main(addr, port)

