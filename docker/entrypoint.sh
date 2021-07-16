#!/bin/bash
set -eou pipefail

vagrant up --provider=virtualbox

iptables --flush

serverip=$(ifconfig eth0 | egrep -o 'inet [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | cut -d' ' -f2)
hostip=$(ifconfig lo | egrep -o 'inet [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | cut -d' ' -f2)

echo "Setting virtual machine IP $hostip for PREROUTING and POSTROUTING for RDP.."
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 3389 -j DNAT --to-destination $hostip
iptables -t nat -A POSTROUTING -o lo -p tcp --dport 3389 -d $hostip -j SNAT --to-source $serverip

echo "Setting virtual machine IP $hostip for PREROUTING and POSTROUTING for SSH.."
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 22 -j DNAT --to-destination $hostip
iptables -t nat -A POSTROUTING -o lo -p tcp --dport 2222 -d $hostip -j SNAT --to-source $serverip

echo "nameserver 8.8.8.8" | tee /etc/resolv.conf > /dev/null
echo "Firewall rules were configured with success."

exec "$@"