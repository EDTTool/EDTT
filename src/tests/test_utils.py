# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

import math
from components.utils import *;
from components.basic_commands import *;
from components.address import *;
from components.events import *;
from components.resolvable import *;
from components.advertiser import *;
from components.scanner import *;
from components.initiator import *;
from components.addata import *;
from components.preambles import *;
from components.dump import PacketType;
from enum import IntEnum

global lowerRandomAddress, upperRandomAddress;

def verifyAndShowEvent(transport, idx, expectedEvent, trace, to=100):

    event = get_event(transport, idx, to);
    trace.trace(7, str(event));
    return event.event == expectedEvent;

def verifyNumCompleteEvents(transport, idx, handle, count, trace, to=100):

    success = True
    while success and count > 0:
        event = get_event(transport, idx, to)
        trace.trace(7, str(event))
        numHandles, handles, packets = event.decode()
        success = (event.event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS and
                   numHandles == 1 and handles[0] == handle and success)
        count -= packets[0]

    return success

def verifyAndShowMetaEvent(transport, idx, expectedEvent, trace):

    event = get_event(transport, idx, 100);
    trace.trace(7, str(event));
    return event.subEvent == expectedEvent;

def verifyAndFetchEvent(transport, idx, expectedEvent, trace):

    event = get_event(transport, idx, 100);
    trace.trace(7, str(event));
    return event.event == expectedEvent, event;

def verifyAndFetchMetaEvent(transport, idx, expectedEvent, trace, to=100):

    event = get_event(transport, idx, to);
    trace.trace(7, str(event));
    return event.subEvent == expectedEvent, event;

def getCommandCompleteEvent(transport, idx, trace):

    return verifyAndShowEvent(transport, idx, Events.BT_HCI_EVT_CMD_COMPLETE, trace);

def readLocalResolvableAddress(transport, idx, identityAddress, trace):

    status, resolvableAddress = le_read_local_resolvable_address(transport, idx, identityAddress.type, identityAddress.address, 100);
    trace.trace(6, "LE Read Local Resolvable Address returns status: 0x%02X" % status);
    return getCommandCompleteEvent(transport, idx, trace) and (status == 0), resolvableAddress;

def readPeerResolvableAddress(transport, idx, identityAddress, trace):

    status, resolvableAddress = le_read_peer_resolvable_address(transport, idx, identityAddress.type, identityAddress.address, 100);
    trace.trace(6, "LE Read Peer Resolvable Address returns status: 0x%02X" % status);
    return getCommandCompleteEvent(transport, idx, trace) and (status == 0), resolvableAddress;

"""
    Issue a channel Map Update
"""
def channelMapUpdate(transport, idx, channelMap, trace):

    status = le_set_host_channel_classification(transport, idx, toArray(channelMap, 5), 100);
    trace.trace(6, "LE Set Host Channel Classification returns status: 0x%02X" % status);
    return getCommandCompleteEvent(transport, idx, trace) and (status == 0);

def setLEEventMask(transport, idx, events, trace):

    status = le_set_event_mask(transport, idx, events, 100);
    trace.trace(6, "LE Set Event Mask returns status: 0x%02X" % status);
    return getCommandCompleteEvent(transport, idx, trace) and (status == 0);

def setPrivacyMode(transport, idx, address, mode, trace):

    status = le_set_privacy_mode(transport, idx, address.type, address.address, mode, 100);
    trace.trace(6, "LE Set Privacy Mode returns status: 0x%02X" % status);
    return getCommandCompleteEvent(transport, idx, trace) and (status == 0);

def setDataLength(transport, idx, handle, octets, time, trace):

    status, handle = le_set_data_length(transport, idx, handle, octets, time, 100);
    trace.trace(6, "LE Set Data Length returns status: 0x%02X handle: 0x%04X" % (status, handle));
    return getCommandCompleteEvent(transport, idx, trace) and (status == 0);

def readBufferSize(transport, idx, trace):

    status, maxPacketLength, maxPacketNumbers = le_read_buffer_size(transport, idx, 100);
    trace.trace(6, "LE Read Buffer Size returns status: 0x%02X - Data Packet length %d, Number of Data Packets %d" % (status, maxPacketLength, maxPacketNumbers));
    return getCommandCompleteEvent(transport, idx, trace) and (status == 0), maxPacketLength, maxPacketNumbers;

def readBufferSizeV2(transport, idx, trace):

    status, maxPacketLength, maxPacketNumbers, maxIsoPacketLength, maxIsoPacketNumbers = le_read_buffer_size_v2(transport, idx, 100);
    trace.trace(6, "LE Read Buffer Size V2 returns status: 0x%02X - Data Packet length %d, Number of Data Packets %d, ISO Data Packet length %d, Number of ISO Data Packets %d" % (status, maxPacketLength, maxPacketNumbers, maxIsoPacketLength, maxIsoPacketNumbers));
    return getCommandCompleteEvent(transport, idx, trace) and (status == 0), maxPacketLength, maxPacketNumbers, maxIsoPacketLength, maxIsoPacketNumbers;

def readLocalFeatures(transport, idx, trace):

    status, features = le_read_local_supported_features(transport, idx, 100)
    trace.trace(6, "LE Read Local Supported Features returns status: 0x%02X" % status);
    return getCommandCompleteEvent(transport, idx, trace) and (status == 0), features;

def readRemoteFeatures(transport, idx, handle, trace):

    status = le_read_remote_features(transport, idx, handle, 100);
    trace.trace(6, "LE Read Remote Features returns status: 0x%02X" % status);
    return verifyAndShowEvent(transport, idx, Events.BT_HCI_EVT_CMD_STATUS, trace) and (status == 0);

def readRemoteVersionInformation(transport, idx, handle, trace):

    status = read_remote_version_information(transport, idx, handle, 100);
    trace.trace(6, "Read Remote Version Information returns status: 0x%02X" % status);
    return verifyAndShowEvent(transport, idx, Events.BT_HCI_EVT_CMD_STATUS, trace) and (status == 0);

def addAddressesToFilterAcceptList(transport, idx, addresses, trace):

    _addresses = [ [ _.type, toNumber(_.address) ] for _ in addresses ];
    return preamble_specific_filter_accept_listed(transport, idx, _addresses, trace);

