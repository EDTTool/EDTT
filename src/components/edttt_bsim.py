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
import signal;
import stat;

def create_dir(folderpath):
    if not os.path.exists(folderpath):
        if ( os.mkdir( folderpath , stat.S_IRWXG | stat.S_IRWXU ) != 0 ) \
            and ( os.access( folderpath, os.F_OK ) == False ):
          raise Exception("Cannot create folder %s"% folderpath);

def create_com_folder(sim_id):
    import getpass
    Com_path = "/tmp/bs_" + getpass.getuser();
    create_dir(Com_path);
    Com_path = Com_path + "/" + sim_id;
    create_dir(Com_path);
    return Com_path;

def Create_FIFO_if_not_there(FIFOName):
    #we try to create a fifo which may already exist, and/or that some other
    #program may be racing to create at the same time
    if ( os.access( FIFOName, os.F_OK ) == False ):
        try:
            err = os.mkfifo(FIFOName,  stat.S_IRWXG | stat.S_IRWXU);
        except OSError as e:
            if (e.errno == 17): #File already exists => we are done
                return;
            else:
                raise Exception("Could not create FIFO %s", FIFOName);

        if (err != 0) and ( os.access( FIFOName, os.F_OK ) == False ):
            raise Exception("Could not create FIFO %s", FIFOName);


class EDTTT:
    COM_DISCONNECT = 0;
    COM_WAIT       = 1;
    COM_SEND       = 2;
    COM_RCV        = 3;

    TO_EDTT  = 0;
    TO_BRIDGE =1;
    FIFOs = [-1, -1];
    FIFOnames = [ "" , "" ];
    verbosity = 0;
    last_t =  0; #last timestamp received from the bridge
    Connected = False;
    n_devices = 0;

    def __init__(self, pending_args, TraceClass):
        self.Trace = TraceClass;
        import argparse
        parser = argparse.ArgumentParser(prog="BabbleSim transport options:", add_help=False)
        parser.add_argument("-s", "--sim_id", required=True, help="Simulation id");
        parser.add_argument("-d", "--bridge-device-nbr", required=True, help="Device number of the EDTT bridge");
        (args, discard) = parser.parse_known_args(pending_args)

        self.device_nbr = args.bridge_device_nbr;
        self.sim_id = args.sim_id;

    def connect(self):
        Com_path = create_com_folder(self.sim_id);

        self.Trace.trace(3,"Connecting to EDTT bridge");

        #Note that python ignores SIGPIPE by default

        self.FIFOnames[self.TO_EDTT] = \
            Com_path + "/Device" + str(self.device_nbr) + ".ToPTT";
        self.FIFOnames[self.TO_BRIDGE] = \
            Com_path + "/Device" + str(self.device_nbr) + ".ToBridge";

        Create_FIFO_if_not_there(self.FIFOnames[self.TO_EDTT]);
        Create_FIFO_if_not_there(self.FIFOnames[self.TO_BRIDGE]);

        self.FIFOs[self.TO_BRIDGE] = os.open(self.FIFOnames[self.TO_BRIDGE], os.O_WRONLY);
        self.FIFOs[self.TO_EDTT] = os.open(self.FIFOnames[self.TO_EDTT], os.O_RDONLY);

        if (self.FIFOs[self.TO_BRIDGE] == -1):
            raise Exception("Could not open FIFO %s"% self.FIFOnames[self.TO_BRIDGE]);

        if (self.FIFOs[self.TO_EDTT] == -1):
            raise Exception("Could not open FIFO %s"% self.FIFOnames[self.TO_EDTT]);

        self.Connected = True;
        self.Trace.trace(4,"Connected to EDTT bridge");

        packet = self.read(2);
        self.n_devices = struct.unpack('<H',packet[0:2])[0];

    def cleanup(self):
        self.Trace.trace(4,"Cleaning up transport");
        try:
            os.close(self.FIFOs[self.TO_BRIDGE]);
            self.Trace.trace(9,"Closed FIFO to Bridge");
            os.close(self.FIFOs[self.TO_EDTT]);
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

        self.ll_send(struct.pack('<BBQH', self.COM_RCV, idx, timeout, number_bytes));

        header = self.read(9);

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
        # pack a message : delay 4 bytes
        end_of_wait = delay_in_ms*1000 + self.last_t;
        self.ll_send(struct.pack('<BQ', self.COM_WAIT, end_of_wait));
        self.last_t = end_of_wait;

    def get_time(self):
        return self.get_last_t()/1000;
