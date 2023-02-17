# EDTT transport for BabbleSim devices

This is a description of the inner workings of the
EDTT transport for BabbleSim (`edttt_bsim.py` and associated embedded driver)

## Introduction

In simulation the picture of how the communication between the EDTT and the
devices looks as follows:

```
 ___________       __________       _________________
|           | --> |          | --> |                 |
|           |     | Device 0 |     |                 |
| EDTT      | <-- |__________| <-- |                 |
| BSim      |      __________      |                 |
| transport | --> |          | --> |                 |
|           |     | Device 1 |     |                 |
|           | <-- |__________| <-- |                 |
|           |                      |                 |
|           | <------------------- |                 |
|___________| -------------------> |                 |
  |                                |    BabbleSim    |
  |                                |                 |
 ________                          |                 |
|        |                         |                 |
| low    | ----------------------> |                 |
| level  |                         |                 |
| device | <---------------------- |                 |
|________|                         |_________________|

```

Each of the “-->” is a POSIX named pipe (FIFO) (which by default can buffer up to
64KB in each direction).

The low level device (if enabled) is a BSim device in itself; It can be used to inject raw
BLE packets without going through a BLE controller first.

The transport has 2 main functions:

* It allows reading and writting from the EDTT data to the appropriate device
* It pauses the simulation while the EDTT is processing, so there is no asynchronous
  behaviour, and let's it advance only when desired (when wait() is called,
  or when a recv() cannot be completed instantenously


The EDTT, will only run while the simulation itself is paused.

The EDTT can interact in 3 ways with the devices and Phy:
* When the EDTT writes to a device, that data is piped immediately to the device (without unblocking the simulation).
* When the EDTT reads from the device, it tries to read from the device pipe immediately:
  * If it succeeds it responds to the caller immediately with the data
  * If there is not enough data yet from the device, it will wait
    `<RxWait>` in simulated time, that is, it will let the
    simulation time to advance by `<RxWait>`, and try again.
    (`<RxWait>` is a  command line option, by default 10ms)
* When the EDTT does `transport.wait(time)`, it tells the Phy to just let
the simulation time go ahead for `<time>`.


### The embedded device transport

* When the app tries to read from the EDTT transport: it will try immediately
  * If there is enough data, it just returns it to the caller
  * If it does not have enough data yet, and the read was blocking,
    will wait for `EDTT_IF_RECHECK_DELTA` (5ms) and retry
* When told to write it will pipe it to the bridge immediately without any delay

So effectively:

* Writing from the EDTT to the device can be aparent to the device only the next
  time the device checks (up to EDTT_IF_RECHECK_DELTA later)
* Reading from the device can take up to the next `<RxWait>` boundary
  for the EDTT bridge to read it out, apart from the simulated time it may
  take for the device to generate it.


## Implementation details:

The named pipes are placed in /tmp/bsim_<user>/<sim_id>/
There are 2 from the EDTT transport to each device

* Device<device_id>.PTTin
* Device<device_id>.PTTout

### Notes about the transport in the EDTT side

When connect() is called the FIFOs to the Phy will be created
(if not yet there), and the EDTT will be blocked until the Phy
connects on the other side.

Rigth after the FIFOs to the devices will be created, similarly
blocking the EDTTT.

When disconnecting, the transport will attempt to delete the FIFOs
(the last one who disconnects from its end succeds)

### Notes about the transport in the DUT side

On the initial connection, edtt_start(), the pipes are opened,
and the simulated device execution is blocked until the EDTTT
connects to the other side.

When sending and receiving data to and towards the EDTT,
the byte stream is passed through unaltered.

Reads can be blocking (EDTTT_BLOCK), waiting for the bytes to arrive,
or non-blocking (EDTTT_NONBLOCK).

Writes are always treated as non-blocking in this trasnport, assuming that
the FIFO is large enough to queue the request. In the very unlikely case in which
it would not be, an error would be printed.

When the transport layer is closed, the EDTTT FIFOs are closed and deleted.

### Note about the low level device

The low level device attached to the EDTT BSim transport is optional (though some test
cases may require it to be present). By default, the EDTT BSim transport will run without
it; To enable it use the --low-level-device (or -l for short) command line argument.

Since the low level device is a BSim device in itself, it requires a BSim device number
to be assigned to it when enabled; Specify this using the --low-level-device-nbr command line argument.
