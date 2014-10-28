#! /usr/bin/python

import sys,socket,struct,select
from socket import getfqdn
from random import randint

BLOCK_SIZE= 512

OPCODE_RRQ=   1
OPCODE_WRQ=   2
OPCODE_DATA=  3
OPCODE_ACK=   4
OPCODE_ERR=   5

MODE_NETASCII= "netascii"
MODE_OCTET=    "octet"
MODE_MAIL=     "mail"

TFTP_PORT= 69

# Timeout in seconds
TFTP_TIMEOUT= 2

ERROR_CODES = ["Undef",
               "File not found",
               "Access violation",
               "Disk full or allocation exceeded",
               "Illegal TFTP operation",
               "Unknown transfer ID",
               "File already exists",
               "No such user"]

# Internal defines
TFTP_GET = 1
TFTP_PUT = 2


def make_send_rrq(filename, mode):
    # Note the exclamation mark in the format string to pack(). What is it for?
    return struct.pack("!H", OPCODE_RRQ) + filename + '\0' + mode + '\0'

def make_send_wrq(filename):
    return struct.pack("!H", OPCODE_WRQ) + filename + '\0' + MODE_OCTET + '\0' # TODO

def make_send_data(blocknr, data):
    return struct.pack("!H", OPCODE_DATA) + struct.pack("!H", blocknr) + data # TODO

def make_send_ack(blocknr):
    return struct.pack("!H",OPCODE_ACK) + '\0' # TODO

def make_send_err(errcode, errmsg):
    return struct.pack("!H",OPCODE_ERR) + errmsg + '\0' # TODO

def parse_message(msg):
    """This function parses a recieved message and returns a tuple where the
        first value is the opcode as an integer and the following values are
        the other parameters of the messages in python data types"""
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
    return None

def tftp_transfer(fd, hostname, direction):
    # Implement this function
    # -----------------------
    
    #Server address provided
    # -----------------------
    #ServURL = "joshua.it.uu.se"
    
    #Ports provided
    # -----------------------
    #69 - The standard port, reserved for TFTP. Only accessible inside the university network.
    #6969 - Same as 69 but accessible outside the university network as well.
    #10069 - Generates packet loss, you need to send a large enough file to get some packet loss. (Accessible both inside and outside the university network)
    #20069 - Generates duplicates, you need to send a large enough file to get duplicates. (Accessible both inside and outside the university network)
    pub_port = 6969
    uni_port = 69
    pkgLoss_port = 10069
    pkgDup_port = 20069
    
    #client_port = randint(1024,49150)#1024 through 49151 
    # hostname =  socket.gethostbyname(hostname)
    server_address = (hostname,TFTP_PORT)
    #client_address = (gethostname(),client_port)
    #server_address = (ServURL, pub_port)
    # Open socket interface
    # -----------------------
    # Create socket
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #client_sock.bind(client_address)
    #client_sock.connect(server_address)# don't need connect for udp (i think). For C, if do sock.connect, then can send udp packets with sock.send
    print 'starting up on %s port %s' % server_address
    # Establish socket connection to server
    
    # client_sock.connect((ServURL, pub_port))
    # client_sock.bind(server_address)
    # Create file-descriptor
    #fdFromSock = client_sock.fileno()
    select.select(fd)
    
    # Check if we are putting a file or getting a file and send
    #  the corresponding request.
    # -----------------------
    
    
    
    if(direction == TFTP_PUT):
        reqPacket = make_send_wrq(fd)
           
    elif(direction == TFTP_GET):
        reqPacket = make_send_rrq(fd, MODE_OCTET) 
        
    client_sock.sendall(reqPacket)    
        
    # Put or get the file, block by block, in a loop.
    # -----------------------
    
    
    
    while True:
        print '\n awaiting packet ack'
        data = client_sock.recv(BLOCK_SIZE)
        print '\n data received: %s' %data
        # Wait for packet, write the data to the filedescriptor or
        # read the next block from the file. Send new message to server.
        # Don't forget to deal with timeouts.
        pass


def usage():
    """Print the usage on stderr and quit with error code"""
    sys.stderr.write("Usage: %s [-g|-p] FILE HOST\n" % sys.argv[0])
    sys.exit(1)


def main():
    # No need to change this function
    direction = TFTP_GET
    if len(sys.argv) == 3:
        filename = sys.argv[1]
        hostname = sys.argv[2]
    elif len(sys.argv) == 4:
        if sys.argv[1] == "-g":
            direction = TFTP_GET
        elif sys.argv[1] == "-p":
            direction = TFTP_PUT
        else:
            usage()
            return
        filename = sys.argv[2]
        hostname = sys.argv[3]
    else:
        usage()
        return

    if direction == TFTP_GET:
        print "Transfer file %s from host %s" % (filename, hostname)
    else:
        print "Transfer file %s to host %s" % (filename, hostname)

    try:
        if direction == TFTP_GET:
            fd = open(filename, "wb")
        else:
            fd = open(filename, "rb")
    except IOError as e:
        sys.stderr.write("File error (%s): %s\n" % (filename, e.strerror))
        sys.exit(2)

    tftp_transfer(fd, hostname, direction)
    fd.close()

if __name__ == "__main__":
    main()