# EDTT transport for BabbleSim devices

This is a description of the inner workings of the
EDTT transport for BabbleSim (`edttt_bsim.py` and associated embedded driver)

## Introduction

In simulation the picture of how the communication between the EDTT and the
devices looks as follows:

```
              _____________       __________
             |             | --> |          |
 ______      |             |     | Device 0 |
|      | --> |             | <-- |__________|
| EDTT |     | EDTT Bridge |      __________
|______| <-- |             | --> |          |
             |             |     | Device 1 |
             |_____________| <-- |__________|

```


Each of the “-->” is a POSIX named pipe (FIFO) (which by default can buffer up to
64KB in each direction).

The bridge has 2 main purposes:

* It routes the EDTT data to the appropriate device
* It pauses the simulation while the EDTT is processing, so there is no asynchronous
  behaviour

This is done by having the EDTT command the brdige to either:

 * read to a device
 * write to a devices
 * let simulation time advance
 * terminate the simulation


1. The EDTT, will only run while the simulation itself is paused.
   The EDTT can interact in 3 ways with the devices (thru the bridge)<br>
   When the EDTT writes to a device, that data is piped immediately to the
   bridge.<br>
   When the EDTT reads from the device, it actually sends a command to the
   bridge requesting N bytes with a timeout.<br>
   When the EDTT does `transport.wait(time)`, it tells the bridge to just let
   the simulation time go ahead for `<time>` without doing anything.

2. The Bridge will fully block the simulation until it gets a new command from
   the EDTT

    * If the bridge is commanded to write to a device, it pipes it to the
      device immediately (without unblocking the simulation) and blocks until it
      gets a new command again from the EDTT
    * If it is commanded to “read” from a device, it tries to read from the
      device pipe immediately:

        * If it succeeds it sends it immediately to the EDTT
        * If there is not enough data yet from the device, it will wait
          `<recv_wait_us>` in simulated time, that is, it will let the
          simulation time to advance by `<recv_wait_us>`, and try again.
          (`<recv_wait_us>` is a bridge command line option, by default 10ms)

3. The embedded device transport

    * When the app tries to read from the EDTT transport: it will try
      immediately

        * If there is enough data, it just returns it to the caller
        * If it does not have enough data yet, and the read was blocking,
          will wait for `EDTT_IF_RECHECK_DELTA` (5ms) and retry

    * When told to write it will pipe it to the bridge immediately without any
      delay


So effectively:

* Writing from the EDTT to the device can be aparent to the device only the next
  time the device checks (up to EDTT_IF_RECHECK_DELTA later)
* Reading from the device can take up to the next `<recv_wait_us>` boundary
  for the EDTT bridge to read it out, apart from the simulated time it may
  take for the device to generate it.


## Implementation details:

The named pipes are placed in /tmp/bsim_<user>/<sim_id>/
There is 2 to communicate between the python tests and the bridge:

* Device<bridge_id>.ToEDTT
* Device<bridge_id>.ToBRIDGE

And 2 from the bridge to each device

* Device<device_id>.EDTTin
* Device<device_id>.EDTTout

Between the EDTT bsim transport and the bridge there is a simple protocol,
in which the EDTT side is the master.
Any action performed by the bridge is initiated by the EDTT transport side.

The protocol with the EDTTool is as follows:
```
  1 byte commands are sent from the EDTTool
  The commands are: SEND, RCV, WAIT, DISCONNECT
  SEND is followed by:
    1 byte : device idx
    2 bytes: (uint16_t) number of bytes
    N bytes: payload to forward
  RCV is followed by:
    1 byte : device idx
    8 bytes: timeout time (simulated absolute time)
    2 bytes: (uint16_t) number of bytes
  WAIT:
    8 bytes: (uint64_t) absolute time stamp until which to wait
    (not the wait duration, but the end of the wait)
  DISCONNECT:
    - nothing

 After receiving a command (and its payload) the bridge device will respond:
   to a SEND: nothing
   to a RCV:
     1 byte : reception done (0) or timeout (1)
     8 bytes: timestamp when the reception or timeout actually happened
     0/N bytes: (0 bytes if timeout, N bytes as requested otherwise)
   to a WAIT: nothing
   to a DISCONNECT: nothing
```

That is, when the EDTT writtes to a DUT, a prefix starting with the SEND
command is sent ahead of the data. The bridge looks into this header to know
for which device this message is meant, and how many bytes the message has.
The header is thrown away in the bridge and the message itself forwarded to
that DUT.

A read from the EDTT to a DUT is effectively a command to the bridge to let
the simulation run until that amount of requested data has been received in
the bridge from that DUT, or the timeout has been reached.

### Notes about the transport in the EDTT side

When connect() is called the FIFOs to the bridge will be created
(if not yet there), and the EDTT will be blocked until the bridge
connects on the other side.

Immediately after the number of devices the bridge is connected to
will be read out from the FIFO.

When disconnecting, the transport will attempt to delete the FIFOs
(the last one who disconnects from its end succeds)

### Notes about the bridge

At startup it will create and connect to its end of the pipes
to the EDTT and devices.
It will then send the number of DUTs it is connected to the EDTT
transport side.
After that it will as described before enter an infinite loop
waiting for commands from the EDTT transport, and reacting accordingly.

### Notes about the transport in the DUT side

On the initial connection, edtt_start(), the pipes are opened,
and the simulated device execution is blocked until the bridge
connects to the other side.

When sending and receiving data to and towards the EDTT,
the byte stream is passed through unaltered.

Reads can be blocking (EDTTT_BLOCK), waiting for the bytes to arrive,
or non-blocking (EDTTT_NONBLOCK).

Writes are always treated as non-blocking in this trasnport, assuming that
the FIFO is large enough to queue the request. In the very unlikely case in which
it would not be, an error would be printed.

When the transport layer is closed, the EDTT Bridge FIFOs are closed and deleted.
