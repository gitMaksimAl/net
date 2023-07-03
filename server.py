import socket
import threading
from sys import argv


def login(host: socket) -> str:
    global clients
    host.send('NICK'.encode(encoding='ascii', errors='strict'))
    nickname = host.recv(1024).decode(encoding='ascii', errors='strict')
    while clients.get(nickname):
        host.send('NICK'.encode(encoding='ascii', errors='strict'))
        nickname = host.recv(1024).decode(encoding='ascii', errors='strict')
    host.send('Welcome to chat.'.encode(encoding='ascii', errors='strict'))
    return nickname


def handle(server_socket: socket) -> None:
    global clients
    while True:
        try:
            client, address = server_socket.accept()
            print(f'Host: {address} - connected.')
        except IOError as err:
            print('Cant accept connection.\n\t{}'.format(err))
            server_socket.close()
            break
        nick = login(client)
        clients[nick] = client
        broadcast(f'{nick} entered the chat.')
        host_receiver = threading.Thread(target=receive_from,
                                         args=(nick,),
                                         name=f'{nick}_receiver')
        host_receiver.start()


def receive_from(nickname: str) -> None:
    global clients
    while True:
        try:
            message = clients[nickname].recv(1024)
            broadcast(message.decode(encoding='ascii', errors='strict'))
        except ConnectionError as err:
            broadcast(f'{nickname} left the chat..')
            clients[nickname].close()
            del clients[nickname]
            break


def broadcast(text: str) -> None:
    global clients
    for client in clients:
        clients[client].send(text.encode(encoding='ascii', errors='str'))


SCRIPT, HOST, PORT = argv
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

sock.bind((HOST, int(PORT)))
sock.listen()
clients = {}
print('Server is listening...')
handle(sock)
sock.close()
