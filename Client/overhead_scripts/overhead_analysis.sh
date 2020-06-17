#!/bin/sh
DATA_PATH="../data/overhead"
SERVERS="https://caddy-testbed.com https://caddy-testbed.com:444 https://caddy-testbed.com:445 http://caddy-testbed.com:8080"
BITRATES="100000 200000 350000 500000 700000 900000 1100000 1300000 1600000 1900000 2300000 2800000 3400000 4500000"
DURATION=65
RUNS=5

for server in $SERVERS
do
  for bitrate in $BITRATES
  do
    for i in `seq $RUNS`
    do
      echo "current measurement run_$i: $server $bitrate"
      tshark -a duration:$DURATION -i en7 -w $DATA_PATH/tmp.pcap &
      /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
      --args --disk-cache-dir=null --disk-cache-size=1 --media-cache-size=1 \
      "$server/single_bitrate_client.html?r=$bitrate" & read -t $DURATION;
      pkill -a -i "Google Chrome"
      sleep 2
      tshark -r $DATA_PATH/tmp.pcap -q -z conv,ip |grep '192.168.0.4' |awk -v s="$server" -v b="$bitrate" '{print s" "b" "$5 >> "overhead"}'
    done
  done
done
