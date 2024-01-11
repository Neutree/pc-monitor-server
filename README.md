pc-monitor-server
===


A PC monitor program, and serve as a server(http/websocket/socket), so you can get these info from any where even MCU devices

## Install and Run

1. Ensure you have Python3 environment.
2. Install by `pip install pc-monitor-server`.
3. Execute `pc-monitor-server` to start server, and you will see one or more QR code in terminal.


## Client

You can get info by HTTP get or post request, to test, visit `http://127.0.0.1:9999` in browser.

The info format is JSON.

Then you can write your own client to get these info.
Here's a example screenshot:
![](./assets/screenshot.png)

