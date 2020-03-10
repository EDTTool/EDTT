# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

from numpy import random;
import statistics;
import os;
import numpy;
import csv
from collections import defaultdict
from enum import IntEnum;
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
from components.test_spec import TestSpec;

global lowerIRK, upperIRK, lowerRandomAddress, upperRandomAddress;

class FragmentOperation(IntEnum):
    INTERMEDIATE_FRAGMENT = 0      # Intermediate fragment of fragmented extended advertising data
    FIRST_FRAGMENT        = 1      # First fragment of fragmented extended advertising data
    LAST_FRAGMENT         = 2      # Last fragment of fragmented extended advertising data
    COMPLETE_FRAGMENT     = 3      # Complete extended advertising data
    UNCHANGED_FRAGMENT    = 4      # Unchanged data (just update the Advertising DID)

class FragmentPreference(IntEnum):
    FRAGMENT_ALL_DATA = 0          # The Controller may fragment all Host advertising data
    FRAGMENT_MIN_DATA = 1          # The Controller should not fragment or should minimize fragmentation of Host advertising data

class PhysicalChannel(IntEnum):
    LE_1M    = 1
    LE_2M    = 2
    LE_CODED = 3

class PreferredPhysicalChannel(IntEnum):
    LE_1M    = 0                   # 0 ~ The Host prefers to use the LE 1M transmitter PHY (possibly among others)
    LE_2M    = 1                   # 1 ~ The Host prefers to use the LE 2M transmitter PHY (possibly among others)
    LE_CODED = 2                   # 2 ~ The Host prefers to use the LE Coded transmitter PHY (possibly among others)

"""
    ========================================================================================================================
    BEGIN                                      U T I L I T Y   P R O C E D U R E S
    ========================================================================================================================
"""
def verifyAndShowEvent(transport, idx, expectedEvent, trace):

    event = get_event(transport, idx, 100);
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

def verifyAndFetchMetaEvent(transport, idx, expectedEvent, trace):

    event = get_event(transport, idx, 100);
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

"""
    ========================================================================================================================
                                               U T I L I T Y   P R O C E D U R E S                                       END
    ========================================================================================================================
"""

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

"""
    LL/DDI/ADV/BV-01-C [Non-Connectable Advertising Packets on one channel]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_01_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 100, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);

    success = advertiser.enable();
    if success:
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = success and scanner.qualifyReports( 100, None, advertiser.advertiseData );

        success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-02-C [Undirected Advertising Packets on one channel]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_02_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 100, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);

    success = advertiser.enable();
    if success:
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = success and scanner.qualifyReports( 100, None, advertiser.advertiseData );

        success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-03-C [Non-Connectable Advertising Packets on all channels]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_03_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 50, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    success = True;
    adData = ADData();
    adData.encode( ADType.COMPLETE_LOCAL_NAME, 'THIS IS JUST A RANDOM NAME...' );

    for dataLength in [ 1, 0, 31, 0 ]:
        trace.trace(7, '-'*80);

        advertiser.advertiseData = [ ] if dataLength == 0 else [ 0x01 ] if dataLength == 1 else adData.asBytes();

        advertising = advertiser.enable();
        success = success and advertising;
        if advertising:
            success = scanner.enable() and success;
            scanner.monitor();
            success = scanner.disable() and success;
            success = scanner.qualifyReports( 50, None, list(advertiser.advertiseData) ) and success;
            success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-04-C [Undirected Advertising with Data on all channels ]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_04_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 50, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    success = True;
    adData = ADData();

    for dataLength in [ 1, 0, 31, 0 ]:
        trace.trace(7, '-'*80);

        advertiser.advertiseData = [ ] if dataLength == 0 else [ 0x01 ] if dataLength == 1 else \
                                   adData.encode( ADType.COMPLETE_LOCAL_NAME, 'THIS IS JUST A RANDOM NAME...' );

        advertising = advertiser.enable();
        success = success and advertising;
        if advertising:
            success = scanner.enable() and success;
            scanner.monitor();
            success = scanner.disable() and success;
            success = success and scanner.qualifyReports( 50, None, advertiser.advertiseData );

            success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-05-C [Undirected Connectable Advertising with Scan Request/Response ]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_05_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 30, 1);

    success = True;
    adData = ADData();

    for address in [ 0x456789ABCDEF, address_scramble_OUI( 0x456789ABCDEF ), address_exchange_OUI_LAP( 0x456789ABCDEF ) ]:
        for nameLength in [ 2, 31 ]:
            trace.trace(7, '-'*80);

            advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, '' ) if nameLength < 31 else \
                                      adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IUT IUT IUT IUT IUT IUT IUT IUT' );

            advertising = advertiser.enable();
            success = success and advertising;

            trace.trace(6, "\nUsing scanner address: %s SCAN_RSP data length: %d\n" % (formatAddress( toArray(address, 6), SimpleAddressType.PUBLIC), nameLength) );
            success = success and preamble_set_public_address( transport, lowerTester, address, trace );

            if advertising:
                success = scanner.enable() and success;
                scanner.monitor();
                success = scanner.disable() and success;
                success = success and scanner.qualifyReports( 1 );
                success = success and scanner.qualifyResponses( 1, advertiser.responseData );

                success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-06-C [Stop Advertising on Connection Request]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_06_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 0);

    success = True;
    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IUT' );

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, publicIdentityAddress(upperTester));

    for address in [ 0x456789ABCDEF, address_scramble_OUI( 0x456789ABCDEF ), address_scramble_LAP( 0x456789ABCDEF ), address_exchange_OUI_LAP( 0x456789ABCDEF ) ]:
        trace.trace(7, '-'*80);

        trace.trace(6, "\nUsing initiator address: %s\n" % formatAddress( toArray(address, 6), SimpleAddressType.PUBLIC));
        success = success and preamble_set_public_address( transport, lowerTester, address, trace );

        success = advertiser.enable() and success;
        connected = initiator.connect();
        success = success and connected;

        if connected:
            """
                If a connection was established Advertising should have seized...
            """
            scanner.expectedResponses = None;
            success = scanner.enable() and success;
            scanner.monitor();
            success = scanner.disable() and success;
            success = success and not scanner.qualifyReports( 1 );

            success = initiator.disconnect(0x3E) and success;
        else:
            success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-07-C [Scan Request/Response followed by Connection Request]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_07_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 1, 1);

    success = True;
    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IUT' );

    success = advertiser.enable();
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, publicIdentityAddress(upperTester));
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            If a connection was established Advertising should have seized...
        """
        scanner.expectedResponses = None;
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = success and not scanner.qualifyReports( 1 );

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-08-C [Advertiser Filtering Scan requests]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_08_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Place Public and static Random addresses of lowerTester in the White List for the Advertiser
    """
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddresses = [ Address( IdentityAddressType.PUBLIC, 0x456789ABCDEF ), Address( IdentityAddressType.RANDOM, 0x456789ABCDEF | 0xC00000000000 ) ];
    success = addAddressesToWhiteList(transport, upperTester, peerAddresses, trace);

    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IUT' );

    for filterPolicy in [ AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS, AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS ]:
        trace.trace(7, "\nTesting Advertising Filter Policy: %s" % filterPolicy.name);
        advertiser.filterPolicy = filterPolicy;

        for addressType, peerAddress in zip([ ExtendedAddressType.PUBLIC, ExtendedAddressType.RANDOM ], peerAddresses):

            advertiser.peerAddress = peerAddress;
            success = advertiser.enable() and success;

            for i in range(3):
                useAddressType = addressType;
                trace.trace(7, '-'*80);
                if   i == 0:
                    """
                        Correct Address Type - scrambled Address
                    """
                    if useAddressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using scrambled PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, address_scramble_LAP( 0x456789ABCDEF ), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using scrambled RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, address_scramble_LAP( 0x456789ABCDEF ) | 0xC00000000000, trace );
                elif i == 1:
                    """
                        Incorrect Address Type - correct Address
                    """
                    useAddressType = ExtendedAddressType.RANDOM if addressType == ExtendedAddressType.PUBLIC else ExtendedAddressType.PUBLIC;
                    if useAddressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using incorrect PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, toNumber(peerAddresses[1].address), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using incorrect RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, toNumber(peerAddresses[0].address), trace );
                else:
                    """
                        Correct Address Type - correct Address
                    """
                    if useAddressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, toNumber(peerAddresses[0].address), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, toNumber(peerAddresses[1].address), trace );

                scanner.ownAddress.type = useAddressType;
                scanner.expectedReports = 30;
                scanner.expectedResponses = 1 if (i == 2) else None;

                success = scanner.enable() and success;
                scanner.monitor();
                success = scanner.disable() and success;
                success = success and scanner.qualifyReports( scanner.expectedReports );
                if not scanner.expectedResponses is None:
                    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                else:
                    success = success and not scanner.qualifyResponses( 1 );

            success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-09-C [Advertiser Filtering Connection requests]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_09_c(transport, upperTester, lowerTester, trace):

    """
        Place Public address and Random static address of lowerTester in the White List for the Advertiser
    """
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddresses = [ Address( IdentityAddressType.PUBLIC, 0x456789ABCDEF ), Address( IdentityAddressType.RANDOM, 0x456789ABCDEF | 0xC00000000000 ) ];
    success = addAddressesToWhiteList(transport, upperTester, peerAddresses, trace);
    """
        Initialize Advertiser with Connectable Undirected advertising using a Public Address
    """
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddresses[0], AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);

    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IUT' );

    for filterPolicy in [ AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS, AdvertisingFilterPolicy.FILTER_CONNECTION_REQUESTS, AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS ]:
        trace.trace(7, "\nTesting Advertising Filter Policy: %s" % filterPolicy.name);
        advertiser.filterPolicy = filterPolicy;

        for addressType, peerAddress in zip([ ExtendedAddressType.PUBLIC, ExtendedAddressType.RANDOM ], peerAddresses):

            advertiser.peerAddress = peerAddress;

            for i in range(3):
                useAddressType = addressType;
                success = advertiser.enable() and success;
                trace.trace(7, '-'*80);
                if   i == 0:
                    """
                        Correct Address Type - scrambled Address
                    """
                    if useAddressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using scrambled PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, address_scramble_OUI( 0x456789ABCDEF ), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using scrambled RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, address_scramble_OUI( 0x456789ABCDEF ) | 0xC00000000000, trace );
                elif i == 1:
                    """
                        Incorrect Address Type - correct Address
                    """
                    useAddressType = ExtendedAddressType.RANDOM if addressType == ExtendedAddressType.PUBLIC else ExtendedAddressType.PUBLIC;
                    if useAddressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using incorrect PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, toNumber(peerAddresses[1].address), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using incorrect RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, toNumber(peerAddresses[0].address), trace );
                else:
                    """
                        Correct Address Type - correct Address
                    """
                    if useAddressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using correct PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, toNumber(peerAddresses[0].address), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using correct RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, toNumber(peerAddresses[1].address), trace );

                initiatorAddress = Address( useAddressType );
                initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, publicIdentityAddress(upperTester));

                for j in range(30):
                    connected = initiator.connect();
                    success = success and (connected if (i == 2 or filterPolicy == AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS) else not connected);

                    if connected:
                        """
                            If a connection was established - disconnect...
                        """
                        success = initiator.disconnect(0x3E) and success;
                        break;

                if not connected:
                    success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-11-C [High Duty Cycle Connectable Directed Advertising on all channels]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_11_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_HDC_DIRECTED, 30, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Place Public address of lowerTester in the White List
    """
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = publicIdentityAddress(lowerTester);
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    success = scanner.enable() and success;
    success = advertiser.enable() and success;
    scanner.monitor(True);
    success = advertiser.timeout() and success;
    success = scanner.disable() and success;

    success = success and scanner.qualifyReportTime( 30, 1280 );

    success = advertiser.enable() and success;

    initiator = Initiator(transport, lowerTester, upperTester, trace, ownAddress, publicIdentityAddress(upperTester));
    connected = initiator.connect();
    success = success and connected;
    if connected:
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-15-C [Discoverable Undirected Advertising on all channels]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_15_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 100, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Place Public address of lowerTester in the White List
    """
    peerAddress = publicIdentityAddress(lowerTester);
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    success = scanner.enable() and success;
    success = advertiser.enable() and success;
    scanner.monitor();
    success = advertiser.disable() and success;
    success = scanner.disable() and success;
    success = success and scanner.qualifyReports( 100, None, advertiser.advertiseData );

    return success;

"""
    LL/DDI/ADV/BV-16-C [Discoverable Undirected Advertising with Data on all channels]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_16_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 50);

    success = True;

    for i in range(4):
        advertiser.advertiseData = [ 0x01 ] if i == 0 else [ ] if i == 1 or i == 3 else [ 0x1E if _ == 0 else 0x00 for _ in range(31) ];

        success = scanner.enable() and success;
        success = advertiser.enable() and success;
        scanner.monitor();
        success = advertiser.disable()and success;
        success = scanner.disable() and success;
        success = success and scanner.qualifyReports( 50, None, advertiser.advertiseData );

    return success;

"""
    LL/DDI/ADV/BV-17-C [Discoverable Undirected Advertising with Scan Request/Response]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_17_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 30, 5);

    success = True;
    adData = ADData();

    for i in range(3):
        for j in range(2):
            advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, '' ) if j == 0 else \
                                      adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IUT IUT IUT IUT IUT IUT IUT I' );
            if   i == 1:
                success = success and preamble_set_public_address( transport, lowerTester, address_scramble_OUI( 0x456789ABCDEF ), trace );
            elif i == 2:
                success = success and preamble_set_public_address( transport, lowerTester, address_exchange_OUI_LAP( 0x456789ABCDEF ), trace );

            success = scanner.enable() and success;
            success = advertiser.enable() and success;
            scanner.monitor();
            success = advertiser.disable() and success;
            success = scanner.disable() and success;
            success = success and scanner.qualifyReports( 5 );
            success = success and scanner.qualifyResponses( 5, advertiser.responseData );

    return success;

"""
    LL/DDI/ADV/BV-18-C [Discoverable Undirected Advertiser Filtering Scan requests ]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_18_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 30, None, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Place Public address of lowerTester in the White List
    """
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = publicIdentityAddress(lowerTester);
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IUT' );

    success = advertiser.enable() and success;

    for i, addressType in enumerate([ ExtendedAddressType.PUBLIC, ExtendedAddressType.RANDOM, ExtendedAddressType.PUBLIC ]):
        if   i == 0:
            success = success and preamble_set_public_address( transport, lowerTester, address_scramble_LAP( 0x456789ABCDEF ), trace);
        elif i == 1:
            success = success and preamble_set_random_address( transport, lowerTester, 0x456789ABCDEF, trace );
        else:
            success = success and preamble_set_public_address( transport, lowerTester, 0x456789ABCDEF, trace );
            scanner.expectedResponses = 1;

        scanner.ownAddress = Address( addressType );

        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = success and scanner.qualifyReports( 1 if i > 1 else 30 );
        success = success and scanner.qualifyResponses( 1 if i > 1 else 0, advertiser.responseData if i > 1 else None );

    success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-19-C [Low Duty Cycle Directed Advertising on all channels]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen (NOTE: The automatic disconnect due to supervision timeout cannot be achieved)
"""
def ll_ddi_adv_bv_19_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED, 100, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Place Public address of lowerTester in the White List
    """
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = publicIdentityAddress(lowerTester);
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    success = advertiser.enable() and success;

    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = success and scanner.qualifyReports( 100 );

    initiator = Initiator(transport, lowerTester, upperTester, trace, ownAddress, publicIdentityAddress(upperTester));
    connected = initiator.connect();
    success = success and connected;

    if connected:
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-20-C [Advertising on the LE 1M PHY on all channels]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen (NOTE: The PHY channel used in advertising can only be verified by looking at the Air trace)
"""
def ll_ddi_adv_bv_20_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 100, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Place Public address of lowerTester in the White List
    """
    peerAddress = publicIdentityAddress(lowerTester);
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    AllPhys, TxPhys, RxPhys = 0, PreferredPhysicalChannel.LE_2M, PreferredPhysicalChannel.LE_2M;

    success = success and preamble_default_physical_channel(transport, upperTester, AllPhys, TxPhys, RxPhys, trace);

    success = scanner.enable() and success;
    success = advertiser.enable() and success;
    scanner.monitor();
    success = advertiser.disable() and success;
    success = scanner.disable() and success;
    success = success and scanner.qualifyReports( 100 );

    return success;

"""
    LL/DDI/ADV/BV-21-C [Non-Connectable Extended Legacy Advertising with Data on all channels]
