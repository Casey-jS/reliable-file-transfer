
import unreliable
import pickle
import socket
import packet

SERVER_ADDR = ("127.0.0.1", 8080)
RECIEVE_WINDOW_SIZE = 5

def processPacket(pkt, file):
    file.write(pkt.data)

def receive(sock, filename):

    bufferedAcks = []
    SeqNumToAck = 0
    LARGEST_ACCEPTABLE_FRAME = RECIEVE_WINDOW_SIZE - 1
    LAST_FRAME_RECIEVED = -1

    try:
        file = open(filename, 'wb')
    except IOError:
        print("Can't open %s" % filename)
    
    while True:
        pkt, address = sock.recvfrom(1099)
        packt: packet = pickle.loads(pkt)

        # If packet seq_num is below of window range, ack was lost and should be re-sent
        if(LAST_FRAME_RECIEVED < packt.seq_num):
            if(packt.seq_num <= LARGEST_ACCEPTABLE_FRAME):
                # if the packet is the next expected, send acknowledgement and process packet
                if(packt.seq_num == SeqNumToAck):
                    # if the packet is shorter then expected, it's the last packet
                    if(len(packt.data) < 1024):
                        LAST_FRAME_RECIEVED += 1
                        print("Sending Ack for packet: %d" % packt.seq_num)
                        send_ack(packt.seq_num, sock, address)
                        processPacket(packt, file)
                        while True:
                            wrapUpPkt, address = sock.recvfrom(1099)
                            wrapUpPackt: packet = pickle.loads(wrapUpPkt)
                            if(wrapUpPackt.seq_num == -1):
                                break
                            else:
                                if(LAST_FRAME_RECIEVED >= wrapUpPackt.seq_num):
                                    print("Re-Sending Ack for packet: %d" % wrapUpPackt.seq_num)
                                    send_ack(wrapUpPackt.seq_num, sock, address)
        
                        break
                    processPacket(packt, file)
                    print("Sending Ack for packet: %d" % packt.seq_num)
                    unreliable.transfer_ack(sock, packt.seq_num, address)
                    # send_ack(packt.seq_num, sock, address) Uncomment later

                    # set next expected sequence number and moves window accordingly
                    LAST_FRAME_RECIEVED = SeqNumToAck
                    LARGEST_ACCEPTABLE_FRAME = LAST_FRAME_RECIEVED + RECIEVE_WINDOW_SIZE
                    SeqNumToAck += 1

                    for packt in bufferedAcks:
                        if packt.seq_num == SeqNumToAck:
                            processPacket(packt, file)
                            send_ack(packt.seq_num, sock, address)
                            LAST_FRAME_RECIEVED = SeqNumToAck
                            LARGEST_ACCEPTABLE_FRAME = LAST_FRAME_RECIEVED + RECIEVE_WINDOW_SIZE
                            SeqNumToAck += 1
                else:
                    # if the packet is not the next packet expected but is within the window, put into buffer
                    bufferedAcks.append(packt)
                    print("Buffered Packet: %d" % packt.seq_num)
        else:
            print("Re-Sending Ack for packet: %d" % packt.seq_num)
            # send_ack(packt.seq_num, sock, address)
            unreliable.transfer_ack(sock, packt.seq_num, address)



def send_ack(seq_num, sock, addr):
    sock.sendto(int.to_bytes(seq_num, 4, byteorder='little', signed=False), addr)

if __name__ == "__main__":

    # TODO - uncomment later, remove hardcoded address

    # Asks for IP Address, Port number, and filename
    # ipAddress = input("Enter an IP Address: ")

    # port = input("Enter a port number: ")

    # SERVER_ADDR = (ipAddress, int(port))


    # create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # send file name to server
    while True:
        filename = input("Enter a FileName: ")

        while True:
            sock.sendto(filename.encode(), SERVER_ADDR)
            sock.settimeout(.1)
            try:
                fileAck, temp = sock.recvfrom(1024)
                break
            except socket.timeout:
                print("Resending filename")

        if(fileAck.decode() == "SUCCESS"):
            break
        else:
            print("File was not opened")

    sock.settimeout(None)

    receive(sock, "pic2.png")

    print("COMPLETE")
        









    