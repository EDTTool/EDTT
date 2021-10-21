# -*- coding: utf-8 -*-
# Copyright 2021 Oticon A/S
# SPDX-License-Identifier: Apache-2.0
import io
import sys
from collections import namedtuple
from enum import IntEnum


class DeviceDumpFile:
    def __init__(self, idx, file_path):
        self.idx = idx
        self.file_path = file_path
        self.f = None
        self.skip_first_line = True

    def __str__(self):
        return self.file_path

    def open(self):
        self.f = io.open(self.file_path, 'r')

    def close(self):
        self.f.close()

    def decode(self, line):
        raise NotImplementedError

    def fetch(self, cnt=-1):
        n = 0
        self.skip_first_line = True
        while True:
            offset = self.f.tell()
            line = self.f.readline()
            if line == '':
                # EOF read, return what was collected
                yield None
            elif not line.endswith('\n'):
                # Partial line read, rewind and return what was collected
                self.f.seek(offset, io.SEEK_SET)
                yield None
            else:
                # Full line read, continue unless a specific number of lines have been collected
                if self.skip_first_line:
                    self.skip_first_line = False
                    continue

                yield self.decode(line.strip())
                n += 1

                if n == cnt:
                    return


class DeviceDumpFileTx(DeviceDumpFile):
    Tx = namedtuple('Tx', 'idx, ts, aa, freq, mod, packet')

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
        packet = bytearray(int(v, 16) for v in packet.split())

        return self.Tx._make((self.idx, start_time, phy_address, center_freq, modulation, memoryview(packet)))


class DeviceDumpFileRx(DeviceDumpFile):
    Rx = namedtuple('Rx', 'idx, ts, aa, freq, mod, status, packet')

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
        packet = bytearray(int(v, 16) for v in packet.split())

        return self.Rx._make((self.idx, rx_time_stamp, phy_address, center_freq, modulation, status,
                              memoryview(packet)))


def unpack_bitfield(fmt, value):
    result = []
    for length in fmt.split(","):
        length = int(length, 10)
        result.append(value & abs(1 - (1 << length)))
        value = value >> length
    return tuple(result)


AdvPdu = ('ADV_UNKNOWN_PDU', 'ADV_IND', 'ADV_DIRECT_IND', 'CONNECT_IND')
LlControlPdu = ('LL_CONTROL_UNKNOWN_PDU', 'LL_TERMINATE_IND', 'LL_CIS_REQ', 'LL_CIS_RSP', 'LL_CIS_IND',
                'LL_CIS_TERMINATE_IND')
IsoPdu = ('ISOC_SDU',)
PacketType = IntEnum('PacketType', ','.join(AdvPdu + LlControlPdu + IsoPdu))


class Packet:
    def __init__(self, direction, idx, ts, aa, channel_num, phy, data, payload_type, header, payload):
        self.direction = direction
        self.idx = idx
        self.ts = ts
        self.aa = aa
        self.channel_num = channel_num
        self.phy = phy
        self.data = data
        self.type = payload_type
        self.header = header
        self.payload = payload

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return f"{self.direction}, {self.type.name}, Idx:{self.idx}, StartTime:{self.ts}, " \
               f"AccessAddress:{hex(self.aa)}, ChannelNumber:{self.channel_num}, PHY:{self.phy}, Length:{len(self)}, " \
               f"{self.header}, {self.payload}"


def adv_ind(data):
    Payload = namedtuple('Payload', 'AdvA, AdvData')
    adv_a = data[:6]
    adv_data = data[6:]
    return Payload(adv_a, adv_data)


def adv_direct_ind(data):
    Payload = namedtuple('Payload', 'AdvA, TargetA')
    adv_a = data[:6]
    target_a = data[6:12]
    return Payload(adv_a, target_a)


def connect_ind(payload):
    Payload = namedtuple('Payload', 'InitA, AdvA, LLData')
    LLData = namedtuple('LLData', 'AA, CRCInit, WinSize, WinOffset, Interval, Latency, Timeout, ChM, Hop, SCA')
    init_a = payload[:6]
    adv_a = payload[6:12]
    aa = int.from_bytes(payload[12:16], 'little', signed=False)
    crc_init = int.from_bytes(payload[16:19], 'little', signed=False)
    win_size = payload[19]
    win_offset = int.from_bytes(payload[20:22], 'little', signed=False)
    interval = int.from_bytes(payload[22:24], 'little', signed=False)
    latency = int.from_bytes(payload[24:26], 'little', signed=False)
    timeout = int.from_bytes(payload[26:28], 'little', signed=False)
    ch_m = int.from_bytes(payload[28:33], 'little', signed=False)
    hop, sca = unpack_bitfield('5,3', payload[33])
    ll_data = LLData(aa, crc_init, win_size, win_offset, interval, latency, timeout, ch_m, hop, sca)
    return Payload(init_a, adv_a, ll_data)


