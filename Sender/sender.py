""" 
www2.tkn.tu-berlin.de/teaching/rn/animations/gbn_sr/

testar com todos os tipos de arquivos 
testar com maquinas distintas (ou docker)
(dá para ir buscar os endereços com o docker inspect)
usar pickle
usar UDP datagrams
implementar com Sliding Window e Go-Back-N protocol model
os 2 programas devem terminar qunaod o ficheiro for transferido
ter atenção ao termino da tranferencia do ficheiro (data < 1024 bytes nao funciona sempre)
instanciar um timeout:
    -latência(tempo de transmissão de um pacote de um lado para o outro)
    -tempo = descobrir a 2*latência com, uns pontos de tempo, descobrir quanto tempo demora a chegar a resposta
    -tem de ser um pouco maior que esse valor (1.1*tempo)
there is no packet corruption

//Usar dicionário para a definição de janela:
//   -key: seqN
//   -value: data

sender to receiver(usar pickle):
|0 | seqN | data|
seqN -> sequence number, starting at 1 for the first block
data -> 1024 bytes max of data

sender:
blocos fixos de 1024 bytes
consola: python sender.py senderHostName senderPort receiverHostName receiverPort filename_receiver windowSizeInBlocks(nº de  blocos)
"""

from io import BufferedReader
from socket import *
import sys
import pickle
import time
import random
import select
import os
import types

#constants

states = types.SimpleNamespace()
states.SENDING_MSG = 0
states.WAIT_ACKS_MSG = 1
states.FILE_SENT = 2

BLOCK_SIZE = 1024
RATE_LOSS = 0
TIMEOUT = 1

DATA_MSG = 0
END_MSG = 1
TIMEOUT_MSG = 0
PCKT_RECEIVED_MSG = 1

def sendData ( sock: socket, data, dest):
    rand = random.randint(1, 10)
    if (rand > RATE_LOSS):
        sock.sendto(data, dest)
    else:
        print("Packet loss, sequence number = ", pickle.loads(data)[1])

def sendChunk (sock: socket, file: BufferedReader, dest, chunkNum):
    fileBytes = file.read(BLOCK_SIZE)
    if (len(fileBytes) == 0) :
        print("End of file")
        return 
        
    data = pickle.dumps((DATA_MSG, chunkNum, fileBytes))
    sendData(sock, data, dest)

    return (len(fileBytes), data)

def waitForAnswer (sock) :
    rx, tx, er = select.select([sock], [], [], TIMEOUT)
    if rx == []:
        print("Timeout")
        return TIMEOUT_MSG
    else:
        return PCKT_RECEIVED_MSG

def sendFile (sock: socket, file: BufferedReader, dest, sizeOfSW, fileSize) :
    #initializing variables
    swBase = 1
    nextSeqNum = 1
    maxSeqNum = fileSize // BLOCK_SIZE + 1
    bytesSent = 0

    #initializing Sliding Window 
    sw = {}

    while (nextSeqNum < swBase + sizeOfSW and nextSeqNum <= maxSeqNum):
        bySent, data = sendChunk(sock, file, dest, nextSeqNum)
        sw[nextSeqNum] = data
        nextSeqNum += 1
        bytesSent += bySent
    
    if nextSeqNum == maxSeqNum:
        state = states.WAIT_ACKS_MSG
    else:
        state = states.SENDING_MSG

    answer = waitForAnswer(sock)

    while True:
        match (state):
            case states.SENDING_MSG:
                if (answer == TIMEOUT_MSG):
                    for i in range(swBase, nextSeqNum):
                        sendData(sock, sw[i], dest)

                elif (answer == PCKT_RECEIVED_MSG):
                    data, adress = sock.recvfrom(BLOCK_SIZE)
                    content = pickle.loads(data)
                    seqNum = content[1]
                    if (seqNum >= swBase):
                        for i in range(swBase, seqNum):
                            del sw[i]
                        swBase = seqNum + 1
                        bySent, data = sendChunk(sock, file, dest, nextSeqNum)
                        sw[nextSeqNum] = data
                        bytesSent += bySent

                        if nextSeqNum == maxSeqNum:
                            state = states.WAIT_ACKS_MSG  

                        nextSeqNum += 1
    
                answer = waitForAnswer(sock)
                continue       
            
            case states.WAIT_ACKS_MSG:
                if (answer == TIMEOUT_MSG):
                    for i in range(swBase-1, maxSeqNum ):
                        sendData(sock, sw[i], dest)
                else:
                    if (swBase > maxSeqNum):
                        state = states.FILE_SENT
                        
                    else:
                        data, adress = sock.recvfrom(BLOCK_SIZE)
                        content = pickle.loads(data)
                        seqNum = content[1]
                        if (seqNum >= swBase):
                            for i in range(swBase, seqNum):
                                del sw[i]
                            swBase = seqNum + 1
                            sendData(sock, sw[maxSeqNum], dest)
                        
                answer = waitForAnswer(sock)
                continue
            
            case states.FILE_SENT:
                sock.sendto(pickle.dumps((END_MSG, 0, 0)), dest)
                print("File sent")
                sock.close()
                file.close() 
                return              
        
def main():
    senderHostName = sys.argv[1]
    senderPort = int(sys.argv[2])
    sender = (senderHostName, senderPort)

    receiverHostName = sys.argv[3]
    receiverPort = int(sys.argv[4])
    receiver = (receiverHostName, receiverPort)

    filename_receiver = sys.argv[5]
    file = open(filename_receiver, "rb")

    windowSizeInBlocks = int(sys.argv[6])

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(sender)

    sendFile( sock, file, receiver, windowSizeInBlocks, os.path.getsize(filename_receiver) )
    
    sock.close()

if __name__ == "__main__":
    main()
