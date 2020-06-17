FROM abiosoft/caddy:latest

RUN apk add --no-cache bash
RUN apk add --no-cache nano
RUN apk add --update iproute2 iperf

COPY conf/favicon.ico /srv/favicon.ico
COPY conf/ssl/caddy-testbed.com.pem /etc/ssl
COPY conf/ssl/caddy-testbed.com.key /etc/ssl
RUN mkdir -p /etc/caddy
COPY conf/Caddyfile_QUIC /etc/caddy
COPY conf/Caddyfile_H2 /etc/caddy
COPY conf/Caddyfile_H1 /etc/caddy

EXPOSE 8088/tcp
EXPOSE 7080/tcp
EXPOSE 443/udp
EXPOSE 443/tcp

ENTRYPOINT ["/bin/parent", "caddy"]
