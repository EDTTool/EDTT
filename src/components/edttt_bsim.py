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
import fcntl;

from components.bsim_device import BSimDevice
from components.bsim_lib import ( PB_MSG_DISCONNECT, PB_MSG_TERMINATE, PB_MSG_WAIT, PB_MSG_WAIT_END, TIME_NEVER, create_com_folder, create_fifo_if_not_there, test_and_create_lock_file);

class EDTTT:
    TO_EDTT  = 0;
    TO_DEVICE = 1;
    TO_PHY = 1;
    PhyFIFOs = [-1,-1];
    PhyFIFO_names = ["",""];
    FIFOs = [];
    FIFOnames = [];
    verbosity = 0;
    last_t =  0; #last timestamp received from the Phy
    Connected = False;
    n_devices = 0;
    low_level_device = None
    com_path = ""
    lock_path = ""
    autoterminate = True
    RxWait = 10000

    def __init__(self, pending_args, TraceClass):
        self.Trace = TraceClass;
        import argparse
        parser = argparse.ArgumentParser(prog="BabbleSim transport options:", add_help=False)
        parser.add_argument("-s", "--sim_id", required=True, help="Simulation id");
        parser.add_argument("-d", "--EDTT_tool_dev_nbr", required=True, type=int, help="Device number of the EDTT tool itself");
        parser.add_argument("-D", "--number-of-devices", required=True, type=int, help="Number of simulated devices we will connect to (the low level device does not count)");
        parser.add_argument("-devs", "--devices-numbers", required=True, type=int, nargs='+', help="Set of simulated devices we will connect to. There should <number-of-devices> in this list, where the first one will be the \"device 0\" for EDTT and so forth");
        parser.add_argument("-RxWait", required=False, default=10000, type=float, help="(10e3) while there is no enough data for a read, the simulation will be advanced in this steps");
        parser.add_argument("-l", "--low-level-device", required=False, help="Enable BSim low level device; Note that this requires --low-level-device-nbr to be supplied", action='store_true');
        parser.add_argument("--low-level-device-nbr", required=False, type=int, help="Device number of the BSim low level device");
        parser.add_argument("--DontAutoTerminate", required=False, action='store_true', help="Do not terminate simulation when the test ends (by default it will)");
        (args, discard) = parser.parse_known_args(pending_args)

        self.sim_id = args.sim_id;
        self.EDTT_tool_dev_nbr = args.EDTT_tool_dev_nbr;
        self.n_devices = args.number_of_devices;
        self.devices_numbers = args.devices_numbers;
        self.RxWait = int(args.RxWait)

        if args.low_level_device:
            if not args.low_level_device_nbr:
                raise Exception("--low-level-device-nbr is required when the BSim low level device is enabled")
            self.low_level_device = BSimDevice(int(args.low_level_device_nbr), self.sim_id, TraceClass)

        if len(args.devices_numbers) < args.number_of_devices:
            raise Exception("--devices-numbers must have as many elements as configured with number-of-devices")
        
        if args.low_level_device_nbr and (args.low_level_device_nbr <= args.EDTT_tool_dev_nbr):
            raise Exception("The low-level-device-nbr must be higher than the EDTT tool device number (otherwise we will deadlock)")
        
        self.FIFOs = [[-1, -1] for i in range(0,args.number_of_devices)];
        self.FIFOnames = [["", ""] for i in range(0,args.number_of_devices)];
        
        if args.DontAutoTerminate:
            self.autoterminate = false

    def connect(self):
        self.Trace.trace(3,"Connecting to EDTT Phy and devices");
        self.com_path = create_com_folder(self.sim_id);
        self.lock_path = test_and_create_lock_file(self.com_path, self.EDTT_tool_dev_nbr, self.Trace)

        #Note that python ignores SIGPIPE by default

        self.PhyFIFO_names[self.TO_PHY] = "%s/%s.d%i.dtp" % (self.com_path, "2G4", self.EDTT_tool_dev_nbr)
        self.PhyFIFO_names[self.TO_EDTT] = "%s/%s.d%i.ptd" % (self.com_path, "2G4", self.EDTT_tool_dev_nbr)

        try:
            create_fifo_if_not_there(self.PhyFIFO_names[self.TO_PHY]);
            create_fifo_if_not_there(self.PhyFIFO_names[self.TO_EDTT]);

            #Note that the order of opening them needs to be like this. To match the Phy order and avoid deadlocking the other
            #We purposedly want to block until the other side is connected to hold until everything is ready 
            self.PhyFIFOs[self.TO_EDTT] = os.open(self.PhyFIFO_names[self.TO_EDTT], os.O_RDONLY);
            self.PhyFIFOs[self.TO_PHY] = os.open(self.PhyFIFO_names[self.TO_PHY], os.O_WRONLY);

            if (self.PhyFIFOs[self.TO_PHY] == -1):
                raise Exception("Could not open FIFO %s"% self.PhyFIFO_names[self.TO_PHY]);
            if (self.PhyFIFOs[self.TO_EDTT] == -1):
                raise Exception("Could not open FIFO %s"% self.PhyFIFO_names[self.TO_EDTT]);
        except:
            self.cleanup()
            raise

        self.Trace.trace(6,"Connected to Phy");

        if self.low_level_device:
            self.low_level_device.connect()
            self.Trace.trace(8,"Low level device connected to Phy");
        
        try:
            for i in range(0, self.n_devices):
                d = self.devices_numbers[i];
                self.Trace.trace(8,"Connecting to device %i"%d);
                self.FIFOnames[i][self.TO_DEVICE] = "%s/Device%i.PTTin" % (self.com_path, d)
                self.FIFOnames[i][self.TO_EDTT]   = "%s/Device%i.PTTout" % (self.com_path, d)
                #Long ago the EDTT was called PTT. The FIFOs were never renamed as it would be a backwards compatibility change.

                create_fifo_if_not_there(self.FIFOnames[i][self.TO_EDTT]);
                create_fifo_if_not_there(self.FIFOnames[i][self.TO_DEVICE]);

                #Note that we don't set O_NONBLOCK during the creating of the FIFO as we want to block until the device is there
                self.FIFOs[i][self.TO_EDTT] = os.open(self.FIFOnames[i][self.TO_EDTT], os.O_RDONLY);
                if (self.FIFOs[i][self.TO_EDTT] == -1):
                    raise Exception("Could not open FIFO %s"% self.FIFOnames[i][self.TO_EDTT]);

                #we want the read end to be non bloking (if the device didn't produce anything yet, we need to let it run a bit)
                flags = fcntl.fcntl(self.FIFOs[i][self.TO_EDTT], fcntl.F_GETFL);
                flags |= os.O_NONBLOCK;
                fcntl.fcntl(self.FIFOs[i][self.TO_EDTT], fcntl.F_SETFL, flags);

                self.FIFOs[i][self.TO_DEVICE] = os.open(self.FIFOnames[i][self.TO_DEVICE], os.O_WRONLY);
                if (self.FIFOs[i][self.TO_DEVICE] == -1):
                    raise Exception("Could not open FIFO %s"% self.FIFOnames[i][self.TO_DEVICE]);
    
                #we want the  write end to be non bloking (if for whatever reason
                # we fill up the FIFO, we would deadlock as the device is stalled
                # => better to catch it in the write function)
                flags = fcntl.fcntl(self.FIFOs[i][self.TO_DEVICE], fcntl.F_GETFL);
                flags |= os.O_NONBLOCK;
                fcntl.fcntl(self.FIFOs[i][self.TO_DEVICE], fcntl.F_SETFL, flags);

                self.Trace.trace(8,"Connected to device %i"%d);
        except:
            self.cleanup()
            raise

        self.Connected = True;
        self.Trace.trace(4,"Connected to Phy and all devices");

        # Wait for dump files to have been opened by the 2G4 phy
        # Since there isn't a method implemented for synchronizing that, use the
        # fact that any commands to the 2G4 phy will not run until after it has
        #opened the files for writing; So use a minimal wait as a blocking mechanism
        self.wait_until_t(1)

    def cleanup(self):
        if self.lock_path:
            try:
                os.remove(self.lock_path)
            except:
                pass
            self.lock_path = ""

        if self.low_level_device:
            self.Trace.trace(4,"Cleaning up low-level device");
            self.low_level_device.cleanup()

        self.Trace.trace(4,"Cleaning up transport");
        try:
            if self.PhyFIFOs[self.TO_EDTT]:
                os.close(self.PhyFIFOs[self.TO_EDTT]);
                self.PhyFIFOs[self.TO_EDTT] = 0
                self.Trace.trace(9,"Closed FIFO to Phy (->EDTT direction)");
            if self.PhyFIFOs[self.TO_PHY]:
                os.close(self.PhyFIFOs[self.TO_PHY]);
                self.PhyFIFOs[self.TO_PHY] = 0
                self.Trace.trace(9,"Closed FIFO to Phy (->Phy direction)");
            os.remove(self.PhyFIFO_names[self.TO_PHY]);
            os.remove(self.PhyFIFO_names[self.TO_EDTT]);

            for i in range(0, self.n_devices):
                self.Trace.trace(9,"Cleaning up interface to Device %i"%i);
                if self.FIFOs[i][self.TO_EDTT]:
                    os.close(self.FIFOs[i][self.TO_EDTT]);
                    self.FIFOs[i][self.TO_EDTT] = 0
                    self.Trace.trace(9,"Closed FIFO to Device %i (->EDTT direction)"%i);
                if self.FIFOs[i][self.TO_DEVICE]:
                    os.close(self.FIFOs[i][self.TO_DEVICE]);
                    self.FIFOs[i][self.TO_DEVICE] = 0
                    self.Trace.trace(9,"Closed FIFO to Device %i (->Device direction)"%i);
                os.remove(self.FIFOnames[i][self.TO_DEVICE]);
                os.remove(self.FIFOnames[i][self.TO_EDTT]);
        except OSError:
            self.Trace.trace(9,"(minor) Error closing FIFO "
                             "(most likely either file does not exist yet)");

    def __disconnect(self):
        if self.Connected:
            self.Connected = False
            if self.autoterminate:
                msg = struct.pack('=I', PB_MSG_TERMINATE)
                self.Trace.trace(4,"Terminating simulation")
            else:
                msg = struct.pack('=I', PB_MSG_DISCONNECT)
                self.Trace.trace(4,"Disconnecting from Phy")
            self.__write_to_phy(msg);
        if self.low_level_device:
            self.low_level_device.disconnect()

    def close(self):
        self.__disconnect();
        self.cleanup();

    def __write_to_device(self, d, content):
        # Write content to device d
        try:
            written = os.write(self.FIFOs[d][self.TO_DEVICE], content);
            if written != len(content):
                raise;
        except:
            self.Trace.trace(4,"The Device %i disappeared when trying to "
                             "write to it"%d);
            self.close();
            raise Exception("Abruptly disconnected from device %i"%d);

    def __read_from_device(self, d, nbytes):
        # Atttempt a non-blocking read of nbytes from device d
        pkt=b""
        try:
            pkt = os.read(self.FIFOs[d][self.TO_EDTT], nbytes);
        except BlockingIOError:
            #No enough data available yet, we just return an empty packet
            #or whatever we got so far
            pass
        except:
            self.Trace.trace(4,"The Device %i disappeared when trying to "
                             "read from it"%d);
            self.close();
            raise Exception("Abruptly disconnected from device %i"%d);

        return pkt;

    def __write_to_phy(self,  content):
        # Write content to the Phy
        try:
            written = os.write(self.PhyFIFOs[self.TO_PHY], content);
            if written != len(content):
                raise;
        except:
            self.Trace.trace(4,"The Phy disappeared when trying to "
                             "write to it");
            self.Connected = False
            self.close();
            raise Exception("Abruptly disconnected from Phy");

    def __read_from_phy(self, nbytes):
        # Read (blocking) nbytes from the Phy.
        # If less bytes are read, we consider it an error
        try:
            pkt = os.read(self.PhyFIFOs[self.TO_EDTT], nbytes);
            if len(pkt) != nbytes:
                raise;
            return pkt;
        except:
            self.Trace.trace(4,"The Phy disappeared when trying to "
                             "read from it");
            self.Connected = False
            self.close();
            raise Exception("Abruptly disconnected from Phy");

    def send(self, idx, message):
        #Send <message> to device <idx>
        if (idx > self.n_devices -1):
            raise Exception("Trying to access unconnected device %i"%idx);

        self.Trace.trace(8,"Writing %i bytes to device %i"%(len(message),idx));
        self.__write_to_device(idx,message)
        # a send is immediate (no time advance)
        self.Trace.btsnoop.send(idx, message)

    def recv(self, idx, number_bytes, to=None):
        #Attempt to receive <number_bytes> from device <idx>, with a timeout of <to> ms
        if (idx > self.n_devices -1):
            raise Exception("Trying to access unconnected device %i"%idx);

        if to == None:
            to = self.default_to
        if ( number_bytes == 0 ):
          return b""

        timeout = to*1000 + self.last_t;
        
        self.Trace.trace(8, "Recv of %iB from dev %d, timeout %i ms"% (number_bytes, idx, to) )

        # Let's try to read from the device. We will either manage right away
        # or we will need to let time advance while we keep retrying
        pending_to_read = number_bytes
        readsofar = 0
        packet = b""
        while self.last_t < timeout:
            segment = self.__read_from_device(idx, pending_to_read)
            packet += segment
            nread = len(segment)
            readsofar += nread
            pending_to_read -= nread;
            if pending_to_read > 0: #we need to wait a bit
                self.Trace.trace(6, "During recv of %iB from dev %d, pending %i, Waiting for %s us"%
                                  (number_bytes, idx, pending_to_read, str(self.RxWait)) )
                self.wait(self.RxWait/1000)
            else:
                break 

        if pending_to_read != 0:
            self.Trace.trace(2, "Attempt to recv from dev %d, but only read %i out of %i bytes"%(idx, readsofar, number_bytes))
        else:
            self.Trace.trace(8, "Attempt to recv from dev %d, read all %i bytes"%(idx, number_bytes))

        return packet

    def wait(self, delay_in_ms):
        end_of_wait = int(delay_in_ms*1000 + self.last_t);
        return self.wait_until_t(end_of_wait)

    def wait_until_t(self, end_of_wait):
        if self.last_t >= end_of_wait:
            self.Trace.trace(3, "Ignoring end_of_wait with a time not in the future: simulation time: %s; Requested end of wait: %s" % (self.last_t, end_of_wait))
            return

        self.Trace.trace(8, "Waiting until %d"%end_of_wait)

        if self.low_level_device:
            self.low_level_device.wait(end_of_wait)

        if self.Connected:
            #A wait request to the Phy is a 32bit PB_MSG_WAIT header followed by
            #a 64 bit time_to_wait integer value in microseconds
            msg = struct.pack("=IQ", PB_MSG_WAIT, end_of_wait)
            self.__write_to_phy(msg)
    
            # Block until we get the reply from the Phy which a 32 bit value. 
            # It can either be an indication that the wait ended PB_MSG_WAIT_END
            # or a PB_MSG_DISCONNECT == an order to disconnected
            raw_header = self.__read_from_phy(4)

            header, = struct.unpack("=I", raw_header)
            if header == PB_MSG_DISCONNECT:
                self.Trace.trace(2, "Phy told us to disconnect")
                self.Connected = False
                self.__disconnect()
                raise Exception("Simulated terminated by the Phy")
            elif header != PB_MSG_WAIT_END:
                raise Exception("Low level communication with PHY failed; Received invalid response %s" % header)

        self.last_t = end_of_wait

    def get_time(self):
        #return current time in miliseconds
        return self.last_t/1000;

    def get_last_t(self):
        #return current time in microseconds
        return self.last_t
