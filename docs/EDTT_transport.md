# EDTT transport

The EDTT transport only function is to deliver data from and to the EDTT tests
into the devices under test.

The transport behaves like a pipe/FIFO.

How a given transport is implemented is fully up to the designer. It must only
fulfill the expected interface in both sides: EDTT and the DUT.

On the PC side the transport layer is implemented in Python. On the DUT side it
is implemented in C.


## EDTTT Python IF:

A transport must be implemented as an importable python module and implement the
following API:

* __init__(args, trace_module): where:
    * `<args>` are any command line arguments the EDTT has not been able
      to parse. The transport may use this to
      receive its own parameters. Note that the transport must be tolerant
      to options which are meant for some other module.
    * `<trace_module>` is the class which should be used for printing out
      any possible message

* connect() : Connect to the devices under test.
* send(idx, message): Send the bytearray message to the device number
  `<idx>`
* recv(idx, number_bytes, timeout): Attempt to retrieve `<number_bytes>`
  from the device number `<idx>`. If it cannot manage in `<timeout>`
  milleseconds it shall just return an empty bytearray
* wait(time): Block (wait) for `<time>` ms. Note that in case of simulated
  devices, `<time>` should refer to simultaed time. For real devices, simply
  use the host time.
* close(): Disconnect from the devices under test
* get_time(): Return the current time (simulated time for simulated devices)
* n_devices : Number of devices it is connected to
* low_level_device: Reference to the low_level_device, if available. See [EDTT_transport_bsim.md](EDTT_transport_bsim.md)

## EDTTT DUT IF:

The embedded side of the transport must implement the following interface:

### `bool edtt_start()`

Initialize the transport to the EDTT

### `bool edtt_stop()`

Stop the transport to the EDTT. The app may not send
any more traffic after this.

### `int edtt_read(u8_t *ptr, size_t size, int flags)`

Attempt to read size bytes thru the EDTT IF into the buffer `<*ptr>`.
`<flags>` can be set to EDTTT_BLOCK or EDTTT_NONBLOCK

If set to EDTTT_BLOCK it will block the calling thread until `<size>`
bytes have been read or the interface has been closed.
If set to EDTTT_NONBLOCK it returns as soon as there is no more data
readily avaliable.

Returns the amount of read bytes, or -1 on error

### `int edtt_write(u8_t *ptr, size_t size, int flags)`

Write `<size>` bytes from `<ptr>` toward the EDTTool

`<flags>` can be set to EDTTT_BLOCK or EDTTT_NONBLOCK

If set to EDTTT_BLOCK it will block the calling thread until `<size>`
bytes have been written or the interface has been closed.
If set to EDTTT_NONBLOCK it returns as soon as no more data could be
"immediately" pushed out. Where, although immediately is ambigious,
it must certainly include any action which would yield the thread.

Returns the number of written bytes or -1 on error.

There may be a delay between the time in which the write returns and the
data is avalaible in the EDTT. But it is guaranteed that once this function
return `<n>`, the first `<n>` bytes from `<ptr>` will be delivered to the EDTT
before those of any subsequent call to this function.
After the call returns, the caller is free to reuse the buffer pointed by
`<ptr>`
