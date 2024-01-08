from flask import Flask, request, Response
import json
import argparse
try:
    from .util import Util
except Exception:
    from util import Util

app = Flask("pc_monitor_server")
util = Util()

@app.route("/", methods=["POST", "GET"])
def home():
    info = util.all()
    return Response(json.dumps(info, ensure_ascii=False, indent = 4), mimetype="application/json")

def main(addr, port):
    app.run(addr, port= port)

def main_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--addr", default="0.0.0.0", help="Address to listen on")
    parser.add_argument("-p", "--port", default=9999, help="Port to listen on")
    args = parser.parse_args()
    main(args.addr, args.port)

if __name__ == "__main__":
    main_cli()

