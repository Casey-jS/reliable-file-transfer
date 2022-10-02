
import pickle
import socket
import packet

SERVER_ADDR = ("127.0.0.1", 8080)
RECIEVE_WINDOW_SIZE = 5

def receive(sock, filename):

    bufferedAcks = []
    LARGEST_ACCEPTABLE_FRAME = RECIEVE_WINDOW_SIZE
    LAST_FRAME_RECIEVED = -1
    SeqNumToAck = 0

    """ try:
        file = open(filename, 'wb')
    except IOError:
        print("Can't open %s" % filename) """
    
    while True:
        pkt, address = sock.recvfrom(1099)

        packt: packet = pickle.loads(pkt)
        
        # If packet seq_num is outside of window range, it is ignored
        if(LAST_FRAME_RECIEVED < packt.seq_num <= LARGEST_ACCEPTABLE_FRAME):

            # if the packet is the next expected, send acknowledgement and process packet
            if(packt.seq_num == SeqNumToAck):
                # if the packet is shorter then expected, it's the last packet
                if(len(packt.data) < 1024):
                    print("Sending Ack for packet: %d" % packt.seq_num)
                    print("COMPLETE")
                    send_ack(packt.seq_num, sock, address)
                    break
                print("Sending Ack for packet: %d" % packt.seq_num)
                send_ack(packt.seq_num, sock, address)

                # TODO - Process Packet (write file)

                
                # set next expected sequence number and moves window accordingly
                if(SeqNumToAck + 1 > 9):
                    LAST_FRAME_RECIEVED = -1
                    LARGEST_ACCEPTABLE_FRAME = RECIEVE_WINDOW_SIZE
                    SeqNumToAck = 0
                else:
                    LAST_FRAME_RECIEVED = SeqNumToAck
                    LARGEST_ACCEPTABLE_FRAME = LAST_FRAME_RECIEVED + RECIEVE_WINDOW_SIZE
                    SeqNumToAck += 1
            else:
                # if the packet is not the next packet expected but is within the window, put into buffer
                bufferedAcks.push(packt)

                # TODO - find out when to process buffer



def send_ack(seq_num, sock, addr):
    sock.sendto(int.to_bytes(seq_num, 4, byteorder='little', signed=False), addr)

if __name__ == "__main__":

    # TODO - uncomment later, remove hardcode address

    # Asks for IP Address, Port number, and filename
    # ipAddress = input("Enter an IP Address: ")

    # port = input("Enter a port number: ")

    # SERVER_ADDR = (ipAddress, port)

    filename = input("Enter a FileName: ")

    # create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # send file name to server
    sock.sendto(filename.encode(), SERVER_ADDR)

    receive(sock, "long.txt")

        









    