import socket
class Server:
	def __init__(self,server,port):
		self.sock = socket.socket()
		self.sock.bind((server,port))
		self.sock.listen(3)
	def sendLoop(self,msg):
		while True:
			c, addr = self.sock.accept()
			c.send(bytes(msg,'utf-8'))
			c.close()
class Client:
	def __init__(self,server,port):
		self.client = socket.socket()
		self.client.connect((server,port))
	def send(msg):
		self.client.send(bytes(msg))
	def get():
		return self.client.recv(1024).decode()