"""
def ll_ddi_adv_bv_21_c(transport, upperTester, lowerTester, trace):

    Handle          = 0;
    Properties      = ExtAdvertiseType.LEGACY;
    PrimMinInterval = toArray(0x0020, 3); # Minimum Advertise Interval = 32 x 0.625 ms = 20.00 ms
    PrimMaxInterval = toArray(0x0022, 3); # Maximum Advertise Interval = 34 x 0.625 ms = 21.25 ms
    PrimChannelMap  = 0x07;  # Advertise on all three channels (#37, #38 and #39)
    OwnAddrType     = SimpleAddressType.PUBLIC;
    PeerAddrType, PeerAddress = random_address( 0x456789ABCDEF );
    FilterPolicy    = AdvertisingFilterPolicy.FILTER_NONE;
    TxPower         = 0;
    PrimAdvPhy      = PhysicalChannel.LE_1M; # Primary advertisement PHY is LE 1M
    SecAdvMaxSkip   = 0;     # AUX_ADV_IND shall be sent prior to the next advertising event
    SecAdvPhy       = PhysicalChannel.LE_2M;
    Sid             = 0;
    ScanReqNotifyEnable = 0; # Scan request notifications disabled

    success = preamble_ext_advertising_parameters_set(transport, upperTester, Handle, Properties, PrimMinInterval, PrimMaxInterval, \
                                                      PrimChannelMap, OwnAddrType, PeerAddrType, PeerAddress, FilterPolicy, TxPower, \
                                                      PrimAdvPhy, SecAdvMaxSkip, SecAdvPhy, Sid, ScanReqNotifyEnable, trace);

    for i in range(3):
        if i == 0:
            AdvData = [ 0x01 ];
        elif i == 1:
            AdvData = [ ];
        else:
            AdvData = [ 0x1F ] + [ 0 for _ in range(30) ];

        Operation      = FragmentOperation.COMPLETE_FRAGMENT;
        FragPreference = FragmentPreference.FRAGMENT_ALL_DATA;

        success = success and preamble_ext_advertising_data_set(transport, upperTester, Handle, Operation, FragPreference, advData, trace);

        scanInterval = 32; # Scan Interval = 32 x 0.625 ms = 20.0 ms
        scanWindow   = 32; # Scan Window   = 32 x 0.625 ms = 20.0 ms
        addrType     = SimpleAddressType.RANDOM;
        filterPolicy = ScanningFilterPolicy.FILTER_NONE;

        success = success and preamble_passive_scanning(transport, lowerTester, scanInterval, scanWindow, addrType, filterPolicy, trace);

        SHandle        = [ Handle ];
        SDuration      = [ 0 ];
        SMaxExtAdvEvts = [ 0 ];

        success = success and preamble_ext_advertise_enable(transport, upperTester, Advertise.ENABLE, SHandle, SDuration, SMaxExtAdvEvts, trace);

        deltas = [];
        reports = 0;
        while reports < 50:
            if has_event(transport, lowerTester, 100)[0]:
                event = get_event(transport, lowerTester, 100);
                # showEvent(event, eventData, trace);
                isReport = event.subEvent == MetaEvents.BT_HCI_EVT_LE_ADVERTISING_REPORT;
                if isReport:
                    eventType, data = event.decode()[0:3:2];
                    if eventType == AdvertisingReport.ADV_NONCONN_IND:
                        reports += 1;
                        reportData = data;
                        if reports > 1:
                            deltas += [event.time - prevTime];
                        prevTime = event.time;

        success = success and preamble_scan_enable(transport, lowerTester, Scan.DISABLE, ScanFilterDuplicate.DISABLE, trace);
        success = success and preamble_ext_advertise_enable(transport, upperTester, Advertise.DISABLE, SHandle, SDuration, SMaxExtAdvEvts, trace);
        success = success and (reportData == AdvData);

        trace.trace(7, "Mean distance between Advertise Events %d ms std. deviation %.1f ms" % (statistics.mean(deltas), statistics.pstdev(deltas)));

    return success;

"""
    LL/DDI/SCN/BV-01-C [Passive Scanning of Non-Connectable Advertising Packets]

    Last modified: 31-07-2019
    Reviewed and verified: 31-07-2019 Henrik Eriksen (NOTE: Advertise data not modified for each advertise event)
"""
def ll_ddi_scn_bv_01_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, upperTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 20);

    success = scanner.enable();

    for i, channel in enumerate([ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ]):
        if   i == 0:
            advertiser.ownAddress = publicIdentityAddress(lowerTester);
        elif i == 1:
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_LAP(0x456789ABCDEF) );
        elif i == 2:
            advertiser.ownAddress = Address( ExtendedAddressType.RANDOM, address_scramble_OUI(0x456789ABCDEF) );

        if advertiser.ownAddress.type == ExtendedAddressType.PUBLIC:
            success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
        else:
            success = success and preamble_set_random_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);

        advertiser.channels = channel;
        advertiser.advertiseData = [ i + 1 ];

        success = advertiser.enable() and success;
        scanner.monitor();
        success = advertiser.disable() and success;
        success = success and scanner.qualifyReports( 20, advertiser.ownAddress, advertiser.advertiseData );

    success = scanner.disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-02-C [Filtered Passive Scanning of Non-Connectable Advertising Packets]

    Last modified: 31-07-2019
    Reviewed and verified: 31-07-2019 Henrik Eriksen (NOTE: Advertise data not modified for each advertise event)
"""
def ll_ddi_scn_bv_02_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, upperTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 20, \
                                             AdvertisingFilterPolicy.FILTER_NONE, AdvertiseChannel.CHANNEL_37, ScanningFilterPolicy.FILTER_WHITE_LIST);
    """
        Place Public address of lowerTester in the White List
    """
    peerAddress = publicIdentityAddress(lowerTester);
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    success = scanner.enable() and success;

    for i in range(4):
        if   i == 0:
            advertiser.ownAddress = publicIdentityAddress(lowerTester);
        elif i == 1:
            advertiser.ownAddress = Address( ExtendedAddressType.RANDOM, 0x456789ABCDEF );
        elif i == 2:
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_LAP(0x456789ABCDEF) );
        elif i == 3:
            advertiser.ownAddress = Address( ExtendedAddressType.RANDOM, address_exchange_OUI_LAP(0x456789ABCDEF) );

        if advertiser.ownAddress.type == ExtendedAddressType.PUBLIC:
            success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
        else:
            success = success and preamble_set_random_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);

        advertiser.advertiseData = [ i + 1 ];

        success = advertiser.enable() and success;
        scanner.monitor();
        success = advertiser.disable() and success;
        if i == 0:
            success = success and scanner.qualifyReports( 20, advertiser.ownAddress, advertiser.advertiseData );
        else:
            success = success and scanner.qualifyReports( 0 );

    success = scanner.disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-03-C [Active Scanning of Connectable Undirected Advertising Packets]

    Last modified: 31-07-2019
    Reviewed and verified: 31-07-2019 Henrik Eriksen (NOTE: Advertise data not modified for each advertise event)
"""
def ll_ddi_scn_bv_03_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 20, 1);

    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IX' );
    success = scanner.enable();

    for channel in [ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ]:
        for i in range(4):
            if   i == 0:
                advertiser.ownAddress = publicIdentityAddress(lowerTester);
            elif i == 1:
                advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_OUI(0x456789ABCDEF) );
            elif i == 2:
                advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_LAP(0x456789ABCDEF) );
            else:
                advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_exchange_OUI_LAP(0x456789ABCDEF) );

            success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
            advertiser.channels = channel;
            advertiser.advertiseData = [ i + 1 ];

            success = advertiser.enable() and success;
            scanner.monitor();
            success = advertiser.disable() and success;
            success = success and scanner.qualifyReports( 20, advertiser.ownAddress, advertiser.advertiseData );
            success = success and scanner.qualifyResponses( 1, advertiser.responseData );

    success = scanner.disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-04-C [Filtered Active Scanning of Connectable Undirected Advertising Packets]

    Last modified: 31-07-2019
    Reviewed and verified: 31-07-2019 Henrik Eriksen (NOTE: Advertise data not modified for each advertise event)
"""
def ll_ddi_scn_bv_04_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 20, 1, \
                                            AdvertisingFilterPolicy.FILTER_NONE, AdvertiseChannel.ALL_CHANNELS, ScanningFilterPolicy.FILTER_WHITE_LIST);
    """
        Place Public address of lowerTester in the White List
    """
    peerAddress = publicIdentityAddress(lowerTester);
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IX' );
    success = scanner.enable();

    for channel in [ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ]:
        for i in range(3):
            if   i == 0:
                advertiser.ownAddress = publicIdentityAddress(lowerTester);
            elif i == 1:
                advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_LAP(0x456789ABCDEF) );
            else:
                advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_exchange_OUI_LAP(0x456789ABCDEF) );

            success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
            advertiser.channels = channel;
            advertiser.advertiseData = [ i + 1 ];

            success = advertiser.enable() and success;
            scanner.monitor();
            success = advertiser.disable() and success;
            if i == 0:
                success = success and scanner.qualifyReports( 20, advertiser.ownAddress, advertiser.advertiseData );
                success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            else:
                success = success and scanner.qualifyReports( 0 );
                success = success and scanner.qualifyResponses( 0 );

    success = scanner.disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-05-C [Scanning for different Advertiser types with and without Data]

    Last modified: 31-07-2019
    Reviewed and verified: 31-07-2019 Henrik Eriksen (NOTE: Advertise data not modified for each advertise event)
"""
def ll_ddi_scn_bv_05_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, upperTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 20, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.FLAGS, ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IX' );
    success = scanner.enable();

    for i, (channel, advertiseType, reports) in enumerate(zip( \
                             [ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ], \
                             [ Advertising.NON_CONNECTABLE_UNDIRECTED, Advertising.SCANNABLE_UNDIRECTED, Advertising.CONNECTABLE_HDC_DIRECTED ], \
                             [ 20, 30, 15 ] )):
        if   i == 0:
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_OUI(0x456789ABCDEF) );
        elif i == 1:
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_LAP(0x456789ABCDEF) );
        else:
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_exchange_OUI_LAP(0x456789ABCDEF) );

        success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
        advertiser.channels = channel;
        advertiser.advertiseType = advertiseType;
        advertiser.advertiseData = [ i + 1 ] if i < 2 else [ ];

        scanner.expectedReports = reports;
        scanner.reportType = matchingReportType(advertiseType);

        success = advertiser.enable() and success;
        scanner.monitor();
        success = advertiser.disable() and success;
        success = success and scanner.qualifyReports( reports, advertiser.ownAddress, advertiser.advertiseData );
        if i == 1:
            success = success and scanner.qualifyResponses( 1, advertiser.responseData );
        else:
            success = success and scanner.qualifyResponses( 0 );

    success = scanner.disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-10-C [Passive Scanning for Undirected Advertising Packets with Data]

    Last modified: 31-07-2019
    Reviewed and verified: 31-07-2019 Henrik Eriksen (NOTE: Advertise data not modified for each advertise event)
"""
def ll_ddi_scn_bv_10_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 20);

    success = True;

    for i, channel in enumerate([ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ]):
        if   i == 0:
            advertiser.ownAddress = publicIdentityAddress(lowerTester);
        elif i == 1:
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_LAP(0x456789ABCDEF) );
        elif i == 2:
            advertiser.ownAddress = Address( ExtendedAddressType.RANDOM, address_scramble_OUI(0x456789ABCDEF) );

        if (advertiser.ownAddress.type == ExtendedAddressType.PUBLIC):
            success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
        else:
            success = success and preamble_set_random_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);

        advertiser.channels = channel;
        advertiser.advertiseData = [ i + 1 ];

        success = advertiser.enable() and success;
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = advertiser.disable() and success;
        success = success and scanner.qualifyReports( 20, advertiser.ownAddress, advertiser.advertiseData );

    return success;

"""
    LL/DDI/SCN/BV-11-C [Passive Scanning for Directed Advertising Packets]

    Last modified: 31-07-2019
    Reviewed and verified: 31-07-2019 Henrik Eriksen (NOTE: Advertise data not modified for each advertise event)
"""
def ll_ddi_scn_bv_11_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED, 20, \
                                             AdvertisingFilterPolicy.FILTER_NONE, AdvertiseChannel.ALL_CHANNELS, ScanningFilterPolicy.FILTER_WHITE_LIST);
    """
        Place Public address of lowerTester in the White List
    """
    peerAddress = publicIdentityAddress(lowerTester);
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    for i, channel in enumerate([ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ]):
        if   i == 0:
            advertiser.ownAddress = publicIdentityAddress(lowerTester);
        elif i == 1:
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_LAP(0x456789ABCDEF) );
        elif i == 2:
            advertiser.ownAddress = Address( ExtendedAddressType.RANDOM, 0x456789ABCDEF );

        if (advertiser.ownAddress.type == ExtendedAddressType.PUBLIC):
            success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
        else:
            success = success and preamble_set_random_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);

        advertiser.channels = channel;

        success = advertiser.enable() and success;
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = advertiser.disable() and success;
        if i == 0:
            success = success and scanner.qualifyReports( 20, advertiser.ownAddress, advertiser.advertiseData );
        else:
            success = success and scanner.qualifyReports( 0 );

    return success;

"""
    LL/DDI/SCN/BV-12-C [Passive Scanning for Discoverable Undirected Advertising Packets]

    Last modified: 31-07-2019
    Reviewed and verified: 31-07-2019 Henrik Eriksen (NOTE: Advertise data not modified for each advertise event)
"""
def ll_ddi_scn_bv_12_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, upperTester, trace, Advertising.SCANNABLE_UNDIRECTED, 20, \
                                             AdvertisingFilterPolicy.FILTER_NONE, AdvertiseChannel.ALL_CHANNELS, ScanningFilterPolicy.FILTER_WHITE_LIST);
    """
        Place Public address of lowerTester in the White List
    """
    peerAddress = publicIdentityAddress(lowerTester);
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    for i, channel in enumerate([ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ]):
        if   i == 0:
            advertiser.ownAddress = publicIdentityAddress(lowerTester);
        elif i == 1:
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_LAP(0x456789ABCDEF) );
        elif i == 2:
            advertiser.ownAddress = Address( ExtendedAddressType.RANDOM, address_scramble_OUI(0x456789ABCDEF) );

        if (advertiser.ownAddress.type == ExtendedAddressType.PUBLIC):
            success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
        else:
            success = success and preamble_set_random_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);

        advertiser.channels = channel;
        advertiser.advertiseData = [ i + 1 ];

        success = advertiser.enable() and success;
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = advertiser.disable() and success;
        if i == 0:
            success = success and scanner.qualifyReports( 20, advertiser.ownAddress, advertiser.advertiseData );
        else:
            success = success and scanner.qualifyReports( 0 );

    return success;

"""
    LL/DDI/SCN/BV-13-C [Passive Scanning for Non-Connectable Advertising Packets using Network Privacy]

    Last modified: 31-07-2019
    Reviewed and verified: 31-07-2019 Henrik Eriksen
"""
def ll_ddi_scn_bv_13_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivatePassiveScanning(transport, upperTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 20);
    advertiser.channels = AdvertiseChannel.CHANNEL_37;
    """
        Add Public address of lowerTester to upperTesters Resolving List
        Add Public address of upperTester to lowerTesters Resolving List (to allow the Controller to generate a Private Resolvable Address)
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester) ) and success;
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    """
        Set Resolvable Private Address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = advertiser.disable() and success;
    """
        Verify that the Advertise address of the lowerTester has been correctly resolved
    """
    success = success and scanner.qualifyReports( 20, Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEF ) );

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-14-C [Passive Scanning for Connectable Directed Advertising Packets using Network Privacy]

    Last modified: 01-08-2019
    Reviewed and verified: 01-08-2019 Henrik Eriksen
"""
def ll_ddi_scn_bv_14_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivatePassiveScanning(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED, 20, \
                                                    ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                                                    AdvertisingFilterPolicy.FILTER_NONE, AdvertiseChannel.CHANNEL_37, ScanningFilterPolicy.FILTER_ID_DIRECTED);
    """
        Add Public address of lowerTester to upperTesters Resolving List
        Add Public address of upperTester to lowerTesters Resolving List (to allow the Controller to generate a Private Resolvable Address)
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester) ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = advertiser.disable() and success;
    success = success and scanner.qualifyDirectedReports( 20 );

    ok, address = readLocalResolvableAddress(transport, upperTester, publicIdentityAddress(upperTester), trace);
    trace.trace(8, "Address used by Scanner: %s" % str(Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, address )));

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-15-C [Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with no Local or Peer IRK]

    Last modified: 01-08-2019
    Reviewed and verified: 01-08-2019 Henrik Eriksen
"""
def ll_ddi_scn_bv_15_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivateActiveScanning(transport, upperTester, trace, Advertising.SCANNABLE_UNDIRECTED, 20, 1, \
                                                   ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_RANDOM);

    adData = ADData();
    advertiser.channels = AdvertiseChannel.CHANNEL_37;
    advertiser.advertiseData = [ 0x00 ];
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IX' );
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester) ) and success;
    success = RPAs[upperTester].add( Address( SimpleAddressType.RANDOM, lowerRandomAddress ) ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = advertiser.disable() and success;
    success = success and scanner.qualifyReports( 5, None, advertiser.advertiseData );
    success = success and scanner.qualifyResponses( 5, advertiser.responseData );

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-16-C [Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with Local and no Peer IRK]

    Last modified: 01-08-2019
    Reviewed and verified: 01-08-2019 Henrik Eriksen (Peer address type not set to 0x01 in entry added to RPA List)
"""
def ll_ddi_scn_bv_16_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivateActiveScanning(transport, upperTester, trace, Advertising.SCANNABLE_UNDIRECTED, 20, 1);

    adData = ADData();
    advertiser.channels = AdvertiseChannel.CHANNEL_37;
    advertiser.advertiseData = [ 0x00 ];
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IX' );

    lowerIdentityAddress = publicIdentityAddress(lowerTester);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPA = ResolvableAddresses( transport, upperTester, trace, upperIRK );
    success = RPA.clear();
    success = RPA.add( lowerIdentityAddress ) and success;
    """
        Set resolvable private address timeout in seconds ( two seconds )
    """
    success = RPA.timeout( 2 ) and success;
    success = RPA.enable() and success;

    success = advertiser.enable() and success;

    resolvableAddresses = [ 0, 0 ];

    for i in range(2):
        if i == 1:
            """
                Wait for Resolvable Private Address timeout to expire...
            """
            transport.wait(2000);
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = success and scanner.qualifyReports( 5, lowerIdentityAddress, advertiser.advertiseData );
        success = success and scanner.qualifyResponses( 5, advertiser.responseData );

        addressRead, resolvableAddresses[i] = readLocalResolvableAddress(transport, upperTester, lowerIdentityAddress, trace);
        trace.trace(6, "Local Resolvable Address: %s" % formatAddress(resolvableAddresses[i]));

    success = advertiser.disable() and success;
    success = success and toNumber(resolvableAddresses[0]) != toNumber(resolvableAddresses[1]);
    success = RPA.disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-17-C [Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with no Local and a Peer IRK]

    Last modified: 01-08-2019
    Reviewed and verified: 01-08-2019 Henrik Eriksen