"""
    Send a DATA package...
"""
def writeData(transport, idx, handle, pbFlags, txData, trace):

    status = le_data_write(transport, idx, handle, pbFlags, 0, txData, 100);
    trace.trace(6, "LE Data Write returns status: 0x%02X" % status);
    success = status == 0;

    dataSent = has_event(transport, idx, 200)[0];
    success = success and dataSent;
    if dataSent:
        dataSent = verifyAndShowEvent(transport, idx, Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS, trace);
        success = success and dataSent;

    return success;

def encrypt(transport, idx, key, plaintext, trace):

    status, encrypted = le_encrypt(transport, idx, key, plaintext, 2000);
    trace.trace(6, "LE Encrypt Command returns status: 0x%02X" % status);
    success = getCommandCompleteEvent(transport, idx, trace) and (status == 0);
    return success, encrypted;

"""
    Read a single DATA Package...
"""
def readData(transport, idx, trace, timeout=200):
    rxData = [];

    dataReady = le_data_ready(transport, idx, timeout);
    if dataReady:
        rxPBFlags, rxBCFlags, rxDataPart = le_data_read(transport, idx, 100)[2:];
        trace.trace(6, "LE Data Read returns PB=%d BC=%d - %2d data bytes: %s" % \
                       (rxPBFlags, rxBCFlags, len(rxDataPart), formatArray(rxDataPart)));
        rxData = list(rxDataPart);

    return (len(rxData) > 0), rxData;

"""
    Read and concatenate multiple DATA Packages...
"""
def readDataFragments(transport, idx, trace, timeout=100):
    success, rxData = True, [];

    while success:
        dataReady = le_data_ready(transport, idx, timeout);
        success = success and dataReady;
        if dataReady:
            rxPBFlags, rxBCFlags, rxDataPart = le_data_read(transport, idx, 100)[2:];
            trace.trace(6, "LE Data Read returns PB=%d BC=%d - %2d data bytes: %s" % \
                           (rxPBFlags, rxBCFlags, len(rxDataPart), formatArray(rxDataPart)));
            rxData += rxDataPart;
            timeout = 99;

    return (len(rxData) > 0), rxData;

def hasConnectionUpdateCompleteEvent(transport, idx, trace):

    success, status = has_event(transport, idx, 100)[0], -1;
    if success:
        success, event = verifyAndFetchMetaEvent(transport, idx, MetaEvents.BT_HCI_EVT_LE_CONN_UPDATE_COMPLETE, trace);
        if success:
            status, handle, interval, latency, timeout = event.decode();
            success = status == 0;
    return success, status;

def hasChannelSelectionAlgorithmEvent(transport, idx, trace):

    success, status, handle, chSelAlgorithm = has_event(transport, idx, 100)[0], -1, -1, -1;
    if success:
        success, event = verifyAndFetchMetaEvent(transport, idx, MetaEvents.BT_HCI_EVT_LE_CHAN_SEL_ALGO, trace);
        if success:
            handle, chSelAlgorithm = event.decode();
    return success, handle, chSelAlgorithm;

def hasDataLengthChangedEvent(transport, idx, trace):

    success, handle, maxTxOctets, maxTxTime, maxRxOctets, maxRxTime = has_event(transport, idx, 200)[0], -1, -1, -1, -1, -1;
    if success:
        success, event = verifyAndFetchMetaEvent(transport, idx, MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE, trace);
        if success:
            handle, maxTxOctets, maxTxTime, maxRxOctets, maxRxTime = event.decode();
    return success, handle, maxTxOctets, maxTxTime, maxRxOctets, maxRxTime;

def hasReadRemoteFeaturesCompleteEvent(transport, idx, trace):

    success, handle, features = has_event(transport, idx, 100)[0], -1, [];
    if success:
        success, event = verifyAndFetchMetaEvent(transport, idx, MetaEvents.BT_HCI_EVT_LE_REMOTE_FEAT_COMPLETE, trace);
        if success:
            status, handle, features = event.decode();
            success = status == 0;
    return success, handle, toArray(features,8);

def hasReadRemoteVersionInformationCompleteEvent(transport, idx, trace):

    success, handle, version, manufacturer, subVersion = has_event(transport, idx, 100)[0], -1, -1, -1, -1;
    if success:
        success, event = verifyAndFetchEvent(transport, idx, Events.BT_HCI_EVT_REMOTE_VERSION_INFO, trace);
        if success:
            status, handle, version, manufacturer, subVersion = event.decode();
            success = status == 0;
    return success, handle, version, manufacturer, subVersion;

def hasLeCisRequestMetaEvent(transport, idx, trace, to):

    success, aclConnectionHandle, cisConnectionHandle, cigId, cisId = has_event(transport, idx, to)[0], -1, -1, -1, -1
    if success:
        success, event = verifyAndFetchMetaEvent(transport, idx, MetaEvents.BT_HCI_EVT_LE_CIS_REQUEST, trace)
        if success:
            aclConnectionHandle, cisConnectionHandle, cigId, cisId = event.decode()
    return success, aclConnectionHandle, cisConnectionHandle, cigId, cisId


def hasLeLtkRequestMetaEvent(transport, idx, trace, to):

    success, handle, rand, ediv = has_event(transport, idx, to)[0], -1, -1, -1
    if success:
        success, event = verifyAndFetchMetaEvent(transport, idx, MetaEvents.BT_HCI_EVT_LE_LTK_REQUEST, trace)
        if success:
            handle, rand, ediv = event.decode()
    return success, handle, rand, ediv


def hasEncryptionChangeEvent(transport, idx, trace, to):
    success, status, handle, enabled, key_size = has_event(transport, idx, to)[0], -1, -1, -1, -1
    if success:
        event = get_event(transport, idx, to)
        trace.trace(7, str(event))
        if event.event == Events.BT_HCI_EVT_ENCRYPT_CHANGE_V1:
            status, handle, enabled = event.decode()
        elif event.event == Events.BT_HCI_EVT_ENCRYPT_CHANGE_V2:
            status, handle, enabled, key_size = event.decode()

    success = status == 0 and success

    return success, handle, enabled, key_size


def calcMaxPacketTime(packetLength):
    #      (preamble + AA + header + packetLength + MIC + CRC) * us/byte
    return (1        + 4  + 2      + packetLength + 4   + 3  ) * 8

def calcMaxIsoSdu(Framing, BN, Max_PDU, ISO_Interval, SDU_Interval, Max_SDU_Supported):
    if Framing == 0:
        return calcUnframedMaxIsoSdu(BN, Max_PDU, ISO_Interval, SDU_Interval, Max_SDU_Supported)
    elif Framing == 1:
        return Max_SDU_Supported
    else:
        raise ValueError("Framing must be 0 or 1")

