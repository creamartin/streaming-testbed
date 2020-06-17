__________________________________________________________________
PREPARE

PRE-REQUISITE Server(LINUX):
- DOCKER
PRE-REQUISITE Client(MACOSX):
- can SSH to root@server with private key
- python3+packages,NPM,Chrome,tshark

both machine need access to the internet(to install dependencies)**

#on client
1. Copy Testbed/Client to client
2. Add certificate to browser/os keychain of client
#!Docker_Caddy/ssl/myCA.pem needs to be added to keychain for TLS to work!
3. Link server with host in /etc/hosts e.g. 192.168.0.2 caddy-testbed.com

#on server
1. Copy Testbed/Server to server
2. the server needs to have access to the internet
___________________________________________________________________
INITIALIZE

#on server
1. docker needs to be running
2. run ./start_encoder.sh
3. run ./start_servers.sh

#on client
4. test connection at caddy-testbed.com
___________________________________________________________________
RUN TESTS
_______
# TEST1
1. Measure complete bytes for each stream and write into 
>> Client/overhead_scripts/bitrate_sizes(important!)
	e.g. Chrome developer Tools	
	open caddy-testbed.com/Overhead/single_bitrate_client.html
	show selectable BITRATE:
		-> [console]>> player.getBitrateInfoListFor("video")
	caddy-testbed.com/Overhead/single_bitrate_client.html?r=$BITRATE
2. run overhead_analysis.sh
_______
# TEST2
1. record data for QoE -> run script Testbed/Client/QoE_scripts/QoE_test.sh
2. create graphs from result, run: python3 Client/qoE_scripts/plot_cdf.py
3. graphs will be in Testbed/Client/graphs
_______
# TEST3
1. record data for adaptation performance -> run script Test
2. create graphs from result, run: python3 