"""
def ll_ddi_scn_bv_17_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivateActiveScanning(transport, upperTester, trace, Advertising.SCANNABLE_UNDIRECTED, 20, 1, \
                                                   ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_RANDOM);
    adData = ADData();
    advertiser.channels = AdvertiseChannel.CHANNEL_37;
    advertiser.advertiseData = [ 0x00 ];
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IX' );
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester) ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = advertiser.disable() and success;
    success = success and scanner.qualifyReports( 5, None, advertiser.advertiseData );
    success = success and scanner.qualifyResponses( 5, advertiser.responseData );

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-18-C [Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with both Local and Peer IRKs]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_ddi_scn_bv_18_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivateActiveScanning(transport, upperTester, trace, Advertising.SCANNABLE_UNDIRECTED, 20);

    adData = ADData();
    advertiser.channels = AdvertiseChannel.CHANNEL_37;
    advertiser.advertiseData = [ 0x00 ];
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IX' );
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[upperTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = advertiser.disable() and success;
    success = success and scanner.qualifyReports( 5, None, advertiser.advertiseData );
    success = success and scanner.qualifyResponses( 5, advertiser.responseData );

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-26-C [Passive Scanning for Non-Connectable Advertising Packets using Network Privacy]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_ddi_scn_bv_26_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivatePassiveScanning(transport, upperTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 20);
    advertiser.channels = AdvertiseChannel.CHANNEL_37;
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPA = ResolvableAddresses( transport, upperTester, trace );
    success = RPA.clear();
    success = RPA.add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPA.timeout( 60 ) and success;
    success = RPA.enable() and success;

    success = advertiser.enable() and success;
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = advertiser.disable() and success;
    success = success and scanner.qualifyReports( 0 );

    success = RPA.disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-28-C [Passive Scanning for Non-Connectable Advertising Packets using Device Privacy]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_ddi_scn_bv_28_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivatePassiveScanning(transport, upperTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 20);
    advertiser.channels = AdvertiseChannel.CHANNEL_37;

    """
        Add Public address of lowerTester to the Resolving List
    """
    lowerIdentityAddress = publicIdentityAddress(lowerTester);
    RPA = ResolvableAddresses( transport, upperTester, trace );
    success = RPA.clear();
    success = RPA.add( lowerIdentityAddress, lowerIRK ) and success;
    """
        Set Device Privacy Mode
    """
    success = setPrivacyMode(transport, upperTester, lowerIdentityAddress, PrivacyMode.DEVICE_PRIVACY, trace) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPA.timeout( 60 ) and success;
    success = RPA.enable() and success;

    success = advertiser.enable() and success;
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = advertiser.disable() and success;
    success = success and scanner.qualifyReports( 20, lowerIdentityAddress );

    success = RPA.disable() and success;

    return success;

"""
    LL/CON/ADV/BV-01-C [Accepting Connection Request]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_con_adv_bv_01_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 5);
    advertiser.channels = AdvertiseChannel.CHANNEL_37;

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, publicIdentityAddress(upperTester));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
    """
        If a connection was established Advertising should have seized...
    """
    if connected:
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = success and not scanner.qualifyReports( 1 );

        transport.wait(24820);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/ADV/BV-04-C [Accepting Connection Request after Directed Advertising]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_con_adv_bv_04_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_HDC_DIRECTED);

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, address_scramble_OUI(0x123456789ABC) ));
    """
        Verify that connection is not established to wrong Init Address
    """
    success = advertiser.enable();
    connected = initiator.connect();
    success = success and not connected;
    if connected:
        success = initiator.disconnect(0x3E) and success;
    else:
        """
            Need to stop connection attempt - otherwise following commands will fail with not allowed...
        """
        success = advertiser.disable() and success;
        success = initiator.cancelConnect() and success;
    """
        Verify that the upper Tester continues to Advertise for 1280 ms.
    """
    transport.wait(200);
    success = scanner.enable() and success;
    success = advertiser.enable() and success;
    scanner.monitor(True);
    success = advertiser.timeout() and success;
    success = scanner.disable() and success;
    success = success and not scanner.qualifyReportTime( 100, 1200 );

    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, publicIdentityAddress(upperTester));
    """
        Verify that connection is established to correct Init Address
    """
    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(26630);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/ADV/BV-09-C [Accepting Connection Request using Channel Selection Algorithm #2]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_con_adv_bv_09_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
       Enable the LE Channel Selection Algorithm Event
    """
    events = [0xFF, 0xFF, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];

    success = setLEEventMask(transport, upperTester, events, trace);

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Check for LE Channel Selection Algorithm Event in upper Tester...
        """
        success, handle, chSelAlgorithm = hasChannelSelectionAlgorithmEvent(transport, upperTester, trace);
        success = success and (chSelAlgorithm == 1);

        transport.wait(2600);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/ADV/BV-10-C [Accepting Connection Request after Directed Advertising using Channel Selection Algorithm #2]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_con_adv_bv_10_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED);
    """
        Enable the LE Channel Selection Algorithm Event
    """
    events = [0xFF, 0xFF, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];

    success = setLEEventMask(transport, upperTester, events, trace);

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Check for LE Channel Selection Algorithm Event in upper Tester...
        """
        success, handle, chSelAlgorithm = hasChannelSelectionAlgorithmEvent(transport, upperTester, trace);
        success = success and (chSelAlgorithm == 1);

        transport.wait(2600);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/INI/BV-01-C [Connection Initiation rejects Address change]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen (NOTE: Timing for connection events not verified - see Air Trace)
"""
def ll_con_ini_bv_01_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    for channel in [ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ]:

        advertiser.channels = channel;

        for address in [ 0x456789ABCDEF, address_scramble_OUI(0x456789ABCDEF), address_scramble_LAP(0x456789ABCDEF), address_exchange_OUI_LAP(0x456789ABCDEF) ]:

            trace.trace(7, "\nUsing channel %s and Lower Tester address %s\n" % (str(channel), formatAddress(toArray(address, 6))));

            success = preamble_set_public_address(transport, lowerTester, address, trace);
            initiator.peerAddress = Address( ExtendedAddressType.PUBLIC, address );

            success = initiator.preConnect() and success;

            randAddress = [ random.randint(0,255) for _ in range(6) ];
            randAddress[5] |= 0xC0;
            status = le_set_random_address(transport, upperTester, randAddress, 100);
            trace.trace(6, "LE Set Random Address Command returns status: 0x%02X" % status);
            success = success and (status == 0x0C);
            getCommandCompleteEvent(transport, upperTester, trace);

            success = advertiser.enable() and success;
            connected = initiator.postConnect();
            success = success and connected;

            if connected:
                transport.wait(2660);
                success = initiator.disconnect(0x3E) and success;
            else:
                success = advertiser.disable() and success;

    return success;

"""
    LL/CON/INI/BV-02-C [Connecting to Advertiser using Directed Advertising Packets]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen (NOTE: Timing for connection events not verified - see Air Trace)
"""
def ll_con_ini_bv_02_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(2660);
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/INI/BV-06-C [Filtered Connection to Advertiser using Undirected Advertising Packets]

    Last modified: 09-12-2019
    Reviewed and verified: 09-12-2019 Henrik Eriksen
"""
def ll_con_ini_bv_06_c(transport, upperTester, lowerTester, trace):
    global lowerRandomAddress, upperRandomAddress;

    success = True;
    for j in range(2):
        if j == 0:
            advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                       AdvertisingFilterPolicy.FILTER_NONE, AdvertiseChannel.CHANNEL_38, InitiatorFilterPolicy.FILTER_WHITE_LIST_ONLY);
        else:
            advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                        ExtendedAddressType.RANDOM, ExtendedAddressType.RANDOM, AdvertisingFilterPolicy.FILTER_NONE, \
                                                        AdvertiseChannel.CHANNEL_38, InitiatorFilterPolicy.FILTER_WHITE_LIST_ONLY);
        """
            Place Public|Random address of lowerTester in the White List
        """
        whiteListAddress = publicIdentityAddress(lowerTester) if j == 0 else randomIdentityAddress(lowerTester);

        success = addAddressesToWhiteList(transport, upperTester, [ whiteListAddress ], trace) and success;

        addresses = [ Address( ExtendedAddressType.RANDOM if whiteListAddress.type == SimpleAddressType.PUBLIC \
                                                          else ExtendedAddressType.PUBLIC, whiteListAddress.address ),
                      Address( ExtendedAddressType.PUBLIC if whiteListAddress.type == SimpleAddressType.PUBLIC \
                                                          else ExtendedAddressType.RANDOM, address_scramble_LAP(toNumber(whiteListAddress.address)) ),
                      whiteListAddress ];

        for i, advertiserAddress in enumerate( addresses ):

            advertiser.ownAddress = advertiserAddress;
            if advertiserAddress.type == ExtendedAddressType.RANDOM:
                success = preamble_set_random_address(transport, lowerTester, toNumber(advertiserAddress.address), trace) and success;
            else:
                success = preamble_set_public_address(transport, lowerTester, toNumber(advertiserAddress.address), trace) and success;

            success = advertiser.enable() and success;
            connected = initiator.connect();
            success = (connected if i == 2 else not connected) and success;

            if connected:
                success = initiator.disconnect(0x3E) and success;
            else:
                """
                    Need to stop connection attempt - otherwise following commands will fail with not allowed...
                """
                success = initiator.cancelConnect() and success;
                success = advertiser.disable() and success;

    return success;

"""
    LL/CON/INI/BV-07-C [Filtered Connection to Advertiser using Directed Advertising Packets]

    Last modified: 09-12-2019
    Reviewed and verified: 09-12-2019 Henrik Eriksen
"""
def ll_con_ini_bv_07_c(transport, upperTester, lowerTester, trace):
    global lowerRandomAddress, upperRandomAddress;

    success = True;
    for j in range(2):
        if j == 0:
            advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED, \
                                                       AdvertisingFilterPolicy.FILTER_NONE, AdvertiseChannel.CHANNEL_38, InitiatorFilterPolicy.FILTER_WHITE_LIST_ONLY);
        else:
            advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED, \
                                                        ExtendedAddressType.RANDOM, ExtendedAddressType.RANDOM, AdvertisingFilterPolicy.FILTER_NONE, \
                                                        AdvertiseChannel.CHANNEL_38, InitiatorFilterPolicy.FILTER_WHITE_LIST_ONLY);
        """
            Place Public|Random address of lowerTester in the White List
        """
        whiteListAddress = publicIdentityAddress(lowerTester) if j == 0 else randomIdentityAddress(lowerTester);

        success = addAddressesToWhiteList(transport, upperTester, [ whiteListAddress ], trace) and success;

        addresses = [ Address( ExtendedAddressType.RANDOM if whiteListAddress.type == SimpleAddressType.PUBLIC \
                                                          else ExtendedAddressType.PUBLIC, whiteListAddress.address ),
                      Address( ExtendedAddressType.PUBLIC if whiteListAddress.type == SimpleAddressType.PUBLIC \
                                                          else ExtendedAddressType.RANDOM, address_scramble_LAP(toNumber(whiteListAddress.address)) ),
                      whiteListAddress ];

        for i, advertiserAddress in enumerate( addresses ):

            advertiser.ownAddress = advertiserAddress;
            if advertiserAddress.type == ExtendedAddressType.RANDOM:
                success = preamble_set_random_address(transport, lowerTester, toNumber(advertiserAddress.address), trace) and success;
            else:
                success = preamble_set_public_address(transport, lowerTester, toNumber(advertiserAddress.address), trace) and success;

            success = advertiser.enable() and success;
            connected = initiator.connect();
            success = (connected if i == 2 else not connected) and success;

            if connected:
                success = initiator.disconnect(0x3E) and success;
            else:
                """
                    Need to stop connection attempt - otherwise following commands will fail with not allowed...
                """
                success = initiator.cancelConnect() and success;
                success = advertiser.disable() and success;

    return success;

"""
    LL/CON/INI/BV-08-C [Connecting to Connectable Undirected Advertiser with Network Privacy]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_con_ini_bv_08_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                ExtendedAddressType.PUBLIC, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_NONE, AdvertiseChannel.CHANNEL_38);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPA = ResolvableAddresses( transport, upperTester, trace, upperIRK );
    success = RPA.clear();
    success = RPA.add( publicIdentityAddress(lowerTester) ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPA.timeout( 60 ) and success;
    success = RPA.enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = connected and success;

    if connected:
        transport.wait(2660);
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    success = RPA.disable() and success;

    return success;

"""
    LL/CON/INI/BV-09-C [Connecting to Connectable Undirected Advertiser with Network Privacy thru Resolving List]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_con_ini_bv_09_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Add Public address of lowerTester to the Resolving List
    """
    randIRK = [ random.randint(0,255) for _ in range(16) ];

    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, randIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = initiator.preConnect() and success;
    success = advertiser.enable() and success;
    connected = initiator.postConnect();
    success = success and not connected;
    if connected:
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[lowerTester].clear() and success;
    RPAs[lowerTester].localIRK = lowerIRK[ : ];
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;

    success = advertiser.enable() and success;
    connected = initiator.postConnect();
    success = success and connected;

    if connected:
        transport.wait(2660);
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/CON/INI/BV-10-C [Connecting to Directed Advertiser with Network Privacy thru Resolving List]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_con_ini_bv_10_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED);
    """
        Add Public address of lowerTester to the Resolving List
    """
    randIRK = [ random.randint(0,255) for _ in range(16) ];

    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, randIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester) ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = initiator.preConnect() and success;
    success = advertiser.enable() and success;
    connected = initiator.postConnect();
    success = success and not connected;
    if connected:
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[lowerTester].clear() and success;
    RPAs[lowerTester].localIRK = lowerIRK[ : ];
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester) ) and success;

    success = advertiser.enable() and success;
    connected = initiator.postConnect();
    success = success and connected;

    if connected:
        transport.wait(2660);
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/CON/INI/BV-11-C [Connecting to Directed Advertiser using  wrong address with Network Privacy thru Resolving List ]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen (NOTE: Cannot confirm that the InitA used in ADV_DIRECT_INT is different from the one used in CONNECT_REQ - see Air trace)
"""
def ll_con_ini_bv_11_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED);
    """
        Add Public address of lowerTester to the Resolving List
    """
    randIRK = [ random.randint(0,255) for _ in range(16) ];

    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, randIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( three seconds and sixty seconds )
    """
    success = RPAs[upperTester].timeout( 3 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = initiator.preConnect() and success;
    success = advertiser.enable() and success;
    connected = initiator.postConnect();
    success = success and not connected;
    if connected:
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[lowerTester].clear() and success;
    RPAs[lowerTester].localIRK = lowerIRK[ : ];
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;

    success = advertiser.enable() and success;
    connected = initiator.postConnect();
    success = success and connected;

    if connected:
        transport.wait(2660);
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/CON/INI/BV-12-C [Connecting to Directed Advertiser using Identity address with Network Privacy thru Resolving List]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Cannot confirm that the InitA used in ADV_DIRECT_INT is different from the one used in CONNECT_REQ - see Air trace)
"""
def ll_con_ini_bv_12_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester) ) and success;
    """
        Set resolvable private address timeout in seconds ( three seconds and sixty seconds )
    """
    success = RPAs[upperTester].timeout( 3 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = initiator.preConnect() and success;
    success = advertiser.enable() and success;
    connected = initiator.postConnect();
    success = success and not connected;
    success = advertiser.disable() and success;

    success = RPAs[lowerTester].clear() and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;

    success = advertiser.enable() and success;
    connected = initiator.postConnect();
    success = success and connected;

    if connected:
        trace.trace(8, "Initiators local RPA: %s" % formatAddress(initiator.localRPA()));

        localRPAs = [ initiator.localRPA()[ : ], [ 0 for _ in range(6) ] ];

        transport.wait(2660);
        success = initiator.disconnect(0x3E) and success;

        success = advertiser.enable() and success;
        connected = initiator.connect();
        success = success and connected;

        if connected:
            trace.trace(8, "Initiators local RPA: %s" % formatAddress(initiator.localRPA()));

            localRPAs[1] = initiator.localRPA()[ : ];

            success = initiator.disconnect(0x3E) and success;
            """
                Verify that the Initiator Address (RPA) used in the CONNECT_IND has changed due to RPA timeout...
            """
            success = success and localRPAs[0] != localRPAs[1];
        else:
            success = advertiser.disable() and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/CON/INI/BV-16-C [Connecting to Advertiser with Channel Selection Algorithm #2]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing requirements cannot be verified - see Air trace)
"""
def ll_con_ini_bv_16_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
       Enable the LE Channel Selection Algorithm Event
    """
    events = [0xFF, 0xFF, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];
    success = setLEEventMask(transport, upperTester, events, trace);

    success = advertiser.enable() and success;
    initiator.checkPrematureDisconnect = False;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Check for LE Channel Selection Algorithm Event in upper Tester...
        """
        ok, handle, chSelAlgorithm = hasChannelSelectionAlgorithmEvent(transport, upperTester, trace);
        success = success and ok and (chSelAlgorithm == 1);

        transport.wait(2840);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/INI/BV-17-C [Connecting to Directed Advertiser with Channel Selection Algorithm #2]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing requirements cannot be verified - see Air trace)
"""
def ll_con_ini_bv_17_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED);
    """
       Enable the LE Channel Selection Algorithm Event
    """
    events = [0xFF, 0xFF, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];
    success = setLEEventMask(transport, upperTester, events, trace);

    success = advertiser.enable() and success;
    initiator.checkPrematureDisconnect = False;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Check for LE Channel Selection Algorithm Event in upper Tester...
        """
        ok, handle, chSelAlgorithm = hasChannelSelectionAlgorithmEvent(transport, upperTester, trace);
        success = success and ok and (chSelAlgorithm == 1);

        transport.wait(2840);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/INI/BV-18-C [Don't connect to Advertiser using Identity address with Network Privacy thru Resolving List]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_ini_bv_18_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, ExtendedAddressType.PUBLIC);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPA = ResolvableAddresses( transport, upperTester, trace, upperIRK );
    success = RPA.clear();
    success = RPA.add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPA.timeout( 60 ) and success;
    success = RPA.enable() and success;

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and not connected;

    if connected:
        success = initiator.disconnect(0x3E) and success;
    else:
        success = initiator.cancelConnect();
        success = advertiser.disable() and success;

    success = RPA.disable() and success;

    return success;

"""
    LL/CON/INI/BV-19-C [Don't connect to Directed Advertiser using Identity address with Network Privacy thru Resolving List]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_ini_bv_19_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPA = ResolvableAddresses( transport, upperTester, trace );
    success = RPA.clear();
    success = RPA.add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPA.timeout( 60 ) and success;
    success = RPA.enable() and success;

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and not connected;

    if connected:
        success = initiator.disconnect(0x3E) and success;
    else:
        success = initiator.cancelConnect();
        success = advertiser.disable() and success;

    success = RPA.disable() and success;

    return success;

"""
    LL/CON/INI/BV-20-C [Connect to Advertiser using Identity address with Device Privacy thru Resolving List]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_ini_bv_20_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;
    """
        Set Privacy Mode
    """
    success = setPrivacyMode(transport, upperTester, publicIdentityAddress(lowerTester), PrivacyMode.DEVICE_PRIVACY, trace) and success;

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(2660);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/CON/INI/BV-21-C [Connect to Directed Advertiser using Identity address with Device Privacy thru Resolving List]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_ini_bv_21_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPA = ResolvableAddresses( transport, upperTester, trace );
    success = RPA.clear();
    success = RPA.add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPA.timeout( 60 ) and success;
    success = RPA.enable() and success;
    """
        Set Privacy Mode
    """
    success = setPrivacyMode(transport, upperTester, publicIdentityAddress(lowerTester), PrivacyMode.DEVICE_PRIVACY, trace) and success;

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(2660);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    success = RPA.disable() and success;

    return success;

"""
    LL/CON/INI/BV-23-C [Network Privacy - Connection Establishment using whitelist and resolving list with address resolution disabled]

    Last modified: 17-12-2019
    Reviewed and verified: 17-12-2019 Henrik Eriksen
"""
def ll_con_ini_bv_23_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, ExtendedAddressType.PUBLIC,
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, AdvertisingFilterPolicy.FILTER_NONE,
                                                AdvertiseChannel.ALL_CHANNELS, InitiatorFilterPolicy.FILTER_WHITE_LIST_ONLY);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester) ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Add two more entries not equal to lower tester with different local IRK for each entry
    """
    extraAddressses = [ Address( SimpleAddressType.PUBLIC, address_scramble_OUI(toNumber(publicIdentityAddress(lowerTester).address)) ),
                        Address( SimpleAddressType.PUBLIC, address_scramble_LAP(toNumber(publicIdentityAddress(lowerTester).address)) ) ];
    RPAs[upperTester].localIRK = [ random.randint(0,255) for _ in range(16) ];
    success = RPAs[upperTester].add( extraAddressses[0] ) and success;
    RPAs[upperTester].localIRK = [ random.randint(0,255) for _ in range(16) ];
    success = RPAs[upperTester].add( extraAddressses[1] ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[lowerTester].enable() and success;
    """
        Add Lower tester identity address to plus two more to White List
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester), extraAddressses[0], extraAddressses[1] ], trace);

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(200);
        """
            Check that the InitA from the connect indication is a RPA
        """
        success = Address( None, initiator.localRPA() ).isResolvablePrivate() and success;
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/CON/INI/BV-24-C [Network Privacy - Connection Establishment using resolving list with address resolution disabled]

    Last modified: 17-12-2019
    Reviewed and verified: 17-12-2019 Henrik Eriksen
