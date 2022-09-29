import socket
import packet
import pickle

WINDOW_SIZE = 5
CLIENT_ADDR = ("127.0.0.1", 8080)
LAST_FRAME_SENT = -1
LAST_ACK_RECEIVED = -1


def get_five_packets(file_name):

    data = open(file_name, 'rb')
    packets = []

    while len(packets) != 5:
        packt = packet.packet(len(packets), b'data', data.read(1024))
        packets.append(packt)
    
    return packets
    

if __name__ == "__main__":

    # create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # bind to client address
    sock.bind(CLIENT_ADDR)

    # get file name from client
    print("Waiting for file name...")
    file_name, addr = sock.recvfrom(1024)
    print("%s requested" % file_name.decode())
    # decode the name
    decoded_name = file_name.decode()

    # get array of packet objects
    packets_to_send = get_five_packets(decoded_name)

    for p in packets_to_send:
        print("Packet.data size before pickle: %d" % len(p.data))
        pickle_packet = pickle.dumps(p, pickle.HIGHEST_PROTOCOL)
        print("len(packet) = %d" % len(pickle_packet))
        
        sock.sendto(pickle_packet, addr)
        print("sent packet %d to client" % p.seq_num)

    while True:
        ack, addr = sock.recvfrom(1024)
        print("ack received:", int.from_bytes(ack, byteorder='little'))
