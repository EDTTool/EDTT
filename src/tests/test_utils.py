# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

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

global lowerRandomAddress, upperRandomAddress;

def verifyAndShowEvent(transport, idx, expectedEvent, trace, to=100):

    event = get_event(transport, idx, to);
    trace.trace(7, str(event));
    return event.event == expectedEvent;

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

def addAddressesToWhiteList(transport, idx, addresses, trace):

    _addresses = [ [ _.type, toNumber(_.address) ] for _ in addresses ];
    return preamble_specific_white_listed(transport, idx, _addresses, trace);

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

def calcMaxPacketTime(packetLength):
    #      (preamble + AA + header + packetLength + MIC + CRC) * us/byte
    return (1        + 4  + 2      + packetLength + 4   + 3  ) * 8

def calcMaxIsoSdu(Framing, BN, Max_PDU, ISO_Interval, SDU_Interval, Max_SDU_Supported):
    if Framing == 0:
        return calcUnframedMaxIsoSdu(BN, Max_PDU, ISO_Interval, SDU_Interval, Max_SDU_Supported)
    elif Framing == 1:
        raise RuntimeError("Framed Max SDU not supported")
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


def le_iso_data_write_nbytes(transport, idx, trace, conn_handle, nbytes, pkt_seq_num, to):
    pb_flag = 2
    ts_flag = 0
    iso_data_sdu = tuple([pkt_seq_num] * nbytes)
    tx_iso_data_load = struct.pack(f'<HH{nbytes}B', pkt_seq_num, nbytes, *iso_data_sdu)
    success = le_iso_data_write(transport, idx, conn_handle, pb_flag, ts_flag, tx_iso_data_load, to) == 0

    return success, iso_data_sdu


def le_iso_data_write_complete(transport, idx, trace, number_of_packets_written, to):
    success = True
    for _ in range(number_of_packets_written):
        success = le_iso_data_write_rsp(transport, idx, to) == 0 and success

    return success


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


def iso_receive_payload_pdu(transport, idx, trace, sdu_interval):
    success, handle, pbflags, rx_iso_sdu = le_iso_data_ready(transport, idx, sdu_interval * 2), -1, -1, []
    if success:
        # Receiver: RX SDU
        time, handle, pbflags, tsflag, rx_iso_data_load = le_iso_data_read(transport, idx, sdu_interval * 2)
        rx_iso_data_load = bytearray(rx_iso_data_load)

        # Unpack ISO_Data_Load
        rx_offset = 0
        # a. Get Time_Stamp if present
        if tsflag:
            fmt = '<I'
            (time_stamp,) = struct.unpack_from(fmt, rx_iso_data_load)
            rx_offset += struct.calcsize(fmt)

        # b. Get Packet_Sequence_Number, ISO_SDU_Length and Packet_Status_Flag
        fmt = '<HH'
        rx_packet_sequence_number, rx_iso_sdu_length = struct.unpack_from(fmt, rx_iso_data_load, rx_offset)
        rx_offset += struct.calcsize(fmt)
        rx_packet_status_flag = rx_iso_sdu_length >> 14
        rx_iso_sdu_length &= 0xfff  # 12 bits valid

        # c. Get ISO_SDU
        fmt = '<{ISO_SDU_Length}B'.format(ISO_SDU_Length=rx_iso_sdu_length)
        rx_iso_sdu = struct.unpack_from(fmt, rx_iso_data_load, rx_offset)

        # Valid data. The complete ISO_SDU was received correctly.
        success = (rx_packet_status_flag == 0x00)

    # TX and RX match
    return success, handle, pbflags, rx_iso_sdu


