#!/bin/sh -e
echo 1 > /proc/sys/net/ipv4/ip_forward
openvpn --config /home/openvpn/openvpn/server.conf --writepid /run/openvpn.pid &
sleep 3
iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -d 10.10.0.0/24 -j MASQUERADE
iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -d 10.20.0.0/24 -j MASQUERADE
exit 0
