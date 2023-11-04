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

import socket
import sys
import pickle
import time
import os