def iso_send_payload_pdu(transport, transmitter, receiver, trace, conn_handle, max_sdu_size, sdu_interval, pkt_seq_num):
    # Create a ISO_SDU of sdu_size length
    tx_iso_sdu = tuple([(pkt_seq_num + x) % 255 for x in range(max_sdu_size)])

    # Pack the ISO_Data_Load (no Time_Stamp) of an HCI ISO Data packet
    # <Packet_Sequence_Number, ISO_SDU_Length, ISO_SDU>
    fmt = '<HH{ISO_SDU_Length}B'.format(ISO_SDU_Length=len(tx_iso_sdu))
    tx_iso_data_load = struct.pack(fmt, pkt_seq_num, len(tx_iso_sdu), *tx_iso_sdu)

    # Transmitter: TX SDU
    PbFlag = 2
    TsFlag = 0
    le_iso_data_write(transport, transmitter, conn_handle, PbFlag, TsFlag, tx_iso_data_load, 100)
    success = verifyAndShowEvent(transport, transmitter, Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS, trace,
                                 sdu_interval * 2)

    s, handle, pbflags, rx_iso_sdu = iso_receive_payload_pdu(transport, receiver, trace, sdu_interval)

    # Transmitter: No RX
    success = not le_iso_data_ready(transport, transmitter, 100) and success

    # The ISO_Data_Load field contains a complete SDU.
    success = (pbflags == 2) and success

    # TX and RX match
    return (tx_iso_sdu == rx_iso_sdu) and success


def set_isochronous_channels_host_support(transport, device, trace, value):
    status = le_set_host_feature(transport, device, FeatureSupport.ISOCHRONOUS_CHANNELS, value, 100)
    return getCommandCompleteEvent(transport, device, trace) and (status == 0x00)


def establish_acl_connection(transport, central, peripheral, trace):
    advertiser, initiator = setPublicInitiator(transport, central, trace, Advertising.CONNECTABLE_UNDIRECTED)
    success = advertiser.enable()
    connected = initiator.connect()
    success = success and connected

    if not connected:
        success = advertiser.disable() and success

    return success, advertiser, initiator


def establish_cis_connection(transport, central, peripheral, trace, params, acl_conn_handle, setup_iso_data_path=True):
    SDU_Interval_C_To_P     = params.SDU_Interval_C_To_P
    SDU_Interval_P_To_C     = params.SDU_Interval_P_To_C
    ISO_Interval            = params.ISO_Interval
    CIS_Count               = params.CIS_Count
    Worst_Case_SCA          = params.Worst_Case_SCA
    Packing                 = params.Packing
    Framing                 = params.Framing
    NSE                     = params.NSE
    Max_PDU_C_To_P          = params.Max_PDU_C_To_P
    Max_PDU_P_To_C          = params.Max_PDU_P_To_C
    PHY_C_To_P              = params.PHY_C_To_P
    PHY_P_To_C              = params.PHY_P_To_C
    FT_C_To_P               = params.FT_C_To_P
    FT_P_To_C               = params.FT_P_To_C
    BN_C_To_P               = params.BN_C_To_P
    BN_P_To_C               = params.BN_P_To_C
    Max_SDU_C_To_P          = params.Max_SDU_C_To_P
    Max_SDU_P_To_C          = params.Max_SDU_P_To_C

    success = True

    # LT: Set CIG Parameters for Test
    status, cigId, cisCount, cisConnectionHandles = \
    le_set_cig_parameters_test(transport, central, 0,
                               SDU_Interval_C_To_P, SDU_Interval_P_To_C,
                               FT_C_To_P, FT_P_To_C,
                               ISO_Interval,
                               Worst_Case_SCA,
                               Packing, Framing,
                               CIS_Count,
                               list(range(CIS_Count)),
                               NSE,
                               Max_SDU_C_To_P, Max_SDU_P_To_C,
                               Max_PDU_C_To_P, Max_PDU_P_To_C,
                               PHY_C_To_P, PHY_P_To_C,
                               BN_C_To_P, BN_P_To_C, 100)
    success = getCommandCompleteEvent(transport, central, trace) and (status == 0x00) and success
    aclConnectionHandles = [acl_conn_handle] * CIS_Count

    # LT: Create CIS
    status = le_create_cis(transport, central, CIS_Count, cisConnectionHandles, aclConnectionHandles, 100)
    success = verifyAndShowEvent(transport, central, Events.BT_HCI_EVT_CMD_STATUS, trace) and (status == 0) and success

    for n in range(CIS_Count):
        # UT: Wait for HCI_EVT_LE_CIS_REQUEST
        s, event = verifyAndFetchMetaEvent(transport, peripheral, MetaEvents.BT_HCI_EVT_LE_CIS_REQUEST, trace)
        success = s and success
        aclConnectionHandle, cisConnectionHandle, cigId, cisId = event.decode()

        # UT: Accept CIS Request
        status = le_accept_cis_request(transport, peripheral, cisConnectionHandle, 100)
        success = verifyAndShowEvent(transport, peripheral, Events.BT_HCI_EVT_CMD_STATUS, trace) and (status == 0) and success

        # LT: Wait for HCI_EVT_LE_CIS_ESTABLISHED
        s, event = verifyAndFetchMetaEvent(transport, central, MetaEvents.BT_HCI_EVT_LE_CIS_ESTABLISHED, trace, 1000)
        success = s and (event.decode()[0] == 0x00) and success

        # UT: Wait for HCI_EVT_LE_CIS_ESTABLISHED
        s, event = verifyAndFetchMetaEvent(transport, peripheral, MetaEvents.BT_HCI_EVT_LE_CIS_ESTABLISHED, trace)
        success = s and (event.decode()[0] == 0x00) and success

    if not setup_iso_data_path:
        return success, cisConnectionHandles

    for cisConnectionHandle in cisConnectionHandles:
        if (Max_SDU_C_To_P != 0):
            # LT: Setup Data Path - Data_Path_Direction=0 (Input)  Data_Path_ID=1 (HCI) Codec_ID=0 Controller_Delay=0 Codec_Configuration_Length=0 Codec_Configuration=NULL
            status, _ = le_setup_iso_data_path(transport, central, cisConnectionHandle, 0, 0, [0, 0, 0, 0, 0], 0, 0, [], 100)
            success = getCommandCompleteEvent(transport, central, trace) and (status == 0x00) and success

            # UT: Setup Data Path - Data_Path_Direction=1 (Output) Data_Path_ID=1 (HCI) Codec_ID=0 Controller_Delay=0 Codec_Configuration_Length=0 Codec_Configuration=NULL
            status, _ = le_setup_iso_data_path(transport, peripheral, cisConnectionHandle, 1, 0, [0, 0, 0, 0, 0], 0, 0, [], 100)
            success = getCommandCompleteEvent(transport, peripheral, trace) and (status == 0x00) and success

        if (Max_SDU_P_To_C != 0):
            # LT: Setup Data Path - Data_Path_Direction=1 (Output)  Data_Path_ID=1 (HCI) Codec_ID=0 Controller_Delay=0 Codec_Configuration_Length=0 Codec_Configuration=NULL
            status, _ = le_setup_iso_data_path(transport, central, cisConnectionHandle, 1, 0, [0, 0, 0, 0, 0], 0, 0, [], 100)
            success = getCommandCompleteEvent(transport, central, trace) and (status == 0x00) and success

            # UT: Setup Data Path - Data_Path_Direction=0 (Input) Data_Path_ID=1 (HCI) Codec_ID=0 Controller_Delay=0 Codec_Configuration_Length=0 Codec_Configuration=NULL
            status, _ = le_setup_iso_data_path(transport, peripheral, cisConnectionHandle, 0, 0, [0, 0, 0, 0, 0], 0, 0, [], 100)
            success = getCommandCompleteEvent(transport, peripheral, trace) and (status == 0x00) and success

    return success, cisConnectionHandles


