# -*- coding: utf-8 -*-
# Copyright 2021 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

import os
import os.path
import time
import io
import collections

class DeviceDumpFile():
    def __init__(self, file_path):
        self.file_path = file_path
        self.f = None
        self.skip_first_line = True

    def open(self):
        while not os.path.exists(self.file_path):
            print('{} not present yet, waiting...'.format(self.file_path))
            time.sleep(1)
        self.f = io.open(self.file_path, 'r')

    def close(self):
        self.f.close()

    def read(self, cnt=-1):
        if self.f:
            lines = []

            while True:
                offset = self.f.tell()
                line = self.f.readline()
                if line == '':
                    # EOF read, return what was collected
                    return lines
                elif not line.endswith('\n'):
                    # Partial line read, rewind and return what was collected
                    self.f.seek(offset, io.SEEK_SET)
                    return lines
                else:
                    # Full line read, continue unless a specific number of lines have been collected
                    if self.skip_first_line:
                        self.skip_first_line = False
                        continue

                    lines.append(line.strip())

                    if len(lines) == cnt:
                        return lines

    def readiter(self, cnt=-1):
        if not self.f:
            raise StopIteration

        n = 0
        while True:
            offset = self.f.tell()
            line = self.f.readline()
            if line == '':
                # EOF read, return what was collected
                raise StopIteration
            elif not line.endswith('\n'):
                # Partial line read, rewind and return what was collected
                self.f.seek(offset, io.SEEK_SET)
                raise StopIteration
            else:
                # Full line read, continue unless a specific number of lines have been collected
                if self.skip_first_line:
                    self.skip_first_line = False
                    continue

                yield line.strip()
                n += 1

                if n == cnt:
                    raise StopIteration

    def fetch(self, cnt=-1):
        for line in self.readiter(cnt):
            yield self.decode(line)

    def drop(self, cnt=-1):
        self.readiter(cnt)

class DeviceDumpFileTx(DeviceDumpFile):
    Tx = collections.namedtuple('Tx', 'ts, aa, packet')
    def decode(self, line):
        try:
            start_time, end_time, center_freq, phy_address, modulation, power_level, abort_time, \
                    recheck_time, packet_size, packet, *_ = line.split(',')
        except ValueError:
            return

        start_time = int(start_time)
        end_time = int(end_time)
        center_freq = float(center_freq)
        phy_address = int(phy_address, 16)
        modulation = int(modulation)
        power_level = float(power_level)
        abort_time = int(abort_time)
        recheck_time = int(recheck_time)
        packet_size = int(packet_size)
        packet = [int(v, 16) for v  in packet.split()]

        return self.Tx._make((start_time, phy_address, packet))

class DeviceDumpFileRx(DeviceDumpFile):
    Rx = collections.namedtuple('Rx', 'ts, aa, status, packet')
    def decode(self, line):
        try:
            start_time, scan_duration, phy_address, modulation, center_freq, antenna_gain, \
                    sync_threshold, header_threshold, pream_and_addr_duration, header_duration, \
                    bps, abort_time, recheck_time, tx_nbr, biterrors, sync_end, header_end, \
                    payload_end, rx_time_stamp, status, RSSI, packet_size, packet, *_ = line.split(',')
        except ValueError:
            return

        start_time = int(start_time)
        scan_duration = int(scan_duration)
        phy_address = int(phy_address, 16)
        modulation = int(modulation)
        center_freq = float(center_freq)
        antenna_gain = float(antenna_gain)
        sync_threshold = int(sync_threshold)
        header_threshold = int(header_threshold)
        pream_and_addr_duration = int(pream_and_addr_duration)
        header_duration = int(header_duration)
        bps = int(bps)
        abort_time = int(abort_time)
        recheck_time = int(recheck_time)
        tx_nbr = int(tx_nbr)
        biterrors = int(biterrors)
        sync_end = int(sync_end)
        header_end = int(header_end)
        payload_end = int(payload_end)
        rx_time_stamp = int(rx_time_stamp)
        status = int(status)
        RSSI = float(RSSI)
        packet_size = int(packet_size)
        packet = [int(v, 16) for v  in packet.split()]

        return self.Rx._make((rx_time_stamp, phy_address, status, packet))
