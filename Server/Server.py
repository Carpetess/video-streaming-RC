import socket
import sys
import os
import pickle
import random
import time


def concatenate_bits(main_bit, bit2):
	return (main_bit << bit2.bit_length()) | bit2


def sendMovie( fileName, cHost, cUDPport, sessionID):
	dest = (cHost, cUDPport)
	su = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# to guarantee that the send buffer has space for the biggest JPEG files
	su.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 32000) 
	frameNo = 1
	fr = open(fileName, 'rb')
		
	while True:
		dat = fr.read(5)
		if len(dat) == 0: 
				return
		else:
			imageLen = int(dat)
			dat=fr.read(imageLen)
			if frameNo % 100 == 0:
				print(f'nseq={frameNo} JPEG file size = {len(dat)}')

			header_init = 32794 #2/2 0/1 0/1 0/4 0/1 26/7
			sequence_num = frameNo << 16-frameNo.bit_length() #16 bits of reference num

			timestamp_bit = int(time.time() * 1000) & 0xFFFFFFFF #32 bits of timestamp
			if(timestamp_bit.bit_length() < 32):
				timestamp_bit = timestamp_bit << 32-timestamp_bit.bit_length()
    
			ssrc = sessionID << 32-sessionID.bit_length() #32 bits of ssrc
			
			complete_header = concatenate_bits(header_init, concatenate_bits(sequence_num, concatenate_bits(timestamp_bit, ssrc)))
			dat = pickle.dumps((complete_header, dat))
			
			su.sendto( dat, dest)
			timestamp_bit = int(time.time() * 1000) & 0xFFFFFFFF #32 bits of timestamp
			time.sleep(0.05)  # one image every 50 ms
			frameNo = frameNo+1

def handleClient( clientHost, sock):
	# receive fileName and UDP port
	# reply with random sessionID, -1 if file not available

	nreq = sock.recv(128)
	req = pickle.loads(nreq)
	fileName = req[1]
	clientUDPPort = req[0]
	if not os.path.exists(fileName):
		rep=(-1,)
		sock.send(pickle.dumps(rep))
		return
	
	sid = random.randint(0,4000000)
	rep=(sid,)
	sock.send(pickle.dumps(rep))
	#wait for ack from client
	rep = sock.recv(128)
	if rep.decode() == "Go":
		sock.close()
		sendMovie( fileName, clientHost, clientUDPPort, sid)

if __name__ == "__main__":
    # python Server.py serverTCPPort
	if len(sys.argv)!=2:
		print("Usage: python3 Server.py  ServerTCPControlPort")
		sys.exit(1)
	else:
		serverTCPControlPort = int(sys.argv[1])
		st = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			st.bind(("0.0.0.0", serverTCPControlPort))
		except socket.error as e:
			print(f"Error binding TCP server socket: {e}")
			st.close()
			sys.exit(2)
		st.listen(1)
		while True:
			print("Waiting for client")
			try:
				sa, end = st.accept()
			except KeyboardInterrupt:
				print("server exiting")
				st.close()
				sys.exit(0)
			print(f"Handling client connecting from {end}")
			handleClient( end[0], sa )


