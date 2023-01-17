# -*- coding: utf-8 -*-
# Copyright 2021 Oticon A/S
# SPDX-License-Identifier: Apache-2.0
import io
import math
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

# Convert RF Channel number to Physical Channel Index (see Bluetooth Core Specification v5.3, vol 6, part B, section 1.4.1)
def channel_num_to_index(channel_num):
    ch_num_ch_idx = [
        37,
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
        38,
        11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
        39
    ]
    return ch_num_ch_idx[channel_num]

AdvPdu = ('ADV_UNKNOWN_PDU', 'ADV_IND', 'ADV_DIRECT_IND', 'CONNECT_IND', 'ADV_EXT_UNKNOWN_PDU', 'ADV_EXT_IND', 'AUX_ADV_IND', 'AUX_SCAN_RSP', 'AUX_SYNC_IND', 'AUX_CHAIN_IND', 'AUX_CONNECT_REQ', 'AUX_CONNECT_RSP')
LlControlPdu = ('LL_CONTROL_UNKNOWN_PDU', 'LL_TERMINATE_IND', 'LL_CIS_REQ', 'LL_CIS_RSP', 'LL_CIS_IND',
                'LL_CIS_TERMINATE_IND')
LlDataPdu = ('LL_DATA_PDU',)
IsoPdu = ('ISOC_UNKNOWN_PDU', 'ISOC_UNFRAMED_PDU', 'ISOC_FRAMED_PDU')
PacketType = IntEnum('PacketType', ','.join(AdvPdu + LlControlPdu + LlDataPdu + IsoPdu))


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


def parse_adv_pdu(direction, idx, ts, aa, channel_num, phy, data, aux_ptr_packets):
    Header = namedtuple('Header', 'PDU_Type, ChSel, TxAdd, RxAdd, Length')
    pdu_type, _, ch_sel, tx_add, rx_add, payload_len = \
        unpack_bitfield('4,1,1,1,1,8', int.from_bytes(data[:2], 'little', signed=False))
    header = Header(pdu_type, ch_sel, tx_add, rx_add, payload_len)
    data = data[2:2 + payload_len]
    if pdu_type in adv_legacy_pdu_dict and channel_num in [0, 12, 39]:
        payload_type, func = adv_legacy_pdu_dict[pdu_type]
        payload = func(data)
    else:
        return parse_ext_adv_pdu(direction, idx, ts, aa, channel_num, phy, header, data, aux_ptr_packets);
    return Packet(direction, idx, ts, aa, channel_num, phy, data, payload_type, header, payload)


def parse_common_ext_adv_payload(data):
    payload = dict()
    extHeaderLength, AdvMode = unpack_bitfield('6,2', int.from_bytes(data[:1], 'little', signed=False))
    data = data[1:]
    payload['AdvMode'] = AdvMode
    dataPtr = 0
    if extHeaderLength > 0:
        extHeaderFlags = bytes(data[dataPtr:dataPtr+1])[0]
        dataPtr += 1
        if extHeaderFlags & 0x01: # AdvA present
            payload['AdvA'] = int.from_bytes(data[dataPtr:dataPtr+6], 'little', signed=False)
            dataPtr += 6
        if extHeaderFlags & 0x02: # TargetA present
            payload['TargetA'] = int.from_bytes(data[dataPtr:dataPtr+6], 'little', signed=False)
            dataPtr += 6
        if extHeaderFlags & 0x04: # CTEInfo present
            # TODO - decode further
            payload['CTEInfo'] = bytes(data[dataPtr:dataPtr+1])[0]
            dataPtr += 1
        if extHeaderFlags & 0x08: # AdvDataInfo present
            ADI = namedtuple('ADI', 'DID, SID')
            did, sid = unpack_bitfield('12,4', int.from_bytes(data[dataPtr:dataPtr+2], 'little', signed=False))
            dataPtr += 2
            payload['ADI'] = ADI(did, sid)
        if extHeaderFlags & 0x10: # AuxPtr present
            chIdx, clockAcc, offsetUnits, auxOffset, auxPHY = unpack_bitfield('6,1,1,13,3', int.from_bytes(data[dataPtr:dataPtr+3], 'little', signed=False))
            dataPtr += 3
            AuxPtr = namedtuple('AuxPtr', 'chIdx, CA, offsetUnits, auxOffset, auxPHY')
            payload['AuxPtr'] = AuxPtr(chIdx, clockAcc, offsetUnits, auxOffset, auxPHY)
        if extHeaderFlags & 0x20: # SyncInfo present
            # TODO - decode further
            payload['SyncInfo'] = bytes(data[dataPtr:dataPtr+18])
            dataPtr += 18
        if extHeaderFlags & 0x40:
            payload['TxPower'] = bytes(data[dataPtr:dataPtr+1])[0]
            dataPtr += 1
        if dataPtr < extHeaderLength:
            payload['ACAD'] = bytes(data[dataPtr:])

    data = data[extHeaderLength:]
    if len(data):
        payload['AD'] = bytes(data)

    return payload

