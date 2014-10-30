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
    #build/bind socket
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_sock.bind(("130.243.130.27",58450))
    
    #create/send data to server
    server_address = socket.getaddrinfo("joshua.it.uu.se", 6969)[0][4:][0]
    data = struct.pack("!H", 1) + "small.txt" + '\0' + "octet" + '\0'
    client_sock.sendto(data,server_address)
    count = 1 #first data pack seq=1
    
    #write data to file (in a loop)
    fd = open('writetothisfile.txt', 'wb')
    while True:
        print("------ waiting for packet [{}] --------".format(count))
        # receive data and server_address
        data, server_address = client_sock.recvfrom(1024)
        opcode, seq = struct.unpack("!HH",data[:4])
        msg = data[4:]
        size = len(msg)
        print("opcode: {} seq: {} count: {}".format(opcode, seq,count))
        print ("size: {}".format(size))
        
        # check correct opcode and seq, throw error possibly?
        if (opcode == 3) and (count == seq):
            print ("writing message [{}]".format(count))
            #send ACK, update count
            ackpacket = struct.pack("!HH", 4,count)
            count = count + 1
            fd.write(msg)
            client_sock.sendto(ackpacket,server_address)
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
    #client_sock.connect(server_address)
    print("server_adrdress: {}".format(server_address))
    client_sock.bind(("130.243.130.27",58449))
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


if __name__ == '__main__':
    
    testread()
    #testwrite()
    #testHostName()