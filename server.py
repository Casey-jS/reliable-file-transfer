
import socket
import packet
import pickle
import unreliable

SENDER_WINDOW_SIZE = 5
MAX_SEQ_NUM = SENDER_WINDOW_SIZE * 2
SERVER_ADDR = ("127.0.0.1", 8080)
global LAST_FRAME_SENT

def print_nums_in_window(sendWindow):
    print("CURRENT WINDOW")
    print("[ ", end="")
    for p in sendWindow:
        print("%d, " % p.seq_num, end="")
    print("]")

# Reads next 1024 bytes of file and puts it into packet
def get_packet(data, seqNum):
    buf = data.read(1024) 
    if buf:
        packt = packet.packet(seqNum, b'data', buf)
        return packt 

def find_oldest_packet(sendWindow):
    oldestPacketNum = sendWindow[0].seq_num
    for p in sendWindow:
        if p is None:
            break
        if p.seq_num < oldestPacketNum:
            oldestPacketNum = p.seq_num
    return oldestPacketNum

# sends packet, p, to address, addr, using sock 
def send_packet(p, addr, sock):
    pickle_packet = pickle.dumps(p, pickle.HIGHEST_PROTOCOL)
    unreliable.transfer(sock, pickle_packet, addr)

def fill_window(sendWindow, fp):
    global LAST_FRAME_SENT
    while(len(sendWindow) < SENDER_WINDOW_SIZE):
        LAST_FRAME_SENT += 1
        packt = get_packet(fp, LAST_FRAME_SENT)
        sendWindow.append(packt)
    return sendWindow

def resend_packets(sendWindow, sock, addr, oldestPacketNum):
    global LAST_FRAME_SENT
    for p in sendWindow:
        if p is None:
            break
        if p.seq_num == oldestPacketNum:
            print("Re-sending packet: %d" % p.seq_num)
            send_packet(p, addr, sock)
            
    while(True):
        sock.settimeout(.5)
        try:
            tempPackt, addr = sock.recvfrom(1024)
            tempAckNum = int.from_bytes(tempPackt, byteorder='little')
            if(tempAckNum == oldestPacketNum):
                print("Ack received: %d" % tempAckNum)
                for p in sendWindow:
                    if tempAckNum == p.seq_num:
                        sendWindow.remove(p)
                break
            else:
                print("Ack received: %d" % tempAckNum)
                for p in sendWindow:
                    if tempAckNum == p.seq_num:
                        sendWindow.remove(p)

        except socket.timeout:
            for p in sendWindow:
                if p.seq_num == oldestPacketNum:
                    print("Re-sending packet: %d" % p.seq_num)
                    send_packet(p, addr, sock)
            
    sock.settimeout(None)
    return sendWindow

def wrap_up(sendWindow, addr, sock):
    print("WRAP UP")
    while(len(sendWindow) > 0):
        sock.settimeout(.1)
        try:
            ack, addr = sock.recvfrom(1024)
            ackNum = int.from_bytes(ack, byteorder='little')
            oldestPacketNum = find_oldest_packet(sendWindow)
            if(ackNum - oldestPacketNum != 0):
                print("Ack received: %d" % ackNum)
                sendWindow = resend_packets(sendWindow, sock, addr, oldestPacketNum)
            else:
                print("Ack recieved: %d" % ackNum)
                for p in sendWindow:
                    if p is None:
                        break
                    if p.seq_num == ackNum:
                        sendWindow.remove(p)
        except socket.timeout:
            oldestPacketNum = find_oldest_packet(sendWindow)
            for p in sendWindow:
                if p.seq_num == oldestPacketNum:
                    send_packet(p, addr, sock)
    return "BREAK"

# When an ack is recieved, take corresponding packet out of the window,
# grab a new one and send it
def ack_recieved(ackNum, sendWindow, fp, sock, addr):
    oldestPacketNum = find_oldest_packet(sendWindow)
    if(ackNum - oldestPacketNum != 0):
        if(ackNum > oldestPacketNum):
            for p in sendWindow:
                if p.seq_num == ackNum:
                    sendWindow.remove(p)

            sendWindow = resend_packets(sendWindow, sock, addr, oldestPacketNum)
            sendWindow = fill_window(sendWindow, fp)
            for p in sendWindow:
                if(len(p.data) >= 1024):
                    print("Sending Packet: %d" % p.seq_num)
                    send_packet(p, addr, sock)
                else:
                    send_packet(p, addr, sock)
                    print("Sending Packet: %d" % p.seq_num)
                    return wrap_up(sendWindow, addr, sock)
    else:
        for p in sendWindow:
            if p.seq_num == ackNum:
                global LAST_FRAME_SENT
                LAST_FRAME_SENT += 1
                packt = get_packet(fp, LAST_FRAME_SENT)
                if(len(packt.data) >= 1024):
                    sendWindow.remove(p)
                    sendWindow.append(packt)
                    send_packet(packt, addr, sock)
                    print("Sending Packet: %d" % packt.seq_num)
                else:
                    sendWindow.remove(p)
                    sendWindow.append(packt)
                    send_packet(packt, addr, sock)
                    print("Sending Packet: %d" % packt.seq_num)
                    return wrap_up(sendWindow, addr, sock)
    return sendWindow
 
def get_file():
    print("Waiting for file name...")
    while True:
        file_name, addr = sock.recvfrom(1024)
        print("%s requested" % file_name.decode())
        # decode the name
        decoded_name = file_name.decode()
        try:
            fp = open(decoded_name, 'rb')
            return fp, addr
        except IOError:
            print("File could not be opened.")
            exit()


if __name__ == "__main__":

    # create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # bind to client address
    sock.bind(SERVER_ADDR)

    # get file name from client
    fp, addr = get_file()

    sendWindow = []
    LAST_FRAME_SENT = -1
    LOWEST_NUM_IN_WINDOW = 0

    # Reads first 5 packets
    for i in range(SENDER_WINDOW_SIZE):
        packt = get_packet(fp, i)
        if(packt != "BREAK"):
            sendWindow.append(packt)
        else:
            wrap_up(sendWindow, addr, sock)

    # Sends packets current in the window
    for p in sendWindow:

        print("Sending Packet: %d" % p.seq_num)
        send_packet(p, addr, sock)
        LAST_FRAME_SENT += 1
    
    # waits for an ack
    while True:
        sock.settimeout(.2)
        try:
            print("AWAITING ACKNOWLEDGEMENTS")
            ack, addr = sock.recvfrom(1024)
            ackNum = int.from_bytes(ack, byteorder='little')
            print("Ack received: %d" % ackNum)
            sendWindow = ack_recieved(ackNum, sendWindow, fp, sock, addr)
        except socket.timeout:
            pkt = find_oldest_packet(sendWindow)
            for p in sendWindow:
                if p.seq_num == pkt:
                    send_packet(p, addr, sock)

        if(sendWindow == "BREAK"):
            break

    packt = packet.packet(-1, b'data', "")
    send_packet(packt, addr, sock)
    print("FILE TRANSFERRED")