def state_connected_isochronous_stream_peripheral(transport, upperTester, lowerTester, trace, params,
                                                  setup_iso_data_path=True):
    # The Isochronous Channels (Host Support) FeatureSet bit is set.
    success = set_isochronous_channels_host_support(transport, upperTester, trace, 1)
    success = set_isochronous_channels_host_support(transport, lowerTester, trace, 1) and success

    ### ACL Connection Established. IUT (upperTester) is Peripheral. ###
    s, advertiser, initiator = establish_acl_connection(transport, lowerTester, upperTester, trace)
    success = s and success
    if not initiator:
        return success, None, []

    s, cisConnectionHandles = establish_cis_connection(transport, lowerTester, upperTester, trace, params,
                                                      initiator.handles[0], setup_iso_data_path)

    return s and success, initiator, cisConnectionHandles


"""
    [CIS Setup Response Procedure, Peripheral]
"""
def cis_setup_response_procedure_peripheral(transport, upperTester, lowerTester, trace, params):
    # Establish Initial Condition
    #
    # The Isochronous Channels (Host Support) FeatureSet bit is set.
    #
    # An ACL connection has been established between the IUT and Lower Tester with a valid Connection
    # Handle on the PHY specified in Table 4.115: Peripheral Test Case Direction Specific Configurations.
    #
    # The Lower Tester sets the parameters specified in Table 4.115: Peripheral Test Case Direction Specific
    # Configurations and Table 4.116: Peripheral Test Case Additional Configurations. Any otherwise
    # unspecified values are specified in Section 4.10.1.3 Default Values for Set CIG Parameters
    # Commands, except for default values for cis_offset_mn and cis_offset_mx. The CIS offset values are
    # specified in Section 4.10.1.2 Timing Requirements.
    #
    # The Lower Tester is configured as the Central.

    # TODO: Instead of steps 1-9, consider using state_connected_isochronous_stream_peripheral

    SDU_Interval_C_To_P     = params.SDU_Interval_C_To_P
    SDU_Interval_P_To_C     = params.SDU_Interval_P_To_C
    ISO_Interval            = params.ISO_Interval
    CIS_Count               = params.CIS_Count
    Worst_Case_SCA          = params.Worst_Case_SCA
    Packing                 = params.Packing
    Framing                 = params.Framing
    NSE                     = params.NSE
    Max_PDU_C_To_P          = params.Max_PDU_C_To_P
    Max_PDU_P_To_C          = params.Max_PDU_P_To_C
    PHY_C_To_P              = params.PHY_C_To_P
    PHY_P_To_C              = params.PHY_P_To_C
    FT_C_To_P               = params.FT_C_To_P
    FT_P_To_C               = params.FT_P_To_C
    BN_C_To_P               = params.BN_C_To_P
    BN_P_To_C               = params.BN_P_To_C
    Max_SDU_C_To_P          = params.Max_SDU_C_To_P
    Max_SDU_P_To_C          = params.Max_SDU_P_To_C

    success = True

    status = le_set_host_feature(transport, lowerTester, FeatureSupport.ISOCHRONOUS_CHANNELS, 1, 100)
    success = getCommandCompleteEvent(transport, lowerTester, trace) and (status == 0x00) and success

    status = le_set_host_feature(transport, upperTester, FeatureSupport.ISOCHRONOUS_CHANNELS, 1, 100)
    success = getCommandCompleteEvent(transport, upperTester, trace) and (status == 0x00) and success

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED)
    success = advertiser.enable() and success
    connected = initiator.connect()
    success = success and connected

    if not connected:
        success = advertiser.disable() and success
        return success

    # 1. The Upper Tester sends an HCI_LE_Set_Event_Mask command with all events enabled,
    #    including the HCI_LE_CIS_Request event. The IUT sends a successful
    #    HCI_Command_Complete in response.
    #
    # NOTE: This is already performed during the preamble step

    # 2. The Lower Tester sends an LL_CIS_REQ to the IUT with the contents specified in Table 4.115.
    # NOTE: CIG_ID is hardcoded to 0
    status, cigId, cisCount, cisConnectionHandles = \
    le_set_cig_parameters_test(transport, lowerTester, 0,
                               SDU_Interval_C_To_P, SDU_Interval_P_To_C,
                               FT_C_To_P, FT_P_To_C,
                               ISO_Interval,
                               Worst_Case_SCA,
                               Packing, Framing,
                               CIS_Count,
                               list(range(CIS_Count)),
                               NSE,
                               Max_SDU_C_To_P, Max_SDU_P_To_C,
                               Max_PDU_C_To_P, Max_PDU_P_To_C,
                               PHY_C_To_P, PHY_P_To_C,
                               BN_C_To_P, BN_P_To_C, 100)
    success = getCommandCompleteEvent(transport, lowerTester, trace) and (status == 0x00) and success
    aclConnectionHandles = [initiator.handles[0]] * CIS_Count

    status = le_create_cis(transport, lowerTester, 1, cisConnectionHandles, aclConnectionHandles, 100)
    success = verifyAndShowEvent(transport, lowerTester, Events.BT_HCI_EVT_CMD_STATUS, trace) and (status == 0) and success

    # 3. The Upper Tester receives an HCI_LE_CIS_Request event from the IUT and the parameters
    #    include CIS_Connection_Handle assigned by the IUT.
    s, event = verifyAndFetchMetaEvent(transport, upperTester, MetaEvents.BT_HCI_EVT_LE_CIS_REQUEST, trace)
    success = s and success
    aclConnectionHandle, cisConnectionHandle, cigId, cisId = event.decode()

    # 4. The Upper Tester sends an HCI_LE_Accept_CIS_Request command to the IUT, with the
    #    Connection_Handle field set to the value of the CIS_Connection_Handle received in step 3.
    status = le_accept_cis_request(transport, upperTester, cisConnectionHandle, 100)

    # 5. The Upper Tester expects the IUT to send a successful Command Status.
    success = verifyAndShowEvent(transport, upperTester, Events.BT_HCI_EVT_CMD_STATUS, trace) and (status == 0) and success

    # 6. The Lower Tester receives an LL_CIS_RSP PDU from the IUT. In the message, the
    #    CIS_Offset_Min field and the CIS_Offset_Max field are equal to or a subset of the values
    #    received in the LL_CIS_REQ sent in step 2.
    #
    # NOTE: Timing is not possible to validate/control
    s, event = verifyAndFetchMetaEvent(transport, lowerTester, MetaEvents.BT_HCI_EVT_LE_CIS_ESTABLISHED, trace, 1000)
    success = s and (event.decode()[0] == 0x00) and success

    # 7. The Lower Tester sends an LL_CIS_IND where the CIS_Offset is the time (ms) from the start of
    #    the ACL connection event in connEvent Count to the first CIS anchor point, the CIS_Sync_Delay
    #    is CIG_Sync_Delay minus the offset from the CIG reference point to the CIS anchor point in us,
    #    and the connEventCount is the CIS_Offset reference point.
    #
    # NOTE: Timing is not possible to validate/control

    # 8. The Upper Tester receives a successful HCI_LE_CIS_Established event from the IUT, after the
    #    first CIS packet sent by the LT. The Connection_Handle parameter is the
    #    CIS_Connection_Handle value provided in the HCI_LE_CIS_Request event.
    #
    # NOTE: Timing is not possible to validate/control
    s, event = verifyAndFetchMetaEvent(transport, upperTester, MetaEvents.BT_HCI_EVT_LE_CIS_ESTABLISHED, trace)
    success = s and (event.decode()[0] == 0x00) and success

    # 9. The Upper Tester sends an HCI_LE_Setup_ISO_Data_Path command to the IUT with the output
    #    path enabled and receives a successful HCI_Command_Complete in response.
    # UT: Setup Data Path - Data_Path_Direction=1 (Output) Data_Path_ID=0 (HCI) Codec_ID=0 Controller_Delay=0
    #     Codec_Configuration_Length=0 Codec_Configuration=NULL
    status, _ = le_setup_iso_data_path(transport, upperTester, cisConnectionHandle, 1, 0, [0, 0, 0, 0, 0], 0, 0, [],
                                       100)
    success = getCommandCompleteEvent(transport, upperTester, trace) and (status == 0x00) and success

    # LT: Setup Data Path - Data_Path_Direction=0 (Input) Data_Path_ID=0 (HCI) Codec_ID=0 Controller_Delay=0
    #     Codec_Configuration_Length=0 Codec_Configuration=NULL
    status, _ = le_setup_iso_data_path(transport, lowerTester, cisConnectionHandle, 0, 0, [0, 0, 0, 0, 0], 0, 0, [],
                                       100)
    success = getCommandCompleteEvent(transport, lowerTester, trace) and (status == 0x00) and success

    # 10. The Lower Tester sends data packets to the IUT.
    # 11. The Upper Tester IUT sends an ISO data packet to the Upper Tester.
    def lt_send_data_packet(pkt_seq_num):
        return iso_send_payload_pdu(transport, lowerTester, upperTester, trace, cisConnectionHandle, Max_SDU_C_To_P[0],
                                    SDU_Interval_C_To_P, pkt_seq_num)

    # 12. Perform either Alternative 12A or 12B depending on whether P_To_C Payload (PDU) in Table 4.146 is 0:
    #     Alternative 12A (P_To_C Payload (PDU) is not equal to 0):
    #       12A.1. TODO: The IUT sends an Ack to the Lower Tester.
    #     Alternative 12B (P_To_C Payload (PDU) is equal to 0):
    #       12B.1. TODO: The IUT sends a CIS Null PDU to the Lower Tester.

    # 13. Repeat steps 10-12 a total of 50 times.
    for j in range(50):
        success = lt_send_data_packet(j) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success

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
        ('Max_Transport_Latency_C_To_P',    None,          True,    40000),  # 40 ms
        ('Max_Transport_Latency_P_To_C',    None,          True,    40000),  # 40 ms
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