def parse_ext_adv_pdu(direction, idx, ts, aa, channel_num, phy, header, data, aux_ptr_packets):
    if channel_num in [0, 12, 39]:
        if header.PDU_Type == 0b0111:
            payload_type = PacketType.ADV_EXT_IND
            payload = parse_common_ext_adv_payload(data)
        else:
            payload_type = PacketType.ADV_UNKNOWN_PDU
            payload = data
    else:
        if header.PDU_Type == 0b0011:
            payload_type = PacketType.AUX_SCAN_REQ
            Payload = namedtuple('Payload', 'AdvA, TargetA')
            advA = int.from_bytes(data[:6], 'little', signed=False)
            targetA = int.from_bytes(data[6:], 'little', signed=False)
            payload = Payload(advA, targetA)
        elif header.PDU_Type == 0b0101:
            payload_type = PacketType.AUX_CONNECT_REQ
            # Payload is the same as CONNECT_IND
            payload = connect_ind(data)
        elif header.PDU_Type == 0b0111:
            payload = parse_common_ext_adv_payload(data)
            payload['SuperiorPackets'] = find_superior_packets(ts, channel_num, phy, aux_ptr_packets)
            payload_type = determine_ext_adv_pdu_type(payload)
        elif header.PDU_Type == 0b1000:
            payload_type = PacketType.AUX_CONNECT_RSP
            payload = parse_common_ext_adv_payload(data)
        else:
            payload_type = PacketType.ADV_UNKNOWN_PDU
            payload = data

    return Packet(direction, idx, ts, aa, channel_num, phy, data, payload_type, header, payload)

def find_superior_packets(ts, channel_num, phy, aux_ptr_packets):
    superiorPackets = []
    for packet in aux_ptr_packets:
        if aux_ptr_matches(packet.payload['AuxPtr'], packet.ts, ts, channel_num, phy):
            superiorPackets += [packet]
    return superiorPackets

def determine_ext_adv_pdu_type(payload):
    if payload['SuperiorPackets']:
        if payload['SuperiorPackets'][0].type == PacketType.ADV_EXT_IND:
            return PacketType.AUX_ADV_IND
        else:
            return PacketType.AUX_CHAIN_IND

    # No matches - we could have missed the packet with an aux_ptr, but assume a AUX_SCAN_RSP provided it matches the known limitations
    if payload['AdvMode'] == 0 and 'AdvA' in payload and 'TargetA' not in payload and 'CTEInfo' not in payload and 'SyncInfo' not in payload and 'AD' in payload:
        return PacketType.AUX_SCAN_RSP
    
    # No matches and does not look like a AUX_SCAN_RSP
    return PacketType.ADV_EXT_UNKNOWN_PDU

def aux_ptr_matches(aux_ptr, superior_packet_ts, ts, channel_num, phy):
    ch = channel_num_to_index(channel_num)
    if ch == aux_ptr.chIdx and ((phy == '1M' and (aux_ptr.auxPHY == 0x00 or aux_ptr.auxPHY == 0x02)) or (phy == '2M' and aux_ptr.auxPHY == 0x01)):
        if (aux_ptr.auxOffset > 0): # AuxOffset == 0 means no auxillary packet will be transmitted
            t_start_offset = (300 if aux_ptr.offsetUnits == 1 else 30) * aux_ptr.auxOffset
            t_end_offset = (300 if aux_ptr.offsetUnits == 1 else 30) * (aux_ptr.auxOffset + 1)
            # Adjust according to clock accuracy value
            ca_adjustment = math.ceil(t_end_offset * ((50 if aux_ptr.CA == 1 else 500)/1000000))
            t_start = superior_packet_ts + (t_start_offset - ca_adjustment)
            t_end = superior_packet_ts + (t_end_offset + ca_adjustment)
            if ts >= t_start and ts <= t_end:
                return True
    return False

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
    elif llid == 0b10 or llid == 0b01:
        payload_type = PacketType.LL_DATA_PDU
        payload = data
    else:
        return None
    return Packet(direction, idx, ts, aa, channel_num, phy, data, payload_type, header, payload)


