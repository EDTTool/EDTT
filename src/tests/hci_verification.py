# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

from numpy import random;
import os;
import math;
from enum import IntEnum;
from components.utils import *;
from components.basic_commands import *;
from components.address import *;
from components.events import *;
from components.resolvable import *;
from components.advertiser import *;
from components.scanner import *;
from components.initiator import *;
from components.preambles import *;
from components.test_spec import TestSpec;

global lowerIRK, upperIRK, lowerRandomAddress, upperRandomAddress;

class Role(IntEnum):
    CENTRAL = 0
    PERIPHERAL  = 1

def __check_command_complete_event(transport, idx, trace):
    event = get_event(transport, idx, 100);
    trace.trace(7, str(event));
    return event.isCommandComplete();

def __check_unknown_command_rsp_event(transport, idx, trace, status):
    event = get_event(transport, idx, 100);
    trace.trace(7, str(event));
    return status == 1 and (event.isCommandComplete() or event.isCommandStatus())

"""
    HCI/GEV/BV-01-C [Status return for Unsupported Commands]
"""
def hci_gev_bv_01_c(transport, idx, trace):

    NumRsp, length, lap = 0, 1, toArray(0x9E8B00, 3);

    status = inquire(transport, idx, lap, length, NumRsp, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status);

    status = read_buffer_size(transport, idx, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    le, simul = 0, 0;

    status = write_le_host_support(transport, idx, le, simul, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    handle, props, PrimChannelMap, OwnAddrType, PeerAddrType = 0, 0, 0, 0, 0;
    PrimMinInterval = [0 for _ in range(3)];
    PrimMaxInterval = [0 for _ in range(3)];
    AVal = [0 for _ in range(6)];
    FilterPolicy, TxPower, PrimAdvPhy, SecAdvMaxSkip, SecAdvPhy, sid, ScanReqNotifyEnable = 0, 0, 0, 0, 0, 0, 0;

    status = le_set_extended_advertising_parameters(transport, idx, handle, props, PrimMinInterval, PrimMaxInterval, PrimChannelMap, \
                                                    OwnAddrType, PeerAddrType, AVal, FilterPolicy, TxPower, PrimAdvPhy, SecAdvMaxSkip, \
                                                    SecAdvPhy, sid, ScanReqNotifyEnable, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    handle, op, FragPref = 0, 0, 0;
    data = [];

    status = le_set_extended_advertising_data(transport, idx, handle, op, FragPref, data, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    handle, op, FragPref = 0, 0, 0;
    data = [];

    status = le_set_extended_scan_response_data(transport, idx, handle, op, FragPref, data, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    enable, SetNum = 0, 0;
    SHandle = [0 for i in range(SetNum)];
    SDuration = [0 for i in range(SetNum)];
    SMaxExtAdvEvts = [0 for i in range(SetNum)];

    status = le_set_extended_advertising_enable(transport, idx, enable, SetNum, SHandle, SDuration, SMaxExtAdvEvts, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    status = le_read_maximum_advertising_data_length(transport, idx, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    status = le_read_number_of_supported_advertising_sets(transport, idx, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    handle = 0;

    status = le_remove_advertising_set(transport, idx, handle, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    status = le_clear_advertising_sets(transport, idx, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    handle, MinInterval, MaxInterval, props = 0, 0, 0, 0;

    status = le_set_periodic_advertising_parameters(transport, idx, handle, MinInterval, MaxInterval, props, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    handle, op, dataLength = 0, 0, 251;
    data = [0 for i in range(dataLength)];

    status = le_set_periodic_advertising_data(transport, idx, handle, op, dataLength, data, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    handle, enable = 0, 0;

    status = le_set_periodic_advertising_enable(transport, idx, enable, handle, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    OwnAddrType, FilterPolicy, phys = 0, 0, 0;
    PType = [0 for i in range(phys)];
    PInterval = [0 for i in range(phys)];
    PWindow = [0 for i in range(phys)];

    status = le_set_extended_scan_parameters(transport, idx, OwnAddrType, FilterPolicy, phys, PType, PInterval, PWindow, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    enable, FilterDup, duration, period = 0, 0, 0, 0;

    status = le_set_extended_scan_enable(transport, idx, enable, FilterDup, duration, period, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    FilterPolicy, OwnAddrType, PeerAddrType, phys = 0, 0, 0, 0;
    AVal = [0 for i in range(6)];
    PInterval = [0 for i in range(phys)];
    PWindow = [0 for i in range(phys)];
    PConnIntervalMin = [0 for i in range(phys)];
    PConnIntervalMax = [0 for i in range(phys)];
    PConnLatency = [0 for i in range(phys)];
    PSupervisionTimeout = [0 for i in range(phys)];
    PMinCeLen = [0 for i in range(phys)];
    PMaxCeLen = [0 for i in range(phys)];

    status = le_extended_create_connection(transport, idx, FilterPolicy, OwnAddrType, PeerAddrType, AVal, phys, PInterval, PWindow, \
                                           PConnIntervalMin, PConnIntervalMax, PConnLatency, PSupervisionTimeout, PMinCeLen, PMaxCeLen, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    FilterPolicy, sid, AddrType, skip, SyncTimeout, unused = 0, 0, 0, 0, 0, 0;
    AVal = [0 for i in range(6)];

    status = le_periodic_advertising_create_sync(transport, idx, FilterPolicy, sid, AddrType, AVal, skip, SyncTimeout, unused, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    status = le_periodic_advertising_create_sync_cancel(transport, idx, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    handle = 0;

    status = le_periodic_advertising_terminate_sync(transport, idx, handle, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    AddrType, sid = 0, 0;
    AVal = [0 for i in range(6)];

    status = le_add_device_to_periodic_advertiser_list(transport, idx, AddrType, AVal, sid, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    AddrType, sid = 0, 0;
    AVal = [0 for i in range(6)];

    status = le_remove_device_from_periodic_advertiser_list(transport, idx, AddrType, AVal, sid, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    status = le_clear_periodic_advertiser_list(transport, idx, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    status = le_read_periodic_advertiser_list_size(transport, idx, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    status = le_read_rf_path_compensation(transport, idx, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    TxPathComp, RxPathComp = 0, 0;

    status = le_write_rf_path_compensation(transport, idx, TxPathComp, RxPathComp, 100);
    success = __check_unknown_command_rsp_event(transport, idx, trace, status) and success;

    return success;

"""
    HCI/CFC/BV-02-C [Reported Buffer Size]
"""
def hci_cfc_bv_02_c(transport, idx, trace):

    status, LeMaxLen, LeMaxNum = le_read_buffer_size(transport, idx, 100);
    trace.trace(6, "LE Read Buffer Size Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);

    if LeMaxLen == 0 and LeMaxNum == 0:
        status, AclMaxLen, ScoMaxLen, AclMaxNum, ScoMaxNum = read_buffer_size(transport, idx, 100);
        trace.trace(6, "Read Buffer Size Command returns status: 0x%02X" % status);
        success = success and __check_command_complete_event(transport, idx, trace) and (status == 0);

    return success;

"""
    HCI/CIN/BV-01-C [Features returned by Read Local Supported Features Command]
"""
def hci_cin_bv_01_c(transport, idx, trace):

    status, features = read_local_supported_features(transport, idx, 100);
    trace.trace(6, "Read Local Supported Features Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);
    if success:
        showFeatures(features, trace);

    return success;

"""
    HCI/CIN/BV-03-C [Supported Commands returned by Read Local Supported Commands Command]
"""
def hci_cin_bv_03_c(transport, idx, trace):

    status, commands = read_local_supported_commands(transport, idx, 100);
    trace.trace(6, "Read Local Supported Commands Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);
    if success:
        showCommands(commands, trace);

    return success;

"""
    HCI/CIN/BV-04-C [Versions returned by Read Local Version Information Command]
"""
def hci_cin_bv_04_c(transport, idx, trace):

    status, HCIVersion, HCIRevision, LMPVersion, manufacturer, LMPSubversion = read_local_version_information(transport, idx, 100);
    trace.trace(6, "Read Local Version Information Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);
    if success:
        trace.trace(6, "HCI Version:    %i" % HCIVersion);
        trace.trace(6, "HCI Revision:   0x%04X" % HCIRevision);
        trace.trace(6, "LMP Version:    %i" % LMPVersion);
        trace.trace(6, "LMP Subversion: 0x%04X" % LMPSubversion);
        trace.trace(6, "Manufacturer:   0x%04X" % manufacturer);

    return success;

"""
    HCI/CIN/BV-06-C [Reported Filter Accept List Size]
"""
def hci_cin_bv_06_c(transport, idx, trace):

    status = le_clear_filter_accept_list(transport, idx, 100);
    trace.trace(6, "LE Clear Filter Accept List Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);

    status, FalSize = le_read_filter_accept_list_size(transport, idx, 100);
    trace.trace(6, "LE Read Filter Accept List Size Command returns status: 0x%02X list size: %i" % (status, FalSize));
    success = success and __check_command_complete_event(transport, idx, trace) and (status == 0);

    for n in range(FalSize+1):
        AddrType = 0;
        AVal = [random.randint(0,255) for _ in range(6)];
        if n < FalSize:
            lastAVal = AVal
        status = le_add_device_to_filter_accept_list(transport, idx, AddrType, AVal, 100);
        trace.trace(6, "LE Add Device to Filter Accept List Command returns status: 0x%02X" % status);
        success = success and __check_command_complete_event(transport, idx, trace) and ((status == 0) if n < FalSize else (status == 7));

        status = le_remove_device_from_filter_accept_list(transport, idx, AddrType, lastAVal, 100);
        trace.trace(6, "LE Remove Device from Filter Accept List Command returns status: 0x%02X" % status);
        success = success and __check_command_complete_event(transport, idx, trace) and (status == 0);

        status = le_add_device_to_filter_accept_list(transport, idx, AddrType, lastAVal, 100);
        trace.trace(6, "LE Add Device to Filter Accept List Command returns status: 0x%02X" % status);
        success = success and __check_command_complete_event(transport, idx, trace) and (status == 0);

    return success;

"""
    HCI/CIN/BV-09-C [Feature Bits returned by Read LE Public Key Validation Feature Bit]
"""
def hci_cin_bv_09_c(transport, idx, trace):

    status, features = le_read_local_supported_features(transport, idx, 100);
    trace.trace(6, "LE Read Local Supported Features Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);
    if success:
        showLEFeatures(features, trace);

    return success;

"""
    HCI/CCO/BV-07-C [BR/EDR Commands Not Supported on LE Device]
"""
def hci_cco_bv_07_c(transport, idx, trace):

    status = inquire(transport, idx, toArray(0x9E8B00, 3), 1, 1, 100);
    trace.trace(6, "Inquire Command returns status: 0x%02X" % status);
    success = status == 1; # Unknown HCI Command (0x01)
    event = get_event(transport, idx, 100);
    success = success and (event.isCommandStatus() or event.isCommandComplete());
    trace.trace(7, str(event));

    return success;

"""
    HCI/CCO/BV-09-C [Handling LE Set Data Length Command]

    Note: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.
"""
def hci_cco_bv_09_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEF ));
    success = advertiser.enable();

    connected = initiator.connect();
    success = success and connected;

    if connected:
        TxOctets, TxTime = 60, 592;
        status, handle = le_set_data_length(transport, upperTester, initiator.handles[0], TxOctets, TxTime, 100);
        trace.trace(6, "LE Set Data Length Command returns status: 0x%02X handle: 0x%04X" % (status, handle));
        success = success and __check_command_complete_event(transport, upperTester, trace) and (status == 0);
        """
            If parameters have changed - both upper- and lower-Tester will receive a LE Data Length Change event
        """
        if has_event(transport, upperTester, 200)[0]:
            event = get_event(transport, upperTester, 100);
            success = success and (event.subEvent == MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE);
            trace.trace(7, str(event));

        if has_event(transport, lowerTester, 200)[0]:
            event = get_event(transport, lowerTester, 100);
            success = success and (event.subEvent == MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE);
            trace.trace(7, str(event));
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = success and initiator.disconnect(0x13);

    else:
        advertiser.disable();

    return success;

"""
    HCI/CCO/BV-10-C [Handling LE Read Suggested Default Data Length Command]
"""
def hci_cco_bv_10_c(transport, idx, trace):

    status, maxTxOctets, maxTxTime = le_read_suggested_default_data_length(transport, idx, 100);
    trace.trace(6, "LE Read Suggested Default Data Length Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);

    trace.trace(6, "Maximum number of transmitted payload octets: 0x%04X (%d)" % (maxTxOctets, maxTxOctets));
    trace.trace(6, "Maximum packet transmission time: 0x%04X (%d) microseconds" % (maxTxTime, maxTxTime));

    return success;

"""
    HCI/CCO/BV-11-C [Handling LE Write Suggested Default Data Length Command]
"""
def hci_cco_bv_11_c(transport, idx, trace):

    maxTxOctetsIn, maxTxTimeIn = (0x001B + 0x00FB)//2, (0x0148 + 0x4290)//2;
    status = le_write_suggested_default_data_length(transport, idx, maxTxOctetsIn, maxTxTimeIn, 100);
    trace.trace(6, "LE Write Suggested Default Data Length Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);

    trace.trace(6, "Maximum number of transmitted payload octets: 0x%04X (%d)" % (maxTxOctetsIn, maxTxOctetsIn));
    trace.trace(6, "Maximum packet transmission time: 0x%04X (%d) microseconds" % (maxTxTimeIn, maxTxTimeIn));

    status, maxTxOctetsOut, maxTxTimeOut = le_read_suggested_default_data_length(transport, idx, 100);
    trace.trace(6, "LE Read Suggested Default Data Length Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, idx, trace) and (status == 0);

    trace.trace(6, "Maximum number of transmitted payload octets: 0x%04X (%d)" % (maxTxOctetsOut, maxTxOctetsOut));
    trace.trace(6, "Maximum packet transmission time: 0x%04X (%d) microseconds" % (maxTxTimeOut, maxTxTimeOut));

    success = success and (maxTxOctetsOut == maxTxOctetsIn) and (maxTxTimeOut == maxTxTimeIn);

    return success;

"""
    HCI/CCO/BV-12-C [Handling LE Remove Device From Resolving List Command]
"""
def hci_cco_bv_12_c(transport, idx, trace):

    peerAddress = Address(SimpleAddressType.PUBLIC, 0x123456789ABC);
    status = le_add_device_to_resolving_list(transport, idx, peerAddress.type, peerAddress.address, lowerIRK, upperIRK, 100);
    trace.trace(6, "LE Add Device to Resolving List Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);

    status = le_remove_device_from_resolving_list(transport, idx, peerAddress.type, peerAddress.address, 100);
    trace.trace(6, "LE Remove Device from Resolving List Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, idx, trace) and (status == 0);

    return success;

"""
    HCI/CCO/BV-13-C [Handling LE Clear Resolving List Command]
"""
def hci_cco_bv_13_c(transport, idx, trace):

    peerAddress = Address(SimpleAddressType.PUBLIC, 0x456789ABCDEF);
    status = le_add_device_to_resolving_list(transport, idx, peerAddress.type, peerAddress.address, lowerIRK, upperIRK, 100);
    trace.trace(6, "LE Add Device to Resolving List Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);

    status = le_clear_resolving_list(transport, idx, 100);
    trace.trace(6, "LE Clear Resolving List Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, idx, trace) and (status == 0);

    return success;

"""
    HCI/CCO/BV-14-C [Handling LE Read Resolving List Size Command]
"""
def hci_cco_bv_14_c(transport, idx, trace):

    status, listSize = le_read_resolving_list_size(transport, idx, 100);
    trace.trace(6, "LE Read Resolving List Size Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0) and (listSize > 0);
    trace.trace(6, "Resolving List Size returned: %d" % listSize);

    return success;

"""
    HCI/CCO/BV-15-C [Handling LE Set Default PHY Command]
"""
def hci_cco_bv_15_c(transport, idx, trace):

    status = le_set_default_phy(transport, idx, 3, 0, 0, 100);
    trace.trace(6, "LE Set Default PHY Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);

    return success;

"""
    HCI/CCO/BV-16-C [Handling LE Read Periodic Advertiser List Size Command]
"""
def hci_cco_bv_16_c(transport, idx, trace):

    status, listSize = le_read_periodic_advertiser_list_size(transport, idx, 100);
    trace.trace(6, "LE Read Periodic Advertiser List Size Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0) and (listSize > 0);
    trace.trace(6, "Periodic Advertiser List Size returned: %d" % listSize);

    return success;

"""
    HCI/CCO/BV-17-C [Handling Add, Remove and Clear Periodic Advertiser List Commands]
"""
def hci_cco_bv_17_c(transport, idx, trace):

    status = le_clear_periodic_advertiser_list(transport, idx, 100);
    trace.trace(6, "LE Clear Periodic Advertiser List Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);

    peerAddress = Address(SimpleAddressType.PUBLIC, 0x123456789ABC);
    status = le_add_device_to_periodic_advertiser_list(transport, idx, peerAddress.type, peerAddress.address, 1, 100);
    trace.trace(6, "LE Add Device to Periodic Advertiser List Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, idx, trace) and (status == 0);

    status = le_remove_device_from_periodic_advertiser_list(transport, idx, peerAddress.type, peerAddress.address, 1, 100);
    trace.trace(6, "LE Remove Device from Periodic Advertiser List Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, idx, trace) and (status == 0);

    status = le_remove_device_from_periodic_advertiser_list(transport, idx, peerAddress.type, peerAddress.address, 1, 100);
    trace.trace(6, "LE Remove Device from Periodic Advertiser List Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, idx, trace) and (status == 0x42);

    status = le_add_device_to_periodic_advertiser_list(transport, idx, peerAddress.type, peerAddress.address, 1, 100);
    trace.trace(6, "LE Add Device to Periodic Advertiser List Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, idx, trace) and (status == 0);

    status = le_clear_periodic_advertiser_list(transport, idx, 100);
    trace.trace(6, "LE Clear Periodic Advertiser List Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, idx, trace) and (status == 0);

    return success;

"""
    HCI/CCO/BV-18-C [Handling LE Read Transmit Power Command]
"""
def hci_cco_bv_18_c(transport, idx, trace):

    status, minTxPower, maxTxPower = le_read_transmit_power(transport, idx, 100);
    trace.trace(6, "LE Read Transmit Power Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);
    success = success and (-127 <= minTxPower) and (minTxPower <= 126) and (-127 <= maxTxPower) and (maxTxPower <= 126) and (minTxPower <= maxTxPower);
    trace.trace(6, "LE Read Transmit Power Command returned range: [%d, %d] dBm." % (minTxPower, maxTxPower));

    return success;

"""
    HCI/DDI/BV-03-C [Disable Advertising with Set Advertising Enable Command]
"""
def hci_ddi_bv_03_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( SimpleAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    ownAddress = Address( SimpleAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 5);

    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 5 );

    success = success and advertiser.disable();
    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and not scanner.qualifyReports( 1 );

    return success;

"""
    HCI/DDI/BV-04-C [Disable Scanning with Set Scan Enable Command]
"""
def hci_ddi_bv_04_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( SimpleAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    ownAddress = Address( SimpleAddressType.PUBLIC );
    scanner = Scanner(transport, upperTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 5);

    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 5 );

    scanner.monitor();
    success = success and not scanner.qualifyReports( 1 );

    success = success and advertiser.disable();

    return success;

"""
    HCI/DDI/BI-02-C [Rejecting invalid Advertising Parameters]
"""
def hci_ddi_bi_02_c(transport, upperTester, trace):

    ownAddress = Address( SimpleAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    advertiser.minInterval, advertiser.maxInterval = 32-2, 32-1;

    successA = not advertiser.enable();
    success = successA and (advertiser.status == 0x12);

    if not successA:
        advertiser.disable();

    return success;

"""
    HCI/DDI/BI-63-C [Reject Set Extended Advertising Data Command, Data Too Long, LE 1M PHY]
"""
def hci_ddi_bi_63_c(transport, upperTester, lowerTester, trace):

    Handle          = 0;
    Properties      = 0;
    PrimMinInterval = toArray(0x0140, 3); # Minimum Advertise Interval = 320 x 0.625 ms = 200.00 ms
    PrimMaxInterval = toArray(0x0140, 3); # Maximum Advertise Interval = 320 x 0.625 ms = 200.00 ms
    PrimChannelMap  = 0x07;  # Advertise on all three channels (#37, #38 and #39)
    OwnAddrType     = SimpleAddressType.PUBLIC;
    PeerAddrType    = 0;
    PeerAddress     = toArray(0, 6);
    FilterPolicy    = AdvertisingFilterPolicy.FILTER_NONE;
    TxPower         = 0;
    PrimAdvPhy      = PhysicalChannel.LE_1M; # Primary advertisement PHY is LE 1M
    SecAdvMaxSkip   = 0;     # AUX_ADV_IND shall be sent prior to the next advertising event
    SecAdvPhy       = PhysicalChannel.LE_1M;
    Sid             = 0;
    ScanReqNotifyEnable = 0; # Scan request notifications disabled

    success = preamble_ext_advertising_parameters_set(transport, upperTester, Handle, Properties, PrimMinInterval, PrimMaxInterval, \
                                                      PrimChannelMap, OwnAddrType, PeerAddrType, PeerAddress, FilterPolicy, TxPower, \
                                                      PrimAdvPhy, SecAdvMaxSkip, SecAdvPhy, Sid, ScanReqNotifyEnable, trace);
    
    if not success:
        return False;

    # Get maximum advertising data size
    status, maxADSize = le_read_maximum_advertising_data_length(transport, upperTester, 100);
    if status != 0:
        return False
    
    FragPref = 0; # The Controller may fragment all Host advertising data

    # Set fragments of advertising data until we hit maxADSize - 1
    fragmentCount = 7;
    fragmentSize = math.ceil((maxADSize-1)/(fragmentCount));
    fragmentData = random.randint(0, 256, fragmentSize);

    count = 0;
    while (count < fragmentCount):

        op = FragmentOperation.FIRST_FRAGMENT
        if (count > 0):
            op = FragmentOperation.INTERMEDIATE_FRAGMENT;
            if count == fragmentCount - 1:
                # Adjust size of last fragment to hit maxADSize - 1 exactly
                fragmentData = fragmentData[:(maxADSize - 1 - fragmentSize*6)]
        
        status = le_set_extended_advertising_data(transport, upperTester, Handle, op, FragPref, fragmentData, 100);
        if status != 0:
            return False;

        count += 1;

    # Now setting another fragment of two bytes should fail
    status = le_set_extended_advertising_data(transport, upperTester, Handle, FragmentOperation.INTERMEDIATE_FRAGMENT, FragPref, random.randint(0, 256, 2), 100);
    return status == 0x07; # Memory Capacity Exceeded expected

"""
    HCI/DDI/BI-65-C [Reject Set Extended Scan Response Data Command, Data Too Long, LE 1M PHY]
"""
def hci_ddi_bi_65_c(transport, upperTester, lowerTester, trace):

    Handle          = 0;
    Properties      = 0x02; # Scannable
    PrimMinInterval = toArray(0x0140, 3); # Minimum Advertise Interval = 320 x 0.625 ms = 200.00 ms
    PrimMaxInterval = toArray(0x0140, 3); # Maximum Advertise Interval = 320 x 0.625 ms = 200.00 ms
    PrimChannelMap  = 0x07;  # Advertise on all three channels (#37, #38 and #39)
    OwnAddrType     = SimpleAddressType.PUBLIC;
    PeerAddrType    = 0;
    PeerAddress     = toArray(0, 6);
    FilterPolicy    = AdvertisingFilterPolicy.FILTER_NONE;
    TxPower         = 0;
    PrimAdvPhy      = PhysicalChannel.LE_1M; # Primary advertisement PHY is LE 1M
    SecAdvMaxSkip   = 0;     # AUX_ADV_IND shall be sent prior to the next advertising event
    SecAdvPhy       = PhysicalChannel.LE_1M;
    Sid             = 0;
    ScanReqNotifyEnable = 0; # Scan request notifications disabled

    success = preamble_ext_advertising_parameters_set(transport, upperTester, Handle, Properties, PrimMinInterval, PrimMaxInterval, \
                                                      PrimChannelMap, OwnAddrType, PeerAddrType, PeerAddress, FilterPolicy, TxPower, \
                                                      PrimAdvPhy, SecAdvMaxSkip, SecAdvPhy, Sid, ScanReqNotifyEnable, trace);
    
    if not success:
        return False;

    # Get maximum advertising data size
    status, maxADSize = le_read_maximum_advertising_data_length(transport, upperTester, 100);
    if status != 0:
        return False;
    
    FragPref = 0; # The Controller may fragment all Host advertising data

    # Set fragments of advertising data until we hit maxADSize - 1
    fragmentCount = 7;
    fragmentSize = math.ceil((maxADSize-1)/(fragmentCount));
    fragmentData = random.randint(0, 256, fragmentSize);

    count = 0;
    while (count < fragmentCount):

        op = FragmentOperation.FIRST_FRAGMENT
        if (count > 0):
            op = FragmentOperation.INTERMEDIATE_FRAGMENT;
            if count == fragmentCount - 1:
                # Adjust size of last fragment to hit maxADSize - 1 exactly
                fragmentData = fragmentData[:(maxADSize - 1 - fragmentSize*6)]
        
        status = le_set_extended_scan_response_data(transport, upperTester, Handle, op, FragPref, fragmentData, 100);
        if status != 0:
            return False;

        count += 1;

    # Now setting another fragment of two bytes should fail
    status = le_set_extended_scan_response_data(transport, upperTester, Handle, FragmentOperation.INTERMEDIATE_FRAGMENT, FragPref, random.randint(0, 256, 2), 100);
    return status == 0x07; # Memory Capacity Exceeded expected

"""
    HCI/HFC/BV-04-C [Events enabled by LE Set Event Mask Command]
"""
def hci_hfc_bv_04_c(transport, upperTester, lowerTester, trace):

    """ Bit:   5  4  4  3  2  1  0  0
               6  8  0  2  4  6  8  0
            0x20 00 00 00 00 00 80 10 ~ Bits 4, 15, 61 (Disconnection Complete Event, Hardware Error Event, LE Meta Event)
    """
    events = [0x10, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20];

    status = set_event_mask(transport, upperTester, events, 100);
    trace.trace(6, "Set Event Mask Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, upperTester, trace) and (status == 0);

    """ Bit:  5  4  4  3  2  1  0  0
              6  8  0  2  4  6  8  0
           0x00 00 00 00 00 07 FF FD ~ All except 'LE Channel Selection Algorithm Event and LE Advertising Report Event'
    """
    events = [0xFD, 0xFF, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00];

    status = le_set_event_mask(transport, upperTester, events, 100);
    trace.trace(6, "LE Set Event Mask Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, upperTester, trace) and (status == 0);

    """
    status = le_set_event_mask(transport, lowerTester, events, 100);
    trace.trace(6, "LE Set Event Mask Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, lowerTester, trace) and (status == 0);
    """

    ownAddress = Address( SimpleAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    ownAddress = Address( SimpleAddressType.PUBLIC );
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 5, 5);
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEF ));

    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and not scanner.qualifyResponses( 5 );
    success = success and not scanner.qualifyReports( 5 );

    transport.wait(100);

    connected = initiator.connect();
    success = success and connected;

    transport.wait(500);

    if connected:
        success = success and initiator.disconnect(0x13);

    return success;

"""
    HCI/CM/BV-01-C [Handling LE Read Peer Resolvable Address Command]
"""
def hci_cm_bv_01_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester and upperTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    ownAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[upperTester].add( peerAddress, lowerIRK );
    success = success and RPAs[lowerTester].add( ownAddress, upperIRK );

    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout(60) and RPAs[lowerTester].timeout(60);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    for iutRole in [ Role.CENTRAL, Role.PERIPHERAL ]:
        ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEF if iutRole is Role.CENTRAL else 0x123456789ABC);
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC if iutRole is Role.CENTRAL else 0x456789ABCDEF);
        if iutRole == Role.CENTRAL:
            advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress);
        else:
            advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress);
        advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

        initiatorAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
        if iutRole == Role.CENTRAL:
            initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( IdentityAddressType.PUBLIC_IDENTITY, toNumber(ownAddress.address) ));
        else:
            initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( IdentityAddressType.PUBLIC_IDENTITY, toNumber(ownAddress.address) ));
        success = success and advertiser.enable();

        connected = initiator.connect();
        success = success and connected;

        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
        status, RPA = le_read_peer_resolvable_address(transport, upperTester, peerAddress.type, peerAddress.address, 100);
        trace.trace(6, "LE Read Peer Resolvable Address Command returns status: 0x%02X RPA: %s" % (status, formatAddress(RPA)));
        success = success and __check_command_complete_event(transport, upperTester, trace) and (status == 0);

        if iutRole == Role.CENTRAL:
            success = success and (initiator.peerRPA() == RPA);
            if initiator.peerRPA() != RPA:
                print((initiator.peerRPA()));
                print(RPA);
                trace.trace(5, "Expected: %s Received: %s" % (Address(None, initiator.peerRPA()), Address(None, RPA)));
        else:
            success = success and (initiator.localRPA() == RPA);
            if initiator.localRPA() != RPA:
                trace.trace(5, "Expected: %s Received: %s" % (Address(None, initiator.localRPA()), Address(None, RPA)));

        transport.wait(200);

        if connected:
            connected = not initiator.disconnect(0x13);
            success = success and not connected;

    return success;

"""
    HCI/CM/BV-02-C [Handling LE Read Local Resolvable Address Command]
"""
def hci_cm_bv_02_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester and upperTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    ownAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[upperTester].add( peerAddress, lowerIRK );
    success = success and RPAs[lowerTester].add( ownAddress, upperIRK );

    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout(60) and RPAs[lowerTester].timeout(60);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    for iutRole in [ Role.CENTRAL, Role.PERIPHERAL ]:
        ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEF if iutRole is Role.CENTRAL else 0x123456789ABC);
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC if iutRole is Role.CENTRAL else 0x456789ABCDEF);
        if iutRole == Role.CENTRAL:
            advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress);
        else:
            advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress);
        advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

        initiatorAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
        if iutRole == Role.CENTRAL:
            initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( IdentityAddressType.PUBLIC_IDENTITY, toNumber(ownAddress.address) ));
        else:
            initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( IdentityAddressType.PUBLIC_IDENTITY, toNumber(ownAddress.address) ));
        success = success and advertiser.enable();

        connected = initiator.connect();
        success = success and connected;

        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
        status, RPA = le_read_local_resolvable_address(transport, upperTester, peerAddress.type, peerAddress.address, 100);
        trace.trace(6, "LE Read Local Resolvable Address Command returns status: 0x%02X RPA: %s" % (status, formatAddress(RPA)));
        success = success and __check_command_complete_event(transport, upperTester, trace) and (status == 0);

        if iutRole == Role.CENTRAL:
            success = success and (initiator.localRPA() == RPA);
        else:
            success = success and (initiator.peerRPA() == RPA);

        transport.wait(200);

        if connected:
            connected = not initiator.disconnect(0x13);
            success = success and not connected;

    return success;

"""
    HCI/CM/BV-03-C [Handling LE Read PHY Command]
"""
def hci_cm_bv_03_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEF ));
    success = advertiser.enable();

    connected = initiator.connect();
    success = success and connected;

    if success:
        status, handle, TxPhy, RxPhy = le_read_phy(transport, upperTester, initiator.handles[0], 100);
        trace.trace(6, "LE Read PHY Command returns status: 0x%02X handle: 0x%04X TxPHY: %d RxPHY: %d" % (status, handle, TxPhy, RxPhy));
        success = success and __check_command_complete_event(transport, upperTester, trace) and (status == 0);

    if connected:
        connected = not initiator.disconnect(0x13);
        success = success and not connected;

    return success;

"""
    HCI/DSU/BV-02-C [Reset Command received in Advertising State]
"""
def hci_dsu_bv_02_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( SimpleAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    ownAddress = Address( SimpleAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 5);

    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 5 );

    status = reset(transport, upperTester, 100);
    trace.trace(6, "Reset Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, upperTester, trace) and (status == 0);

    """
        Verify that the IUT has stopped Advertising
    """
    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and not scanner.qualifyReports( 5 );

    return success;

"""
    HCI/DSU/BV-03-C [Reset Command received in Peripheral Role]
"""
def hci_dsu_bv_03_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABC ));
    success = advertiser.enable();

    success = success and initiator.connect();

    transport.wait(200);

    status = reset(transport, upperTester, 100);
    trace.trace(6, "Reset Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, upperTester, trace) and (status == 0);

    """
       There might be pending disconnect events lying around...
    """
    while has_event(transport, lowerTester, 200)[0]:
        event = get_event(transport, lowerTester, 100);
        trace.trace(7, str(event));
        if event.event == Events.BT_HCI_EVT_DISCONN_COMPLETE:
            status, handle, reason = event.decode();
            success = success and (reason == 0x08); # Connection Timeout

    while has_event(transport, upperTester, 200)[0]:
        event = get_event(transport, upperTester, 100);
        trace.trace(7, str(event));
        if event.event == Events.BT_HCI_EVT_DISCONN_COMPLETE:
            status, handle, reason = event.decode();
            success = success and (reason == 0x08); # Connection Timeout

    return success;

"""
    HCI/DSU/BV-04-C [Reset Command received in Scanning State]
"""
def hci_dsu_bv_04_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( SimpleAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    ownAddress = Address( SimpleAddressType.PUBLIC );
    scanner = Scanner(transport, upperTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 5);

    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 5 );

    status = reset(transport, upperTester, 100);
    trace.trace(6, "Reset Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, upperTester, trace) and (status == 0);

    """
        Verify that the IUT has stopped Advertising
    """
    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and not scanner.qualifyReports( 5 );

    return success;

"""
    HCI/DSU/BV-05-C [Reset Command received in Initiating State]
"""
def hci_dsu_bv_05_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEF ));

    success = initiator.preConnect();

    status = reset(transport, upperTester, 100);
    trace.trace(6, "Reset Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, upperTester, trace) and (status == 0);

    success = success and advertiser.enable();
    success = success and not initiator.postConnect();
    success = success and advertiser.disable();

    return success;

"""
    HCI/DSU/BV-06-C [Reset Command received in Central Role]
"""
def hci_dsu_bv_06_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEF ));
    success = advertiser.enable();

    success = success and initiator.connect();

    transport.wait(200);

    status = reset(transport, upperTester, 100);
    trace.trace(6, "Reset Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, upperTester, trace) and (status == 0);

    return success;

__tests__ = {
    "HCI/CCO/BV-07-C": [ hci_cco_bv_07_c, 'BR/EDR Commands Not Supported on LE Device' ],
    "HCI/CCO/BV-09-C": [ hci_cco_bv_09_c, 'Handling LE Set Data Length Command' ],
    "HCI/CCO/BV-10-C": [ hci_cco_bv_10_c, 'Handling LE Read Suggested Default Data Length Command' ],
    "HCI/CCO/BV-11-C": [ hci_cco_bv_11_c, 'Handling LE Write Suggested Default Data Length Command' ],
    "HCI/CCO/BV-12-C": [ hci_cco_bv_12_c, 'Handling LE Remove Device From Resolving List Command' ],
    "HCI/CCO/BV-13-C": [ hci_cco_bv_13_c, 'Handling LE Clear Resolving List Command' ],
    "HCI/CCO/BV-14-C": [ hci_cco_bv_14_c, 'Handling LE Read Resolving List Size Command' ],
    "HCI/CCO/BV-15-C": [ hci_cco_bv_15_c, 'Handling LE Set Default PHY Command' ],
#   "HCI/CCO/BV-16-C": [ hci_cco_bv_17_c, 'Handling LE Read Periodic Advertiser List Size Command' ],
#   "HCI/CCO/BV-17-C": [ hci_cco_bv_17_c, 'Handling Add, Remove and Clear Periodic Advertiser List Commands' ],
    "HCI/CCO/BV-18-C": [ hci_cco_bv_18_c, 'Handling LE Read Transmit Power Command' ],
    "HCI/CFC/BV-02-C": [ hci_cfc_bv_02_c, 'Reported Buffer Size' ],
    "HCI/CIN/BV-01-C": [ hci_cin_bv_01_c, 'Features returned by Read Local Supported Features Command' ],
    "HCI/CIN/BV-03-C": [ hci_cin_bv_03_c, 'Supported Commands returned by Read Local Supported Commands Command' ],
    "HCI/CIN/BV-04-C": [ hci_cin_bv_04_c, 'Versions returned by Read Local Version Information Command' ],
    "HCI/CIN/BV-06-C": [ hci_cin_bv_06_c, 'Reported Filter Accept List Size' ],
    "HCI/CIN/BV-09-C": [ hci_cin_bv_09_c, 'Feature Bits returned by Read LE Public Key Validation Feature Bit' ],
    "HCI/CM/BV-01-C":  [ hci_cm_bv_01_c,  'Handling LE Read Peer Resolvable Address Command' ],
    "HCI/CM/BV-02-C":  [ hci_cm_bv_02_c,  'Handling LE Read Local Resolvable Address Command' ],
    "HCI/CM/BV-03-C":  [ hci_cm_bv_03_c,  'Handling LE Read PHY Command' ],
    "HCI/DDI/BI-02-C": [ hci_ddi_bi_02_c, 'Rejecting invalid Advertising Parameters' ],
    "HCI/DDI/BI-63-C": [ hci_ddi_bi_63_c, 'Reject Set Extended Advertising Data Command, Data Too Long, LE 1M PHY' ],
    "HCI/DDI/BI-65-C": [ hci_ddi_bi_65_c, 'Reject Set Extended Scan Response Data Command, Data Too Long, LE 1M PHY' ],
    "HCI/DDI/BV-03-C": [ hci_ddi_bv_03_c, 'Disable Advertising with Set Advertising Enable Command' ],
    "HCI/DDI/BV-04-C": [ hci_ddi_bv_04_c, 'Disable Scanning with Set Scan Enable Command' ],
    "HCI/DSU/BV-02-C": [ hci_dsu_bv_02_c, 'Reset Command received in Advertising State' ],
    "HCI/DSU/BV-03-C": [ hci_dsu_bv_03_c, 'Reset Command received in Peripheral Role' ],
    "HCI/DSU/BV-04-C": [ hci_dsu_bv_04_c, 'Reset Command received in Scanning State' ],
    "HCI/DSU/BV-05-C": [ hci_dsu_bv_05_c, 'Reset Command received in Initiating State' ],
    "HCI/DSU/BV-06-C": [ hci_dsu_bv_06_c, 'Reset Command received in Central Role' ],
    "HCI/GEV/BV-01-C": [ hci_gev_bv_01_c, 'Status return for Unsupported Commands' ],
    "HCI/HFC/BV-04-C": [ hci_hfc_bv_04_c, 'Events enabled by LE Set Event Mask Command' ]
};

_maxNameLength = max([ len(key) for key in __tests__ ]);

_spec = { key: TestSpec(name = key, number_devices = 2, description = "#[" + __tests__[key][1] + "]", test_private = __tests__[key][0]) for key in __tests__ };

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
def run_a_test(args, transport, trace, test_spec, device_dumps):
    try:
        success = preamble(transport, trace);
    except Exception as e:
        trace.trace(3, "Preamble generated exception: %s" % str(e));
        success = False;

    trace.trace(2, "%-*s %s test started..." % (_maxNameLength, test_spec.name, test_spec.description[1:]));
    test_f = test_spec.test_private;
    try:
        if test_f.__code__.co_argcount > 4:
            success = success and test_f(transport, 0, 1, trace, device_dumps);
        elif test_f.__code__.co_argcount > 3:
            success = success and test_f(transport, 0, 1, trace);
        else:
            success = success and test_f(transport, 0, trace);
    except Exception as e:
        import traceback
        traceback.print_exc()
        trace.trace(3, "Test generated exception: %s" % str(e));
        success = False;

    return not success