"""
def ll_con_ini_bv_24_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, ExtendedAddressType.PUBLIC);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPA = ResolvableAddresses( transport, upperTester, trace, upperIRK );
    success = RPA.clear();
    success = RPA.add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPA.timeout( 60 ) and success;
    success = RPA.disable() and success;

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and not connected;

    if connected:
        success = initiator.disconnect(0x3E) and success;
    else:
        success = initiator.cancelConnect();
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-04-C [Connection where Slave sends data to Master]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_04_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, upperTester, trace);

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        txData = [0 for _ in range(10)];
        pbFlags = 1;
        """
            Sending Data Packets with a fixed length less than 27...
        """
        for count in [ 100, 100, 1, 99 ]:
            pbFlags ^= 1;
            for j in range(count):

                dataSent = writeData(transport, upperTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, lowerTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);

        if maxPacketLength > 27:
            """
                Sending Data Packets with a random length greater than 27...
            """
            pbFlags, count = 0, 0;

            while count < 1000:
                txData = [0 for _ in range(random.randint(28, maxPacketLength))];

                dataSent = writeData(transport, upperTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);

                count += len(txData);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-05-C [Connection where Slave receives data from Master]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_05_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        txData = [0 for _ in range(10)];
        pbFlags = 1;
        """
            Sending Data Packets with a fixed length less than 27...
        """
        for count in [ 100, 100, 1, 99 ]:
            pbFlags ^= 1;
            trace.trace(7, '-'*77);
            for j in range(count):
                dataSent = writeData(transport, lowerTester, initiator.handles[0], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
        trace.trace(7, '-'*77);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-06-C [Connection where Slave sends and receives data to and from Master]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_06_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        txData = [0 for _ in range(10)];
        pbFlags = 0;
        """
            Sending Data Packets with a fixed length less than 27...
        """
        for j in range(100):
            """
                Upper Tester is sending Data...
            """
            pbFlags ^= 1;
            trace.trace(7, '-'*77);
            dataSent = writeData(transport, upperTester, initiator.handles[1], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readData(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
            """
                Lower Tester is sending Data...
            """
            pbFlags ^= 1;
            dataSent = writeData(transport, lowerTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readData(transport, upperTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
        trace.trace(7, '-'*77);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-10-C [Slave accepting Connection Parameter Update from Master]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing cannot be verified - see Air trace)
"""
def ll_con_sla_bv_10_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(100);

        for interval, timeout in zip([ 6, 3200, 6 ], [ 300, 3200, 300 ]):
            """
                Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            """
            success = initiator.update(interval, interval, initiator.latency, timeout) and success;
            """
                Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
            """
            success = initiator.acceptUpdate() and success;
            """
                Both lower and upper Tester should receive a LE Connection Update Complete Event...
            """
            success = initiator.updated() and success;

            transport.wait(int(4 * interval * 1.25));

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-11-C [Slave sending Termination to Master]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing cannot be verified - see Air trace)
"""
def ll_con_sla_bv_11_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and (initiator.reasons[0] == 0x16) and (initiator.reasons[1] == 0x13) and success;
        initiator.resetRoles();
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-12-C [Slave accepting Termination from Master]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing cannot be verified - see Air trace)
"""
def ll_con_sla_bv_12_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        success = initiator.disconnect(0x13) and (initiator.reasons[0] == 0x16) and (initiator.reasons[1] == 0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-13-C [Slave Terminating Connection on Supervision Timer]
"""
def ll_con_sla_bv_13_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    initiator.supervisionTimer = 3200;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(3200);
        hasEvent = has_event(transport, upperTester, 3200)[0];
        success = success and hasEvent;
        if hasEvent:
            event = get_event(transport, upperTester, 100);
            trace.trace(7, str(event));
        else:
            success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-14-C [Slave performs Feature Setup procedure]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_14_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Send LL_FEATURE_REQ to IUT
        """
        success = readRemoteFeatures(transport, lowerTester, initiator.handles[0], trace) and success;
        """
            Verify if lower tester received LE Read Remote Features Complete Event
        """
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, lowerTester, trace);
        success = hasFeatures and success;
        if hasFeatures:
            showFeatures(features, trace);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-19-C [Slave requests Version Exchange procedure]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_19_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        success = readRemoteVersionInformation(transport, upperTester, initiator.handles[1], trace) and success;

        hasVersion, handle, version, manufacturer, subVersion = hasReadRemoteVersionInformationCompleteEvent(transport, upperTester, trace);
        success = success and hasVersion;
        if hasVersion:
            trace.trace(8, "     version: 0x%02x" % version);
            trace.trace(8, " sub-version: 0x%04x" % subVersion);
            trace.trace(8, "manufacturer: 0x%04x" % manufacturer);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-20-C [Slave responds to Version Exchange procedure]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_20_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        success = readRemoteVersionInformation(transport, lowerTester, initiator.handles[1], trace) and success;

        hasVersion, handle, version, manufacturer, subVersion = hasReadRemoteVersionInformationCompleteEvent(transport, lowerTester, trace);
        success = success and hasVersion;
        if hasVersion:
            trace.trace(8, "     version: 0x%02x" % version);
            trace.trace(8, " sub-version: 0x%04x" % subVersion);
            trace.trace(8, "manufacturer: 0x%04x" % manufacturer);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-22-C [Slave requests Feature Exchange procedure]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_22_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Upper Tester sends an HCI_LE_Read_Local_Supported_Features command...
        """
        success = readLocalFeatures(transport, upperTester, trace)[0] and success;
        """
            Upper Tester sends an HCI_LE_Read_Remote_Features command...
        """
        success = readRemoteFeatures(transport, upperTester, initiator.handles[1], trace) and success;
        """
            Upper tester expects LE Read Remote Features Complete event...
        """
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, upperTester, trace);
        success = hasFeatures and success;
        if hasFeatures:
            showFeatures(features, trace);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-24-C [Slave requests Connection Parameters – Master Accepts]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing not verified - see Air trace)
"""
def ll_con_sla_bv_24_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        initiator.switchRoles();
        """
            The test consists of 3 cases for specific connection intervals and supervision timeouts
        """
        for interval, timeout in zip([ 6, 3200, 6 ], [ 300, 3200, 300 ]):
            """
                Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            """
            success = initiator.update(interval, interval, initiator.latency, timeout) and success;
            """
                Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
            """
            success = initiator.acceptUpdate() and success;
            """
                Both lower and upper Tester should receive a LE Connection Update Complete Event...
            """
            success = initiator.updated() and success;

            transport.wait(int(4 * interval * 1.25));

        initiator.resetRoles();
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-25-C [Slave requests Connection Parameters – Master Rejects]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing not verified - see Air trace)
"""
def ll_con_sla_bv_25_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        initiator.switchRoles();

        interval, timeout = 6, 300;
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECTEXT_IND...
        """
        success = initiator.rejectUpdate(0x0C) and success;
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event... if request was accepted
        """
        success = not initiator.updated() and initiator.status == 0x0C and success;

        transport.wait(int(4 * interval * 1.25));

        initiator.resetRoles();
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-26-C [Slave requests Connection Parameters – same procedure collision]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing not verified - see Air trace)
"""
def ll_con_sla_bv_26_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        initiator.switchRoles();

        interval, timeout, errCode = 6, 300, 0x23;
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECTEXT_IND...
            NOTE: Not according to test specification, LL_CONNECTION_PARAM_REQ should be issued prior to LL_REJECTEXT_IND,
                  but Zephyr is preventing us from sending the the LL_CONNECTION_PARAM_REQ first, returning COMMAND DISALLOWED
        """
        success = initiator.rejectUpdate(errCode) and success;

        initiator.resetRoles();
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        updInitiatorRequest = initiator.update(interval, interval, initiator.latency, timeout);
        updPeerRequest = initiator.updPeerRequest;
        success = success and updInitiatorRequest and updPeerRequest;

        initiator.switchRoles();
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event... if request was accepted
        """
        updated = initiator.updated();
        success = success and not updated and (initiator.status == errCode);

        initiator.resetRoles();
        """
            Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
        """
        initiator.updInitiatorRequest, initiator.updPeerRequest = updInitiatorRequest, updPeerRequest;
        success = initiator.acceptUpdate() and success;
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event...
        """
        success = initiator.updated() and success;

        transport.wait(int(4 * interval * 1.25));

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-27-C [Slave requests Connection Parameters – channel map update procedure collision]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing not verified - see Air trace)
"""
def ll_con_sla_bv_27_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        initiator.switchRoles();

        interval, timeout, errCode, channelMap = 6, 300, 0x2A, 0x1555555555;
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Request an update of used channels - sends an LL_CHANNEL_MAP_IND...
        """
        success = channelMapUpdate(transport, lowerTester, channelMap, trace) and success;
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECTEXT_IND...
        """
        success = initiator.rejectUpdate(errCode) and success;
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event... if request was accepted
        """
        success = not initiator.updated() and (initiator.status == errCode) and success;

        initiator.resetRoles();

        transport.wait(int(4 * interval * 1.25));

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-29-C [Slave responds to Connection Parameters – Master no Preferred Periodicity]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing not verified - see Air trace)
"""
def ll_con_sla_bv_29_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        for interval, timeout in zip([6, 3200, 6], [300, 3200, 200]):
            """
                Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            """
            success = initiator.update(interval, interval, initiator.latency, timeout) and success;
            """
                Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
            """
            success = initiator.acceptUpdate() and success;
            """
                Both lower and upper Tester should receive a LE Connection Update Complete Event... if request was accepted
            """
            success = initiator.updated() and success;

            transport.wait(int(4 * interval * 1.25));

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-33-C [Slave responds to Connection Parameters request – event masked]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_33_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
    """
        Mask LE Remote Connection Parameter Request Event
    """
    events = [0x1F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    success = setLEEventMask(transport, upperTester, events, trace) and success;

    if connected:
        interval, timeout, errCode = 6, 300, 0x1A;
        """
            Send LL_CONNECTION_PARAM_REQ to IUT...
        """
        success = initiator.update(interval, interval, initiator.latency, timeout) and not initiator.updPeerRequest and success;
        """
            Verify that lower tester receives a LL_REJECT_EXT_IND... unfortunately we cannot verify that (but it appears in the Air trace)!
        """
        success = initiator.updated() and success;

        transport.wait(int(4 * interval * 1.25))

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-34-C [Slave responds to Connection Parameters request – Host rejects]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_34_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        interval, timeout, errCode = 6, 300, 0x3B;
        """
            Send LL_CONNECTION_PARAM_REQ to IUT...
        """
        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECT_EXT_IND...
        """
        success = initiator.rejectUpdate(errCode) and success;
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event... if request was accepted
        """
        success = not initiator.updated() and (initiator.status == errCode) and success;

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-40-C [Slave requests PHY Update procedure]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_40_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    columns = defaultdict(list); # each value in each column is appended to a list

    with open('src/tests/params_con_sla_bv_40.csv') as f:
        reader = csv.reader(f);
        next(reader);
        for row in reader:
            for (i,v) in enumerate(row):
                columns[i].append(int(v, 16));

    all_phys, tx_phys, rx_phys = columns[1], columns[2], columns[3];

    if connected:
        initiator.switchRoles();

        for i in range(0, len(columns[0])):
            if (tx_phys[i] == 0) or (tx_phys[i] > 3) or (rx_phys[i] == 0) or (rx_phys[i] > 3):
                continue

            trace.trace(7, "Execute PHY Update with the following parameters:\tALL_PHYS: %s\tTX: %s\tRX: %s" % (str(all_phys[i]), str(tx_phys[i]), str(rx_phys[i])));

            success = initiator.updatePhys(all_phys[i], tx_phys[i], rx_phys[i], 0) and success;

            trace.trace(4, "Updated PHYs:\tTX: %s\tRX: %s\n" % (str(initiator.txPhys), str(initiator.rxPhys)))

        transport.wait(int(4 * initiator.intervalMin * 1.25))

        initiator.resetRoles()

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-42-C [Slave responds to PHY Update procedure]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_42_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        initiator.switchRoles();

        success = initiator.updatePhys( 3, 0, 0, 0 ) and success;

        initiator.resetRoles();

        tabel = list(zip( [2, 1, 2, 1, 3, 3, 1, 2, 3], [2, 2, 1, 1, 2, 1, 3, 3, 3], [2, 1, 2, 1, 2, 2, 1, 2, 2], [2, 2, 1, 1, 2, 1, 2, 2, 2] ));

        for i in range(2):
            for txPhys, rxPhys, expTxPhys, expRxPhys in tabel:
                success = initiator.updatePhys(0, txPhys, rxPhys, 0) and success;
                success = success and (initiator.txPhys == expTxPhys) and (initiator.rxPhys == expRxPhys);
            random.shuffle(tabel)

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-77-C [Slave Packet Data Length Update – Pesponding to Packet Data Length Update Procedure; LE 1M PHY]

    Last modified: 09-08-2019
    Reviewed and verified: 09-08-2019 Henrik Eriksen (Note: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.)
"""
def ll_con_sla_bv_77_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);
    maxPacketTime, cmaxTxOctets, cmaxTxTime = 2120 * maxPacketLength // 251, 27, 328;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Feature exchange as specified in LL.TS.5.1.1, chapter 4.1.5
        """
        success = readRemoteFeatures(transport, lowerTester, initiator.handles[1], trace) and success;
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, lowerTester, trace);
        showLEFeatures(features, trace);

        """
            Exchange data...
        """
        lenValues  = list(range(28, maxPacketLength-1)) + list(range(maxPacketLength+1, 250));
        timeValues = list(range(329, maxPacketTime-1)) + list(range(maxPacketTime+1, 2119));

        for txOctets, txTime in zip( [ 27, 251, maxPacketLength, 27, 27, 27, 251, 251, 251, maxPacketLength, maxPacketLength, maxPacketLength, \
                                       random.choice(lenValues), random.choice(lenValues), random.choice(lenValues), random.choice(lenValues) ], \
                                     [ 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, \
                                       random.choice(timeValues), random.choice(timeValues), random.choice(timeValues), random.choice(timeValues) ] ):

            success = setDataLength(transport, upperTester, initiator.handles[1], txOctets, txTime, trace) and success;

            changed = not ((cmaxTxOctets == min(txOctets, maxPacketLength)) and (cmaxTxTime == min(txTime, 328)));

            if changed:
                gotEvent, handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = hasDataLengthChangedEvent(transport, upperTester, trace);
                success = success and gotEvent;
                gotEvent = hasDataLengthChangedEvent(transport, lowerTester, trace)[0];
                success = success and gotEvent;

            pbFlags = 0;
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)];
            dataSent = writeData(transport, lowerTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readDataFragments(transport, upperTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
            """
                Lower Tester is sending Data...
            """
            txData = [_ for _ in range(27)];
            for i in range(20):
                dataSent = writeData(transport, upperTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, lowerTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-78-C [Slave requests Packet Data Length Update procedure; LE 1M PHY]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.)
"""
def ll_con_sla_bv_78_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);
    cmaxTxOctets, cmaxTxTime, maxPacketTime = 27, 328, int(2120 * maxPacketLength / 251);

    trace.trace(8, "Max supported packet length: %d octets. Max supported transmit time: %d micro seconds" % (maxPacketLength, maxPacketTime));

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Feature exchange as specified in LL.TS.5.1.1, chapter 4.1.5
        """
        success = readRemoteFeatures(transport, lowerTester, initiator.handles[1], trace) and success;
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, lowerTester, trace);
        showLEFeatures(features, trace);

        for txOctets, txTime in zip([ maxPacketLength, 27, 251, maxPacketLength, 27, 251, maxPacketLength, 27, 251, maxPacketLength, 27, 251 ], \
                                    [ maxPacketTime, maxPacketTime, maxPacketTime, 328, 328, 328, 2120, 2120, 2120, 2120, 2120, 2120 ]):

            success = setDataLength(transport, upperTester, initiator.handles[0], txOctets, txTime, trace) and success;

            changed = not ((cmaxTxOctets == min(txOctets, maxPacketLength)) and (cmaxTxTime == min(txTime, 328)));

            if changed:
                gotEvent, handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = hasDataLengthChangedEvent(transport, upperTester, trace);
                if not gotEvent:
                    trace.trace(7, "Missing Data Length Changed event from upperTester!");
                success = success and gotEvent;
                gotEvent = hasDataLengthChangedEvent(transport, lowerTester, trace)[0];
                if not gotEvent:
                    trace.trace(7, "Missing Data Length Changed event from lowerTester!");
                success = success and gotEvent;

            pbFlags = 0;
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)];
            dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData));
            """
                Lower Tester is sending Data...
            """
            txData = [_ for _ in range(27)];
            for i in range(20):
                dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData));
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-80-C [Slave Packet Data Length Update – Pesponding to Packet Data Length Update Procedure; LE 2M PHY]

    Last modified: 09-08-2019
    Reviewed and verified: 09-08-2019 Henrik Eriksen (Note: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.)
