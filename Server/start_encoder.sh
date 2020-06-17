#!/bin/sh
echo 'starting encoder' &
docker run --name live_encoder -v $(pwd)/root:/media \
jrottenberg/ffmpeg \
  -stream_loop -1 -re -i /media/adaptive_dash.mp4 -c:v copy -map 0 \
    -b:v:0 100k \
    -b:v:1 200k \
    -b:v:2 350k \
    -b:v:3 500k \
    -b:v:4 700k \
    -b:v:5 900k \
    -b:v:6 1100k \
    -b:v:7 1300k \
    -b:v:8 1600k \
    -b:v:9 1900k \
    -b:v:10 2300k \
    -b:v:11 2800k \
    -b:v:12 3400k \
    -b:v:13 4500k \
  -seg_duration 2 \
  -utc_timing_url "https://time.akamai.com?iso" \
   -use_timeline 0  \
   -use_template 1 \
   -index_correction 1 \
   -media_seg_name 'chunk-stream-$RepresentationID$-$Number%05d$.m4s' \
   -init_seg_name 'init-stream$RepresentationID$.mp4' \
  -adaptation_sets "id=0,streams=v id=1,streams=a" \
  -window_size 30 -extra_window_size 15 -remove_at_exit 1 \
  -f dash /media/stream/stream.mpd