def calcUnframedMaxIsoSdu(BN, Max_PDU, ISO_Interval, SDU_Interval, Max_SDU_Supported):
    # BLUETOOTH CORE SPECIFICATION Version 5.2 | Vol 6, Part G, 2.1 UNFRAMED PDU:
    #
    # BN = ceil(Max_SDU / Max_PDU) * (ISO_Interval / SDU_Interval).
    # (BN / (ISO_Interval / SDU_Interval)) = ceil(Max_SDU / Max_PDU)
    # (BN / (ISO_Interval / SDU_Interval)) - 1 < Max_SDU / Max_PDU <= (BN / (ISO_Interval / SDU_Interval))
    # ((BN / (ISO_Interval / SDU_Interval)) - 1) * Max_PDU < Max_SDU <= (BN / (ISO_Interval / SDU_Interval)) * Max_PDU
    #
    # Max_SDU = Max_PDU * BN * (SDU_Interval / ISO_Interval)

    Max_SDU = int(Max_PDU * BN * (SDU_Interval / ISO_Interval))

    # Clamp
    return min(Max_SDU, Max_SDU_Supported)

def matchingReportType(advertiseType):

    if   advertiseType == Advertising.CONNECTABLE_UNDIRECTED:
        reportType = AdvertisingReport.ADV_IND;
    elif advertiseType == Advertising.CONNECTABLE_HDC_DIRECTED or advertiseType == Advertising.CONNECTABLE_LDC_DIRECTED:
        reportType = AdvertisingReport.ADV_DIRECT_IND;
    elif advertiseType == Advertising.SCANNABLE_UNDIRECTED:
        reportType = AdvertisingReport.ADV_SCAN_IND;
    elif advertiseType == Advertising.NON_CONNECTABLE_UNDIRECTED:
        reportType = AdvertisingReport.ADV_NONCONN_IND;
    else:
        reportType = AdvertisingReport.ADV_IND;
    return reportType;

def publicIdentityAddress(idx):

    return Address( SimpleAddressType.PUBLIC, 0x123456789ABC if idx == 0 else 0x456789ABCDEF );

def randomIdentityAddress(idx):
    global lowerRandomAddress, upperRandomAddress;

    return Address( SimpleAddressType.RANDOM, upperRandomAddress if idx == 0 else lowerRandomAddress );

def resolvablePublicAddress(idx):

    return Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x123456789ABC if idx == 0 else 0x456789ABCDEF );

def setStaticRandomAddress(transport, idx, trace):
    global lowerRandomAddress, upperRandomAddress;

    address = upperRandomAddress if idx == 0 else lowerRandomAddress;
    if (toNumber(address)) & 0xC00000000000 != 0xC00000000000:
        address = toArray(toNumber(address) | 0xC00000000000, 6);
        preamble_set_random_address(transport, idx, toNumber(address), trace);
        if idx == 0:
            upperRandomAddress = address;
        else:
            lowerRandomAddress = address;

def setNonResolvableRandomAddress(transport, idx, trace):
    global lowerRandomAddress, upperRandomAddress;

    address = upperRandomAddress if idx == 0 else lowerRandomAddress;
    if (toNumber(address)) & 0xC00000000000 != 0x000000000000:
        address = toArray(toNumber(address) & 0x3FFFFFFFFFFF, 6);
        preamble_set_random_address(transport, idx, toNumber(address), trace);
        if idx == 0:
            upperRandomAddress = address;
        else:
            lowerRandomAddress = address;

def setPassiveScanning(transport, scannerId, trace, advertiseType, advertiseReports=100, \
                       advertiseFilter=AdvertisingFilterPolicy.FILTER_NONE, advertiseChannels=AdvertiseChannel.ALL_CHANNELS, \
                       scanFilter=ScanningFilterPolicy.FILTER_NONE):

    advertiserId = scannerId ^ 1;
    advertiserAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = publicIdentityAddress( scannerId );

    advertiser = Advertiser(transport, advertiserId, trace, advertiseChannels, advertiseType, advertiserAddress, peerAddress, advertiseFilter);

    scannerAddress = Address( ExtendedAddressType.PUBLIC );

    scanner = Scanner(transport, scannerId, trace, ScanType.PASSIVE, matchingReportType(advertiseType), scannerAddress, scanFilter, advertiseReports);

    return advertiser, scanner;

def setActiveScanning(transport, scannerId, trace, advertiseType, advertiseReports=1, advertiseResponses=1, \
                      advertiseFilter=AdvertisingFilterPolicy.FILTER_NONE, advertiseChannels=AdvertiseChannel.ALL_CHANNELS, \
                      scanFilter=ScanningFilterPolicy.FILTER_NONE):

    advertiserId = scannerId ^ 1;
    advertiserAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = publicIdentityAddress( scannerId );

    advertiser = Advertiser(transport, advertiserId, trace, advertiseChannels, advertiseType, advertiserAddress, peerAddress, advertiseFilter);

    scannerAddress = Address( ExtendedAddressType.PUBLIC );

    scanner = Scanner(transport, scannerId, trace, ScanType.ACTIVE, matchingReportType(advertiseType), scannerAddress, scanFilter, advertiseReports, advertiseResponses);

    return advertiser, scanner;

def setPrivatePassiveScanning(transport, scannerId, trace, advertiseType, advertiseReports=100, \
                              advertiserAddressType=ExtendedAddressType.RESOLVABLE_OR_PUBLIC, scannerAddressType=ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                              advertiseFilter=AdvertisingFilterPolicy.FILTER_NONE, advertiseChannels=AdvertiseChannel.ALL_CHANNELS, \
                              scanFilter=ScanningFilterPolicy.FILTER_NONE):

    advertiserId = scannerId ^ 1;
    advertiserAddress = Address( advertiserAddressType );
    if (advertiserAddressType == ExtendedAddressType.RANDOM) or (advertiserAddressType == ExtendedAddressType.RESOLVABLE_OR_RANDOM):
        peerAddress = randomIdentityAddress( scannerId );
    else:
        peerAddress = publicIdentityAddress( scannerId );

    advertiser = Advertiser(transport, advertiserId, trace, advertiseChannels, advertiseType, advertiserAddress, peerAddress, advertiseFilter);

    scannerAddress = Address( scannerAddressType );

    scanner = Scanner(transport, scannerId, trace, ScanType.PASSIVE, matchingReportType(advertiseType), scannerAddress, scanFilter, advertiseReports);

    return advertiser, scanner;

