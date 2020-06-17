#!/bin/sh
CYCLES=20 # repetition per server + network combination
PROBES=100 # number of probes
INTERVAL=1000 # probe interval
STRATEGY=0 # abr strategies 0=dynamic 1=Throughput 2=bola
SSH_USER_HOST="root@caddy-testbed.com"
DEV="eno1"

# bandwidth delay loss
#  kBit/s    ms    %
network_conditions=(
                    #bandwith
                    'network=(16000 0 0)'
                    'network=(8000 0 0)'
                    'network=(4000 0 0)'
                    'network=(2000 0 0)'
                    'network=(1000 0 0)'
                    #delay
					          'network=(16000 50 0)'
                    'network=(16000 100 0)'
                    'network=(16000 150 0)'
                    'network=(16000 200 0)'
                    'network=(16000 250 0)'
                    #loss
                    'network=(16000 0 0.5)'
                    'network=(16000 0 1.5)'
                    'network=(16000 0 2.5)'
                    'network=(16000 0 3.5)'
                    'network=(16000 0 4.5)'
                    #combined
                    'network=(16000 50 0.5)'
                    'network=(8000 100 1.5)'
                    'network=(4000 150 2.5)'
                    'network=(2000 200 3.5)'
                    'network=(1000 250 4.5)'
										)
bold=$(tput bold)
normal=$(tput sgr0)
for value in "${network_conditions[@]}"
do
  #set network emulation via ssh
  eval $value;
  echo "${bold}Applying network condition via SSH: network_${network[0]}_${network[1]}_${network[2]}${normal}";
  ssh -i ~/.ssh/foo $SSH_USER_HOST DEV=$DEV DOWNLOAD=${network[0]} UPLOAD=${network[0]} DELAY=${network[1]} LOSS=${network[2]} 'bash -s' <<'ENDSSH'
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
  sleep 1
  node QoE.js --cycles $CYCLES --probes $PROBES --interval $INTERVAL --strategy $STRATEGY --network="network_${network[0]}_${network[1]}_${network[2]}"
	#reset network emulation
	echo "${bold}Removing network condition via SSH: network_${network[0]}_${network[1]}_${network[2]}${normal}";
  ssh -i ~/.ssh/foo $SSH_USER_HOST DEV=$DEV 'bash -s' <<'ENDSSH'
  tc qdisc del dev $DEV root
ENDSSH
done