adv_legacy_pdu_dict = {
    0b0000: (PacketType.ADV_IND, adv_ind),
    0b0001: (PacketType.ADV_DIRECT_IND, adv_direct_ind),
    0b0101: (PacketType.CONNECT_IND, connect_ind),
}


def parse_adv_pdu(direction, idx, ts, aa, channel_num, phy, data):
    Header = namedtuple('Header', 'PDU_Type, ChSel, TxAdd, RxAdd, Length')
    pdu_type, _, ch_sel, tx_add, rx_add, payload_len = \
        unpack_bitfield('4,1,1,1,1,8', int.from_bytes(data[:2], 'little', signed=False))
    header = Header(pdu_type, ch_sel, tx_add, rx_add, payload_len)
    data = data[2:2 + payload_len]
    if channel_num in [0, 12, 39]:
        if pdu_type in adv_legacy_pdu_dict:
            payload_type, func = adv_legacy_pdu_dict[pdu_type]
            payload = func(data)
        else:
            payload_type, payload = PacketType.ADV_UNKNOWN_PDU, data
    else:
        return None
    return Packet(direction, idx, ts, aa, channel_num, phy, data, payload_type, header, payload)


def ll_terminate_ind(data):
    CtrData = namedtuple('CtrData', 'ErrorCode')
    return CtrData(data[0])


def ll_cis_req(data):
    CtrData = namedtuple('CtrData', 'CIG_ID, CIS_ID, PHY_C_To_P, PHY_P_To_C, Max_SDU_C_To_P, Framed, Max_SDU_P_To_C,'
                                    'SDU_Interval_C_To_P, SDU_Interval_P_To_C, Max_PDU_C_To_P, Max_PDU_P_To_C, NSE,'
                                    'Sub_Interval, BN_C_To_P, BN_P_To_C, FT_C_To_P, FT_P_To_C, ISO_Interval,'
                                    'CIS_Offset_Min, CIS_Offset_Max, connEventCount')
    cig_id, cis_id, phy_c_to_p, phy_p_to_c = data[:4]
    max_sdu_c_to_p, _, framed = unpack_bitfield('12,3,1', int.from_bytes(data[4:6], 'little', signed=False))
    max_sdu_p_to_c, _ = unpack_bitfield('12,4', int.from_bytes(data[6:8], 'little', signed=False))
    sdu_interval_c_to_p, _ = unpack_bitfield('20,4', int.from_bytes(data[8:11], 'little', signed=False))
    sdu_interval_p_to_c, _ = unpack_bitfield('20,4', int.from_bytes(data[11:14], 'little', signed=False))
    max_pdu_c_to_p = int.from_bytes(data[14:16], 'little', signed=False)
    max_pdu_p_to_c = int.from_bytes(data[16:18], 'little', signed=False)
    nse = data[19]
    sub_interval = int.from_bytes(data[19:22], 'little', signed=False)
    bn_c_to_p, bn_p_to_c = unpack_bitfield('4,4', data[22])
    ft_c_to_p, ft_p_to_c = data[23:25]
    iso_interval = int.from_bytes(data[25:27], 'little', signed=False)
    cis_offset_min = int.from_bytes(data[27:30], 'little', signed=False)
    cis_offset_max = int.from_bytes(data[30:33], 'little', signed=False)
    conn_event_count = int.from_bytes(data[33:35], 'little', signed=False)
    return CtrData(cig_id, cis_id, phy_c_to_p, phy_p_to_c, max_sdu_c_to_p, framed, max_sdu_p_to_c, sdu_interval_c_to_p,
                   sdu_interval_p_to_c, max_pdu_c_to_p, max_pdu_p_to_c, nse, sub_interval, bn_c_to_p, bn_p_to_c,
                   ft_c_to_p, ft_p_to_c, iso_interval, cis_offset_min, cis_offset_max, conn_event_count)