"""
def ll_con_sla_bv_80_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);
    maxPacketTime, cmaxTxOctets, cmaxTxTime = 2120 * maxPacketLength // 251, 27, 328;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Feature exchange as specified in LL.TS.5.1.1, chapter 4.1.5
        """
        success = readRemoteFeatures(transport, lowerTester, initiator.handles[1], trace) and success;
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, lowerTester, trace);
        showLEFeatures(features, trace);

        """
            Switch to LE 2M PHY channel...
        """
        allPhys, txPhys, rxPhys, optionPhys = 0, 2, 2, 0;

        success = initiator.updatePhys(allPhys, txPhys, rxPhys, optionPhys) and success;
        success = (initiator.txPhys == txPhys) and (initiator.rxPhys == rxPhys) and success
        """
            Exchange data...
        """
        lenValues  = list(range(28, maxPacketLength-1)) + list(range(maxPacketLength+1, 250));
        timeValues = list(range(329, maxPacketTime-1)) + list(range(maxPacketTime+1, 2119));

        for txOctets, txTime in zip( [ 27, 251, maxPacketLength, 27, 27, 27, 251, 251, 251, maxPacketLength, maxPacketLength, maxPacketLength, \
                                       random.choice(lenValues), random.choice(lenValues), random.choice(lenValues), random.choice(lenValues) ], \
                                     [ 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, \
                                       random.choice(timeValues), random.choice(timeValues), random.choice(timeValues), random.choice(timeValues) ] ):

            success = setDataLength(transport, upperTester, initiator.handles[1], txOctets, txTime, trace) and success;

            changed = not ((cmaxTxOctets == min(txOctets, maxPacketLength)) and (cmaxTxTime == min(txTime, 328)));

            if changed:
                gotEvent, handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = hasDataLengthChangedEvent(transport, upperTester, trace);
                success = success and gotEvent;
                gotEvent = hasDataLengthChangedEvent(transport, lowerTester, trace)[0];
                success = success and gotEvent;

            pbFlags = 0;
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)];
            dataSent = writeData(transport, lowerTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readDataFragments(transport, upperTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
            """
                Lower Tester is sending Data...
            """
            txData = [_ for _ in range(27)];
            for i in range(20):
                dataSent = writeData(transport, upperTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, lowerTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-81-C [Slave requests Packet Data Length Update procedure; LE 2M PHY]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.)
"""
def ll_con_sla_bv_81_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);
    cmaxTxOctets, cmaxTxTime, maxPacketTime = 27, 328, int(2120 * maxPacketLength / 251);

    trace.trace(8, "Max supported packet length: %d octets. Max supported transmit time: %d micro seconds" % (maxPacketLength, maxPacketTime));

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Feature exchange as specified in LL.TS.5.1.1, chapter 4.1.5
        """
        success = readRemoteFeatures(transport, lowerTester, initiator.handles[1], trace) and success;
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, lowerTester, trace);
        showLEFeatures(features, trace);

        initiator.switchRoles();
        """
            Switch to the 2M PHY channel
        """
        txPhys, rxPhys, allPhys, optionPhys = 2, 2, 0, 0;
        success = initiator.updatePhys(allPhys, txPhys, rxPhys, optionPhys) and success;
        success = success and (initiator.txPhys == txPhys) and (initiator.rxPhys == rxPhys);

        initiator.resetRoles();

        for txOctets, txTime in zip([ maxPacketLength, 27, 251, maxPacketLength, 27, 251, maxPacketLength, 27, 251, maxPacketLength, 27, 251 ], \
                                    [ maxPacketTime, maxPacketTime, maxPacketTime, 328, 328, 328, 2120, 2120, 2120, 2120, 2120, 2120 ]):

            success = setDataLength(transport, upperTester, initiator.handles[0], txOctets, txTime, trace) and success;

            changed = not ((cmaxTxOctets == min(txOctets, maxPacketLength)) and (cmaxTxTime == min(txTime, 328)));

            if changed:
                gotEvent, handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = hasDataLengthChangedEvent(transport, upperTester, trace);
                success = success and gotEvent;
                gotEvent = hasDataLengthChangedEvent(transport, lowerTester, trace)[0];
                success = success and gotEvent;

            pbFlags = 0;
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)];
            dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData));
            """
                Lower Tester is sending Data...
            """
            txData = [_ for _ in range(27)];
            for i in range(20):
                dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData));
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BI-08-C [Slave responds to Connection Parameters request – Illegal Parameters]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_sla_bi_08_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        interval, errCode = 4, 0x1E;
        """
            Send LL_CONNECTION_PARAM_REQ to IUT...
        """
        success = initiator.update(interval, interval, initiator.latency, 300) and success;
        """
            Verify that lower tester receives a CONNECTION UPDATE COMPLETE Event...
        """
        success = not initiator.updated() and (initiator.status == errCode) and success;

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-03-C [Master sending Data packets to Slave]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_03_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
       Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        txData = [0 for _ in range(10)];
        pbFlags = 1;
        """
            Sending Data Packets with a fixed length less than 27...
        """
        for count in [ 100, 100, 1, 99 ]:
            pbFlags ^= 1;
            for j in range(count):
                dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, lowerTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);

        if maxPacketLength > 27:
            """
                Sending Data Packets with a random length greater than 27...
            """
            pbFlags, count = 0, 0;

            while count < 1000:
                txData = [0 for _ in range(random.randint(28, maxPacketLength))];

                dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
                success = success and dataSent;
                count += len(txData);
                if dataSent:
                    dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
                else:
                    break;

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-04-C [Master receiving Data packets from Slave]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_04_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        txData = [0 for _ in range(10)];
        pbFlags = 1;
        """
            Sending Data Packets with a fixed length less than 27...
        """
        for count in [ 100, 100, 1, 99 ]:
            pbFlags ^= 1;
            trace.trace(7, '-'*77);
            for j in range(count):
                dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
        trace.trace(7, '-'*77);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-05-C [Master sending and receiving Data packets to and form Slave]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_05_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        pbFlags = 0;
        """
            Sending Data Packets with a fixed length less than 27...
        """
        for j in range(100):
            """
                Upper Tester is sending Data...
            """
            trace.trace(7, '-'*77);
            txData = [0x00 for _ in range(10)];
            dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readData(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
            """
                Lower Tester is sending Data...
            """
            txData = [0xFF for _ in range(10)];
            dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readData(transport, upperTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);

            if j == 0:
                pbFlags = 1;
        trace.trace(7, '-'*77);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-07-C [Master requests Connection Parameter Update]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: connection event where change take place cannot be verified - see Air trace)
"""
def ll_con_mas_bv_07_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        interval, timeout = 64, 3200;
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
        """
        success = initiator.acceptUpdate() and success;
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event...
        """
        success = initiator.updated() and success;
        """
            Wait for change to take place...
        """
        transport.wait(int(4 * interval * 1.25));

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success

"""
    LL/CON/MAS/BV-08-C [Master Terminating Connection]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Not verified that IUT stops sending empty data packets - see Air trace)
