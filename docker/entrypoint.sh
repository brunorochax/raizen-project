#!/bin/bash
set -eou pipefail

vagrant up --provider=virtualbox

iptables-save > $HOME/firewall.txt
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

virtual_host=$(vagrant ssh-config | grep HostName)
virtual_ip=${virtual_host//"HostName "/""}
virtual_ip=${virtual_ip//[[:space:]]/}

iptables -A FORWARD -i eth0 -o virbr1 -p tcp --syn --dport 3389 -m conntrack --ctstate NEW -j ACCEPT
iptables -A FORWARD -i eth0 -o virbr1 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -i virbr1 -o eth0 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

echo "Setting virtual machine IP $virtual_ip for PREROUTING and POSTROUTING for RDP.."
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 3389 -j DNAT --to-destination $virtual_ip
iptables -t nat -A POSTROUTING -o virbr1 -p tcp --dport 3389 -d $virtual_ip -j SNAT --to-source 192.168.121.1

echo "Setting virtual machine IP $virtual_ip for PREROUTING and POSTROUTING for SSH.."
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 22 -j DNAT --to-destination $virtual_ip
iptables -t nat -A POSTROUTING -o virbr1 -p tcp --dport 22 -d $virtual_ip -j SNAT --to-source 192.168.121.1

iptables -D FORWARD -o virbr1 -j REJECT --reject-with icmp-port-unreachable
iptables -D FORWARD -i virbr1 -j REJECT --reject-with icmp-port-unreachable
iptables -D FORWARD -o virbr0 -j REJECT --reject-with icmp-port-unreachable
iptables -D FORWARD -i virbr0 -j REJECT --reject-with icmp-port-unreachable

echo "nameserver 8.8.8.8" | tee /etc/resolv.conf > /dev/null
echo "Firewall rules were configured with success."

exec "$@"