def ll_cis_rsp(data):
    CtrData = namedtuple('CtrData', 'CIS_Offset_Min, CIS_Offset_Max, connEventCount')
    cis_offset_min = int.from_bytes(data[:3], 'little', signed=False)
    cis_offset_max = int.from_bytes(data[3:6], 'little', signed=False)
    conn_event_count = int.from_bytes(data[6:8], 'little', signed=False)
    return CtrData(cis_offset_min, cis_offset_max, conn_event_count)


def ll_cis_ind(data):
    CtrData = namedtuple('CtrData', 'AA, CIS_Offset, CIG_Sync_Delay, CIS_Sync_Delay, connEventCount')
    aa = int.from_bytes(data[0:4], 'little', signed=False)
    cis_offset = int.from_bytes(data[4:7], 'little', signed=False)
    cig_sync_delay = int.from_bytes(data[7:10], 'little', signed=False)
    cis_sync_delay = int.from_bytes(data[10:13], 'little', signed=False)
    conn_event_counter = int.from_bytes(data[13:15], 'little', signed=False)
    return CtrData(aa, cis_offset, cig_sync_delay, cis_sync_delay, conn_event_counter)


def ll_cis_terminate_ind(data):
    CtrData = namedtuple('CtrData', 'CIG_ID, CIS_ID, ErrorCode')
    return CtrData(*data[:3])


ll_control_pdu_dict = {
    0x02: (PacketType.LL_TERMINATE_IND, ll_terminate_ind),
    0x1F: (PacketType.LL_CIS_REQ, ll_cis_req),
    0x20: (PacketType.LL_CIS_RSP, ll_cis_rsp),
    0x21: (PacketType.LL_CIS_IND, ll_cis_ind),
    0x22: (PacketType.LL_CIS_TERMINATE_IND, ll_cis_terminate_ind),
}


def parse_data_pdu(direction, idx, ts, aa, channel_num, phy, data):
    Header = namedtuple('Header', 'LLID, NESN, SN, MD, CP, Length, CTEInfo')
    llid, nesn, sn, md, cp, rfu, payload_length = \
            unpack_bitfield('2,1,1,1,1,2,8', int.from_bytes(data[:2], 'little', signed=False))
    cte_info = data[2] if cp else None
    header = Header(llid, nesn, sn, md, cp, payload_length, cte_info)
    pdu_offset = 3 if cp else 2
    data = data[pdu_offset:pdu_offset + payload_length]
    if llid == 0b11:
        Payload = namedtuple('Payload', 'Opcode, CtrData')
        opcode = data[0]
        if opcode in ll_control_pdu_dict:
            payload_type, func = ll_control_pdu_dict[opcode]
            payload = Payload(opcode, func(data[1:]))
        else:
            payload_type, payload = PacketType.LL_CONTROL_UNKNOWN_PDU, Payload(opcode, data[1:])
    else:
        return None
    return Packet(direction, idx, ts, aa, channel_num, phy, data, payload_type, header, payload)


def parse_isoc_pdu(direction, idx, ts, aa, channel_num, phy, data):
    Header = namedtuple('Header', 'LLID, NESN, SN, CIE, NPI, Length')
    llid, nesn, sn, cie, rfu_1, npi, rfu_2, payload_length = \
        unpack_bitfield('2,1,1,1,1,1,1,8', int.from_bytes(data[:2], 'little', signed=False))
    header = Header(llid, nesn, sn, cie, npi, payload_length)
    payload_type = PacketType.ISOC_SDU
    payload = data[2:2 + payload_length]
    return Packet(direction, idx, ts, aa, channel_num, phy, data, payload_type, header, payload)


class ConnectionData:
    def __init__(self, interval):
        self.connection_interval = interval
        self.cis_to_aa_map = {}