def setPrivateActiveScanning(transport, scannerId, trace, advertiseType, advertiseReports=1, advertiseResponses=1, \
                             advertiserAddressType=ExtendedAddressType.RESOLVABLE_OR_PUBLIC, scannerAddressType=ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                             advertiseFilter=AdvertisingFilterPolicy.FILTER_NONE, advertiseChannels=AdvertiseChannel.ALL_CHANNELS, \
                             scanFilter=ScanningFilterPolicy.FILTER_NONE):

    advertiserId = scannerId ^ 1;
    advertiserAddress = Address( advertiserAddressType );
    if (advertiserAddressType == ExtendedAddressType.RANDOM) or (advertiserAddressType == ExtendedAddressType.RESOLVABLE_OR_RANDOM):
        peerAddress = randomIdentityAddress( scannerId );
    else:
        peerAddress = publicIdentityAddress( scannerId );

    advertiser = Advertiser(transport, advertiserId, trace, advertiseChannels, advertiseType, advertiserAddress, peerAddress, advertiseFilter);

    scannerAddress = Address( scannerAddressType );

    scanner = Scanner(transport, scannerId, trace, ScanType.ACTIVE, matchingReportType(advertiseType), scannerAddress, scanFilter, advertiseReports, advertiseResponses);

    return advertiser, scanner;

def setPublicInitiator(transport, initiatorId, trace, advertiseType, advertiseFilter=AdvertisingFilterPolicy.FILTER_NONE, \
                       advertiseChannels=AdvertiseChannel.ALL_CHANNELS, initiatorFilterPolicy=InitiatorFilterPolicy.FILTER_NONE):

    advertiserId = initiatorId ^ 1;
    advertiserAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = publicIdentityAddress( initiatorId );

    advertiser = Advertiser(transport, advertiserId, trace, advertiseChannels, advertiseType, advertiserAddress, peerAddress, advertiseFilter);

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    responderAddress = publicIdentityAddress( advertiserId );

    initiator = Initiator(transport, initiatorId, advertiserId, trace, initiatorAddress, responderAddress, initiatorFilterPolicy);

    return advertiser, initiator;

def setPrivateInitiator(transport, initiatorId, trace, advertiseType, advertiserAddressType=ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                        initiatorAddressType=ExtendedAddressType.RESOLVABLE_OR_PUBLIC, advertiseFilter=AdvertisingFilterPolicy.FILTER_NONE, \
                        advertiseChannels=AdvertiseChannel.ALL_CHANNELS, initiatorFilterPolicy=InitiatorFilterPolicy.FILTER_NONE):

    advertiserId = initiatorId ^ 1;
    advertiserAddress = Address( advertiserAddressType );
    if (advertiserAddressType == ExtendedAddressType.RANDOM) or (advertiserAddressType == ExtendedAddressType.RESOLVABLE_OR_RANDOM):
        peerAddress = randomIdentityAddress( initiatorId );
    else:
        peerAddress = publicIdentityAddress( initiatorId );

    advertiser = Advertiser(transport, advertiserId, trace, advertiseChannels, advertiseType, advertiserAddress, peerAddress, advertiseFilter);

    initiatorAddress = Address( initiatorAddressType );
    if (initiatorAddressType == ExtendedAddressType.RANDOM) or (initiatorAddressType == ExtendedAddressType.RESOLVABLE_OR_RANDOM):
        responderAddress = randomIdentityAddress( advertiserId );
    else:
        responderAddress = publicIdentityAddress( advertiserId );

    initiator = Initiator(transport, initiatorId, advertiserId, trace, initiatorAddress, responderAddress, initiatorFilterPolicy);

    return advertiser, initiator;


def le_iso_data_write_fragments(transport, idx, trace, conn_handle, data, iso_buffer_len):
    TsFlag = 0
    cont = False
    offset = 0
    fragments = 0
    success = True

    while success and offset < len(data):
        fragment_len = min(iso_buffer_len, len(data[offset:]))

        PbFlag = 0
        if cont:
            PbFlag |= 1
        if len(data[offset:]) <= iso_buffer_len:
            PbFlag |= 2
        cont = True

        status = le_iso_data_write(transport, idx, conn_handle, PbFlag, TsFlag, data[offset:offset+fragment_len], 0)
        success = (status == 0) and success

        offset += fragment_len
        fragments += 1

    return success, fragments


def le_iso_data_write_complete(transport, idx, trace, number_of_packets_written, to):
    success = True
    for _ in range(number_of_packets_written):
        success = le_iso_data_write_rsp(transport, idx, to) == 0 and success

    return success


def le_iso_data_write_nbytes(transport, idx, trace, conn_handle, nbytes, pkt_seq_num, iso_buffer_len):
    iso_data_sdu = tuple([pkt_seq_num] * nbytes)
    tx_iso_data_load = struct.pack(f'<HH{nbytes}B', pkt_seq_num, nbytes, *iso_data_sdu)
    success, fragments = le_iso_data_write_fragments(transport, idx, trace, conn_handle, tx_iso_data_load, iso_buffer_len)

    return success, iso_data_sdu


def fetch_number_of_completed_packets(transport, idx, trace, number_of_packets_written, to):
    number_of_completed_packets = {}

    while sum(number_of_completed_packets.values()) < number_of_packets_written:
        event = get_event(transport, idx, to)
        if event.event != Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS:
            break

        num_handles, conn_handles, num_packets = event.decode()
        for i in range(num_handles):
            if conn_handles[i] in number_of_completed_packets:
                number_of_completed_packets[conn_handles[i]] += num_packets[i]
            else:
                number_of_completed_packets[conn_handles[i]] = num_packets[i]

    return len(number_of_completed_packets), number_of_completed_packets.keys(), number_of_completed_packets.values()


class PbFlags(IntEnum):
    FIRST = 0
    CONTINUATION = 1
    COMPLETE = 2
    LAST = 3


