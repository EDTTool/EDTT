# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

import random;
import os;
from enum import IntEnum;
from components.utils import *;
from components.basic_commands import *;
from components.address import *;
from components.resolvable import *;
from components.advertiser import *;
from components.scanner import *;
from components.initiator import *;
from components.preambles import *;
from components.test_spec import TestSpec;

global lowerIRK, upperIRK, lowerRandomAddress, upperRandomAddress;

class Role(IntEnum):
    MASTER = 0
    SLAVE  = 1
    
def __check_command_complete_event(transport, idx, trace):
    eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
    showEvent(event, eventData, trace);
    return (event == Events.BT_HCI_EVT_CMD_COMPLETE);

"""
    HCI/GEV/1-C [Status return for Unsupported Commands]
"""
def hci_gev_1_c(transport, idx, trace):

    NumRsp, length, lap = 0, 1, toArray(0x9E8B00, 3);

    status = inquire(transport, idx, lap, length, NumRsp, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1);

    FlowEnable = 0;
        
    status = set_controller_to_host_flow_control(transport, idx, FlowEnable, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    AclMtu, ScoMtu, AclPkts, ScoPkts = 23, 23, 6, 6;

    status = host_buffer_size(transport, idx, AclMtu, ScoMtu, AclPkts, ScoPkts, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    NumHandles = 0;
    HHandle = [0 for i in range(NumHandles)];
    HCount = [0 for i in range(NumHandles)];

    status = host_number_of_completed_packets(transport, idx, NumHandles, HHandle, HCount, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    status = read_buffer_size(transport, idx, 100)[0];
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    handle = 0;
        
    status = read_rssi(transport, idx, handle, 100)[0];
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    le, simul = 0, 0;
        
    status = write_le_host_support(transport, idx, le, simul, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    handle, props, PrimChannelMap, OwnAddrType, PeerAddrType = 0, 0, 0, 0, 0;
    PrimMinInterval = [0 for _ in range(3)];
    PrimMaxInterval = [0 for _ in range(3)];
    AVal = [0 for _ in range(6)];
    FilterPolicy, TxPower, PrimAdvPhy, SecAdvMaxSkip, SecAdvPhy, sid, ScanReqNotifyEnable = 0, 0, 0, 0, 0, 0;

    status = le_set_extended_advertising_parameters(transport, idx, handle, props, PrimMinInterval, PrimMaxInterval, PrimChannelMap, \
                                                    OwnAddrType, PeerAddrType, AVal, FilterPolicy, TxPower, PrimAdvPhy, SecAdvMaxSkip, \
                                                    SecAdvPhy, sid, ScanReqNotifyEnable, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    handle, op, FragPref, dataLength = 0, 0, 0, 0;
    data = [0 for _ in range(251)];

    status = le_set_extended_advertising_data(transport, idx, handle, op, FragPref, dataLength, data, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    handle, op, FragPref, dataLength = 0, 0, 0, 0;
    data = [0 for _ in range(251)];
        
    status = le_set_extended_scan_response_data(transport, idx, handle, op, FragPref, dataLength, data, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    enable, SetNum = 0, 0;
    SHandle = [0 for i in range(SetNum)];
    SDuration = [0 for i in range(SetNum)];
    SMaxExtAdvEvts = [0 for i in range(SetNum)];
    
    status = le_set_extended_advertising_enable(transport, idx, enable, SetNum, SHandle, SDuration, SMaxExtAdvEvts, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    status = le_read_maximum_advertising_data_length(transport, idx, 100)[0];
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    status = le_read_number_of_supported_advertising_sets(transport, idx, 100)[0];
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    handle = 0;

    status = le_remove_advertising_set(transport, idx, handle, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    status = le_clear_advertising_sets(transport, idx, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    handle, MinInterval, MaxInterval, props = 0, 0, 0, 0;
        
    status = le_set_periodic_advertising_parameters(transport, idx, handle, MinInterval, MaxInterval, props, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    handle, op, dataLength = 0, 0, 251;
    data = [0 for i in range(dataLength)];

    status = le_set_periodic_advertising_data(transport, idx, handle, op, dataLength, data, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    handle, enable = 0, 0;
    
    status = le_set_periodic_advertising_enable(transport, idx, enable, handle, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    OwnAddrType, FilterPolicy, phys = 0, 0, 0;
    PType = [0 for i in range(phys)];
    PInterval = [0 for i in range(phys)];
    PWindow = [0 for i in range(phys)];

    status = le_set_extended_scan_parameters(transport, idx, OwnAddrType, FilterPolicy, phys, PType, PInterval, PWindow, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    enable, FilterDup, duration, period = 0, 0, 0, 0;

    status = le_set_extended_scan_enable(transport, idx, enable, FilterDup, duration, period, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

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
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    FilterPolicy, sid, AddrType, skip, SyncTimeout, unused = 0, 0, 0, 0, 0, 0;
    AVal = [0 for i in range(6)];

    status = le_periodic_advertising_create_sync(transport, idx, FilterPolicy, sid, AddrType, AVal, skip, SyncTimeout, unused, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    status = le_periodic_advertising_create_sync_cancel(transport, idx, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    handle = 0;
        
    status = le_periodic_advertising_terminate_sync(transport, idx, handle, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    AddrType, sid = 0, 0;
    AVal = [0 for i in range(6)];

    status = le_add_device_to_periodic_advertiser_list(transport, idx, AddrType, AVal, sid, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    AddrType, sid = 0;
    AVal = [0 for i in range(6)];

    status = le_remove_device_from_periodic_advertiser_list(transport, idx, AddrType, AVal, sid, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    status = le_clear_periodic_advertiser_list(transport, idx, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    status = le_read_periodic_advertiser_list_size(transport, idx, 100)[0];
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

    status = le_read_rf_path_compensation(transport, idx, 100)[0];
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;
        
    TxPathComp, RxPathComp = 0, 0;
        
    status = le_write_rf_path_compensation(transport, idx, TxPathComp, RxPathComp, 100);
    success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;
        
    return success;

"""
    HCI/CFC/2-C [Reported Buffer Size]
"""
def hci_cfc_2_c(transport, idx, trace):

    status, LeMaxLen, LeMaxNum = le_read_buffer_size(transport, idx, 100);
    trace.trace(6, "LE Read Buffer Size Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);

    if LeMaxLen == 0 and LeMaxNum == 0:
        status, AclMaxLen, ScoMaxLen, AclMaxNum, ScoMaxNum = read_buffer_size(transport, idx, 100);
        trace.trace(6, "Read Buffer Size Command returns status: 0x%02X" % status);
        success = success and __check_command_complete_event(transport, idx, trace) and (status == 0);

    return success;

"""
    HCI/COI/1-C [Features returned by Read Local Supported Features Command]
"""
def hci_coi_1_c(transport, idx, trace):

    status, features = read_local_supported_features(transport, idx, 100);
    trace.trace(6, "Read Local Supported Features Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);
    if success:
        showFeatures(features, trace);

    return success;

"""
    HCI/COI/3-C [Supported Commands returned by Read Local Supported Commands Command]
"""
def hci_coi_3_c(transport, idx, trace):

    status, commands = read_local_supported_commands(transport, idx, 100);
    trace.trace(6, "Read Local Supported Commands Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);
    if success:
        showCommands(commands, trace);

    return success;

"""
    HCI/COI/4-C [Versions returned by Read Local Version Information Command]
"""
def hci_coi_4_c(transport, idx, trace):

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
    HCI/COI/5-C [Reported White List Size]
"""
def hci_coi_5_c(transport, idx, trace):

    status = le_clear_white_list(transport, idx, 100);
    trace.trace(6, "LE Clear White List Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);

    status, WlSize = le_read_white_list_size(transport, idx, 100);
    trace.trace(6, "LE Read White List Size Command returns status: 0x%02X list size: %i" % (status, WlSize));
    success = success and __check_command_complete_event(transport, idx, trace) and (status == 0);

    for n in range(WlSize+1):
        AddrType = 0;
        AVal = [random.randint(0,255) for _ in range(6)];
        if n < WlSize:
            lastAVal = AVal
        status = le_add_device_to_white_list(transport, idx, AddrType, AVal, 100);
        trace.trace(6, "LE Add Device to White List Command returns status: 0x%02X" % status);
        success = success and __check_command_complete_event(transport, idx, trace) and ((status == 0) if n < WlSize else (status == 7));

        status = le_remove_device_from_white_list(transport, idx, AddrType, lastAVal, 100);    
        trace.trace(6, "LE Remove Device from White List Command returns status: 0x%02X" % status);
        success = success and __check_command_complete_event(transport, idx, trace) and (status == 0);

        status = le_add_device_to_white_list(transport, idx, AddrType, lastAVal, 100);
        trace.trace(6, "LE Add Device to White List Command returns status: 0x%02X" % status);
        success = success and __check_command_complete_event(transport, idx, trace) and (status == 0);

    return success;

"""
    HCI/COI/7-C [Feature Bits returned by Read LE Public Key Validation Feature Bit]
"""
def hci_coi_7_c(transport, idx, trace):

    status, features = le_read_local_supported_features(transport, idx, 100);
    trace.trace(6, "LE Read Local Supported Features Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);
    if success:
        showLEFeatures(features, trace);

    return success;
    
"""
    HCI/COC/6-C [BR/EDR Commands Not Supported on LE Device]
"""
def hci_coc_6_c(transport, idx, trace):

    status = inquire(transport, idx, toArray(0x9E8B00, 3), 1, 1, 100);
    trace.trace(6, "Inquire Command returns status: 0x%02X" % status);
    success = status == 1; # Unknown HCI Command (0x01)
    eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
    success = success and (event == Events.BT_HCI_EVT_CMD_STATUS or event == Events.BT_HCI_EVT_CMD_COMPLETE);
    showEvent(event, eventData, trace);

    return success;

"""
    HCI/COC/8-C [Handling LE Set Data Length Command]

    Note: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.
"""
def hci_coc_8_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));
    success = advertiser.enable();

    connected = initiator.connect();
    success = success and connected;

    if connected:
        TxOctets, TxTime = 60, 728;
        status, handle = le_set_data_length(transport, upperTester, initiator.handles[0], TxOctets, TxTime, 100);
        trace.trace(6, "LE Set Data Length Command returns status: 0x%02X handle: 0x%04X" % (status, handle));
        success = success and __check_command_complete_event(transport, upperTester, trace) and (status == 0);
        """
            If parameters have changed - both upper- and lower-Tester will receive a LE Data Length Change event
        """
        if has_event(transport, upperTester, 200):
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
            success = success and (subEvent == MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE);
            showEvent(event, eventData, trace);
        
        if has_event(transport, lowerTester, 200):
            eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
            success = success and (subEvent == MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE);
            showEvent(event, eventData, trace);
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = success and initiator.disconnect(0x3E);

    else:
        advertiser.disable();

    return success;

"""
    HCI/COC/9-C [Handling LE Read Suggested Default Data Length Command]
"""
def hci_coc_9_c(transport, idx, trace):

    status, maxTxOctets, maxTxTime = le_read_suggested_default_data_length(transport, idx, 100);
    trace.trace(6, "LE Read Suggested Default Data Length Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);

    trace.trace(6, "Maximum number of transmitted payload octets: 0x%04X (%d)" % (maxTxOctets, maxTxOctets));
    trace.trace(6, "Maximum packet transmission time: 0x%04X (%d) microseconds" % (maxTxTime, maxTxTime));

    return success;

"""
    HCI/COC/10-C [Handling LE Write Suggested Default Data Length Command]
"""
def hci_coc_10_c(transport, idx, trace):

    maxTxOctetsIn, maxTxTimeIn = (0x001B + 0x00FB)/2, (0x0148 + 0x4290)/2;
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
    HCI/COC/11-C [Handling LE Remove Device From Resolving List Command]
"""
def hci_coc_11_c(transport, idx, trace):

    peerAddress = Address(SimpleAddressType.PUBLIC, 0x123456789ABCL);
    status = le_add_device_to_resolving_list(transport, idx, peerAddress.type, peerAddress.address, lowerIRK, upperIRK, 100);
    trace.trace(6, "LE Add Device to Resolving List Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);

    status = le_remove_device_from_resolving_list(transport, idx, peerAddress.type, peerAddress.address, 100);
    trace.trace(6, "LE Remove Device from Resolving List Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, idx, trace) and (status == 0);

    return success;

"""
    HCI/COC/12-C [Handling LE Clear Resolving List Command]
"""
def hci_coc_12_c(transport, idx, trace):

    peerAddress = Address(SimpleAddressType.PUBLIC, 0x456789ABCDEFL);
    status = le_add_device_to_resolving_list(transport, idx, peerAddress.type, peerAddress.address, lowerIRK, upperIRK, 100);
    trace.trace(6, "LE Add Device to Resolving List Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);

    status = le_clear_resolving_list(transport, idx, 100);
    trace.trace(6, "LE Clear Resolving List Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, idx, trace) and (status == 0);

    return success;

"""
    HCI/COC/13-C [Handling LE Read Resolving List Size Command]
"""
def hci_coc_13_c(transport, idx, trace):

    status, listSize = le_read_resolving_list_size(transport, idx, 100);
    trace.trace(6, "LE Read Resolving List Size Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0) and (listSize > 0);
    trace.trace(6, "Resolving List Size returned: %d" % listSize);

    return success;

"""
    HCI/COC/14-C [Handling LE Set Default PHY Command]
"""
def hci_coc_14_c(transport, idx, trace):

    status = le_set_default_phy(transport, idx, 3, 0, 0, 100);
    trace.trace(6, "LE Set Default PHY Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);

    return success;

"""
    HCI/COC/15-C [Handling LE Read Periodic Advertiser List Size Command]
"""
def hci_coc_15_c(transport, idx, trace):

    status, listSize = le_read_periodic_advertiser_list_size(transport, idx, 100);
    trace.trace(6, "LE Read Periodic Advertiser List Size Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0) and (listSize > 0);
    trace.trace(6, "Periodic Advertiser List Size returned: %d" % listSize);

    return success;

"""
    HCI/COC/16-C [Handling Add, Remove and Clear Periodic Advertiser List Commands]
"""
def hci_coc_16_c(transport, idx, trace):

    status = le_clear_periodic_advertiser_list(transport, idx, 100);
    trace.trace(6, "LE Clear Periodic Advertiser List Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);

    peerAddress = Address(SimpleAddressType.PUBLIC, 0x123456789ABCL);
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
    HCI/COC/17-C [Handling LE Read Transmit Power Command]
"""
def hci_coc_17_c(transport, idx, trace):

    status, minTxPower, maxTxPower = le_read_transmit_power(transport, idx, 100);
    trace.trace(6, "LE Read Transmit Power Command returns status: 0x%02X" % status);
    success = __check_command_complete_event(transport, idx, trace) and (status == 0);
    success = success and (-127 <= minTxPower) and (minTxPower <= 126) and (-127 <= maxTxPower) and (maxTxPower <= 126) and (minTxPower <= maxTxPower);
    trace.trace(6, "LE Read Transmit Power Command returned range: [%d, %d] dBm." % (minTxPower, maxTxPower));

    return success;

"""
    HCI/DED/3-C [Disable Advertising with Set Advertising Enable Command]
"""
def hci_ded_3_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( SimpleAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
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
    HCI/DED/4-C [Disable Scanning with Set Scan Enable Command]
"""
def hci_ded_4_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( SimpleAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
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
    HCI/DED/7-C [Rejecting invalid Advertising Parameters]
"""
def hci_ded_7_c(transport, upperTester, trace):

    ownAddress = Address( SimpleAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    advertiser.minInterval, advertiser.maxInterval = 32-2, 32-1;
        
    successA = not advertiser.enable();
    successA = successA and (advertiser.status == 0x12);

    if not successA:
        advertiser.disable();

    advertiser.minInterval, advertiser.maxInterval = 32+1, 32;
        
    successB = not advertiser.enable();
    successB = successB and (advertiser.status == 0x11);

    success = successA and successB;
        
    return success;

"""
    HCI/HFC/4-C [Events enabled by LE Set Event Mask Command]
"""
def hci_hfc_4_c(transport, upperTester, lowerTester, trace):

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
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    ownAddress = Address( SimpleAddressType.PUBLIC );
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 5, 5);
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

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
        success = success and initiator.disconnect(0x3E);

    return success;

"""
    HCI/LCM/1-C [Handling LE Read Peer Resolvable Address Command]
"""
def hci_lcm_1_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester and upperTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    ownAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[upperTester].add( peerAddress, lowerIRK );
    success = success and RPAs[lowerTester].add( ownAddress, upperIRK );

    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout(60) and RPAs[lowerTester].timeout(60);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    for iutRole in [ Role.MASTER, Role.SLAVE ]:
        ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL if iutRole is Role.MASTER else 0x123456789ABCL);
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL if iutRole is Role.MASTER else 0x456789ABCDEFL);
        if iutRole == Role.MASTER:        
            advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress);
        else:
            advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress);
        advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        
        initiatorAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
        if iutRole == Role.MASTER:        
            initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( IdentityAddressType.PUBLIC_IDENTITY, toNumber(ownAddress.address) ));
        else:
            initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( IdentityAddressType.PUBLIC_IDENTITY, toNumber(ownAddress.address) ));
        success = success and advertiser.enable();

        connected = initiator.connect();
        success = success and connected;

        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );        
        status, RPA = le_read_peer_resolvable_address(transport, upperTester, peerAddress.type, peerAddress.address, 100);
        trace.trace(6, "LE Read Peer Resolvable Address Command returns status: 0x%02X RPA: %s" % (status, formatAddress(RPA)));
        success = success and __check_command_complete_event(transport, upperTester, trace) and (status == 0);

        if iutRole == Role.MASTER:        
            success = success and (initiator.peerRPA() == RPA);
        else:
            success = success and (initiator.localRPA() == RPA);
        
        transport.wait(200);
      
        if connected:
            connected = not initiator.disconnect(0x3E);
            success = success and not connected;

    return success;

"""
    HCI/LCM/2-C [Handling LE Read Local Resolvable Address Command]
"""
def hci_lcm_2_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester and upperTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    ownAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[upperTester].add( peerAddress, lowerIRK );
    success = success and RPAs[lowerTester].add( ownAddress, upperIRK );

    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout(60) and RPAs[lowerTester].timeout(60);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    for iutRole in [ Role.MASTER, Role.SLAVE ]:
        ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL if iutRole is Role.MASTER else 0x123456789ABCL);
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL if iutRole is Role.MASTER else 0x456789ABCDEFL);
        if iutRole == Role.MASTER:        
            advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress);
        else:
            advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress);
        advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        
        initiatorAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
        if iutRole == Role.MASTER:        
            initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( IdentityAddressType.PUBLIC_IDENTITY, toNumber(ownAddress.address) ));
        else:
            initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( IdentityAddressType.PUBLIC_IDENTITY, toNumber(ownAddress.address) ));
        success = success and advertiser.enable();

        connected = initiator.connect();
        success = success and connected;

        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );        
        status, RPA = le_read_local_resolvable_address(transport, upperTester, peerAddress.type, peerAddress.address, 100);
        trace.trace(6, "LE Read Local Resolvable Address Command returns status: 0x%02X RPA: %s" % (status, formatAddress(RPA)));
        success = success and __check_command_complete_event(transport, upperTester, trace) and (status == 0);

        if iutRole == Role.MASTER:        
            success = success and (initiator.localRPA() == RPA);
        else:
            success = success and (initiator.peerRPA() == RPA);
        
        transport.wait(200);
      
        if connected:
            connected = not initiator.disconnect(0x3E);
            success = success and not connected;

    return success;

"""
    HCI/LCM/3-C [Handling LE Read PHY Command]
"""
def hci_lcm_3_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));
    success = advertiser.enable();

    connected = initiator.connect();
    success = success and connected;

    if success:
        status, handle, TxPhy, RxPhy = le_read_phy(transport, upperTester, initiator.handles[0], 100);
        trace.trace(6, "LE Read PHY Command returns status: 0x%02X handle: 0x%04X TxPHY: %d RxPHY: %d" % (status, handle, TxPhy, RxPhy));
        success = success and __check_command_complete_event(transport, upperTester, trace) and (status == 0);

    if connected:
        connected = not initiator.disconnect(0x3E);
        success = success and not connected;

    return success;

"""
    HCI/DES/2-C [Reset Command received in Advertising State]
"""
def hci_des_2_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( SimpleAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
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
    HCI/DES/3-C [Reset Command received in Slave Role]
"""
def hci_des_3_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    success = advertiser.enable();

    success = success and initiator.connect();

    transport.wait(200);
        
    status = reset(transport, upperTester, 100);
    trace.trace(6, "Reset Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, upperTester, trace) and (status == 0);

    """
       There might be pending disconnect events lying around...
    """
    while has_event(transport, lowerTester, 200):
        eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
        showEvent(event, eventData, trace);
        if event == Events.BT_HCI_EVT_DISCONN_COMPLETE:
            status, handle, reason = disconnectComplete(eventData);
            success = success and (reason == 0x08); # Connection Timeout

    while has_event(transport, upperTester, 200):
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
        showEvent(event, eventData, trace);
        if event == Events.BT_HCI_EVT_DISCONN_COMPLETE:
            status, handle, reason = disconnectComplete(eventData);
            success = success and (reason == 0x08); # Connection Timeout
        
    return success;

"""
    HCI/DES/4-C [Reset Command received in Scanning State]
"""
def hci_des_4_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( SimpleAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
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
    HCI/DES/5-C [Reset Command received in Initiating State]
"""
def hci_des_5_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = initiator.preConnect();

    status = reset(transport, upperTester, 100);
    trace.trace(6, "Reset Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, upperTester, trace) and (status == 0);

    success = success and advertiser.enable();
    success = success and not initiator.postConnect();
    success = success and advertiser.disable();

    return success;

"""
    HCI/DES/6-C [Reset Command received in Master Role]
"""
def hci_des_6_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));
    success = advertiser.enable();

    success = success and initiator.connect();

    transport.wait(200);
        
    status = reset(transport, upperTester, 100);
    trace.trace(6, "Reset Command returns status: 0x%02X" % status);
    success = success and __check_command_complete_event(transport, upperTester, trace) and (status == 0);
        
    return success;

__tests__ = {
    "HCI/COC/6-C":  [ hci_coc_6_c,  'BR/EDR Commands Not Supported on LE Device' ],
    "HCI/COC/8-C":  [ hci_coc_8_c,  'Handling LE Set Data Length Command' ],
    "HCI/COC/9-C":  [ hci_coc_9_c,  'Handling LE Read Suggested Default Data Length Command' ],
    "HCI/COC/10-C": [ hci_coc_10_c, 'Handling LE Write Suggested Default Data Length Command' ],
    "HCI/COC/11-C": [ hci_coc_11_c, 'Handling LE Remove Device From Resolving List Command' ],
    "HCI/COC/12-C": [ hci_coc_12_c, 'Handling LE Clear Resolving List Command' ],
    "HCI/COC/13-C": [ hci_coc_13_c, 'Handling LE Read Resolving List Size Command' ],
    "HCI/COC/14-C": [ hci_coc_14_c, 'Handling LE Set Default PHY Command' ],
#   "HCI/COC/15-C": [ hci_coc_16_c, 'Handling LE Read Periodic Advertiser List Size Command' ],
#   "HCI/COC/16-C": [ hci_coc_16_c, 'Handling Add, Remove and Clear Periodic Advertiser List Commands' ],
    "HCI/COC/17-C": [ hci_coc_17_c, 'Handling LE Read Transmit Power Command' ],
    "HCI/CFC/2-C":  [ hci_cfc_2_c,  'Reported Buffer Size' ],
    "HCI/COI/1-C":  [ hci_coi_1_c,  'Features returned by Read Local Supported Features Command' ],
    "HCI/COI/3-C":  [ hci_coi_3_c,  'Supported Commands returned by Read Local Supported Commands Command' ],
    "HCI/COI/4-C":  [ hci_coi_4_c,  'Versions returned by Read Local Version Information Command' ],
    "HCI/COI/5-C":  [ hci_coi_5_c,  'Reported White List Size' ],
    "HCI/COI/7-C":  [ hci_coi_7_c,  'Feature Bits returned by Read LE Public Key Validation Feature Bit' ],
    "HCI/LCM/1-C":  [ hci_lcm_1_c,  'Handling LE Read Peer Resolvable Address Command' ],
    "HCI/LCM/2-C":  [ hci_lcm_2_c,  'Handling LE Read Local Resolvable Address Command' ],
    "HCI/LCM/3-C":  [ hci_lcm_3_c,  'Handling LE Read PHY Command' ],
    "HCI/DED/7-C":  [ hci_ded_7_c,  'Rejecting invalid Advertising Parameters' ],
    "HCI/DED/3-C":  [ hci_ded_3_c,  'Disable Advertising with Set Advertising Enable Command' ],
    "HCI/DED/4-C":  [ hci_ded_4_c,  'Disable Scanning with Set Scan Enable Command' ],
    "HCI/DES/2-C":  [ hci_des_2_c,  'Reset Command received in Advertising State' ],
    "HCI/DES/3-C":  [ hci_des_3_c,  'Reset Command received in Slave Role' ],
    "HCI/DES/4-C":  [ hci_des_4_c,  'Reset Command received in Scanning State' ],
    "HCI/DES/5-C":  [ hci_des_5_c,  'Reset Command received in Initiating State' ],
    "HCI/DES/6-C":  [ hci_des_6_c,  'Reset Command received in Master Role' ],
    "HCI/GEV/1-C":  [ hci_gev_1_c,  'Status return for Unsupported Commands' ],
    "HCI/HFC/4-C":  [ hci_hfc_4_c,  'Events enabled by LE Set Event Mask Command' ]
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
        trace.trace(3, "Test generated exception: %s" % str(e));
        success = False;

    return not success