"""
def ll_con_mas_bv_08_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        success = initiator.disconnect(0x13) and (initiator.reasons[0] == 0x16) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-09-C [Master accepting Connection Termination]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Not verified that IUT stops sending empty data packets - see Air trace)
"""
def ll_con_mas_bv_09_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and (initiator.reasons[1] == 0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-13-C [Master requests Feature Setup procedure]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_13_c(transport, upperTester, lowerTester, trace):

    LL_FEAT_BIT_MASK_VALID = 0x1CF2F # Bitmask for features not impacting feature masking (ll_feat.h)

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Read local features from lower- and upperTester to establish expected remote read
            result
        """
        hasFeatures, expectedFeatures = readLocalFeatures(transport, lowerTester, trace)
        hasFeatures, upperFeatures    = readLocalFeatures(transport, upperTester, trace)
        upperLocalFeatures = toNumber(upperFeatures)
        expectedMaskedFeatures = toNumber(expectedFeatures) & (upperLocalFeatures | ~LL_FEAT_BIT_MASK_VALID)
        """
            Issue the LE Read Remote Features Command, verify the reception of a Command Status Event
        """
        success = readRemoteFeatures(transport, upperTester, initiator.handles[1], trace) and success;
        """
            Await the reception of a LE Read Remote Features Command Complete Event
        """
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, upperTester, trace);
        success = success and hasFeatures;
        if hasFeatures:
            showLEFeatures(features, trace)
            success = (toNumber(features) == expectedMaskedFeatures) and success

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-20-C [Master requests Version Exchange procedure]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_20_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Issue the Read Remote Version Information Command, verify the reception of a Command Status Event
        """
        success = readRemoteVersionInformation(transport, upperTester, initiator.handles[1], trace) and success;
        """
            Await the reception of a Read Remote Version Information Complete Event
        """
        hasVersion, handle, version, manufacturer, subVersion = hasReadRemoteVersionInformationCompleteEvent(transport, upperTester, trace);
        success = success and hasVersion;
        if hasVersion:
            trace.trace(8, "     version: 0x%02x" % version);
            trace.trace(8, " sub-version: 0x%04x" % subVersion);
            trace.trace(8, "manufacturer: 0x%04x" % manufacturer);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-21-C [Master responds to Version Exchange procedure]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_21_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Issue the Read Remote Version Information Command, verify the reception of a Command Status Event
        """
        success = readRemoteVersionInformation(transport, lowerTester, initiator.handles[1], trace) and success;
        """
            Await the reception of a Read Remote Version Information Complete Event
        """
        hasVersion, handle, version, manufacturer, subVersion = hasReadRemoteVersionInformationCompleteEvent(transport, lowerTester, trace);
        success = success and hasVersion;
        if hasVersion:
            trace.trace(8, "     version: 0x%02x" % version);
            trace.trace(8, " sub-version: 0x%04x" % subVersion);
            trace.trace(8, "manufacturer: 0x%04x" % manufacturer);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-23-C [Master responds to Feature Exchange procedure]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_23_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Issue the LE Read Remote Features Command, verify the reception of a Command Status Event
        """
        success = success and readRemoteFeatures(transport, lowerTester, initiator.handles[1], trace);
        """
            Await the reception of a LE Read Remote Features Command Complete Event
        """
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, lowerTester, trace);
        success = success and hasFeatures;
        if hasFeatures:
            showLEFeatures(features, trace);
            # Bit 27 is "Masked to Peer" an must be cleared
            success = ((toNumber(features) & (1 << 27)) == 0) and success;

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-24-C [Master requests Connection Parameters – Slave Accepts]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Actual effect of change cannot be verified - see Air trace)
"""
def ll_con_mas_bv_24_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        for interval, timeout in zip([ 6, 3200, 6 ], [ 300, 3200, 300 ]):
            """
                Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            """
            success = initiator.update(interval, interval, initiator.latency, timeout) and success;
            """
                Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
            """
            success = initiator.acceptUpdate() and success;
            """
                Both lower and upper Tester should receive a LE Connection Update Complete Event...
            """
            success = initiator.updated() and success;
            """
                Wait for change to take place...
            """
            transport.wait(int(4 * interval * 1.25));

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-25-C [Master requests Connection Parameters – Slave Rejects]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Actual effect of change cannot be verified - see Air trace)
"""
def ll_con_mas_bv_25_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        interval, timeout = 6, 300;
        for reject in [ True, False ]:
            """
                Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            """
            success = initiator.update(interval, interval, initiator.latency, timeout) and success;
            """
                Accept or Reject the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP or a LL_REJECT_EXT_IND...
            """
            success = (initiator.rejectUpdate(0x3B) if reject else initiator.acceptUpdate()) and success;
            """
                Both lower and upper Tester should receive a LE Connection Update Complete Event... if request was accepted
            """
            if reject:
                success = not initiator.updated() and (initiator.status == 0x3B) and success;
            else:
                success = initiator.updated() and success;
            """
                Wait for optional change to take place...
            """
            transport.wait(int(4 * interval * 1.25));

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-26-C [Master requests Connection Parameters – same procedure collision]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Test not according to specs - not possible!)
"""
def ll_con_mas_bv_26_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        interval, timeout = 6, 300;
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        updRequested = initiator.update(interval, interval, initiator.latency, timeout);
        success = success and updRequested;
        """
            Verify that the lower tester receives a LE Remote Connection Parameter Request Event...
        """
        updPeerInvolved = initiator.updPeerRequest;
        success = success and updPeerInvolved;
        """
            Send a LL_CONNECTION_PARAM_REQ as a reaction to the LE Remote Connection Parameter Request Event...
            NOTE: We use a little nasty trick here. Swap the roles of initiator and peer and swap assigned handles...
        """
        initiator.switchRoles();
        """
            Update request will be rejected with an error code 0x0C - command disallowed...
        """
        success = success and not initiator.update(interval, interval, initiator.latency, timeout) and initiator.status == 0x0C;
        """
            Get back to original roles of initiator and peer...
        """
        initiator.resetRoles();
        """
            Send a LL_CONNECTION_PARAM_RSP as a reaction to the original LE Remote Connection Parameter Request Event...
        """
        initiator.updInitiatorRequest, initiator.updPeerRequest = updRequested, updPeerInvolved;
        success = success and initiator.acceptUpdate();
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event...
        """
        success = success and initiator.updated();
        """
            Wait for change to take place...
        """
        transport.wait(int(4 * interval * 1.25));

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-27-C [Master requests Connection Parameters - Channel Map Update procedure collision]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Switch to only even channels cannot be verified - see Air trace)
"""
def ll_con_mas_bv_27_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        interval, timeout = 6, 300;
        """
            Use only even channels...
        """
        success = channelMapUpdate(transport, upperTester, 0x1555555555, trace) and success;
        """
            Lower tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            NOTE: We use a little nasty trick here. Swap the roles of initiator and peer and swap assigned handles...
        """
        initiator.switchRoles();
        """
            Lower tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECT_EXT_IND...
        """
        success = initiator.rejectUpdate(0x2A) and success;
        """
            Verify that the update was rejected with error code 0x2A
        """
        success = not initiator.updated() and (initiator.status == 0x2A) and success;
        """
            Get back to original roles of initiator and peer...
        """
        initiator.resetRoles();
        initiator.pre_updated = True;
        interval = 24;
        """
            Wait for change to take place...
        """
        transport.wait(int(8 * interval * 1.25));

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-29-C [Master requests Connection Parameters – Slave unsupported]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Change to connection interval cannot be verified - see Air trace)
"""
def ll_con_mas_bv_29_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        interval, timeout = 6, 300;
        """
            Upper tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECT_EXT_IND... (update will take place)
        """
        success = initiator.rejectUpdate(0x1A) and success;
        """
            Verify that the update was accepted
        """
        success = initiator.updated() and success;
        """
            Wait for change to take place...
        """
        transport.wait(int(8 * interval * 1.25));

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-30-C [Master responds to Connection Parameters request – no Preferred_Periodicity]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Change to connection interval cannot be verified - see Air trace)
"""
def ll_con_mas_bv_30_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        for interval, timeout in zip([ 6, 3200, 6 ], [ 300, 3200, 300 ]):
            """
                Lower tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
                NOTE: We use a little nasty trick here. Swap the roles of initiator and peer and swap assigned handles...
            """
            initiator.switchRoles();

            success = initiator.update(interval, interval, initiator.latency, timeout) and success;
            """
                Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
            """
            success = initiator.acceptUpdate() and success;
            """
                Both lower and upper Tester should receive a LE Connection Update Complete Event...
            """
            success = initiator.updated() and success;
            """
                Wait for change to take place...
            """
            transport.wait(int(4 * interval * 1.25));

            initiator.resetRoles();

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-34-C [Master responds to Connection Parameters request – event masked]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_34_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
    """
        Disable the LE Remote Connection Parameter Request event (Bit 5)
    """
    events = [0xDF, 0xFF, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];
    success = setLEEventMask(transport, upperTester, events, trace) and success;

    if connected:
        interval, timeout = 6, 300;
        """
            Lower tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            NOTE: We use a little nasty trick here. Swap the roles of initiator and peer and swap assigned handles...
        """
        initiator.switchRoles();

        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Update request should be rejected with a LL_REJECT_EXT_IND...
        """
        success = not initiator.updated() and (initiator.status == 0x1A) and success;

        initiator.resetRoles();

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-35-C [Master responds to Connection Parameters request – Host rejects]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_35_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        interval, timeout = 6, 300;
        """
            Lower tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            NOTE: We use a little nasty trick here. Swap the roles of initiator and peer and swap assigned handles...
        """
        initiator.switchRoles();

        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECT_EXT_IND...
        """
        success = initiator.rejectUpdate(0x3B) and success;
        """
            Verify that the update was rejected...
        """
        success = not initiator.updated() and success;

        initiator.resetRoles();

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-41-C [Master requests PHY Update procedure]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_41_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        optionPhys = 0;

        table = list(zip( [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3], \
                     [2, 1, 2, 1, 3, 3, 1, 2, 3, 0, 2, 0], \
                     [2, 2, 1, 1, 2, 1, 3, 3, 3, 2, 0, 0], \
                     [2, 1, 2, 1, 2, 2, 1, 2, 2, 2, 2, 2], \
                     [2, 2, 1, 1, 2, 1, 2, 2, 2, 2, 2, 2] ));

        for i in range(2):
            for allPhys, txPhys, rxPhys, expTxPhys, expRxPhys in table:
                success = initiator.updatePhys(allPhys, txPhys, rxPhys, optionPhys) and success;
                success = success and (initiator.txPhys == expTxPhys) and (initiator.rxPhys == expRxPhys);
            random.shuffle(table);

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-43-C [Master responds to PHY Update procedure]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_43_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        allPhys, optionPhys, expTxPhys, expRxPhys = 3, 0, 2, 2;

        success = initiator.updatePhys(allPhys, 1, 1, optionPhys) and success;
        success = success and (initiator.txPhys == expTxPhys) and (initiator.rxPhys == expRxPhys);

        table = list(zip( [2, 1, 2, 1, 3, 3, 1, 2, 3], \
                     [2, 2, 1, 1, 2, 1, 3, 3, 3], \
                     [2, 1, 2, 1, 2, 2, 1, 2, 2], \
                     [2, 2, 1, 1, 2, 1, 2, 2, 2] ));
        allPhys = 0;

        initiator.switchRoles();

        for i in range(2):
            for txPhys, rxPhys, expTxPhys, expRxPhys in table:
                success = initiator.updatePhys(allPhys, txPhys, rxPhys, optionPhys) and success;
                success = success and (initiator.txPhys == expTxPhys) and (initiator.rxPhys == expRxPhys);
            random.shuffle(table);

        initiator.resetRoles();

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-73-C [Master Packet Data Length Update – Pesponding to Packet Data Length Update Procedure; LE 1M PHY]

    Last modified: 08-08-2019
    Reviewed and verified: 08-08-2019 Henrik Eriksen (Note: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.)
"""
def ll_con_mas_bv_73_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);
    maxPacketTime, cmaxTxOctets, cmaxTxTime = 2120 * maxPacketLength // 251, 27, 328;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Feature exchange as specified in LL.TS.5.1.1, chapter 4.1.5
        """
        success = readRemoteFeatures(transport, upperTester, initiator.handles[1], trace) and success;
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, upperTester, trace);
        showLEFeatures(features, trace);

        """
            Exchange data...
        """
        lenValues  = list(range(28, maxPacketLength-1)) + list(range(maxPacketLength+1, 250));
        timeValues = list(range(329, maxPacketTime-1)) + list(range(maxPacketTime+1, 2119));

        for txOctets, txTime in zip( [ 27, 251, maxPacketLength, 27, 27, 27, 251, 251, 251, maxPacketLength, maxPacketLength, maxPacketLength, \
                                       random.choice(lenValues), random.choice(lenValues), random.choice(lenValues), random.choice(lenValues) ], \
                                     [ 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, \
                                       random.choice(timeValues), random.choice(timeValues), random.choice(timeValues), random.choice(timeValues) ] ):

            success = setDataLength(transport, lowerTester, initiator.handles[1], txOctets, txTime, trace) and success;
            trace.trace(6, "Setting TX Data Length %d and TX Data Time %d" % (txOctets, txTime));
            changed = not ((cmaxTxOctets == min(txOctets, maxPacketLength)) and (cmaxTxTime == min(txTime, 328)));

            if changed:
                gotEvent, handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = hasDataLengthChangedEvent(transport, lowerTester, trace);
                success = success and gotEvent;
                if not gotEvent:
                    trace.trace(6, "Error: Missed Data Length Changed Event from lowerTester");
                gotEvent = hasDataLengthChangedEvent(transport, upperTester, trace)[0];
                success = success and gotEvent;
                if not gotEvent:
                    trace.trace(6, "Error: Missed Data Length Changed Event from upperTester");

            pbFlags = 0;
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)];
            dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
            """
                Lower Tester is sending Data...
            """
            txData = [_ for _ in range(27)];
            for i in range(20):
                dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-74-C [Master Packet Data Length Update – Initiating Packet Data Length Update Procedure; LE 1M PHY]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (Note: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.)
"""
def ll_con_mas_bv_74_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);
    maxPacketTime, cmaxTxOctets, cmaxTxTime = 2120 * maxPacketLength // 251, 27, 328;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Feature exchange as specified in LL.TS.5.1.1, chapter 4.1.5
        """
        success = readRemoteFeatures(transport, upperTester, initiator.handles[1], trace) and success;
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, upperTester, trace);
        showLEFeatures(features, trace);

        for txOctets, txTime in zip( [ maxPacketLength, 27, 251, maxPacketLength, 27, 251, maxPacketLength, 27, 251, 60, 27, 251 ], \
                                     [ maxPacketTime, maxPacketTime, maxPacketTime, 328, 328, 328, 2120, 2120, 2120, 2120, 2120, 2120 ] ):

            success = setDataLength(transport, upperTester, initiator.handles[0], txOctets, txTime, trace) and success;

            changed = not ((cmaxTxOctets == min(txOctets, maxPacketLength)) and (cmaxTxTime == min(txTime, 328)));

            if changed:
                gotEvent, handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = hasDataLengthChangedEvent(transport, upperTester, trace);
                success = success and gotEvent;
                gotEvent = hasDataLengthChangedEvent(transport, lowerTester, trace)[0];
                success = success and gotEvent;

            pbFlags = 0;
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)];
            dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
            """
                Lower Tester is sending Data...
            """
            txData = [_ for _ in range(27)];
            for i in range(20):
                dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-76-C [Master Packet Data Length Update – Pesponding to Packet Data Length Update Procedure; LE 2M PHY]

    Last modified: 08-08-2019
    Reviewed and verified: 08-08-2019 Henrik Eriksen (Note: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.)
"""
def ll_con_mas_bv_76_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);
    maxPacketTime, cmaxTxOctets, cmaxTxTime = 2120 * maxPacketLength // 251, 27, 328;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Feature exchange as specified in LL.TS.5.1.1, chapter 4.1.5
        """
        success = readRemoteFeatures(transport, upperTester, initiator.handles[1], trace) and success;
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, upperTester, trace);
        showLEFeatures(features, trace);

        """
            Switch to LE 2M PHY channel...
        """
        allPhys, txPhys, rxPhys, optionPhys = 0, 2, 2, 0;

        success = initiator.updatePhys(allPhys, txPhys, rxPhys, optionPhys) and success;
        success = (initiator.txPhys == txPhys) and (initiator.rxPhys == rxPhys) and success
        """
            Exchange data...
        """
        lenValues  = list(range(28, maxPacketLength-1)) + list(range(maxPacketLength+1, 250));
        timeValues = list(range(329, maxPacketTime-1)) + list(range(maxPacketTime+1, 2119));

        for txOctets, txTime in zip( [ 27, 251, maxPacketLength, 27, 27, 27, 251, 251, 251, maxPacketLength, maxPacketLength, maxPacketLength, \
                                       random.choice(lenValues), random.choice(lenValues), random.choice(lenValues), random.choice(lenValues) ], \
                                     [ 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, \
                                       random.choice(timeValues), random.choice(timeValues), random.choice(timeValues), random.choice(timeValues) ] ):

            success = setDataLength(transport, lowerTester, initiator.handles[1], txOctets, txTime, trace) and success;

            changed = not ((cmaxTxOctets == min(txOctets, maxPacketLength)) and (cmaxTxTime == min(txTime, 328)));

            if changed:
                gotEvent, handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = hasDataLengthChangedEvent(transport, lowerTester, trace);
                success = success and gotEvent;
                gotEvent = hasDataLengthChangedEvent(transport, upperTester, trace)[0];
                success = success and gotEvent;

            pbFlags = 0;
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)];
            dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
            """
                Lower Tester is sending Data...
            """
            txData = [_ for _ in range(27)];
            for i in range(20):
                dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-77-C [Master Packet Data Length Update – Initiating Packet Data Length Update Procedure; LE 2M PHY]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (Note: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.)
"""
def ll_con_mas_bv_77_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);
    maxPacketTime, cmaxTxOctets, cmaxTxTime = 2120 * maxPacketLength // 251, 27, 328;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Feature exchange as specified in LL.TS.5.1.1, chapter 4.1.5
        """
        success = readRemoteFeatures(transport, upperTester, initiator.handles[1], trace) and success;
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, upperTester, trace);
        showLEFeatures(features, trace);

        allPhys, txPhys, rxPhys, optionPhys = 0, 2, 2, 0;

        success = initiator.updatePhys(allPhys, txPhys, rxPhys, optionPhys) and success;
        success = (initiator.txPhys == txPhys) and (initiator.rxPhys == rxPhys) and success

        for txOctets, txTime in zip( [ maxPacketLength, 27, 251, maxPacketLength, 27, 251, maxPacketLength, 27, 251, maxPacketLength, 27, 251 ], \
                                     [ maxPacketTime, maxPacketTime, maxPacketTime, 328, 328, 328, 2120, 2120, 2120, 2120, 2120, 2120 ] ):

            success = setDataLength(transport, upperTester, initiator.handles[0], txOctets, txTime, trace) and success;

            changed = not ((cmaxTxOctets == min(txOctets, 60)) and (cmaxTxTime == min(txTime, 328)));

            if changed:
                gotEvent, handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = hasDataLengthChangedEvent(transport, upperTester, trace);
                if not gotEvent:
                    trace.trace(7, "Missing Data Length Changed Event from upperTester!");
                success = success and gotEvent;
                gotEvent = hasDataLengthChangedEvent(transport, lowerTester, trace)[0];
                if not gotEvent:
                    trace.trace(7, "Missing Data Length Changed Event from lowerTester!");
                success = success and gotEvent;

            pbFlags = 0
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)]
            dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData));
            """
                Lower Tester is sending Data...
            """
            txData = [_ for _ in range(27)]
            for i in range(20):
                dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData));
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BI-06-C [Master responds to Connection Parameter Request – illegal parameters]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bi_06_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        interval, timeout = 4, 300;
        """
            Lower tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            NOTE: We use a little nasty trick here. Swap the roles of initiator and peer and swap assigned handles...
        """
        initiator.switchRoles();

        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Verify that the update was rejected...
        """
        success = not initiator.updated() and (initiator.status == 0x1E) and success;

        initiator.resetRoles();

        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-01-C [Changing Static Address while Advertising]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen (NOTE: Test fails - test specification is omitting White List addition!)