def iso_receive_sdu(transport, idx, trace, sdu_interval):
    iso_sdu = []
    iso_sdu_len = 0
    success = True
    while success:
        success = le_iso_data_ready(transport, idx, sdu_interval * 2) and success
        if not success:
            return success, -1, tuple([])

        time, handle, pbflags, tsflag, rx_iso_data_load = le_iso_data_read(transport, idx, 100)
        rx_iso_data_load = bytearray(rx_iso_data_load)

        # Unpack ISO_Data_Load
        rx_offset = 0
        # a. Get Time_Stamp if present
        if tsflag:
            fmt = '<I'
            (time_stamp,) = struct.unpack_from(fmt, rx_iso_data_load)
            rx_offset += struct.calcsize(fmt)

        # FIXME: Temporary workaround for Packetcraft not being along with Core version Sydney.
        #  Packet_Sequence_Number, Packet_Status_Flag and ISO_SDU_Length shall be sent for all fragments
        if pbflags == PbFlags.FIRST or pbflags == PbFlags.COMPLETE:
            # b. Get Packet_Sequence_Number, ISO_SDU_Length and Packet_Status_Flag
            fmt = '<HH'
            rx_packet_sequence_number, rx_iso_sdu_length = struct.unpack_from(fmt, rx_iso_data_load, rx_offset)
            rx_offset += struct.calcsize(fmt)
            rx_packet_status_flag = rx_iso_sdu_length >> 14
            rx_iso_sdu_length &= 0xfff  # 12 bits valid

            success = (iso_sdu_len == 0) and success
            iso_sdu_len = rx_iso_sdu_length

        rx_iso_sdu = rx_iso_data_load[rx_offset:]
        iso_sdu.extend(rx_iso_sdu)

        # Valid data. The complete ISO_SDU was received correctly.
        success = (rx_packet_status_flag == 0x00) and success

        if pbflags == PbFlags.LAST or pbflags == PbFlags.COMPLETE:
            success = (len(iso_sdu) == iso_sdu_len) and success
            break

        success = (len(iso_sdu) < iso_sdu_len) and success

    return success, handle, tuple(iso_sdu)


def iso_send_payload_pdu(transport, transmitter, receiver, trace, conn_handle, max_data_size, sdu_interval, pkt_seq_num,
                         tx_iso_sdu=None):
    # Create a ISO_SDU of sdu_size length
    if not tx_iso_sdu:
        tx_iso_sdu = tuple([(pkt_seq_num + x) % 255 for x in range(max_data_size)])

    # Pack the ISO_Data_Load (no Time_Stamp) of an HCI ISO Data packet
    # <Packet_Sequence_Number, ISO_SDU_Length, ISO_SDU>
    fmt = '<HH{ISO_SDU_Length}B'.format(ISO_SDU_Length=len(tx_iso_sdu))
    tx_iso_data_load = struct.pack(fmt, pkt_seq_num, len(tx_iso_sdu), *tx_iso_sdu)

    # Transmitter: TX SDU
    success, _, _, iso_buffer_len, _ = readBufferSizeV2(transport, transmitter, trace)
    s, fragments = le_iso_data_write_fragments(transport, transmitter, trace, conn_handle, tx_iso_data_load, iso_buffer_len)
    sucess = s and success
    success = le_iso_data_write_complete(transport, transmitter, trace, fragments, 100) and success
    success = verifyNumCompleteEvents(transport, transmitter, conn_handle, fragments, trace, sdu_interval * 2) and success

    s, _, rx_iso_sdu = iso_receive_sdu(transport, receiver, trace, sdu_interval)
    success = s and success

    # Transmitter: No RX
    success = not le_iso_data_ready(transport, transmitter, 100) and success

    # Receiver: No more RX data
    success = not le_iso_data_ready(transport, receiver, 100) and success

    # TX and RX match
    return (tx_iso_sdu == rx_iso_sdu) and success


def iso_send_payload_pdu_parallel(transport, idx_1, idx_2, trace, conn_handle_1, conn_handle_2, max_data_size,
                                  sdu_interval, pkt_seq_num):
    # Create a ISO_SDU of sdu_size length
    tx_iso_sdu = tuple([(pkt_seq_num + x) % 255 for x in range(max_data_size)])

    # Pack the ISO_Data_Load (no Time_Stamp) of an HCI ISO Data packet
    # <Packet_Sequence_Number, ISO_SDU_Length, ISO_SDU>
    fmt = '<HH{ISO_SDU_Length}B'.format(ISO_SDU_Length=len(tx_iso_sdu))
    tx_iso_data_load = struct.pack(fmt, pkt_seq_num, len(tx_iso_sdu), *tx_iso_sdu)

    # Feed TX buffers
    success, _, _, iso_buffer_len_1, _ = readBufferSizeV2(transport, idx_1, trace)
    s, _, _, iso_buffer_len_2, _ = readBufferSizeV2(transport, idx_2, trace)
    success = s and success
    s, fragments_1 = le_iso_data_write_fragments(transport, idx_1, trace, conn_handle_1, tx_iso_data_load, iso_buffer_len_1)
    success = s and success
    s, fragments_2 = le_iso_data_write_fragments(transport, idx_2, trace, conn_handle_2, tx_iso_data_load, iso_buffer_len_2)
    success = s and success

    # Wait for data to be sent; fetch EDTT command response and Number of Completed packets event
    success = le_iso_data_write_complete(transport, idx_1, trace, fragments_1, 100) and success
    success = le_iso_data_write_complete(transport, idx_2, trace, fragments_2, 100) and success
    success = verifyNumCompleteEvents(transport, idx_1, conn_handle_1, fragments_1, trace) and success
    success = verifyNumCompleteEvents(transport, idx_2, conn_handle_2, fragments_2, trace) and success

    # Check the data received
    s, _, rx_iso_sdu = iso_receive_sdu(transport, idx_1, trace, sdu_interval)
    success = s and tx_iso_sdu == rx_iso_sdu and success

    s, _, rx_iso_sdu = iso_receive_sdu(transport, idx_2, trace, sdu_interval)
    success = s and tx_iso_sdu == rx_iso_sdu and success

    return success


def set_isochronous_channels_host_support(transport, device, trace, value):
    status = le_set_host_feature(transport, device, FeatureSupport.ISOCHRONOUS_CHANNELS, value, 100)
    return getCommandCompleteEvent(transport, device, trace) and (status == 0x00)


def establish_acl_connection(transport, central, peripheral, trace, interval=None, supervision_timeout=None):
    advertiser, initiator = setPublicInitiator(transport, central, trace, Advertising.CONNECTABLE_UNDIRECTED)
    if interval:
        initiator.intervalMin = initiator.intervalMax = interval

    if supervision_timeout:
        initiator.supervisionTimeout = supervision_timeout

    success = advertiser.enable()
    connected = initiator.connect()
    success = success and connected

    if not connected:
        success = advertiser.disable() and success

    return success, advertiser, initiator