def parse_isoc_pdu(direction, idx, ts, aa, channel_num, phy, data):
    Header = namedtuple('Header', 'LLID, NESN, SN, CIE, NPI, Length')
    llid, nesn, sn, cie, rfu_1, npi, rfu_2, payload_length = \
        unpack_bitfield('2,1,1,1,1,1,1,8', int.from_bytes(data[:2], 'little', signed=False))
    header = Header(llid, nesn, sn, cie, npi, payload_length)
    if llid == 0b00 or llid == 0b01:
        payload_type = PacketType.ISOC_UNFRAMED_PDU
        payload = data[2:2 + payload_length]
    elif llid == 0b10:
        payload_type = PacketType.ISOC_FRAMED_PDU
        SegmentationHeader = namedtuple('SegmentationHeader', 'SC, CMPLT, RFU, Length')
        sc, cmplt, rfu, payload_length = unpack_bitfield('1,1,6,8', int.from_bytes(data[2:4], 'little', signed=False))
        segmentation_header = SegmentationHeader(sc, cmplt, rfu, payload_length)
        Payload = namedtuple('Payload', 'SegmentationHeader, Payload')
        payload = Payload(segmentation_header, data[4:4 + payload_length])
    else:
        payload_type = PacketType.ISOC_UNKNOWN_PDU
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
        self.__aux_ptr_packets = [];

    def __get_packet(self, direction, idx, ts, aa, channel_num, phy, packet):
        if aa in self.__func_by_aa:
            if self.__func_by_aa[aa] == parse_adv_pdu:
                return self.__func_by_aa[aa](direction, idx, ts, aa, channel_num, phy, packet, self.__aux_ptr_packets)
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
        if modulation == 32 or modulation == 33:
            return '2M'
        return 'unknown'

    def __on_ext_adv_packet(self, packet, _):
        # TODO - handle SyncInfo packets as well
        if 'AuxPtr' in packet.payload:
            self.__aux_ptr_packets.append(packet)

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
        PacketType.ADV_EXT_IND: __on_ext_adv_packet,
        PacketType.AUX_ADV_IND: __on_ext_adv_packet,
        PacketType.AUX_SYNC_IND: __on_ext_adv_packet,
        PacketType.AUX_CHAIN_IND: __on_ext_adv_packet,
        PacketType.AUX_SCAN_RSP: __on_ext_adv_packet,
        PacketType.CONNECT_IND: __on_connect_ind,
        PacketType.AUX_CONNECT_REQ: __on_connect_ind,
        PacketType.LL_TERMINATE_IND: __on_terminate_ind,
        PacketType.LL_CIS_REQ: __on_cis_req,
        PacketType.LL_CIS_IND: __on_cis_ind,
        PacketType.LL_CIS_TERMINATE_IND: __on_cis_terminate_ind,
    }


class SortedDumps:
    class Dump:
        def __init__(self, file):
            self.file = file
            self.generator = self.file.fetch()
            self.dump = None

    def __init__(self):
        self.dumps = []

    def __del__(self):
        for dump in self.dumps:
            dump.file.close()

    def __open(self, file):
        try:
            file.open()
            self.dumps.append(self.Dump(file))
        except FileNotFoundError:
            print('{} so such file'.format(file))
            return

    def add_tx(self, idx, file_path):
        self.__open(DeviceDumpFileTx(idx, file_path))

    def add_rx(self, idx, file_path):
        # TODO
        pass

    def flush(self):
        for dump in self.dumps:
            while next(dump.generator):
                pass

            dump.dump = None

    def fetch(self):
        while True:
            for dump in self.dumps:
                if not dump.dump:
                    try:
                        dump.dump = next(dump.generator)
                    except StopIteration:
                        pass

            # sort by timestamp
            self.dumps.sort(key=lambda entry: entry.dump.ts if entry.dump else sys.maxsize)
            dump = self.dumps[0]
            if not dump.dump:
                return

            yield dump.dump
            dump.dump = None


class Packets:
    def __init__(self, dumps):
        self.__dumps = dumps
        self.__dumps.flush()
        self.__parser = PacketParser()
        self.__packets = []

    def fetch(self, packet_filter=()):
        try:
            iter(packet_filter)
        except TypeError:
            packet_filter = (packet_filter,)
        else:
            packet_filter = packet_filter

        i = 0
        while True:
            # Append new packets
            for dump in self.__dumps.fetch():
                self.__packets.append(self.__parser.parse(dump))

            if i < len(self.__packets):
                if self.__packets[i] != None and (not packet_filter or self.__packets[i].type.name in packet_filter):
                    yield self.__packets[i]
                i += 1
            else:
                return

    def find(self, packet_type=None):
        try:
            return next(self.fetch(packet_type))
        except StopIteration:
            return None

    def findLast(self, packet_filter=()):
        try:
            iter(packet_filter)
        except TypeError:
            packet_filter = (packet_filter,)
        else:
            packet_filter = packet_filter

        # Append new packets
        for dump in self.__dumps.fetch():
            self.__packets.append(self.__parser.parse(dump))

        for i in reversed(range(len(self.__packets))):
            if self.__packets[i] != None and (not packet_filter or self.__packets[i].type.name in packet_filter):
                return self.__packets[i]
        return None

    def flush(self):
        for dump in self.__dumps.fetch():
            pass
        self.__parser = PacketParser()
        self.__packets = []
