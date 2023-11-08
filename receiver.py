"""
receiver to sender(usar pickle):
|1 | cSeqN|
ACK messages -> confirmations of correctly received packets
cSeqN -> cumulative sequence number, acknowledging all packets up to and including the given value

receiver:
vai receber blocos e produzir acks (para o sender)
consola: python receiver.py receiverIP receiverPort fileNameInReceiver(nome que vai ter no receiver)
"""

from socket import *
import sys
import pickle
import os
import time
import select

#constants
ACK_MSG = 1
BLOCK_SIZE = 1024


def receiveData(receiverSocket, fileNameInReceiver):
    expectedseqnum = 1
    
    data = receiverSocket.recv(BLOCK_SIZE)
    rcvpkt = pickle.loads(data) # recebe isto pickle.dumps((DATA_MSG, chunkNum, fileBytes))
    
    seqNumber = 0

    if rcvpkt[0] == 0 and rcvpkt[1] == expectedseqnum :
        with open(fileNameInReceiver, 'wb') as f :
            f.write(rcvpkt[2])
        seqNumber = expectedseqnum
        expectedseqnum += 1
        
    elif rcvpkt[0] == 1:
        f.close
        receiverSocket.close()
        return

    answer = pickle.dumps((ACK_MSG, seqNumber))    
    receiverSocket.send(answer)
   
def main():
    receiverIP = sys.argv[1]
    receiverPort = int(sys.argv[2])
    fileNameInReceiver = sys.argv[3]

    receiver = (receiverIP, receiverPort)

    receiverSocket = socket(AF_INET, SOCK_DGRAM)
    receiverSocket.bind(receiver)

    receiveData(receiverSocket, fileNameInReceiver)

if __name__ == "__main__":
    main()