# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

#EDTT Transport driver for BabbleSim
# Any EDTT Transport shall implement the following interface:
#   __init__(args)
#   connect()
#   send(idx, message)
#   recv(idx, number_bytes, timeout)
#   wait(time)
#   close()
#   get_time()
#   n_devices : Number of devices it is connected to

import struct;
import os;

from components.bsim_device import BSimDevice
from components.bsim_lib import create_com_folder, create_fifo_if_not_there;

class EDTTT:
    COM_DISCONNECT = 0;
    COM_WAIT       = 1;
    COM_WAIT_WRESP = 5;
    COM_SEND       = 2;
    COM_RCV        = 3;
    COM_RCV_WAIT_NOTIFY = 4
    COM_WAIT_NOTIFICATION = 0xF0
    COM_UNKNOWN_COMMAND = 0xFF

    TO_EDTT  = 0;
    TO_BRIDGE =1;
    FIFOs = [-1, -1];
    FIFOnames = [ "" , "" ];
    verbosity = 0;
    last_t =  0; #last timestamp received from the bridge
    Connected = False;
    n_devices = 0;
    low_level_device = None

    def __init__(self, pending_args, TraceClass):
        self.Trace = TraceClass;
        import argparse
        parser = argparse.ArgumentParser(prog="BabbleSim transport options:", add_help=False)
        parser.add_argument("-s", "--sim_id", required=True, help="Simulation id");
        parser.add_argument("-d", "--bridge-device-nbr", required=True, help="Device number of the EDTT bridge");
        parser.add_argument("-l", "--low-level-device", required=False, help="Enable BSim low level device; Note that this requires --low-level-device-nbr to be supplied", action='store_true');
        parser.add_argument("--low-level-device-nbr", required=False, help="Device number of the BSim low level device");
        (args, discard) = parser.parse_known_args(pending_args)

        self.device_nbr = args.bridge_device_nbr;
        self.sim_id = args.sim_id;

        if args.low_level_device:
            if not args.low_level_device_nbr:
                raise Exception("--low-level-device-nbr is required when the BSim low level device is enabled")
            self.low_level_device = BSimDevice(int(args.low_level_device_nbr), self.sim_id, TraceClass)

    def connect(self):
        Com_path = create_com_folder(self.sim_id);

        self.Trace.trace(3,"Connecting to EDTT bridge");

        #Note that python ignores SIGPIPE by default

        self.FIFOnames[self.TO_EDTT] = \
            Com_path + "/Device" + str(self.device_nbr) + ".ToPTT";
        self.FIFOnames[self.TO_BRIDGE] = \
            Com_path + "/Device" + str(self.device_nbr) + ".ToBridge";

        create_fifo_if_not_there(self.FIFOnames[self.TO_EDTT]);
        create_fifo_if_not_there(self.FIFOnames[self.TO_BRIDGE]);

        self.FIFOs[self.TO_BRIDGE] = os.open(self.FIFOnames[self.TO_BRIDGE], os.O_WRONLY);
        self.FIFOs[self.TO_EDTT] = os.open(self.FIFOnames[self.TO_EDTT], os.O_RDONLY);

        if (self.FIFOs[self.TO_BRIDGE] == -1):
            raise Exception("Could not open FIFO %s"% self.FIFOnames[self.TO_BRIDGE]);

        if (self.FIFOs[self.TO_EDTT] == -1):
            raise Exception("Could not open FIFO %s"% self.FIFOnames[self.TO_EDTT]);

        self.Connected = True;
        self.Trace.trace(4,"Connected to EDTT bridge");

        if self.low_level_device:
            self.low_level_device.connect()

        packet = self.read(2);
        self.n_devices = struct.unpack('<H',packet[0:2])[0];

        # Wait for dump files to have been opened by the 2G4 phy
        # Since there isn't a method implemented for synchronizing that, use the fact that any commands to the 2G4 phy will not
        # run until after it has opened the files for writing; So use a minimal wait as a blocking mechanism
        self.wait_until_t(1)

    def cleanup(self):
        if self.low_level_device:
            self.Trace.trace(4,"Cleaning up low-level device");
            self.low_level_device.cleanup()

        self.Trace.trace(4,"Cleaning up transport");
        try:
            if self.FIFOs[self.TO_BRIDGE]:
                os.close(self.FIFOs[self.TO_BRIDGE]);
                self.FIFOs[self.TO_BRIDGE] = 0
                self.Trace.trace(9,"Closed FIFO to Bridge");
            if self.FIFOs[self.TO_EDTT]:
                os.close(self.FIFOs[self.TO_EDTT]);
                self.FIFOs[self.TO_EDTT] = 0
                self.Trace.trace(9,"Closed FIFO to EDTT");
            os.remove(self.FIFOnames[self.TO_BRIDGE]);
            os.remove(self.FIFOnames[self.TO_EDTT]);
        except OSError:
            self.Trace.trace(9,"(minor) Error closing FIFO "
                             "(most likely either file does not exist yet)");

    def disconnect(self):
        if self.Connected:
            self.Trace.trace(4,"Disconnecting bridge")
            self.ll_send(struct.pack('<B', self.COM_DISCONNECT));
            self.Connected = False;
        if self.low_level_device:
            self.low_level_device.disconnect()

    def close(self):
        self.disconnect();
        self.cleanup();

    def get_last_t(self):
      return self.last_t

    def ll_send(self, content):
        try:
            written = os.write(self.FIFOs[self.TO_BRIDGE], content);
            if written != len(content):
                raise;
        except:
            self.Trace.trace(4,"The EDTT bridge disappeared when trying to "
                             "write to it");
            self.cleanup();
            raise Exception("Abruptly disconnected from bridge");

    def ll_read(self, nbytes):
        try:
            pkt = os.read(self.FIFOs[self.TO_EDTT], nbytes);
            if len(pkt) == 0:
                raise;
            return pkt;
        except:
           self.Trace.trace(4,"The EDTT bridge disapeared when trying to read "
                              "from it");
           self.cleanup();
           raise Exception("Abruptly disconnected from bridge");

    def send(self, idx, message):
        if (idx > self.n_devices -1):
            raise Exception("Trying to access unconnected device %i"%idx);
        # build the packet
        packet = struct.pack('<BBH', self.COM_SEND, idx, len(message)) + message
        # send the packet
        self.ll_send(packet)
        # a send is immediate (no time advance)
        self.Trace.btsnoop.send(idx, message)

    def read(self, nbytes):
        received_nbytes = 0;
        packet = bytearray();

        #print "Will try to pick " + str(nbytes) + " bytes"
        while ( len(packet) < nbytes):
            packet += self.ll_read(nbytes - received_nbytes);
            #print "Got so far " + str(len(packet)) + " bytes"
            #print 'packet: "' + repr(packet) + '"'
        return packet;

    def recv(self, idx, number_bytes, to=None):
        if (idx > self.n_devices -1):
            raise Exception("Trying to access unconnected device %i"%idx);

        #print ("EDTT: ("+str(idx)+") request rcv of "+ str(number_bytes) + " bytes; to = " + str(to));
        if to == None:
            to = self.default_to
        if ( number_bytes == 0 ):
          return b""

        timeout = to*1000 + self.last_t;
        # Poll the bridge for a response
        #print ("EDTT: ("+str(idx)+") request rcv of "+ str(number_bytes) + " bytes; timeout = " + str(timeout));

        if self.low_level_device:
            self.ll_send(struct.pack('<BBQH', self.COM_RCV_WAIT_NOTIFY, idx, timeout, number_bytes));
        else:
            self.ll_send(struct.pack('<BBQH', self.COM_RCV, idx, timeout, number_bytes));

        header = bytearray()
        if self.low_level_device:
            header = self.read(1)
            while (header[0] == self.COM_WAIT_NOTIFICATION):
                rawTime = self.read(8)
                timestamp, = struct.unpack("<Q", rawTime)
                self.Trace.trace(6, "Advancing time to " + str(timestamp))
                self.low_level_device.wait(timestamp)
                header = self.read(1)
            header += self.read(8)
        else:
            header = self.read(9)

        #print '"' + repr(header[1:])+ '"'
        #print "length = " + str(len(header[1:]))
        self.last_t = struct.unpack('<Q',header[1:])[0];
        #print "last_t updated to " + str(self.last_t)

        packet=b""
        if header[0] == 0x00: #correct reception => packet follows
          #print "correctly received " + str(number_bytes) + " bytes"
          packet = self.read(number_bytes)
          if (len(packet) != number_bytes):
            raise Exception("very weird..")
          #print "packet itself =" + repr(packet)

        return packet

    def wait(self, delay_in_ms):
        end_of_wait = delay_in_ms*1000 + self.last_t;
        return self.wait_until_t(end_of_wait)

    def wait_until_t(self, end_of_wait):
        if self.last_t >= end_of_wait:
            self.Trace.trace(3, "Ignoring end_of_wait with a time not in the future: simulation time: %s; Requested end of wait: %s" % (self.last_t, end_of_wait))
            return

        if self.low_level_device:
            self.low_level_device.wait(end_of_wait)
        # pack a message : delay 4 bytes
        self.ll_send(struct.pack('<BQ', self.COM_WAIT_WRESP, end_of_wait))
        # Read dummy byte reply from bridge, signalling wait completion
        resp = self.read(1);
        if (resp[0] != 0x00 or resp[0] == self.COM_UNKNOWN_COMMAND):
            raise Exception("You are using a too old EDTT bridge, please update it "
                            "(Most likely you can find the EDTT bridge in the bsim components folder,"
                            "%{BSIM_COMPONENTS_PATH} )\nLow level resp = " + str(resp[0]))
        self.last_t = end_of_wait

    def get_time(self):
        return self.get_last_t()/1000;
