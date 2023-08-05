import socket

sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()
port = 8080

sock.bind((host, port))

sock.listen(1)

conn, addr = sock.accept()

data = "Hello!"
data = bytes(data, 'utf-8')

conn.send(data)

sock.close()
