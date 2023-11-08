"""
receiver to sender(usar pickle):
|1 | cSeqN|
ACK messages -> confirmations of correctly received packets
cSeqN -> cumulative sequence number, acknowledging all packets up to and including the given value

receiver:
vai receber blocos e produzir acks (para o sender)
consola: python receiver.py receiverIP receiverPort fileNameInReceiver(nome que vai ter no receiver) twatw
"""

from socket import *
import sys
import pickle
import os
import time
import select

#constants
ACK_MSG = 1
DIAGRAM_SIZE = 1500
BLOCK_SIZE = 1024


def receiveData(receiverSocket : socket, fileNameInReceiver, receiver):
    expectedseqnum = 1
    file = open(fileNameInReceiver, 'wb')
    
    while True:
        
        data,addr = receiverSocket.recvfrom(DIAGRAM_SIZE)
        rcvpkt = pickle.loads(data)
        
        msg = rcvpkt[0]
        seqNum = rcvpkt[1]
        bytes = rcvpkt[2]

        if msg == 0 and  seqNum == expectedseqnum :
            file.write(bytes)
            expectedseqnum += 1
            
        elif msg == 1:
            file.close()
            receiverSocket.close()
            return
        
        answer = pickle.dumps((ACK_MSG, expectedseqnum))
        receiverSocket.sendto(answer, addr)
   
def main():
    receiverIP = sys.argv[1]
    receiverPort = int(sys.argv[2])
    fileNameInReceiver = sys.argv[3]

    receiver = (receiverIP, receiverPort)

    receiverSocket = socket(AF_INET, SOCK_DGRAM)
    receiverSocket.bind(receiver)

    receiveData(receiverSocket, fileNameInReceiver, receiver)

if __name__ == "__main__":
    main()
