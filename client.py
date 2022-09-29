
import pickle
import socket
import packet

SERVER_ADDR = ("127.0.0.1", 8080)
WINDOW_SIZE = 5

def receive(sock, filename):
    """ try:
        file = open(filename, 'wb')
    except IOError:
        print("Can't open %s" % filename) """
    
    expected = 0
    print("this line hit")
    while True:
        pkt, address = sock.recvfrom(1097)

        packt: packet = pickle.loads(pkt)
        print("Raw packet seq_num: ", packt.seq_num)
        sequence_num = packt.seq_num
        print("Packet %d received" % sequence_num)

        

        if sequence_num == expected:
            print("Expected packet received")
            print("Sending ack for packet: ", sequence_num)
            send_ack(sequence_num, sock, address)
            expected += 1

        """ else:
            print("Sending ack ", expected - 1)
            send_ack(sequence_num - 1, sock, address) """



        



def send_ack(seq_num, sock, addr):
    sock.sendto(int.to_bytes(seq_num, 4, byteorder='little', signed=False), addr)

if __name__ == "__main__":
    # create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # send file name to server
    sock.sendto(b"long.txt", SERVER_ADDR)

    while True:

        receive(sock, "long.txt")

        









    