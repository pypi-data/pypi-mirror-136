import socket
class Server:
	sock = socket.socket()
	def __init__(self,server,port):
		sock.bind((server,port))
		sock.listen(3)
	def sendLoop(msg):
		while True:
			c, addr = s.accept()
			c.send(bytes(msg,'utf-8'))
			c.close()
class Client:
	client = socket.socket()
	def __init__(self,server,port):
		client.connect((server,port))
	def send(msg):
		client.send(bytes(msg))
	def get():
		return client.recv(1024).decode()
