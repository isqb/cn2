'''
Created on Oct 28, 2014

@author: Rsandhu
'''
import sys,socket,struct,select
from socket import getfqdn, gethostbyname
from _socket import gethostname
from multiprocessing.connection import Client

def testHostName():
    smthing = socket.getaddrinfo("joshua.it.uu.se",6969)
    smthing = smthing[0]
    smthing = smthing[4:]#[0]
    print("getaddrinfo return: {}".format(smthing) )
    myLocalHost = gethostname()
    print (myLocalHost)
    myIP = gethostbyname(myLocalHost)
    print(myIP)

def testread():
    # choose a file
    #filename = "small.txt"
    #filename = "medium.pdf"
    filename = "large.jpeg"
    
    #build/bind socket
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #client_sock.bind((client_addresss))
    
    #create/send data to server
    server_address = socket.getaddrinfo("joshua.it.uu.se", 6969)[0][4:][0]
    data = struct.pack("!H", 1) + filename + '\0' + "octet" + '\0'
    client_sock.sendto(data,server_address)
    client_address = client_sock.getsockname()
    print("myip: {} myport: {}".format(client_address[0],client_address[1]))
    count = 1 #first data pack seq=1
    
    #write data to file (in a loop)
    fd = open(filename, 'wb')
    print("fd: {}".format(fd))
    while True:
        print("------ waiting for packet [{}] --------".format(count))
        # receive data and server_address
        data, server_address = client_sock.recvfrom(1024)
        parsed = parse_message(data)
        opcode = parsed[0]
        
        # check correct opcode and seq, throw error possibly?
        if (opcode == 3):
            opcode,seq,msg = parsed
            size = len(msg)
            print("opcode: {} seq: {} count: {}".format(opcode, seq,count))
            print ("size: {}".format(size))
            if (count == seq):
                print ("writing message [{}]".format(count))
                #send ACK, update count
                ackpacket = struct.pack("!HH", 4,count)
                count = count + 1
                fd.write(msg)
                client_sock.sendto(ackpacket,server_address)
            #else: #todo?
        # check size and close if small (send final?)
            if (size < 512):
                break
        
    # shutdown
    fd.close()
    client_sock.close()
    
def testwrite():
    #struct.pack("!H", OPCODE_WRQ) + filename + '\0' + MODE_OCTET + '\0'
    data = struct.pack("!H", 2) + "somefile.txt" + '\0' + "octet" + '\0'
    server_address = socket.getaddrinfo("joshua.it.uu.se", 6969)[0][4:][0]
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    fd = open('C:\Users\Rsandhu\Desktop\writetothisfile.txt', 'rb')
    print("fd: {}".format(fd.read(512)))
    print("fd: {}".format(fd.read(512)))
    return
    
    
    
    #client_sock.connect(server_address)
    print("server_adrdress: {}".format(server_address))
    client_sock.sendto(data,server_address)
    client_address = client_sock.getsockname()
    print 'starting client_sock on {} port {}'.format(client_address[:1],client_address[1:])
    print ("waiting to read...")
    data, server_address = client_sock.recvfrom(1024)
    msg = struct.unpack("!HH",data)
    print ("receive: {}".format(msg))
    print ("server: {}".format(server_address))
    
    #construct data packet
    f = open('C:\\Users\\Rsandhu\\Desktop\\copyThisFile.txt', 'rb')
    print f
    data = struct.pack("!HH", 3,1) + f.read()
    print ("sending : {}".format(data)) # how format this <<?
    
    client_sock.sendto(data, server_address)
    data, server_address = client_sock.recvfrom(1024)
    print (data)
    msg1, msg2 = struct.unpack("!HH",data)
    print("msg1: {} msg2: {}".format(msg1, msg2))
    client_sock.close()    
    print ("done")
    return None

def parse_message(msg):
    """This function parses a recieved message and returns a tuple where the
        first value is the opcode as an integer and the following values are
        the other parameters of the messages in python data types"""
########################################
    OPCODE_RRQ = 1
    OPCODE_WRQ = 2
    OPCODE_DATA=3
########################################
    opcode = struct.unpack("!H", msg[:2])[0]
    if opcode == OPCODE_RRQ:
        l = msg[2:].split('\0')
        if len(l) != 3:
            return None
        return opcode, l[1], l[2]
    elif opcode == OPCODE_WRQ:
        # TDOO
        return opcode, # something here
    # TDOD
    elif (opcode == OPCODE_DATA):
        seq = struct.unpack("!H",msg[2:4])[0]
        block = msg[4:]
        return opcode, seq, block
    return None

if __name__ == '__main__':
    
    #testread()
    testwrite()
    #testHostName()