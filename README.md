# FileQrcoder
# INTRODUCTION
Pyproxy is a proxy written in Python for rapid deployment and secondary development.
<center><img src="https://github.com/lulinpeng/PyProxy/blob/main/http_proxy.png" alt="http_proxy" width="60%" height="auto"></center>

# QUICK START
## First Attempt
```shell
# client -> http proxy -> http server -> http proxy -> client

# add '0.0.0.0 a.b.c' to /etc/hosts

# start http server
python3 http_server.py --port 8090

# start http proxy server 
python3 http_proxy.py --port 8080

# start a http proxy request
python3 http_client.py
```