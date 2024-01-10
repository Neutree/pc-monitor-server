from flask import Flask, request, Response
import json
import argparse
import qrcode
import socket
import fcntl
import struct
import netifaces
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

def print_addr_qrcode(port):
    def get_ip_address(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack("256s", bytes(ifname[:15], "utf-8")))[20:24])
    ip_list = []
    # get all NICs
    for nic in netifaces.interfaces():
        try:
            ip = get_ip_address(nic)
            if ip.startswith("192."):
                ip_list.append([nic, ip])
        except Exception as e:
            print(e)
            pass
    for ifname, ip in ip_list:
        content = f"http://{ip}:{port}"
        qr = qrcode.QRCode()
        qr.add_data(content)
        qr.print_ascii()
        print(ifname, ip)
        print(content)

def main_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--addr", default="0.0.0.0", help="Address to listen on")
    parser.add_argument("-p", "--port", default=9999, help="Port to listen on")
    args = parser.parse_args()
    print_addr_qrcode(args.port)
    main(args.addr, args.port)

if __name__ == "__main__":
    main_cli()

