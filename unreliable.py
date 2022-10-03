import socket
import random
import packet


def transfer(sock: socket.socket, pkt, addr):

    r = random.randint(1, 5)

    if r == 2:
        sock.sendto(pkt, addr)