class PacketParser:
    def __init__(self):
        self.__conn_data_by_aa = {}
        self.__func_by_aa = {
            0x8E89BED6: parse_adv_pdu,
        }

    def __get_packet(self, direction, idx, ts, aa, channel_num, phy, packet):
        if aa in self.__func_by_aa:
            return self.__func_by_aa[aa](direction, idx, ts, aa, channel_num, phy, packet)
        return None

    def parse(self, dump):
        packet = self.__get_packet(type(dump).__name__, dump.idx, dump.ts, dump.aa,
                                   self.__get_phy_channel_num(dump.freq), self.__get_phy(dump.mod), dump.packet)
        if packet:
            self.__run_hook(packet)

        return packet

    def __run_hook(self, packet):
        if packet.type in self.__hooks__:
            self.__hooks__[packet.type](self, packet, self.__conn_data_by_aa.get(packet.aa))

    @staticmethod
    def __get_phy_channel_num(center_freq):
        return int((center_freq - 2) / 2)

    @staticmethod
    def __get_phy(modulation):
        if modulation == 16:
            return '1M'
        if modulation == 32:
            return '2M'
        return 'unknown'

    def __on_connect_ind(self, packet, _):
        self.__func_by_aa[packet.payload.LLData.AA] = parse_data_pdu
        self.__conn_data_by_aa[packet.payload.LLData.AA] = ConnectionData(packet.payload.LLData.Interval)

    def __on_terminate_ind(self, packet, conn_data):
        del self.__func_by_aa[packet.aa]
        for _, cis_aa in conn_data.cis_to_aa_map.items():
            del self.__func_by_aa[cis_aa]
        del self.__conn_data_by_aa[packet.aa]

    def __on_cis_req(self, packet, conn_data):
        conn_data.pending_cis_req_ctr_data = packet.payload.CtrData

    def __on_cis_ind(self, packet, conn_data):
        cis_id = (conn_data.pending_cis_req_ctr_data.CIG_ID, conn_data.pending_cis_req_ctr_data.CIS_ID)
        cis_aa = packet.payload.CtrData.AA
        self.__func_by_aa[cis_aa] = parse_isoc_pdu
        conn_data.cis_to_aa_map[cis_id] = cis_aa
        del conn_data.pending_cis_req_ctr_data

    def __on_cis_terminate_ind(self, packet, conn_data):
        cis_id = (packet.payload.CtrData.CIG_ID, packet.payload.CtrData.CIS_ID)
        cis_aa = conn_data.cis_to_aa_map.pop(cis_id, None)
        if cis_aa:
            del self.__func_by_aa[cis_aa]

    __hooks__ = {
        PacketType.CONNECT_IND: __on_connect_ind,
        PacketType.LL_TERMINATE_IND: __on_terminate_ind,
        PacketType.LL_CIS_REQ: __on_cis_req,
        PacketType.LL_CIS_IND: __on_cis_ind,
        PacketType.LL_CIS_TERMINATE_IND: __on_cis_terminate_ind,
    }


class SortedDumps:
    class Dump:
        def __init__(self, generator, dump):
            self.generator, self.dump = generator, dump

    def __init__(self, files):
        self.files = []
        for file in files:
            try:
                file.open()
                self.files.append(file)
            except FileNotFoundError:
                print('{} so such file'.format(file))
                continue

    def __del__(self):
        for file in self.files:
            file.close()

    def fetch(self):
        dumps = []
        for file in self.files:
            dump = self.Dump(file.fetch(), None)
            try:
                dump.dump = next(dump.generator)
            except StopIteration:
                return
            dumps.append(dump)

        while True:
            # sort by timestamp
            dumps.sort(key=lambda entry: entry.dump.ts if entry.dump else sys.maxsize)
            next_dump = dumps[0]
            yield next_dump.dump
            try:
                next_dump.dump = next(next_dump.generator)
            except StopIteration:
                return


class Packets:
    def __init__(self, dumps, parser):
        self.__filter = ()
        self.__packets = self.__generator_func(dumps, parser)

    def fetch(self, packet_filter=()):
        try:
            iter(packet_filter)
        except TypeError:
            self.__filter = (packet_filter,)
        else:
            self.__filter = packet_filter
        for packet in self.__packets:
            if packet:
                yield packet
            else:
                return

    def get(self, packet_filter=()):
        try:
            return next(self.fetch(packet_filter))
        except StopIteration:
            return None

    def flush(self):
        f = self.__filter
        self.__filter = ()
        while next(self.__packets):
            pass
        self.__filter = f

    def __generator_func(self, dumps, parser):
        for dump in dumps.fetch():
            result = dump
            if dump:
                packet = parser.parse(dump)
                if packet and (not self.__filter or packet.type.name in self.__filter):
                    result = packet
                else:
                    continue
            yield result


class DeviceDumps:
    def __init__(self):
        self.__dump_files = []

    def add_tx(self, idx, file_path):
        self.__dump_files.append(DeviceDumpFileTx(idx, file_path))

    def add_rx(self, idx, file_path):
        # TODO
        pass

    def packets(self):
        dumps = SortedDumps(self.__dump_files)
        parser = PacketParser()
        return Packets(dumps, parser)
