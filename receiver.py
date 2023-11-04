"""
receiver to sender(usar pickle):
|1 | cSeqN|
ACK messages -> confirmations of correctly received packets
cSeqN -> cumulative sequence number, acknowledging all packets up to and including the given value

receiver:
vai receber blocos e produzir acks (para o sender)
consola: python receiver.py receiverIP receiverPort fileNameInReceiver(nome que vai ter no receiver)
"""