"""
def ll_sec_adv_bv_01_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivateActiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 30, 5, \
                                                   ExtendedAddressType.RANDOM, ExtendedAddressType.RANDOM, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IUT' );
    """
        Adding lowerTester address to the White List
    """
    success = addAddressesToWhiteList(transport, upperTester, [ randomIdentityAddress(lowerTester) ], trace);

    success = advertiser.enable();
    success = scanner.enable() and success;
    scanner.monitor();
    """
        Attempt to change advertiser (upperTester) address...
    """
    status = le_set_random_address(transport, upperTester, toArray(address_scramble_OUI( toNumber(upperRandomAddress) ), 6), 100);
    trace.trace(6, "LE Set Random Address Command returns status: 0x%02X" % status);
    success = getCommandCompleteEvent(transport, upperTester, trace) and (status == 0x0C) and success;

    success = scanner.disable() and success;
    success = success and scanner.qualifyReports( 5 );
    success = success and scanner.qualifyResponses( 5, advertiser.responseData);

    success = advertiser.disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-02-C [Non Connectable Undirected Advertising with non-resolvable private address]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_02_c(transport, upperTester, lowerTester, trace):

    """
        Make sure that random address for upperTester is a non-resolvable private addresses
    """
    setNonResolvableRandomAddress(transport, upperTester, trace);

    advertiser, scanner = setPrivatePassiveScanning(transport, lowerTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 100, \
                                                    ExtendedAddressType.RESOLVABLE_OR_RANDOM, ExtendedAddressType.PUBLIC);
    """
        Add Random address of upperTester to the Resolving List
    """
    RPA = ResolvableAddresses( transport, upperTester, trace );
    success = RPA.add( publicIdentityAddress( lowerTester ) );
    """
        Enable Private Address Resolution
     """
    success = RPA.timeout( 60 ) and success;
    success = RPA.enable() and success;

    """
        Start NON_CONNECTABLE_ADVERTISING using non-resolvable private adddress
    """
    success = advertiser.enable() and success;
    success = scanner.enable() and success;
    scanner.monitor()
    success = scanner.disable() and success;
    success = success and scanner.qualifyReports( 100, randomIdentityAddress(upperTester) );

    success = advertiser.disable() and success;
    success = RPA.disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-03-C [Non Connectable Undirected Advertising with resolvable private address]

    Last modified: 21-08-2019
    Reviewed and verified: 21-08-2019 Henrik Eriksen
    Change: ReadLocalResolvableAddress() -> ReadPeerResolvableAddress()
"""
def ll_sec_adv_bv_03_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivatePassiveScanning(transport, lowerTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 20);
    """
        Add Public address of lowerTester to the Resolving List with the upperIRK
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester) ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( two and sixty seconds )
    """
    success = RPAs[upperTester].timeout( 2 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    resolvableAddresses = [ 0, 0 ];
    success = advertiser.enable() and success;

    for n in range(2):
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = success and scanner.qualifyReports( 20, resolvablePublicAddress(upperTester) );
        """
            Read local address in resolving list.
        """
        addressRead, resolvableAddresses[n] = readPeerResolvableAddress(transport, lowerTester, publicIdentityAddress(upperTester), trace);
        trace.trace(6, "Local Resolvable Address: %s" % formatAddress(resolvableAddresses[n]));

        if n == 0:
            transport.wait(2000); # Wait for RPA timeout to expire

    success = advertiser.disable() and success;
    success = success and toNumber(resolvableAddresses[0]) != toNumber(resolvableAddresses[1]);
    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-04-C [Scannable Undirected Advertising with non-resolvable private address]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_04_c(transport, upperTester, lowerTester, trace):

    """
        Make sure that random addresses for lower- and upper-Tester are non-resolvable private addresses
    """
    setNonResolvableRandomAddress(transport, lowerTester, trace);
    setNonResolvableRandomAddress(transport, upperTester, trace);

    advertiser, scanner = setPrivateActiveScanning(transport, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 100, 5, \
                                                   ExtendedAddressType.RANDOM, ExtendedAddressType.RANDOM);

    success = advertiser.enable();
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = advertiser.disable() and success;
    success = scanner.qualifyReports( 100, randomIdentityAddress(upperTester) ) and success;
    success = scanner.qualifyResponses( 5, advertiser.responseData) and success;

    return success;

"""
    LL/SEC/ADV/BV-05-C [Scannable Undirected Advertising with resolvable private address]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_05_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivateActiveScanning(transport, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 20, 1, \
                                                   ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                                                   AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS);

    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Adding lowerTester address to the White List
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;
    """
        Set resolvable private address timeout in seconds ( two and sixty seconds )
    """
    success = RPAs[upperTester].timeout( 2 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = success and advertiser.enable();

    resolvableAddresses = [ 0, 0 ];
    for n in range(2):
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = scanner.qualifyReports( 20, resolvablePublicAddress(upperTester) ) and success;
        success = scanner.qualifyResponses( 1, advertiser.responseData ) and success;

        addressRead, resolvableAddresses[n] = readLocalResolvableAddress(transport, upperTester, publicIdentityAddress(lowerTester), trace);
        trace.trace(6, "AdvA: %s" % formatAddress(resolvableAddresses[n]));
        if n == 0:
            transport.wait(2000); # Wait for RPA timeout

    success = advertiser.disable() and success;
    success = success and toNumber(resolvableAddresses[0]) != toNumber(resolvableAddresses[1]);
    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-06-C [Connecting with Undirected Connectable Advertiser using non-resolvable private address]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_06_c(transport, upperTester, lowerTester, trace):

    """
        Make sure that random address for upperTester is a non-resolvable private addresses
    """
    setNonResolvableRandomAddress(transport, upperTester, trace);

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_RANDOM, ExtendedAddressType.PUBLIC);

    lowerAddresses = [ publicIdentityAddress(lowerTester), \
                       Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM, toNumber(lowerRandomAddress) | 0xC00000000000 ), \
                       Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM, toNumber(lowerRandomAddress) & 0x3FFFFFFFFFFF ) ];

    success = True;
    for lowerAddress in lowerAddresses:
        advertiser.peerAddress = lowerAddress;
        initiator.initiatorAddress = lowerAddress;
        initiator.peerAddress = randomIdentityAddress(upperTester);

        if lowerAddress.type == ExtendedAddressType.PUBLIC:
            success = preamble_set_public_address(transport, lowerTester, toNumber(lowerAddress.address), trace) and success;
        else:
            success = preamble_set_random_address(transport, lowerTester, toNumber(lowerAddress.address), trace) and success;

        success = advertiser.enable() and success;
        connected = initiator.connect();
        success = connected and success;
        if connected:
            success = initiator.disconnect(0x13) and success;
        else:
            success = advertiser.disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-07-C [Connecting with Undirected Connectable Advertiser with Local IRK but no Peer IRK]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen (NOTE: Test fails - filtering doesn't work!)
"""
def ll_sec_adv_bv_07_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_CONNECTION_REQUESTS);
    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester) ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Adding lowerTester address to the White List
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Upper tester terminates the connection
        """
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and success;
        initiator.resetRoles();
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-08-C [Connecting with Undirected Connectable Advertiser with both Local and Peer IRK]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_08_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Adding lowerTester address to the White List
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and success;
        initiator.resetRoles();
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-09-C [Connecting with Undirected Connectable Advertiser with no Local IRK but peer IRK]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_09_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester) ) and success;
    """
        Adding lowerTester address to the White List
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and success;
        initiator.resetRoles();
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success

    return success;

"""
    LL/SEC/ADV/BV-10-C [Connecting with Undirected Connectable Advertiser where no match for Peer Device Identity]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_10_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    """
        Add Identity Addresses to Resolving Lists
    """
    bogusIRK = [ random.randint(0,255) for _ in range(16) ];
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), bogusIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Add Identity Address of lower Tester to White List to enable responding to Scan Requests
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;

    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;

    for n in range(10):
        connected = initiator.connect();
        success = success and not connected;
        if connected:
            success = initiator.disconnect(0x13) and success;
            break;

    success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-11-C [Connecting with Directed Connectable Advertiser using local and remote IRK]

    Last modified: 17-12-2019
    Reviewed and verified: 17-12-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_11_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_HDC_DIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Verify that connection was established with resolvable private addresses
        """
        isRPA = Address( None, initiator.localRPA() ).isResolvablePrivate();
        isRPA = Address( None, initiator.peerRPA() ).isResolvablePrivate() and isRPA;
        success = isRPA and success;
        if not isRPA:
            trace.trace(6, "Wrong RPAs - local RPA: %s peer RPA: %s" %(Address( None, initiator.localRPA() ), Address( None, initiator.peerRPA() )));
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and success;
        initiator.resetRoles();
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and success;

    advertiserTimeout = False;
    success = advertiser.enable() and success;
    initiator.checkPrematureDisconnect = False;
    """
        Retry connection 20 times.
    """
    for i in range(20):
        connected = initiator.connect();
        success = success and not connected;
        if connected:
            success = initiator.disconnect(0x13) and success;
            break;
        else:
            advertiserTimeout, waitTime = False, 0;
            while not advertiserTimeout:
                flush_events(transport, lowerTester, 100);
                advertiserTimeout = advertiser.timeout();
                waitTime += 100;
                if waitTime >= 1300:
                    break;
            if advertiserTimeout:
                trace.trace(7, "Advertising done!");
                success = advertiser.enable(True) and success;
            else:
                break;

    if not advertiserTimeout:
        success = advertiser.disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-12-C [Connecting with Directed Connectable Advertising with local IRK but without remote IRK]

    Last modified: 21-08-2019
    Reviewed and verified: 21-08-2019 Henrik Eriksen
    Change: ReadLocalResolvableAddress() -> ReadPeerResolvableAddress()
