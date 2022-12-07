# Copyright 2022 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

# Simple BabbleSim device that supports sending of raw packets on the 2G4 phy
#
# The device supports two actions right now (in addition to connecting and tearing down the device):
# * wait() to allow the simulation time to advance without taking any action
#          This will be called automatically by the EDTT BSim transport when needed
# * tx() for transmitting a raw packet at the specified time
#        Note that only one packet can be transmitting at any given time
#
# The public functions are non-blocking; They simply add to a command queue
# An internally handled thread will pick up these commands and execute them in order

import math
import os
import queue
import struct
import threading

from components.bsim_lib import ( P2G4_MOD_BLE, P2G4_MOD_BLE2M, P2G4_MSG_TX, P2G4_MSG_TX_END, PB_MSG_DISCONNECT, PB_MSG_WAIT, PB_MSG_WAIT_END, TIME_NEVER,
                                  ch_idx_to_2G4_freq, create_com_folder, create_fifo_if_not_there, test_and_create_lock_file )

class BSimDevice:

    device_nbr = -1
    sim_id = ""
    com_path = ""
    lock_path = ""
    ff_path_dtp = ""
    ff_path_ptd = ""
    ff_ptd = 0
    ff_dtp = 0
    connected = False
    simulation_time = 0

    command_queue = queue.Queue()
    worker_thread = None

    def __init__(self, device_nbr, sim_id, TraceClass):
        self.Trace = TraceClass

        self.device_nbr = device_nbr
        self.sim_id = sim_id

    def __process_commands(self):
        while self.connected:
            command, args = self.command_queue.get()
            if (command == PB_MSG_DISCONNECT):
                self.__device_disconnect()
            elif (command == PB_MSG_WAIT):
                self.__device_wait(args[0])
            elif (command == P2G4_MSG_TX):
                self.__device_tx(args[0], args[1], args[2], args[3], args[4])

    def __read(self, fifo, nbr_bytes):
        result = os.read(fifo, nbr_bytes)
        if len(result) != nbr_bytes:
            raise Exception("Low level communication with PHY failed; (tried to get %s got %s bytes)" % (nbr_bytes, len(result)))
        return result

    def connect(self):
        self.com_path = create_com_folder(self.sim_id)

        self.lock_path = test_and_create_lock_file(self.com_path, self.device_nbr, self.Trace)

        self.ff_path_dtp = "%s/%s.d%i.dtp" % (self.com_path, "2G4", self.device_nbr)
        self.ff_path_ptd = "%s/%s.d%i.ptd" % (self.com_path, "2G4", self.device_nbr)

        try:
            create_fifo_if_not_there(self.ff_path_dtp)
            create_fifo_if_not_there(self.ff_path_ptd)

            self.ff_ptd = os.open(self.ff_path_ptd, os.O_RDONLY)
            self.ff_dtp = os.open(self.ff_path_dtp, os.O_WRONLY)

            self.connected = True

            # Start worker
            self.worker_thread = threading.Thread(target=self.__process_commands, daemon=True)
            self.worker_thread.start()
        except:
            self.cleanup()
            raise

    def cleanup(self):
        if self.lock_path:
            try:
                os.remove(self.lock_path)
            except:
                pass
            self.lock_path = ""

        self.connected = False

        if self.ff_path_dtp:
            if self.ff_dtp:
                os.close(self.ff_dtp)
            self.ff_dtp = 0
            try:
                os.remove(self.ff_path_dtp)
            except:
                pass
            self.ff_path_dtp = ""

        if self.ff_path_ptd:
            if self.ff_ptd:
                os.close(self.ff_ptd)
            self.ff_ptd = 0
            try:
                os.remove(self.ff_path_ptd)
            except:
                pass
            self.ff_path_ptd = ""

        if self.com_path:
            try:
                os.rmdir(self.com_path)
            except:
                pass
            self.com_path = ""

    def __device_disconnect(self):
        if self.connected:
            msg = struct.pack('=I', PB_MSG_DISCONNECT)
            os.write(self.ff_dtp, msg)
            self.connected = False

    def disconnect(self):
        if self.connected:
            self.command_queue.put_nowait((PB_MSG_DISCONNECT, []))
            self.worker_thread.join(1.0)
        self.cleanup()

    def __device_wait(self, end_of_wait):
        if self.connected and end_of_wait > self.simulation_time:
            msg = struct.pack("=IQ", PB_MSG_WAIT, end_of_wait)
            os.write(self.ff_dtp, msg)

            # wait for reply
            raw_header = self.__read(self.ff_ptd, 4)

            header, = struct.unpack("=I", raw_header)
            if header == PB_MSG_DISCONNECT:
                self.connected = False
            elif header != PB_MSG_WAIT_END:
                raise Exception("Low level communication with PHY failed; Received invalid response %s" % header)
            self.simulation_time = end_of_wait

    def wait(self, end_of_wait):
        if self.connected:
            self.command_queue.put_nowait((PB_MSG_WAIT, [end_of_wait]))

    def __device_tx(self, ch_idx, phy, aa, transmit_time, packet_data):
        if self.connected:
            # Note: Packet air length is: pre-amble + AA + packetData
            airtime = math.ceil(((2 if phy == '2M' else 1) + 4 + len(packet_data))*8/(2 if phy == '2M' else 1))
            modulation = P2G4_MOD_BLE2M if phy == '2M' else P2G4_MOD_BLE
            freq = ch_idx_to_2G4_freq(ch_idx)

            # Header structure: start_time, end_time, abort_time, (abort_)recheck_time, phy_address, modulation, frequency, power, packet_size
            msg = struct.pack("=IQQQQIHHHH", P2G4_MSG_TX, transmit_time, transmit_time + airtime, TIME_NEVER, TIME_NEVER, aa, modulation, freq, 0, len(packet_data))
            os.write(self.ff_dtp, msg)
            os.write(self.ff_dtp, packet_data)

            # wait for reply
            raw_header = self.__read(self.ff_ptd, 4)

            header, = struct.unpack("=I", raw_header)
            if header == PB_MSG_DISCONNECT:
                self.connected = False
            elif header != P2G4_MSG_TX_END:
                raise Exception("Low level communication with PHY failed; Received invalid response %s" % header)

            raw_end_time = self.__read(self.ff_ptd, 8)
            end_time, = struct.unpack("=Q", raw_end_time)
            self.simulation_time = end_time

    def tx(self, ch_idx, phy, aa, transmit_time, packet_data):
        # Note: packet_data is expected to include CRC
        if self.connected:
            self.command_queue.put_nowait((P2G4_MSG_TX, [ch_idx, phy, aa, transmit_time, packet_data]))
