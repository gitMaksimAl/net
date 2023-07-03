import socket
from sys import stderr, argv
import threading

SCRIPT, HOST, PORT = argv
nickname = input('Please enter your nickname: ')


def recv_message() -> None:
    while True:
        try:
            message = sock.recv(1024).decode(encoding='ascii', errors='strict')
            if message == 'NICK':
                sock.send(nickname.encode(encoding='ascii', errors='strict'))
            else:
                print(message)
        except (IOError, InterruptedError, UnicodeWarning) as err:
            sock.close()
            print('Some issue. Connection closed.')
            print(err, file=stderr)
            stderr.close()
            break


def send_message() -> None:
    while True:
        try:
            message = '{}: {}'.format(nickname, input())
            sock.send(message.encode(encoding='ascii', errors='strict'))
        except (IOError, InterruptedError, KeyboardInterrupt) as err:
            sock.close()
            print('Connection closed by client side.')
            print(err, file=stderr)
            stderr.close()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((HOST, int(PORT)))
    print('Connected.')
except ConnectionError as err:
    print(f'Cant connect to remote host: {(HOST, PORT)}')
    print(err, file=stderr)
    exit(1)

in_stream = threading.Thread(target=recv_message, name='in_stream')
out_stream = threading.Thread(target=send_message, name='out_stream')
in_stream.start()
out_stream.start()
in_stream.join()
out_stream.join()
