FROM ubuntu:22.04 AS base
WORKDIR /root
RUN apt update && \
    apt -y install iputils-ping curl tcpdump vim python3 python3-pip && \
    pip3 install flask requests -i https://mirrors.aliyun.com/pypi/simple/