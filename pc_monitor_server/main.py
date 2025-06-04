from flask import Flask, request, Response
import json
import argparse
import qrcode
import netifaces
import psutil
from PIL import Image, ImageDraw, ImageFont
import platform

try:
    from .util import Util
except Exception:
    from util import Util

app = Flask("pc_monitor_server")
util = Util()
pretty = False

@app.route("/", methods=["POST", "GET"])
def home():
    info = util.all()
    return Response(json.dumps(info, ensure_ascii=False, indent = 4 if pretty else None), mimetype="application/json")

def main(addr, port):
    app.run(addr, port= port)

def get_ip_address(ifname):
    family = netifaces.AF_INET
    # 获取指定网卡的IP地址信息
    addresses = netifaces.ifaddresses(ifname).get(family)
    if addresses:
        return [addr['addr'] for addr in addresses]


def print_addr_qrcode(port):
    ip_list = []
    # get all NICs
    net_io_counters = psutil.net_io_counters(pernic=True)
    names = list(net_io_counters.keys())
    for i, nic in enumerate(netifaces.interfaces()):
        name = names[i]
        print(name)
        if "lo" in name.lower() or "veth" in name.lower() or "docker" in name.lower() or "br-" in name.lower() or "vmware" in name.lower() or "virtual" in name.lower():
            continue
        try:
            ips = get_ip_address(nic)
            if ips:
                for ip in ips:
                    ip_list.append([name, ip])
        except Exception as e:
            print(f"-- get ip from {nic} failed:", e)
            continue

    imgs = []
    contents = []
    for ifname, ip in ip_list:
        content = f"http://{ip}:{port}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"ip_{ip}.png")
        imgs.append(img)
        contents.append(f"{ifname}: {content}")
        print("--------------")
        print(ifname, content)
        print("--------------")

    if len(imgs) == 0:
        raise Exception("No network interface found")
    # Calculate image dimensions
    max_width = max([max(img.width, img.height) for img in imgs])
    total_height = sum([img.height for img in imgs])
    total_height += len(imgs) * 32

    # Create a new blank image
    result_img = Image.new("RGB", (max_width, total_height), color="white")
    y_offset = 0

    # Draw each QR code and its content onto the result image
    draw = ImageDraw.Draw(result_img)
    if platform.system() == "Windows":
        # Windows默认中文字体是SimSun（宋体）
        font = ImageFont.truetype("simsun.ttc", size=14)
    elif platform.system() == "Darwin":
        # macOS默认中文字体是PingFang SC
        font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", size=14)
    else:
        # Linux默认中文字体是Noto Sans CJK
        font = ImageFont.truetype("/usr/share/fonts/noto/NotoSansCJK-Regular.ttc", size=14)

    for img, content in zip(imgs, contents):
        result_img.paste(img.get_image(), (0, y_offset))
        draw.text((2, y_offset + img.height), content, fill="black", font=font)
        y_offset += img.height + 32

    # Save the result image
    path = "ip_qrcode.png"
    result_img.save(path)
    print("===================================")
    print("||")
    print(f"|| Saved QR codes to {path}")
    print("||")
    print("===================================")
    try:
        result_img.show()
    except Exception:
        pass


def main_cli():
    global pretty
    parser = argparse.ArgumentParser()
    parser.add_argument("--addr", default="0.0.0.0", help="Address to listen on")
    parser.add_argument("-p", "--port", default=9999, help="Port to listen on")
    parser.add_argument("--pretty", action="store_true", help="Pretty print for json(add indent)")
    args = parser.parse_args()
    print_addr_qrcode(args.port)
    pretty = args.pretty
    main(args.addr, args.port)

if __name__ == "__main__":
    main_cli()

