#!/bin/sh
#docker system prune -f
#docker volume prune -f
#sudo docker volume create --name 'root'
docker build --no-cache -t "caddy-server" .
echo 'HTTP/1.1        -> port:8080(+SSL port:445)'
docker rm -f HTTP1
docker run --name='HTTP1' -v $(pwd)/root:/srv -p 445:445/tcp -p 8080:8080/tcp --rm caddy-server:latest -conf /etc/caddy/Caddyfile_H1 -http2=false -https-port=445 -http-port=8080 &

echo 'HTTP/2.0        -> port:444'
docker rm -f HTTP2
docker run --name='HTTP2' -v $(pwd)/root:/srv -p 444:444/tcp --rm caddy-server:latest -conf /etc/caddy/Caddyfile_H2 -http2=true -https-port=444 -quic=false &

echo 'HTTP-OVER-QUIC  -> port:443' &
docker rm -f HTTP-OVER-QUIC
docker run --name='HTTP-OVER-QUIC' -v $(pwd)/root:/srv -p 443:443/udp -p 443:443/tcp --rm caddy-server:latest -conf /etc/caddy/Caddyfile_QUIC -quic
