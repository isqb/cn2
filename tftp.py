#! /usr/bin/python

import sys,socket,struct,select

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


def make_packet_rrq(filename, mode):
    # Note the exclamation mark in the format string to pack(). What is it for?
    return struct.pack("!H", OPCODE_RRQ) + filename + '\0' + mode + '\0'

def make_packet_wrq(filename, mode):
    return struct.pack("!H", OPCODE_WRQ) + filename + '\0' + MODE_OCTET + '\0' 

def make_packet_data(blocknr, data):
    return struct.pack("!HH", OPCODE_DATA,blocknr) + data

def make_packet_ack(blocknr):
    return struct.pack("!HH",OPCODE_ACK,blocknr) 

def make_packet_err(errcode, errmsg):
    return struct.pack("!H",OPCODE_ERR) + errmsg + '\0'

def parse_packet(msg):
    """This function parses a recieved packet and returns a tuple where the
        first value is the opcode as an integer and the following values are
        the other parameters of the packets in python data types"""
    opcode = struct.unpack("!H", msg[:2])[0]
    if opcode == OPCODE_RRQ:
        l = msg[2:].split('\0')
        if len(l) != 3:
            return None
        return opcode, l[1], l[2]
    elif opcode == OPCODE_WRQ:
        l = msg[2:].split('\0')
        if len(l) != 3:
            return None
        return opcode, l[1], l[2]
    elif (opcode == OPCODE_DATA):
        seq = struct.unpack("!H",msg[2:4])[0]
        data = msg[4:]
        return opcode, seq, data
    elif (opcode == OPCODE_ACK):
        blocknr = struct.unpack("!H", msg[2:4])[0]
        data = ""
        return opcode,blocknr,msg
    elif(opcode == OPCODE_ERR):
        errcode = struct.unpack("!H",msg[2:4])[0]
        l = msg[4:].split('\0')
        if len(l) != 2:
            return None
        return opcode, errcode, l[0]
    return None

def tftp_transfer(fd, hostname, direction):
    ## Implement this function
    
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
    servURL = "joshua.it.uu.se"
    
    #### PRGRM WITH THESE ####
    sendtoport = pub_port
    
    ## Open socket interface
    #build socket
    server_address = socket.getaddrinfo(servURL, sendtoport)[0][4:][0]
    print("serveradress: {} {}".format(server_address[0], server_address[1]))
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    ## Check if we are putting a file or getting a file and send
    ##  the corresponding request. 
    if(direction == TFTP_PUT):
        print ("write request packet")
        reqPacket = make_packet_wrq(fd.name, MODE_OCTET)
        count = 0 
    elif(direction == TFTP_GET):
        print("read request packet")
        reqPacket = make_packet_rrq(fd.name, MODE_OCTET)
        count = 1 #either we receive data(1), or we send data(1) 
        
    lastpacketsent = False
    updated = False
    tosendpacket = ""
    client_sock.sendto(reqPacket,server_address)    
    
    ## Put or get the file, block by block, in a loop.
    while True:
        print("------ waiting for packet [{}]--------".format(count))
        readable, writable, exceptional = select.select([client_sock],[],[],1)
        
        # received packet
        if len(readable)> 0:
            packet,packet_address = client_sock.recvfrom(1024)
            opcode, blocknr, data = parse_packet(packet)
            #print("opcode: {} blocknr:{} data: {}".format(opcode, blocknr, data))
            if updated == False:
                updated = True
                server_address = packet_address
                print("SAchanged: {} {}".format(server_address[0], server_address[1]))
            
            # check if packet is being sent from correct destination
            # send errpacket to packet src if wrong packet. no BREAK.
            if packet_address != server_address:
                errpacket = make_packet_err(5, "Invalid Destination")
                client_sock.sendto(errpacket,packet_address)
                opcode = 0 #<-- will cause to skip rest of code

        #print("parsed: {}".format(parsed))
        ##(GET) Wait for packet, write the data to the filedescriptor or
        
        # Timeout. Did not receive packet, resend, skips rest of elif's
        if (len(readable)< 1) and (opcode != 0):
            if (direction == TFTP_GET) and (lastpacketsent):
                break
            print("TIMEOUT. resend count-1: {}".format(count-1))
            client_sock.sendto(tosendpacket,server_address)
        elif (blocknr == count-1) and (opcode != 0):
            print("DUPLICATE resend count-1: {}".format(count-1))
            client_sock.sendto(tosendpacket,server_address)
        elif (opcode == OPCODE_ERR):
            print ("err: opcode: {} errcode: {} errmsg: {}".format(opcode,ERROR_CODES[blocknr],data))
            break
        elif (opcode == OPCODE_DATA):
            size = len(data)
            if (count == blocknr):
                #send ACK, update count
                tosendpacket = make_packet_ack(count)
                count = count + 1
                fd.write(data)
                client_sock.sendto(tosendpacket,server_address)
            if (size < 512): #need to wait in case duplicate of previous packet sent. Might get solved by select()
                lastpacketsent = True
        
        ##(PUT) read the next block from the file. Send new message to server.
        elif (opcode == OPCODE_ACK):
            if count == blocknr:
                if lastpacketsent == True:
                    break
                count = count + 1
                data = fd.read(512)
                size = len(data)
                tosendpacket = make_packet_data(count, data)
                client_sock.sendto(tosendpacket,server_address)
                if size < 512:
                    lastpacketsent = True
                    
        elif opcode == OPCODE_RRQ:
            pass
        elif opcode == OPCODE_WRQ:
            pass
        else:
            # send error packet
            # break?
            pass
        
                
        ## Don't forget to deal with timeouts.
        #    ^ for this we will have to implement select and change our code.
    client_sock.close()
    print("done")
    

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