"""
def ll_sec_adv_bv_12_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_HDC_DIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.PUBLIC);
    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester) ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( two seconds )
    """
    success = RPAs[upperTester].timeout( 2 ) and RPAs[lowerTester].timeout( 2 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    privateAddresses = [ 0, 0 ];

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Read the resolvable address used in the AdvA field
        """
        addressRead, privateAddresses[0] = readPeerResolvableAddress(transport, lowerTester, publicIdentityAddress(upperTester), trace);
        trace.trace(6, "AdvA Address: %s" % formatAddress(privateAddresses[0]));
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and success;
        initiator.resetRoles();

        transport.wait( 2000 ); # wait for RPA to timeout
        """
            Extra connect step is necassary in order to the read the
        """
        success = advertiser.enable() and success;
        connected = initiator.connect();
        success = success and connected;

        if connected:
            """
                Read the resolvable address used in the AdvA field
            """
            addressRead, privateAddresses[1] = readPeerResolvableAddress(transport, lowerTester, publicIdentityAddress(upperTester), trace);
            trace.trace(6, "AdvA Address: %s" % formatAddress(privateAddresses[1]));

            success = initiator.disconnect(0x13) and success;
        else:
            success = advertiser.disable() and success;
    else:
        success = advertiser.disable() and success;

    success = success and (privateAddresses[0] != privateAddresses[1]);
    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-13-C [Directed Connectable Advertising without local IRK but with remote IRK]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen (NOTE: Test fails!)
"""
def ll_sec_adv_bv_13_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_HDC_DIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester) ) and success;
    """
        Set resolvable private address timeout in seconds ( two seconds )
    """
    success = RPAs[upperTester].timeout( 2 ) and RPAs[lowerTester].timeout( 2 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    privateAddresses = [ 0, 0 ];

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Read the resolvable address used in the AdvA field
        """
        addressRead, privateAddresses[0] = readLocalResolvableAddress(transport, lowerTester, publicIdentityAddress(upperTester), trace);
        trace.trace(6, "InitA Address: %s" % formatAddress(privateAddresses[0]));
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and success;
        initiator.resetRoles();

        transport.wait( 2000 ); # wait for RPA to timeout

        success = advertiser.enable() and success;
        connected = initiator.connect();
        success = success and connected;
        """
            Read the resolvable address used in the AdvA field
        """
        addressRead, privateAddresses[1] = readLocalResolvableAddress(transport, lowerTester, publicIdentityAddress(upperTester), trace);
        trace.trace(6, "InitA Address: %s" % formatAddress(privateAddresses[1]));

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = success and (privateAddresses[0] != privateAddresses[1]);
    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-14-C [Directed Connectable Advertising using Resolving List and Peer Device Identity not in the List]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_14_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_HDC_DIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    """
        Add Identity Addresses to Resolving Lists
    """
    bogusIRK = [ random.randint(0,255) for _ in range(16) ];
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), bogusIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Add Identity Address of lower Tester to White List to enable responding to Scan Requests
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;

    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and not connected;

    if connected:
        success = initiator.disconnect(0x13) and success;
    else:
        """
            Need to stop connection attempt - otherwies Resolvable List disable will fail with command not allowed...
        """
        success = initiator.cancelConnect() and success;
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-15-C [Scannable Advertising with resolvable private address, no Scan Response to Identity Address]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_15_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivateActiveScanning(transport, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 20, 1, \
                                                   ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.PUBLIC, AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS);
    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Adding lowerTester address to the White List
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;

    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.qualifyReports( 20, resolvablePublicAddress(upperTester) ) and success;
    success = not scanner.qualifyResponses( 1 ) and success;
    success = scanner.disable() and success;
    success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-16-C [Undirected Connectable Advertising with resolvable private address; no Connection to Identity Address]

    Last modified: 10-09-2019
    Reviewed and verified: 10-09-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_16_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Adding lowerTester address to the White List
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and not connected;
    if connected:
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-17-C [Directed Connectable Advertising using local and remote IRK, Ignore Identity Address]

    Last modified: 08-08-2019
    Reviewed and verified: 08-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_17_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_HDC_DIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and not connected;
    if connected:
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success

"""
    LL/SEC/ADV/BV-18-C [Scannable Advertising with resolvable private address, accept Identity Address]

    Last modified: 08-08-2019
    Reviewed and verified: 08-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_18_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivateActiveScanning(transport, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 20, 1, \
                                                   ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.PUBLIC);
    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set Device Privacy
    """
    success = setPrivacyMode(transport, upperTester, publicIdentityAddress(lowerTester), PrivacyMode.DEVICE_PRIVACY, trace) and success;
    """
        Add Identity Address of lower Tester to White List to enable responding to Scan Requests
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = advertiser.disable() and success;
    success = scanner.qualifyReports( 20, resolvablePublicAddress(upperTester) ) and success;
    success = scanner.qualifyResponses( 1, advertiser.responseData ) and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-19-C [Undirected Connectable Advertising with Local IRK and Peer IRK, accept Identity Address]

    Last modified: 08-08-2019
    Reviewed and verified: 08-08-2019 Henrik Eriksen (NOTE: Test fails!)
"""
def ll_sec_adv_bv_19_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set Device Privacy
    """
    success = setPrivacyMode(transport, upperTester, publicIdentityAddress(lowerTester), PrivacyMode.DEVICE_PRIVACY, trace) and success;
    """
        Add Identity Address of lower Tester to White List to enable responding to Scan Requests
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;
    """
        Set resolvable private address timeout in seconds ( two and sixty seconds )
    """
    success = RPAs[upperTester].timeout( 2 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(2100); # Wait for address renewal
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-20-C [Directed Connectable Advertising with resolvable private address; Connect to Identity Address]

    Last modified: 08-08-2019
    Reviewed and verified: 08-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_20_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_HDC_DIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set Device Privacy
    """
    success = setPrivacyMode(transport, upperTester, publicIdentityAddress(lowerTester), PrivacyMode.DEVICE_PRIVACY, trace) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success

"""
    LL/SEC/SCN/BV-01-C [Changing Static Address while Scanning]

    Last modified: 08-08-2019
    Reviewed and verified: 08-08-2019 Henrik Eriksen
"""
def ll_sec_scn_bv_01_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivateActiveScanning(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 20, 1, \
                                                   ExtendedAddressType.RANDOM, ExtendedAddressType.RANDOM);
    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IUT' );

    success = advertiser.enable();
    success = scanner.enable() and success;
    scanner.monitor();
    """
        Attempt to change scanner (upperTester) address...
    """
    status = le_set_random_address(transport, upperTester, toArray(address_scramble_OUI( toNumber(upperRandomAddress) ), 6), 100);
    trace.trace(6, "LE Set Random Address Command returns status: 0x%02X" % status);
    """
        Event queue may hold several Advertising Events...
    """
    while not getCommandCompleteEvent(transport, upperTester, trace):
        pass;
    success = (status == 0x0C) and success;

    success = scanner.disable() and success;
    success = scanner.qualifyReports( 20, randomIdentityAddress(lowerTester) ) and success;
    success = scanner.qualifyResponses( 5, advertiser.responseData) and success;

    success = advertiser.disable() and success;

    address = toNumber( randomIdentityAddress(lowerTester).address );
    randAddr = (address >> 24) & 0xFFFFFF;
    hashAddr = address & 0xFFFFFF;

    trace.trace(8, "Address parts: rand: 0x%06X hash: 0x%06X" % (randAddr, hashAddr));
    ok, localHash = encrypt(transport, upperTester, lowerIRK, toArray(randAddr, 16), trace);
    success = success and ok and (toNumber(localHash) & 0xFFFFFF == hashAddr);
    trace.trace(8, "Regenerated: hash: 0x%06X" % (toNumber(localHash) & 0xFFFFFF));

    return success;

__tests__ = {
    "LL/CON/ADV/BV-01-C": [ ll_con_adv_bv_01_c, "Accepting Connection Request" ],
    "LL/CON/ADV/BV-04-C": [ ll_con_adv_bv_04_c, "Accepting Connection Request after Directed Advertising" ],
    "LL/CON/ADV/BV-09-C": [ ll_con_adv_bv_09_c, "Accepting Connection Request using Channel Selection Algorithm #2" ],
    "LL/CON/ADV/BV-10-C": [ ll_con_adv_bv_10_c, "Accepting Connection Request after Directed Advertising using Channel Selection Algorithm #2" ],
    "LL/CON/INI/BV-01-C": [ ll_con_ini_bv_01_c, "Connection Initiation rejects Address change" ],
    "LL/CON/INI/BV-02-C": [ ll_con_ini_bv_02_c, "Connecting to Advertiser using Directed Advertising Packets" ],
    "LL/CON/INI/BV-06-C": [ ll_con_ini_bv_06_c, "Filtered Connection to Advertiser using Undirected Advertising Packets" ],
    "LL/CON/INI/BV-07-C": [ ll_con_ini_bv_07_c, "Filtered Connection to Advertiser using Directed Advertising Packets" ],
    "LL/CON/INI/BV-08-C": [ ll_con_ini_bv_08_c, "Connecting to Connectable Undirected Advertiser with Network Privacy" ],
    "LL/CON/INI/BV-09-C": [ ll_con_ini_bv_09_c, "Connecting to Connectable Undirected Advertiser with Network Privacy thru Resolving List" ],
    "LL/CON/INI/BV-10-C": [ ll_con_ini_bv_10_c, "Connecting to Directed Advertiser with Network Privacy thru Resolving List" ],
    "LL/CON/INI/BV-11-C": [ ll_con_ini_bv_11_c, "Connecting to Directed Advertiser using  wrong address with Network Privacy thru Resolving List " ],
    "LL/CON/INI/BV-12-C": [ ll_con_ini_bv_12_c, "Connecting to Directed Advertiser using Identity address with Network Privacy thru Resolving List" ],
    "LL/CON/INI/BV-16-C": [ ll_con_ini_bv_16_c, "Connecting to Advertiser with Channel Selection Algorithm #2" ],
    "LL/CON/INI/BV-17-C": [ ll_con_ini_bv_17_c, "Connecting to Directed Advertiser with Channel Selection Algorithm #2" ],
    "LL/CON/INI/BV-18-C": [ ll_con_ini_bv_18_c, "Don't connect to Advertiser using Identity address with Network Privacy thru Resolving List" ],
    "LL/CON/INI/BV-19-C": [ ll_con_ini_bv_19_c, "Don't connect to Directed Advertiser using Identity address with Network Privacy thru Resolving List" ],
    "LL/CON/INI/BV-20-C": [ ll_con_ini_bv_20_c, "Connect to Advertiser using Identity address with Device Privacy thru Resolving List" ],
    "LL/CON/INI/BV-21-C": [ ll_con_ini_bv_21_c, "Connect to Directed Advertiser using Identity address with Device Privacy thru Resolving List" ],
    "LL/CON/INI/BV-23-C": [ ll_con_ini_bv_23_c, "Network Privacy - Connection Establishment using whitelist and resolving list with address resolution disabled" ],
    "LL/CON/INI/BV-24-C": [ ll_con_ini_bv_24_c, "Network Privacy - Connection Establishment using resolving list with address resolution disabled" ],
    "LL/CON/MAS/BI-06-C": [ ll_con_mas_bi_06_c, "Master responds to Connection Parameter Request – illegal parameters" ],
    "LL/CON/MAS/BV-03-C": [ ll_con_mas_bv_03_c, "Master sending Data packets to Slave" ],
    "LL/CON/MAS/BV-04-C": [ ll_con_mas_bv_04_c, "Master receiving Data packets from Slave" ],
    "LL/CON/MAS/BV-05-C": [ ll_con_mas_bv_05_c, "Master sending and receiving Data packets to and form Slave" ],
    "LL/CON/MAS/BV-07-C": [ ll_con_mas_bv_07_c, "Master requests Connection Parameter Update" ],
    "LL/CON/MAS/BV-08-C": [ ll_con_mas_bv_08_c, "Master Terminating Connection" ],
    "LL/CON/MAS/BV-09-C": [ ll_con_mas_bv_09_c, "Master accepting Connection Termination" ],
    "LL/CON/MAS/BV-13-C": [ ll_con_mas_bv_13_c, "Master requests Feature Setup procedure" ],
    "LL/CON/MAS/BV-20-C": [ ll_con_mas_bv_20_c, "Master requests Version Exchange procedure" ],
    "LL/CON/MAS/BV-21-C": [ ll_con_mas_bv_21_c, "Master responds to Version Exchange procedure" ],
    "LL/CON/MAS/BV-23-C": [ ll_con_mas_bv_23_c, "Master responds to Feature Exchange procedure" ],
    "LL/CON/MAS/BV-24-C": [ ll_con_mas_bv_24_c, "Master requests Connection Parameters – Slave Accepts" ],
    "LL/CON/MAS/BV-25-C": [ ll_con_mas_bv_25_c, "Master requests Connection Parameters – Slave Rejects" ],
    "LL/CON/MAS/BV-26-C": [ ll_con_mas_bv_26_c, "Master requests Connection Parameters – same procedure collision" ],
    "LL/CON/MAS/BV-27-C": [ ll_con_mas_bv_27_c, "Master requests Connection Parameters - Channel Map Update procedure collision" ],
    "LL/CON/MAS/BV-29-C": [ ll_con_mas_bv_29_c, "Master requests Connection Parameters – Slave unsupported" ],
    "LL/CON/MAS/BV-30-C": [ ll_con_mas_bv_30_c, "Master responds to Connection Parameters request – no Preferred_Periodicity" ],
    "LL/CON/MAS/BV-34-C": [ ll_con_mas_bv_34_c, "Master responds to Connection Parameters request – event masked" ],
    "LL/CON/MAS/BV-35-C": [ ll_con_mas_bv_35_c, "Master responds to Connection Parameters request – Host rejects" ],
    "LL/CON/MAS/BV-41-C": [ ll_con_mas_bv_41_c, "Master requests PHY Update procedure" ],
    "LL/CON/MAS/BV-43-C": [ ll_con_mas_bv_43_c, "Master responds to PHY Update procedure" ],
    "LL/CON/MAS/BV-73-C": [ ll_con_mas_bv_73_c, "Master Packet Data Length Update – Pesponding to Packet Data Length Update Procedure; LE 1M PHY" ],
    "LL/CON/MAS/BV-74-C": [ ll_con_mas_bv_74_c, "Master Packet Data Length Update – Initiating Packet Data Length Update Procedure; LE 1M PHY" ],
    "LL/CON/MAS/BV-76-C": [ ll_con_mas_bv_76_c, "Master Packet Data Length Update – Pesponding to Packet Data Length Update Procedure; LE 2M PHY" ],
    "LL/CON/MAS/BV-77-C": [ ll_con_mas_bv_77_c, "Master Packet Data Length Update – Initiating Packet Data Length Update Procedure; LE 2M PHY" ],
    "LL/CON/SLA/BI-08-C": [ ll_con_sla_bi_08_c, "Slave responds to Connection Parameters request – Illegal Parameters" ],
    "LL/CON/SLA/BV-04-C": [ ll_con_sla_bv_04_c, "Connection where Slave sends data to Master" ],
    "LL/CON/SLA/BV-05-C": [ ll_con_sla_bv_05_c, "Connection where Slave receives data from Master" ],
    "LL/CON/SLA/BV-06-C": [ ll_con_sla_bv_06_c, "Connection where Slave sends and receives data to and from Master" ],
    "LL/CON/SLA/BV-10-C": [ ll_con_sla_bv_10_c, "Slave accepting Connection Parameter Update from Master" ],
    "LL/CON/SLA/BV-11-C": [ ll_con_sla_bv_11_c, "Slave sending Termination to Master" ],
    "LL/CON/SLA/BV-12-C": [ ll_con_sla_bv_12_c, "Slave accepting Termination from Master" ],
#   "LL/CON/SLA/BV-13-C": [ ll_con_sla_bv_13_c, "Slave Terminating Connection on Supervision Timer" ],
    "LL/CON/SLA/BV-14-C": [ ll_con_sla_bv_14_c, "Slave performs Feature Setup procedure" ],
    "LL/CON/SLA/BV-19-C": [ ll_con_sla_bv_19_c, "Slave requests Version Exchange procedure" ],
    "LL/CON/SLA/BV-20-C": [ ll_con_sla_bv_20_c, "Slave responds to Version Exchange procedure" ],
    "LL/CON/SLA/BV-22-C": [ ll_con_sla_bv_22_c, "Slave requests Feature Exchange procedure" ],
    "LL/CON/SLA/BV-24-C": [ ll_con_sla_bv_24_c, "Slave requests Connection Parameters – Master Accepts" ],
    "LL/CON/SLA/BV-25-C": [ ll_con_sla_bv_25_c, "Slave requests Connection Parameters – Master Rejects" ],
    "LL/CON/SLA/BV-26-C": [ ll_con_sla_bv_26_c, "Slave requests Connection Parameters – same procedure collision" ],
    "LL/CON/SLA/BV-27-C": [ ll_con_sla_bv_27_c, "Slave requests Connection Parameters – channel map update procedure collision" ],
    "LL/CON/SLA/BV-29-C": [ ll_con_sla_bv_29_c, "Slave responds to Connection Parameters – Master no Preferred Periodicity" ],
    "LL/CON/SLA/BV-33-C": [ ll_con_sla_bv_33_c, "Slave responds to Connection Parameters request – event masked" ],
    "LL/CON/SLA/BV-34-C": [ ll_con_sla_bv_34_c, "Slave responds to Connection Parameters request – Host rejects" ],
    "LL/CON/SLA/BV-40-C": [ ll_con_sla_bv_40_c, "Slave requests PHY Update procedure" ],
    "LL/CON/SLA/BV-42-C": [ ll_con_sla_bv_42_c, "Slave responds to PHY Update procedure" ],
    "LL/CON/SLA/BV-77-C": [ ll_con_sla_bv_77_c, "Slave Packet Data Length Update – Pesponding to Packet Data Length Update Procedure; LE 1M PHY" ],
    "LL/CON/SLA/BV-78-C": [ ll_con_sla_bv_78_c, "Slave requests Packet Data Length Update procedure; LE 1M PHY" ],
    "LL/CON/SLA/BV-80-C": [ ll_con_sla_bv_80_c, "Slave Packet Data Length Update – Pesponding to Packet Data Length Update Procedure; LE 2M PHY" ],
    "LL/CON/SLA/BV-81-C": [ ll_con_sla_bv_81_c, "Slave requests Packet Data Length Update procedure; LE 2M PHY" ],
    "LL/DDI/ADV/BV-01-C": [ ll_ddi_adv_bv_01_c, "Non-Connectable Advertising Packets on one channel" ],
    "LL/DDI/ADV/BV-02-C": [ ll_ddi_adv_bv_02_c, "Undirected Advertising Packets on one channel" ],
    "LL/DDI/ADV/BV-03-C": [ ll_ddi_adv_bv_03_c, "Non-Connectable Advertising Packets on all channels" ],
    "LL/DDI/ADV/BV-04-C": [ ll_ddi_adv_bv_04_c, "Undirected Advertising with Data on all channels " ],
    "LL/DDI/ADV/BV-05-C": [ ll_ddi_adv_bv_05_c, "Undirected Connectable Advertising with Scan Request/Response " ],
    "LL/DDI/ADV/BV-06-C": [ ll_ddi_adv_bv_06_c, "Stop Advertising on Connection Request" ],
    "LL/DDI/ADV/BV-07-C": [ ll_ddi_adv_bv_07_c, "Scan Request/Response followed by Connection Request" ],
    "LL/DDI/ADV/BV-08-C": [ ll_ddi_adv_bv_08_c, "Advertiser Filtering Scan requests" ],
    "LL/DDI/ADV/BV-09-C": [ ll_ddi_adv_bv_09_c, "Advertiser Filtering Connection requests" ],
    "LL/DDI/ADV/BV-11-C": [ ll_ddi_adv_bv_11_c, "High Duty Cycle Connectable Directed Advertising on all channels" ],
    "LL/DDI/ADV/BV-15-C": [ ll_ddi_adv_bv_15_c, "Discoverable Undirected Advertising on all channels" ],
    "LL/DDI/ADV/BV-16-C": [ ll_ddi_adv_bv_16_c, "Discoverable Undirected Advertising with Data on all channels" ],
    "LL/DDI/ADV/BV-17-C": [ ll_ddi_adv_bv_17_c, "Discoverable Undirected Advertising with Scan Request/Response" ],
    "LL/DDI/ADV/BV-18-C": [ ll_ddi_adv_bv_18_c, "Discoverable Undirected Advertiser Filtering Scan requests " ],
    "LL/DDI/ADV/BV-19-C": [ ll_ddi_adv_bv_19_c, "Low Duty Cycle Directed Advertising on all channels" ],
    "LL/DDI/ADV/BV-20-C": [ ll_ddi_adv_bv_20_c, "Advertising on the LE 1M PHY on all channels" ],
#   "LL/DDI/ADV/BV-21-C": [ ll_ddi_adv_bv_21_c, "Non-Connectable Extended Legacy Advertising with Data on all channels" ],
    "LL/DDI/SCN/BV-01-C": [ ll_ddi_scn_bv_01_c, "Passive Scanning of Non-Connectable Advertising Packets" ],
    "LL/DDI/SCN/BV-02-C": [ ll_ddi_scn_bv_02_c, "Filtered Passive Scanning of Non-Connectable Advertising Packets" ],
    "LL/DDI/SCN/BV-03-C": [ ll_ddi_scn_bv_03_c, "Active Scanning of Connectable Undirected Advertising Packets" ],
    "LL/DDI/SCN/BV-04-C": [ ll_ddi_scn_bv_04_c, "Filtered Active Scanning of Connectable Undirected Advertising Packets" ],
    "LL/DDI/SCN/BV-05-C": [ ll_ddi_scn_bv_05_c, "Scanning for different Advertiser types with and without Data" ],
    "LL/DDI/SCN/BV-10-C": [ ll_ddi_scn_bv_10_c, "Passive Scanning for Undirected Advertising Packets with Data" ],
    "LL/DDI/SCN/BV-11-C": [ ll_ddi_scn_bv_11_c, "Passive Scanning for Directed Advertising Packets" ],
    "LL/DDI/SCN/BV-12-C": [ ll_ddi_scn_bv_12_c, "Passive Scanning for Discoverable Undirected Advertising Packets" ],
    "LL/DDI/SCN/BV-13-C": [ ll_ddi_scn_bv_13_c, "Passive Scanning for Non-Connectable Advertising Packets using Network Privacy" ],
    "LL/DDI/SCN/BV-14-C": [ ll_ddi_scn_bv_14_c, "Passive Scanning for Connectable Directed Advertising Packets using Network Privacy" ],
    "LL/DDI/SCN/BV-15-C": [ ll_ddi_scn_bv_15_c, "Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with no Local or Peer IRK" ],
    "LL/DDI/SCN/BV-16-C": [ ll_ddi_scn_bv_16_c, "Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with Local and no Peer IRK" ],
    "LL/DDI/SCN/BV-17-C": [ ll_ddi_scn_bv_17_c, "Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with no Local and a Peer IRK" ],
    "LL/DDI/SCN/BV-18-C": [ ll_ddi_scn_bv_18_c, "Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with both Local and Peer IRKs" ],
    "LL/DDI/SCN/BV-26-C": [ ll_ddi_scn_bv_26_c, "Passive Scanning for Non-Connectable Advertising Packets using Network Privacy" ],
    "LL/DDI/SCN/BV-28-C": [ ll_ddi_scn_bv_28_c, "Passive Scanning for Non-Connectable Advertising Packets using Device Privacy" ],
#   "LL/SEC/ADV/BV-01-C": [ ll_sec_adv_bv_01_c, "Changing Static Address while Advertising" ],
    "LL/SEC/ADV/BV-02-C": [ ll_sec_adv_bv_02_c, "Non Connectable Undirected Advertising with non-resolvable private address" ],
    "LL/SEC/ADV/BV-03-C": [ ll_sec_adv_bv_03_c, "Non Connectable Undirected Advertising with resolvable private address" ],
    "LL/SEC/ADV/BV-04-C": [ ll_sec_adv_bv_04_c, "Scannable Undirected Advertising with non-resolvable private address" ],
    "LL/SEC/ADV/BV-05-C": [ ll_sec_adv_bv_05_c, "Scannable Undirected Advertising with resolvable private address" ],
    "LL/SEC/ADV/BV-06-C": [ ll_sec_adv_bv_06_c, "Connecting with Undirected Connectable Advertiser using non-resolvable private address" ],
#   "LL/SEC/ADV/BV-07-C": [ ll_sec_adv_bv_07_c, "Connecting with Undirected Connectable Advertiser with Local IRK but no Peer IRK" ],
    "LL/SEC/ADV/BV-08-C": [ ll_sec_adv_bv_08_c, "Connecting with Undirected Connectable Advertiser with both Local and Peer IRK" ],
    "LL/SEC/ADV/BV-09-C": [ ll_sec_adv_bv_09_c, "Connecting with Undirected Connectable Advertiser with no Local IRK but peer IRK" ],
    "LL/SEC/ADV/BV-10-C": [ ll_sec_adv_bv_10_c, "Connecting with Undirected Connectable Advertiser where no match for Peer Device Identity" ],
    "LL/SEC/ADV/BV-11-C": [ ll_sec_adv_bv_11_c, "Connecting with Directed Connectable Advertiser using local and remote IRK" ],
    "LL/SEC/ADV/BV-12-C": [ ll_sec_adv_bv_12_c, "Connecting with Directed Connectable Advertising with local IRK but without remote IRK" ],
    "LL/SEC/ADV/BV-13-C": [ ll_sec_adv_bv_13_c, "Directed Connectable Advertising without local IRK but with remote IRK" ],
    "LL/SEC/ADV/BV-14-C": [ ll_sec_adv_bv_14_c, "Directed Connectable Advertising using Resolving List and Peer Device Identity not in the List" ],
    "LL/SEC/ADV/BV-15-C": [ ll_sec_adv_bv_15_c, "Scannable Advertising with resolvable private address, no Scan Response to Identity Address" ],
    "LL/SEC/ADV/BV-16-C": [ ll_sec_adv_bv_16_c, "Undirected Connectable Advertising with resolvable private address; no Connection to Identity Address" ],
    "LL/SEC/ADV/BV-17-C": [ ll_sec_adv_bv_17_c, "Directed Connectable Advertising using local and remote IRK, Ignore Identity Address" ],
    "LL/SEC/ADV/BV-18-C": [ ll_sec_adv_bv_18_c, "Scannable Advertising with resolvable private address, accept Identity Address" ],
#   "LL/SEC/ADV/BV-19-C": [ ll_sec_adv_bv_19_c, "Undirected Connectable Advertising with Local IRK and Peer IRK, accept Identity Address" ],
    "LL/SEC/ADV/BV-20-C": [ ll_sec_adv_bv_20_c, "Directed Connectable Advertising with resolvable private address; Connect to Identity Address" ],
    "LL/SEC/SCN/BV-01-C": [ ll_sec_scn_bv_01_c, "Changing Static Address while Scanning" ]
};

_maxNameLength = max([ len(key) for key in __tests__ ]);

_spec = { key: TestSpec(name = key, number_devices = 1, description = "#[" + __tests__[key][1] + "]", test_private = __tests__[key][0]) for key in __tests__ };

"""
    Return the test spec which contains info about all the tests
    this test module provides
"""
def get_tests_specs():
    return _spec;

def preamble(transport, trace):
    global lowerIRK, upperIRK, lowerRandomAddress, upperRandomAddress;

    ok = success = preamble_standby(transport, 0, trace);
    trace.trace(4, "preamble Standby " + ("PASS" if success else "FAIL"));
    success = preamble_standby(transport, 1, trace);
    ok = ok and success;
    trace.trace(4, "preamble Standby " + ("PASS" if success else "FAIL"));
    success, upperIRK, upperRandomAddress = preamble_device_address_set(transport, 0, trace);
    trace.trace(4, "preamble Device Address Set " + ("PASS" if success else "FAIL"));
    ok = ok and success;
    success, lowerIRK, lowerRandomAddress = preamble_device_address_set(transport, 1, trace);
    trace.trace(4, "preamble Device Address Set " + ("PASS" if success else "FAIL"));
    return ok and success;

"""
    Run a test given its test_spec
"""
def run_a_test(args, transport, trace, test_spec):
    try:
        success = preamble(transport, trace);
    except Exception as e:
        trace.trace(3, "Preamble generated exception: %s" % str(e));
        success = False;

    trace.trace(2, "%-*s %s test started..." % (_maxNameLength, test_spec.name, test_spec.description[1:]));
    test_f = test_spec.test_private;
    try:
        if test_f.__code__.co_argcount > 3:
            success = success and test_f(transport, 0, 1, trace);
        else:
            success = success and test_f(transport, 0, trace);
    except Exception as e:
        import traceback
        traceback.print_exc()
        trace.trace(3, "Test generated exception: %s" % str(e));
        success = False;

    return not success