def establish_cis_connection(transport, central, peripheral, trace, params, acl_conn_handle, setup_iso_data_path=True,
                             use_test_cmd=True):
    success = True

    # LT: Set CIG Parameters for Test
    if use_test_cmd:
        status, cigId, cisCount, central_cis_handles = \
            le_set_cig_parameters_test(transport, central, 0, *params.get_cig_parameters_test(), 100)
    else:
        status, cigId, cisCount, central_cis_handles = \
            le_set_cig_parameters(transport, central, 0, *params.get_cig_parameters(), 100)

    success = getCommandCompleteEvent(transport, central, trace) and (status == 0x00) and success
    central_acl_handles = [acl_conn_handle] * cisCount
    peripheral_cis_handles = [-1] * cisCount

    # LT: Create CIS
    status = le_create_cis(transport, central, cisCount, central_cis_handles, central_acl_handles, 100)
    success = verifyAndShowEvent(transport, central, Events.BT_HCI_EVT_CMD_STATUS, trace) and (status == 0) and success

    for n in range(cisCount):
        # UT: Wait for HCI_EVT_LE_CIS_REQUEST
        s, event = verifyAndFetchMetaEvent(transport, peripheral, MetaEvents.BT_HCI_EVT_LE_CIS_REQUEST, trace)
        success = s and success
        _, peripheral_cis_handles[n], cigId, cisId = event.decode()

        # UT: Accept CIS Request
        status = le_accept_cis_request(transport, peripheral, peripheral_cis_handles[n], 100)
        success = verifyAndShowEvent(transport, peripheral, Events.BT_HCI_EVT_CMD_STATUS, trace) and (status == 0) and success

        # LT: Wait for HCI_EVT_LE_CIS_ESTABLISHED
        s, event = verifyAndFetchMetaEvent(transport, central, MetaEvents.BT_HCI_EVT_LE_CIS_ESTABLISHED, trace, 2000)
        success = s and (event.decode()[0] == 0x00) and success

        # UT: Wait for HCI_EVT_LE_CIS_ESTABLISHED
        s, event = verifyAndFetchMetaEvent(transport, peripheral, MetaEvents.BT_HCI_EVT_LE_CIS_ESTABLISHED, trace)
        success = s and (event.decode()[0] == 0x00) and success

    if not setup_iso_data_path:
        return success, central_cis_handles, peripheral_cis_handles

    for n in range(cisCount):
        if (params.Max_SDU_C_To_P != 0):
            # LT: Setup Data Path - Data_Path_Direction=0 (Input)  Data_Path_ID=1 (HCI) Codec_ID=0 Controller_Delay=0 Codec_Configuration_Length=0 Codec_Configuration=NULL
            status, _ = le_setup_iso_data_path(transport, central, central_cis_handles[n], 0, 0, [0, 0, 0, 0, 0], 0, 0, [], 100)
            success = getCommandCompleteEvent(transport, central, trace) and (status == 0x00) and success

            # UT: Setup Data Path - Data_Path_Direction=1 (Output) Data_Path_ID=1 (HCI) Codec_ID=0 Controller_Delay=0 Codec_Configuration_Length=0 Codec_Configuration=NULL
            status, _ = le_setup_iso_data_path(transport, peripheral, peripheral_cis_handles[n], 1, 0, [0, 0, 0, 0, 0], 0, 0, [], 100)
            success = getCommandCompleteEvent(transport, peripheral, trace) and (status == 0x00) and success

        if (params.Max_SDU_P_To_C != 0):
            # LT: Setup Data Path - Data_Path_Direction=1 (Output)  Data_Path_ID=1 (HCI) Codec_ID=0 Controller_Delay=0 Codec_Configuration_Length=0 Codec_Configuration=NULL
            status, _ = le_setup_iso_data_path(transport, central, central_cis_handles[n], 1, 0, [0, 0, 0, 0, 0], 0, 0, [], 100)
            success = getCommandCompleteEvent(transport, central, trace) and (status == 0x00) and success

            # UT: Setup Data Path - Data_Path_Direction=0 (Input) Data_Path_ID=1 (HCI) Codec_ID=0 Controller_Delay=0 Codec_Configuration_Length=0 Codec_Configuration=NULL
            status, _ = le_setup_iso_data_path(transport, peripheral, peripheral_cis_handles[n], 0, 0, [0, 0, 0, 0, 0], 0, 0, [], 100)
            success = getCommandCompleteEvent(transport, peripheral, trace) and (status == 0x00) and success

    return success, central_cis_handles, peripheral_cis_handles


def calc_supervision_timeout(iso_interval_ms):
    """
    Calculate the Supervision timeout for the LE Link that can be used to create a CIG with given ISO_Interval
    :param iso_interval_ms: ISO_Interval in milliseconds
    :return: Supervision timeout for the LE Link
    """
    # TS 4.10.1.2 Timing Requirements
    # "The connSupervisionTimeout for an ACL with associated CISes shall be greater than twice that of the
    #  ISO_Intervals of the associated CISes."
    supervision_timeout_ms = int(iso_interval_ms * 2 + 250)
    assert (supervision_timeout_ms < 32000)

    return int(supervision_timeout_ms / 10)


def enable_encryption(transport, central, peripheral, trace, conn_handle_c, keys):
    rand = keys[0]
    ediv = keys[1]
    ltk = keys[2]

    status = le_start_encryption(transport, central, conn_handle_c, rand, ediv, ltk, 100)
    success = verifyAndShowEvent(transport, central, Events.BT_HCI_EVT_CMD_STATUS, trace, 1000) and status == 0x00

    s, conn_handle_p, req_rand, req_ediv = hasLeLtkRequestMetaEvent(transport, peripheral, trace, 1000)
    success = s and req_rand == rand and req_ediv == ediv and success

    status, handle = le_long_term_key_request_reply(transport, peripheral, conn_handle_p, ltk, 1000)
    success = getCommandCompleteEvent(transport, peripheral, trace) and status == 0x00 and \
              handle == conn_handle_p and success

    s, handle, enabled, key_size = hasEncryptionChangeEvent(transport, peripheral, trace, 1000)
    success = s and handle == conn_handle_p and enabled == 0x01 and success

    s, handle, enabled, key_size = hasEncryptionChangeEvent(transport, central, trace, 1000)
    success = s and handle == conn_handle_c and enabled == 0x01 and success

    return success


