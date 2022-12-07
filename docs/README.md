## Introduction

The EDTT (Embedded Device Test Tool) is a collection of python scripts, which include:

* The PC side of a simple basic Remote Procedure Call (RPC)
* A transport mechanism, which is used by this RPC to transport
  data in an out of an embedded device
* A set of self checking tests of the BLE functionality
  (both host and controller)
* A basic tool which wraps all of this, and executes a set of
  tests as selected from command line

## More information

More information about the RPC transport can be found in
[EDTT_transport.md](EDTT_transport.md)<br>
And about the transport used with BabbleSim in
[EDTT_transport_bsim.md](EDTT_transport_bsim.md)

A document giving an introduction on how to use the EDTT
with BabbleSim and how to write tests can be found in
[EDTT_framework_BabbleSim.md](docs/EDTT_framework_BabbleSim.md)

## License

Please see LICENSE

## Developer Certification of Origin (DCO)

This project requires the Developer Certificate of Origin (DCO)
process to be followed for its contributions.

This is done as a resonable measure to ensure all code in the project
can be licensed under the claimed terms.

By adding a ``Signed-off-by`` line to the commit body message like:
```
   Signed-off-by: John Doe <JohnDoe@somedomain.com>
```
the contributor certifies that he has the right to, and does submit
that patch, under the applicable license, and, that he agrees to the DCO.

The DCO agreement can be found in http://developercertificate.org/, and is
shown below:

```
   Developer Certificate of Origin
   Version 1.1

   Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
   1 Letterman Drive
   Suite D4700
   San Francisco, CA, 94129

   Everyone is permitted to copy and distribute verbatim copies of this
   license document, but changing it is not allowed.

   Developer's Certificate of Origin 1.1

   By making a contribution to this project, I certify that:

   (a) The contribution was created in whole or in part by me and I
       have the right to submit it under the open source license
       indicated in the file; or

   (b) The contribution is based upon previous work that, to the best
       of my knowledge, is covered under an appropriate open source
       license and I have the right under that license to submit that
       work with modifications, whether created in whole or in part
       by me, under the same open source license (unless I am
       permitted to submit under a different license), as indicated
       in the file; or

   (c) The contribution was provided directly to me by some other
       person who certified (a), (b) or (c) and I have not modified
       it.

   (d) I understand and agree that this project and the contribution
       are public and that a record of the contribution (including all
       personal information I submit with it, including my sign-off) is
       maintained indefinitely and may be redistributed consistent with
       this project or the open source license(s) involved.
