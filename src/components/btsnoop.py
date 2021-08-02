#! /usr/bin/env python3
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

import socket
import struct
import time

from components.basic_commands import Commands
from datetime import datetime
from enum import IntEnum

class BleMonitorOpcode(IntEnum):
    NEW_INDEX = 0
    DEL_INDEX = 1
    COMMAND = 2
    EVENT = 3
    ACL_TX = 4
    ACL_RX = 5
    OPEN_INDEX = 8
    SYSTEM_NOTE = 12
    USER_LOGGING = 13
    ISO_TX = 18
    ISO_RX = 19

class BtsnoopPriority(IntEnum):
    EMERGENCY = 0
    ALERT = 1
    CRITICAL = 2
    ERROR = 3
    WARNING = 4
    NOTICE = 5
    INFO = 6
    DEBUG = 7

class Btsnoop:
    def __init__(self, store_to_file, socket_path) -> None:

        self.non_hci_edtt_cmds = (Commands.CMD_HAS_EVENT_REQ, Commands.CMD_HAS_EVENT_RSP,
                                Commands.CMD_FLUSH_EVENTS_REQ, Commands.CMD_FLUSH_EVENTS_RSP,
                                Commands.CMD_GET_EVENT_REQ,
                                Commands.CMD_LE_DATA_FLUSH_REQ, Commands.CMD_LE_DATA_FLUSH_RSP,
                                Commands.CMD_LE_DATA_READY_REQ, Commands.CMD_LE_DATA_READY_RSP,
                                Commands.CMD_LE_DATA_READ_REQ, Commands.CMD_LE_DATA_WRITE_RSP,
                                Commands.CMD_LE_ISO_DATA_FLUSH_REQ, Commands.CMD_LE_ISO_DATA_FLUSH_RSP,
                                Commands.CMD_LE_ISO_DATA_READY_REQ, Commands.CMD_LE_ISO_DATA_READY_RSP,
                                Commands.CMD_LE_ISO_DATA_READ_REQ, Commands.CMD_LE_ISO_DATA_WRITE_RSP)

        self.tx_data_edtt_cmds = (Commands.CMD_LE_DATA_WRITE_REQ, Commands.CMD_LE_ISO_DATA_WRITE_REQ)

        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(5)

        try:
          print("Opening socket ", socket_path)
          self.sock.connect(socket_path)
        except Exception:
          self.sock = None
          print("Could not connect to the btmon socket: ", socket_path, Exception)

        self.start_time = time.time()

        if store_to_file == False:
            self.file = None
            return

        now = datetime.now()
        btsnoop_file_name = "btsnoop_" + str(now.date()) + "_" + str(now.time()) +".log"

        print("Opening file ", btsnoop_file_name)
        self.file = open(btsnoop_file_name, "wb")

        """
        btsnoop header
        0----------------------------------------64
        |                  Id                     |
        +------------------32---------------------+
        |   btsnoop_ver= 1  |         type        |
        +-------------------+---------------------+
        """
        btsnoop_id = [0x62, 0x74, 0x73, 0x6e, 0x6f, 0x6f, 0x70, 0x00 ]
        btsnoop_monitor_format = 2001
        header = struct.pack(">BBBBBBBBLL", btsnoop_id[0], btsnoop_id[1],
                                            btsnoop_id[2], btsnoop_id[3],
                                            btsnoop_id[4], btsnoop_id[5],
                                            btsnoop_id[6], btsnoop_id[7],
                                            1, btsnoop_monitor_format)
        self.file.write(header)


    def close(self):
        if self.file:
            self.file.close()
        if self.sock:
            self.sock.close()


    def send_monitor_hdr_btmon_socket(self, idx, opcode, data_len):
        """
        mgmt_hdr
        0----------16---------32---------------48
        |   opcode |   index  |          len    |
        +----------+----------+-----------------

        """
        ble_monitor_hdr = struct.pack("<HHH", opcode, idx, data_len)
        self.sock.send(ble_monitor_hdr)


    def send_monitor_hdr_file(self, idx, opcode, data_len, timestamp):
        """
        btsnoop_pkt
        0-----------------32---------------64
        |   original len   | included len   |
        +------------------+----------------+
        |   flags          |cumulative drops|
        +-----------------------------------+
        |              timestamp            |
        +------------------+----------------+
        """
        flags = (idx << 16) | opcode
        pkt_hdr = struct.pack(">LLLLQ", data_len, data_len, flags, 0, timestamp)
        self.file.write(pkt_hdr)


    def send_monitor_hdr(self, idx, opcode, data_len):
        idx +=10
        timestamp = int((time.time() - self.start_time) * 1000)

        if self.file:
            self.send_monitor_hdr_file(idx, opcode, data_len, timestamp)
        if self.sock:
            self.send_monitor_hdr_btmon_socket(idx, opcode, data_len)


    def send_event_sock(self, packet, data, eventLen):
        self.sock.send(packet[8:10])
        if eventLen > 0:
            self.sock.send(data)


    def send_event_file(self, packet, data, eventLen):
        self.file.write(packet[8:10])
        if eventLen > 0:
            self.file.write(data)


    def send_event(self, idx, packet, data):
        opcode = BleMonitorOpcode.EVENT
        RespCmd, RespLen, time, event, eventLen = struct.unpack('<HHIBB', packet[:10]);
        self.send_monitor_hdr(idx, opcode, eventLen + 2)

        if self.file:
            self.send_event_file(packet, data, eventLen)
        if self.sock:
            self.send_event_sock(packet, data, eventLen)


    def send_command_sock(self, opcode, len, data):
        self.sock.send(opcode)
        #This is this additional octet
        hci_len=struct.pack("<B", len)
        self.sock.send(hci_len)
        if len > 0:
            self.sock.send(data)


    def send_command_file(self, opcode, len, data):
        self.file.write(opcode)
        #This is this additional octet
        hci_len=struct.pack("<B", len)
        self.file.write(hci_len)
        if len > 0:
            self.file.write(data)


    def send_monitor_command(self, opcode, len, data):
        if self.file:
            self.send_command_file(opcode, len, data)
        if self.sock:
            self.send_command_sock( opcode, len, data)


    def send_index_added(self, idx, addr, name):
        """
        NewIndexHdr
        0------8-----16-----...-----64 -------+
        | type | bus  |  address     |  name  |
        +------+---------------------+--------+
        """
        new_index = struct.pack("<BB6B", 0, 10, addr[0], addr[1], addr[2], addr[3], addr[4], addr[5])
        l = len(name)
        packed_name = struct.pack("<%dsb" % l, name.encode('ascii'), 0)
        self.send_monitor_hdr(idx, BleMonitorOpcode.NEW_INDEX, 8 + len(packed_name))
        if self.file:
            self.file.write(new_index)
            self.file.write(packed_name)

        if self.sock:
            self.sock.send(new_index)
            self.sock.send(packed_name)


    def send_monitor_iso_rx(self, idx, handle, dataLen, packet):
        self.send_monitor_hdr(idx, BleMonitorOpcode.ISO_RX, dataLen + 4)

        hdr = struct.pack('<HH', handle, dataLen)
        if self.file:
            self.file.write(hdr)
            self.file.write(packet)
        if self.sock:
            self.sock.send(hdr)
            self.sock.send(packet)


    def send_monitor_acl_rx(self, idx, handle, dataLen, packet):
        self.send_monitor_hdr(idx, BleMonitorOpcode.ACL_RX, dataLen + 4)

        hdr = struct.pack('<HH', handle, dataLen)
        if self.file:
            self.file.write(hdr)
            self.file.write(packet)
        if self.sock:
            self.sock.send(hdr)
            self.sock.send(packet)


    def send(self, idx, message):
          # unpack and validate EDTT header first
        op, payload_len = struct.unpack_from('<HH', message)

        if op in self.non_hci_edtt_cmds:
            return

        if payload_len == 0:
            return

        if op in self.tx_data_edtt_cmds:
            # Assume it is ACL data
            opcode = BleMonitorOpcode.ACL_TX

            if op == Commands.CMD_LE_ISO_DATA_WRITE_REQ:
                opcode = BleMonitorOpcode.ISO_TX

            self.send_monitor_hdr(idx, opcode, payload_len)
            if self.file:
                self.file.write(message[4:])
            if self.sock:
                self.sock.send(message[4:])

            return

        # All requests are even.
        if op % 2 == 1:
            opcode = BleMonitorOpcode.COMMAND
            # + 1 is because we need to add octet for the hci command len
            self.send_monitor_hdr(idx, opcode, payload_len + 1)
            data = None
            if (payload_len - 2 > 0):
                data = message[6:]

            self.send_monitor_command(message[4:6], payload_len - 2, data)


    def send_user_data(self, idx, priority, string):
        l = len(string)
        hdr = struct.pack("<BB", priority, l)
        log = struct.pack("<%dsb" % l, string.encode('ascii'), 0)
        self.send_monitor_hdr(idx, BleMonitorOpcode.USER_LOGGING, 2 + len(log))

        if self.file:
            self.file.write(hdr)
            self.file.write(log)
        if self.sock:
            self.sock.send(hdr)
            self.sock.send(log)
