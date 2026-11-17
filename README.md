# Reliable File Transfer over UDP

A **Go-Back-N** sliding-window protocol built on top of UDP, written from scratch in Python. It transfers a file between two hosts over an unreliable datagram channel, handling loss, reordering and timeouts.


## Why this is interesting

UDP gives you nothing: no ordering, no acknowledgements, no retransmission. This project rebuilds those guarantees manually.

## Protocol

Each datagram is a `pickle`-encoded tuple, so the receiver can tell frames apart without a separate header parser:

| Direction | Frame | Meaning |
|---|---|---|
| sender → receiver | `(0, seqN, data)` | Data block, up to 1024 bytes |
| receiver → sender | `(1, cumulativeSeqN, 0)` | Cumulative ACK — everything up to and including `seqN` arrived |
| sender → receiver | `(END_MSG, 0, 0)` | Transfer complete |

**Sliding window.** The sender may have up to `windowSizeInBlocks` unacknowledged blocks in flight.

**Go-Back-N.** On timeout the sender retransmits from the first unacknowledged block; the receiver discards anything out of order and re-ACKs the last in-order sequence number.

**Timeout.** Chosen relative to the measured round-trip latency with a safety margin (> 1.1× RTT), so a slow link does not trigger spurious retransmissions.

**Termination.** The transfer ends with an explicit end-of-file frame rather than relying on a short final block, which is unreliable when the file size is a multiple of the block size.

## Run

Two terminals (or two machines):

```bash
# receiver
python3 Receiver/receiver.py 127.0.0.1 9000 received.bin

# sender
python3 Sender/sender.py 127.0.0.1 9001 127.0.0.1 9000 file_to_send.bin 8
```

Sender arguments: `senderHost senderPort receiverHost receiverPort file windowSize`.
Receiver arguments: `receiverIP receiverPort outputFileName`.

## Files

| Path | Responsibility |
|---|---|
| `Sender/sender.py` | Window management, timers, retransmission |
| `Receiver/receiver.py` | In-order delivery, cumulative ACKs |
| `Sender/`, `Receiver/` | Test payloads used during development |

## Notes

- Standard library only (`socket`, `pickle`, `select`, `os`, `time`).
- The protocol assumes **no packet corruption** — only loss and reordering — as the protocol requires.
- Educational code; there is no encryption or authentication.
