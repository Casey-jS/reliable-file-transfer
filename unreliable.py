import socket
import random
import packet


def transfer(sock: socket.socket, pkt, addr):

    r = random.randint(1, 5)

    if r != 2:
        sock.sendto(pkt, addr)


def transfer_ack(sock: socket.socket, seq_num, addr):

    r = random.randint(1, 5)

    if r == 2:
        sock.sendto(int.to_bytes(seq_num, 4, byteorder='little', signed=False), addr)