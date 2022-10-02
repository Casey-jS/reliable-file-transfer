
import socket
import packet
import pickle

SENDER_WINDOW_SIZE = 5
MAX_SEQ_NUM = SENDER_WINDOW_SIZE * 2
SERVER_ADDR = ("127.0.0.1", 8080)
global LAST_FRAME_SENT

# Reads next 1024 bytes of file and puts it into packet
def get_packet(data, seqNum):
    buf = data.read(1024) 
    if buf:
        packt = packet.packet(seqNum, b'data', buf)
        return packt 
    else:
        return "END" 

# sends packet, p, to address, addr, using sock 
def send_packet(p, addr, sock):
    pickle_packet = pickle.dumps(p, pickle.HIGHEST_PROTOCOL)
    sock.sendto(pickle_packet, addr)

# When an ack is recieved, take corresponding packet out of the window,
# grab a new one and send it
def ack_recieved(ackNum, sendWindow, fp, sock, addr):
    for p in sendWindow:
        if p.seq_num == ackNum:
            global LAST_FRAME_SENT
            LAST_FRAME_SENT += 1
            packt = get_packet(fp, LAST_FRAME_SENT)
            if(packt != "END"):
                sendWindow.remove(p)
                sendWindow.append(packt)
                send_packet(packt, addr, sock)
                print("Sending Packet: %d" % packt.seq_num)
            else:
                return "BREAK"
        if p.seq_num < ackNum:
            send_packet(p, addr, sock)
    return sendWindow
 


if __name__ == "__main__":

    # create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # bind to client address
    sock.bind(SERVER_ADDR)

    # get file name from client
    print("Waiting for file name...")
    file_name, addr = sock.recvfrom(1024)
    print("%s requested" % file_name.decode())
    # decode the name
    decoded_name = file_name.decode()

    fp = open(decoded_name, 'rb')

    sendWindow = []
    LAST_FRAME_SENT = -1

    # Reads first 5 packets
    for i in range(SENDER_WINDOW_SIZE):
        packt = get_packet(fp, i)
        if(packt != "END"):
            sendWindow.append(packt)

    # Sends packets current in the window
    for p in sendWindow:
        print("Sending Packet: %d" % p.seq_num)
        send_packet(p, addr, sock)
        LAST_FRAME_SENT += 1
    
    # waits for an ack
    while True:
        print("AWAITING ACKNOWLEDGEMENTS")
        ack, addr = sock.recvfrom(1024)
        ackNum = int.from_bytes(ack, byteorder='little')
        print("Ack received: %d" % ackNum)
        sendWindow = ack_recieved(ackNum, sendWindow, fp, sock, addr) 
        if(sendWindow == "BREAK"):
            break

    print("FILE TRANSFERRED")

