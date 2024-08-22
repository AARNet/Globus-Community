# Rate limit Globus transfers

By default, Globus will use all available bandwidth on the network for transfers. It is possible to configure concurrency and “aggressiveness” within Globus, but not the effective bandwidth, which must be managed from the operating system or network configuration.

If you’d like to throttle the speed at which the files are transferred, you can enable rate limiting on the sending server using tc. This method uses packet marking, and packets can be tagged by IP address, port number, or both. This means it is possible to throttle outbound Globus traffic to a single recipient or all recipients.

## Limitations

- This method only limits outbound data. To limit inbound data, you need to change configuration on the sending service or a network gateway device. 

- The tc commands are not persistent and must be re-applied at boot time.

## Prerequisites

- You will need administration privileges on the server that is sending the Globus data.

## Procedure to enable rate limiting

**Note: These instructions are specific to a server running Ubuntu 22.04. If you are running a different Linux distribution or operating system, you may need to update the commands accordingly.**

Run these commands at the sending server’s command line, replacing the following placeholders in the commands below with your own values:

- ```\<NIC_DEVICE>```: Your NIC device name, for example enp79s0np0.
- ```\<DESTINATION_IP>```: the destination IP address to which file transfers will be throttled.
- ```\<LIMIT>```: the throttle rate, for example 1mbit.

Note Do NOT change the port ranges for Globus (443 and 50000-51000).

```
# Create qdisc with default 0 to pass packets unmolested
sudo tc qdisc add dev <NIC_DEVICE> root handle 1:0 htb default 0
sudo tc qdisc list dev <NIC_DEVICE>

# Create HTB class – this example limits traffic to a strict 1Mbps (change as required)
sudo tc class add dev <NIC_DEVICE> parent 1:0 classid 1:10 htb rate <LIMIT> ceil <LIMIT> prio 0
sudo tc class list dev <NIC_DEVICE>

# Add filter for marked packets (mark value 10)
sudo tc filter add dev <NIC_DEVICE> parent 1:0 protocol ip prio 16 handle 10 fw flowid 1:10
sudo tc filter list dev <NIC_DEVICE>

# Add iptables rules to mark throttled packets (mark value 10)
sudo iptables -A OUTPUT -t mangle -p tcp --dest <DESTINATION_IP> --sport 50000:51000 -j MARK --set-mark 10
sudo iptables -A OUTPUT -t mangle -p tcp --dest <DESTINATION_IP> --dport 50000:51000 -j MARK --set-mark 10
sudo iptables -A OUTPUT -t mangle -p tcp --dest <DESTINATION_IP> --sport 443 -j MARK --set-mark 10
sudo iptables -A OUTPUT -t mangle -p tcp --dest <DESTINATION_IP> --dport 443 -j MARK --set-mark 10
sudo nft list table mangle
```

## Procedure to disable rate limiting

Run the following commands on the sending server’s command line:

```
# Delete iptables rules
sudo iptables -D OUTPUT -t mangle -p tcp --dest <DESTINATION_IP> --sport 50000:51000 -j MARK --set-mark 10
sudo iptables -D OUTPUT -t mangle -p tcp --dest <DESTINATION_IP> --dport 50000:51000 -j MARK --set-mark 10
sudo iptables -D OUTPUT -t mangle -p tcp --dest <DESTINATION_IP> --sport 443 -j MARK --set-mark 10
sudo iptables -D OUTPUT -t mangle -p tcp --dest <DESTINATION_IP> --dport 443 -j MARK --set-mark 10
sudo nft list table mangle

# Delete filter for marked packets (10)
sudo tc filter del dev <NIC_DEVICE> sudo tc filter list dev <NIC_DEVICE>

# Delete HTB class
sudo tc class del dev <NIC_DEVICE> classid 1:10
sudo tc class list dev <NIC_DEVICE>

# Delete qdisc
sudo tc qdisc del dev <NIC_DEVICE> root handle 1:0 htb
sudo tc qdisc list dev <NIC_DEVICE>
```