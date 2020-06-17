#!/bin/sh
SSH_USER_HOST="root@caddy-testbed.com"
DEV="eno1"

if [ $1 -eq -1 ]
then
  echo "Removing network conditions via SSH";
  ssh -i ~/.ssh/foo $SSH_USER_HOST DEV=$DEV 'bash -s' <<'ENDSSH'
  tc qdisc del dev $DEV root &>/dev/null
ENDSSH
  exit 0
fi

echo "Applying network condition via SSH: network_$1";
ssh -i ~/.ssh/foo $SSH_USER_HOST DEV=$DEV DOWNLOAD=$1 UPLOAD=$1 DELAY=75 LOSS=0 'bash -s' <<'ENDSSH'
#remove old qdiscs
tc qdisc del dev $DEV root &>/dev/null
tc qdisc del dev $DEV ingress &>/dev/null
tc qdisc del dev ifb0 root &>/dev/null
#egress
tc qdisc add dev $DEV root handle 1: htb
tc class add dev $DEV parent 1:0 classid 1:1 htb rate ${DOWNLOAD}kbit ceil ${DOWNLOAD}kbit
if [ "`echo "$LOSS > 0.0" | bc`" -eq 0 ]
then
  tc qdisc add dev $DEV parent 1:1 handle 10:0 netem delay ${DELAY}ms limit 100000
else
  tc qdisc add dev $DEV parent 1:1 handle 10:0 netem delay ${DELAY}ms loss $LOSS limit 100000
fi
tc filter add dev $DEV protocol ip parent 1:0 prio 1 u32 match ip dst 0.0.0.0/0 flowid 1:1
#ingress
modprobe ifb
ip link set dev ifb0 up
tc qdisc add dev $DEV ingress
tc filter add dev $DEV parent ffff: \
 protocol ip u32 match u32 0 0 action mirred egress redirect dev ifb0
tc qdisc add dev ifb0 root handle 2: htb
tc class add dev ifb0 parent 2:0 classid 2:10 htb rate ${UPLOAD}kbit ceil ${UPLOAD}kbit
tc qdisc add dev ifb0 parent 2:10 handle 20:0 netem delay ${DELAY}ms limit 100000
tc filter add dev ifb0 protocol ip parent 2:0 prio 1 u32 match ip src 0.0.0.0/0 flowid 2:10
ENDSSH
