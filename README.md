# FileQrcoder
# INTRODUCTION
Pyproxy is a proxy written in Python for rapid deployment and secondary development.
![image](https://github.com/lulinpeng/PyProxy/blob/main/http_proxy.png)
# QUICK START
## First Attempt
```shell
# client -> http proxy -> http server -> http proxy -> client

# start http server
python3 http_server.py --port 8090

# start http proxy server 
python3 http_proxy.py --port 8080

# start http request
python3 http_client.py --port 8080
```