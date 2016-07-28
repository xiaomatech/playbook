#!/usr/bin/env bash

#use ali_lvs
yum remove -y kernel-devel kernel-firmware
yum install -y kernel-firmware-2.6.32-279.el6.ucweb.snat.mz0605
yum install -y kernel-2.6.32-279.el6.ucweb.snat.mz0605
yum install -y kernel-devel-2.6.32-279.el6.ucweb.snat.mz0605
#lvs-tools
yum install -y lvs-tools

echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf
#not flow director NIC , enable rps_framework
echo 'net.core.rps_framework = 1' >> /etc/sysctl.conf

chkconfig keepalived on

#gw ip gro/lro

interfaces=`ifconfig | grep ^e | awk '{print $1}' | fgrep -v :`

for t_iface in $interfaces ; do
	ethtool -K $t_iface gro off
	ethtool -K $t_iface lro off

	ethtool -K $t_iface gso off
	ethtool -K $t_iface tso off
done



chkconfig irqbalance off