def state_connected_isochronous_stream(transport, peripheral, central, trace, params,
                                       setup_iso_data_path=True, enc_keys=None, use_test_cmd=True,
                                       adjust_conn_interval=False):
    # The Isochronous Channels (Host Support) FeatureSet bit is set.
    success = set_isochronous_channels_host_support(transport, peripheral, trace, 1)
    success = set_isochronous_channels_host_support(transport, central, trace, 1) and success

    # Adjust connection interval to avoid CIG and ACL events collision
    if adjust_conn_interval:
        conn_interval = params.ISO_Interval
    else:
        conn_interval = None

    ### ACL Connection Established. IUT (upperTester) is Peripheral. ###
    s, advertiser, initiator = establish_acl_connection(transport, central, peripheral, trace, conn_interval,
                                                        calc_supervision_timeout(params.ISO_Interval * 1.25))
    success = s and success
    if not initiator:
        return success, None, [0xFFFF] * params.CIS_Count

    if enc_keys:
        success = enable_encryption(transport, central, peripheral, trace, initiator.handles[0], enc_keys) and success

    s, central_cis_handles, peripheral_cis_handles = \
        establish_cis_connection(transport, central, peripheral, trace, params, initiator.handles[0],
                                 setup_iso_data_path, use_test_cmd)

    return s and success, initiator, peripheral_cis_handles, central_cis_handles

# Helper function for set_complete_ext_adv_data()/set_complete_ext_scan_response_data()
def _set_complete_ad_sr_data(transport, idx, handle, fragmentPref, advData, set_data_function):
    maxFragmentSize = 251
    remainingAdvData = advData[:]
    firstFragment = True
    while (len(remainingAdvData) > 0):
        if firstFragment:
            if len(remainingAdvData) <= maxFragmentSize:
                op = FragmentOperation.COMPLETE_FRAGMENT
            else:
                op = FragmentOperation.FIRST_FRAGMENT
        else:
            if len(remainingAdvData) <= maxFragmentSize:
                op = FragmentOperation.LAST_FRAGMENT
            else:
                op = FragmentOperation.INTERMEDIATE_FRAGMENT
        endIndex = maxFragmentSize if len(remainingAdvData) >= maxFragmentSize else len(remainingAdvData)
        status = set_data_function(transport, idx, handle, op, fragmentPref, remainingAdvData[:endIndex], 100)
        if status != 0:
            return False
        remainingAdvData = remainingAdvData[endIndex:]
        firstFragment = False
    return True

"""
   Sets extended advertising data handling fragmentation as needed. The number of fragments used is kept as low as possible.
   Returns true if succeeded, false otherwise
"""
def set_complete_ext_adv_data(transport, idx, handle, fragmentPref, advData):
    return _set_complete_ad_sr_data(transport, idx, handle, fragmentPref, advData, le_set_extended_advertising_data)

"""
   Sets extended advertising scan response data handling fragmentation as needed. The number of fragments used is kept as low as possible.
   Returns true if succeeded, false otherwise
"""
def set_complete_ext_scan_response_data(transport, idx, handle, fragmentPref, advData):
    return _set_complete_ad_sr_data(transport, idx, handle, fragmentPref, advData, le_set_extended_scan_response_data)

"""
    Wait for the backend of an ADV_IND packet - will advance the time to be just after the next ADV_IND packet
    (just after in this case meaning within T_IFS so a response can be sent)

    Returns the ADV_IND packet or None if it fails to find one before the timeout
"""
def wait_for_ADV_IND_end(transport, packets, timeout):
    checkInterval = 100 # Note: Has to be less than T_IFS
    advIndPacket = None
    timeout = timeout*1000 # Convert to microseconds
    while timeout > 0:
        lastPacket = packets.findLast(packet_filter=('ADV_IND'))
        if lastPacket:
            # Check that simulation time is just after the ADV_IND has ended (so we can transmit a response)
            simulation_time = transport.get_last_t()
            if simulation_time < lastPacket.ts + get_packet_air_time(lastPacket) + 150:
                # Success, we can continue
                advIndPacket = lastPacket
                break
        # No packet yet - wait a little and try again
        transport.wait_until_t(transport.get_last_t() + checkInterval)
        timeout -= checkInterval
    return advIndPacket

"""
    Wait for the backend of an AUX_ADV_IND packet - will advance the time to be just after the next AUX_ADV_IND packet
    (just after in this case meaning within T_IFS so a response can be sent)

    Returns the AUX_ADV_IND packet
"""
def wait_for_AUX_ADV_IND_end(transport, packets):
    # Get an ADV_EXT_IND with an aux ptr pointing to an AUX_ADV_IND packet that hasn't been sent yet
    auxAdvIndPacket = None
    auxAdvIndEndTs = 0
    while auxAdvIndPacket == None:
        while True:
            lastPacket = packets.findLast(packet_filter=('ADV_EXT_IND', 'AUX_ADV_IND'))
            if not auxAdvIndPacket:
                auxAdvIndPacket = packets.findLast(packet_filter='AUX_ADV_IND')
            if lastPacket.type == PacketType.ADV_EXT_IND and auxAdvIndPacket:
                # Calculate end of offset window
                offsetEnd = (lastPacket.payload['AuxPtr'].auxOffset + 1) * (30 if lastPacket.payload['AuxPtr'].offsetUnits == 0 else 300)
                # Expected air time of the AUX_ADV_IND packet (assuming no changes from the last one)
                airTime = get_packet_air_time(auxAdvIndPacket)
                # Calculate expected (last possible) end time of the coming AUX_ADV_IND packet
                auxAdvIndEndTs = int(lastPacket.ts + offsetEnd + airTime)
                break
            # Don't have the needed packets yet or the last packet was not an ADV_EXT_IND; Wait a little and try again
            transport.wait(1)
        # Wait until the calculated end time (but make sure to always wait at least 1 us to avoid deadlocks)
        transport.wait_until_t(max(auxAdvIndEndTs + 1, transport.get_last_t() + 1))
    
        # Verify that the simulation time is within T_IFS of the end of the AUX_ADV_IND packet
        auxAdvIndPacket = None
        simulationTime = transport.get_last_t()
        lastPacket = packets.findLast()
        if lastPacket.type == PacketType.AUX_ADV_IND and simulationTime < lastPacket.ts + get_packet_air_time(lastPacket) + 150:
            # Success, we can continue
            auxAdvIndPacket = lastPacket
    
    return auxAdvIndPacket

