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

# FYI

HTTP has evolved through versions HTTP/0.9 (1991), HTTP/1.0 (1996), HTTP/1.1 (1997), HTTP/2 (2015), and HTTP/3 (2022), each enhancing speed, efficiency, and security.

| #  | Method    | Supported HTTP Versions | Description                          |
|----|-----------|-------------------------|--------------------------------------|
| 1  | GET       | HTTP/1.0, 1.1, 2, 3     | Fetch resource data |
| 2  | POST      | HTTP/1.0, 1.1, 2, 3     | Submit data to process/create|
| 3  | PUT       | HTTP/1.1, 2, 3          | Replace/recreate target resource|
| 4  | DELETE    | HTTP/1.1, 2, 3          | Remove the target resource |
| 5  | HEAD      | HTTP/1.0, 1.1, 2, 3     | Fetch resource headers only|
| 6  | OPTIONS   | HTTP/1.1, 2, 3          | List allowed methods for resource|
| 7  | CONNECT   | HTTP/1.1, 2, 3          | Establish a network tunnel  |
| 8  | TRACE     | HTTP/1.1, 2, 3          | Echo received request         |
| 9  | PATCH     | HTTP/1.1, 2, 3          | Apply partial resource modifications|
