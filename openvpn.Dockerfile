FROM ubuntu:22.04 AS base
WORKDIR /root
RUN apt update && apt install -y wget libnl-3-dev libnl-genl-3-dev pkg-config libcap-ng-dev libssl-dev liblz4-dev liblzo2-dev libpam-dev g++ make && \
    wget https://github.com/OpenVPN/openvpn/releases/download/v2.6.14/openvpn-2.6.14.tar.gz && \
    tar -zxvf openvpn-2.6.14.tar.gz && \
    cd openvpn-2.6.14 && ./configure && make -j8 && make install && openvpn --version