"""
    Get air time of given packet in microseconds
"""
def get_packet_air_time(packet):
    # Note: Packet air length is: pre-amble + AA + header + payload + CRC
    return math.ceil(((2 if packet.phy == '2M' else 1) + 4 + 2 + len(packet) + 3)*8/(2 if packet.phy == '2M' else 1))

"""
LL.TS.p17
4.10.1.3     Default Values for Set CIG Parameters Commands
When using either the HCI_LE_Set_CIG_Parameters or HCI_LE_Set_CIG_Parameters_Test commands,
the following table defines common default parameters for this section. The test case may specify
different values.
"""
class SetCIGParameters:
    # Known parameter fields
    data = [
        # Name,                             Alias,         Per CIS, Default Value
        ('SDU_Interval_C_To_P',             'sdu_int_m2s', False,   20000),  # 20 ms
        ('SDU_Interval_P_To_C',             'sdu_int_s2m', False,   20000),  # 20 ms
        ('ISO_Interval',                    'iso_int',     False,   int(20 // 1.25)), # 20 ms
        ('CIS_Count',                       'cis_cnt',     False,   1),  # NOTE: Needs to be located before the first "Per CIS" field
        ('Worst_Case_SCA',                  None,          False,   0),
        ('Packing',                         'packing',     False,   0),  # Sequential
        ('Framing',                         'framing',     False,   0),  # Unframed
        ('NSE',                             'nse',         True,    3),  # Note: Set to 3 or the Max Supported CIS NSE defined in IXIT, whichever is less.
        ('Max_SDU_C_To_P',                  'mx_sdu_m2s',  True,    None),  # NOTE: Calculated in __init__
        ('Max_SDU_P_To_C',                  'mx_sdu_s2m',  True,    None),  # NOTE: Calculated in __init__
        ('Max_PDU_C_To_P',                  'mx_pdu_m2s',  True,    251),
        ('Max_PDU_P_To_C',                  'mx_pdu_s2m',  True,    251),
        ('PHY_C_To_P',                      'phy_m2s',     True,    1),  # LE 1M PHY
        ('PHY_P_To_C',                      'phy_s2m',     True,    1),  # LE 1M PHY
        ('FT_C_To_P',                       'ft_m2s',      False,   1),
        ('FT_P_To_C',                       'ft_s2m',      False,   1),
        ('BN_C_To_P',                       'bn_m2s',      True,    1),
        ('BN_P_To_C',                       'bn_s2m',      True,    1),
        ('Max_Transport_Latency_C_To_P',    None,          False,   40000),  # 40 ms
        ('Max_Transport_Latency_P_To_C',    None,          False,   40000),  # 40 ms
        ('RTN_C_To_P',                      None,          True,    3),
        ('RTN_P_To_C',                      None,          True,    3),
        ('Max_SDU_Supported',               None,          False,   247),  # Maximum ISOAL SDU length
    ]

    def __init__(self, **kwargs):
        # Make a list of the known fields
        fields = [t[0] for t in self.data] + [t[1] for t in self.data]

        # Check for unknown fields
        for key in kwargs.keys():
            if key not in fields:
                raise ValueError('Unknown field {}'.format(key))

        # Dynamically set the attributes of the class instance
        for (field, alias, per_cis, default) in self.data:
            # Get supplied value or default
            value = kwargs.get(field, default)

            # Per CIS field?
            if per_cis:
                value = self.per_cis_value(value)

            # Create field attribute
            setattr(self, field, value)

            # Create alias attribute
            if alias:
                setattr(self, alias, value)

        # Calculate the Max_SDU_C_To_P and Max_SDU_P_To_C unless given
        Max_SDU_C_To_P = [None] * self.CIS_Count
        Max_SDU_P_To_C = [None] * self.CIS_Count

        for n in range(self.CIS_Count):
            # Calculate default values
            Max_SDU_C_To_P[n] = calcMaxIsoSdu(self.Framing, self.BN_C_To_P[n], self.Max_PDU_C_To_P[n],
                                              self.ISO_Interval * 1.25 * 1000, self.SDU_Interval_C_To_P,
                                              self.Max_SDU_Supported)
            Max_SDU_P_To_C[n] = calcMaxIsoSdu(self.Framing, self.BN_P_To_C[n], self.Max_PDU_P_To_C[n],
                                              self.ISO_Interval * 1.25 * 1000, self.SDU_Interval_P_To_C,
                                              self.Max_SDU_Supported)

        # Override
        self.Max_SDU_C_To_P = self.per_cis_value(kwargs.get('Max_SDU_C_To_P', Max_SDU_C_To_P))
        self.Max_SDU_P_To_C = self.per_cis_value(kwargs.get('Max_SDU_P_To_C', Max_SDU_P_To_C))

    def per_cis_value(self, value):
        if isinstance(value, list):
            # List value given, so must match CIS_Count
            if len(value) != self.CIS_Count:
                raise ValueError('Field {} has wrong length {}, expected {}'.format(key, len(value), self.CIS_Count))
        else:
            # Single value given, so multiply by CIS_Count
            value = [value] * self.CIS_Count
        return value

    def get_cig_parameters_test(self):
        return (self.SDU_Interval_C_To_P, self.SDU_Interval_P_To_C, self.FT_C_To_P, self.FT_P_To_C, self.ISO_Interval,
                self.Worst_Case_SCA, self.Packing, self.Framing, self.CIS_Count, list(range(self.CIS_Count)), self.NSE,
                self.Max_SDU_C_To_P, self.Max_SDU_P_To_C, self.Max_PDU_C_To_P, self.Max_PDU_P_To_C, self.PHY_C_To_P,
                self.PHY_P_To_C, self.BN_C_To_P, self.BN_P_To_C)

    def get_cig_parameters(self):
        return (self.SDU_Interval_C_To_P, self.SDU_Interval_P_To_C, self.Worst_Case_SCA, self.Packing, self.Framing,
                self.Max_Transport_Latency_C_To_P, self.Max_Transport_Latency_P_To_C, self.CIS_Count,
                list(range(self.CIS_Count)), self.Max_SDU_C_To_P, self.Max_SDU_P_To_C, self.PHY_C_To_P, self.PHY_P_To_C,
                self.RTN_C_To_P, self.RTN_P_To_C)
