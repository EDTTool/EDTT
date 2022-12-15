# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

# from enum import IntFlag;
from components.utils import *;
from components.basic_commands import *;
from components.address import *;
from components.events import *;
from components.scanner import *;

# class LE_Events(IntFlag):
#     LE_Connection_Complete_Event                   = 1<<0
#     LE_Advertising_Report_Event                    = 1<<1
#     LE_Connection_Update_Complete_Event            = 1<<2
#     LE_Read_Remote_Features_Complete_Event         = 1<<3
#     LE_Long_Term_Key_Request_Event                 = 1<<4
#     LE_Remote_Connection_Parameter_Request_Event   = 1<<5
#     LE_Data_Length_Change_Event                    = 1<<6
#     LE_Read_Local_P_256_Public_Key_Complete_Event  = 1<<7
#     LE_Generate_DHKey_Complete_Event               = 1<<8
#     LE_Enhanced_Connection_Complete_Event          = 1<<9
#     LE_Directed_Advertising_Report_Event           = 1<<10
#     LE_PHY_Update_Complete_Event                   = 1<<11
#     LE_Extended_Advertising_Report_Event           = 1<<12
#     LE_Periodic_Advertising_Sync_Established_Event = 1<<13
#     LE_Periodic_Advertising_Report_Event           = 1<<14
#     LE_Periodic_Advertising_Sync_Lost_Event        = 1<<15
#     LE_Extended_Scan_Timeout_Event                 = 1<<16
#     LE_Extended_Advertising_Set_Terminated_Event   = 1<<17
#     LE_Scan_Request_Received_Event                 = 1<<18
#     LE_Channel_Selection_Algorithm_Event           = 1<<19
#     LE_Events_All                                  = (1<<20)-1

def __verifyAndShowEvent(transport, idx, expectedEvent, trace):

    event = get_event(transport, idx, 100);
    trace.trace(7, str(event));
    return event.event == expectedEvent;

def __verifyAndShowMetaEvent(transport, idx, expectedEvent, trace):

    event = get_event(transport, idx, 100);
    trace.trace(7, str(event));
    return event.subEvent == expectedEvent;

def __verifyAndFetchEvent(transport, idx, expectedEvent, trace):

    event = get_event(transport, idx, 100)[1:];
    trace.trace(7, str(event));
    return event.event == expectedEvent, event.data;

def __verifyAndFetchMetaEvent(transport, idx, expectedEvent, trace):

    event = get_event(transport, idx, 100)[1:];
    trace.trace(7, str(event));
    return event.subEvent == expectedEvent, event.data;

def __getCommandCompleteEvent(transport, idx, trace):

    return __verifyAndShowEvent(transport, idx, Events.BT_HCI_EVT_CMD_COMPLETE, trace);

def __random(transport, idx, trace):
    status, rand = le_rand(transport, idx, 100);
    trace.trace(6, "LE Rand Command returns status: 0x%02X; rand: 0x%016X" % (status, toNumber(rand)));
    success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0);
    return success, rand;

def __encrypt(transport, idx, key, plaintext, trace):
    status, encrypted = le_encrypt(transport, idx, key, plaintext, 2000);
    trace.trace(6, "LE Encrypt Command returns status: 0x%02X" % status);
    success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0);
    return success, encrypted;

"""
    Prepare for testing, by
    - Resetting the DUT
    - Read Local Supported Features and insure that 'LE Supported (Controller)' and 'BR/EDR Not Supported' are both set
    - Read LE Local Supported Features
    - Set Event Masks: 'Event Mask', 'LE Event Mask' and 'Event Mask Page 2'

    Returns a boolean indicating whether all went well.
"""
def preamble_standby(transport, idx, trace):
    trace.trace(3, "Standby preamble steps...");

    try:
        flush_events(transport, idx, 100);
        le_data_flush(transport, idx, 100);

        status = reset(transport, idx, 100);
        trace.trace(6, "Reset Command returns status: 0x%02X" % status);
        success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0);
        if not success:
            trace.trace(6, "RESET command not confirmed!");

        status, features = read_local_supported_features(transport, idx, 100);
        trace.trace(6, "Read Local Supported Features Command returns status: 0x%02X" % status);
        """
            Check that features 'BR/EDR Not Supported' and 'LE Supported (Controller)' are both enabled
        """
        success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0) and ((features[4] & 0x60) == 0x60) and success;

        status, features = le_read_local_supported_features(transport, idx, 100);
        trace.trace(6, "LE Read Local Supported Features Command returns status: 0x%02X" % status);
        success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0) and success;
        """
            Bit Parameter Description
             0 Inquiry Complete Event
             1 Inquiry Result Event
             2 Connection Complete Event
             3 Connection Request Event
             4 Disconnection Complete Event
             5 Authentication Complete Event
             6 Remote Name Request Complete Event
             7 Encryption Change Event
             8 Change Connection Link Key Complete Event
             9 Central Link Key Complete Event
            10 Read Remote Supported Features Complete Event
            11 Read Remote Version Information Complete Event
            12 QoS Setup Complete Event
            13 Reserved for future use
            14 Reserved for future use
            15 Hardware Error Event
            16 Flush Occurred Event
            17 Role Change Event
            18 Reserved for future use
            19 Mode Change Event
            20 Return Link Keys Event
            21 PIN Code Request Event
            22 Link Key Request Event
            23 Link Key Notification Event
            24 Loopback Command Event
            25 Data Buffer Overflow Event
            26 Max Slots Change Event
            27 Read Clock Offset Complete Event
            28 Connection Packet Type Changed Event
            29 QoS Violation Event
            30 Page Scan Mode Change Event [deprecated]
            31 Page Scan Repetition Mode Change Event
            32 Flow Specification Complete Event
            33 Inquiry Result with RSSI Event
            34 Read Remote Extended Features Complete Event
            35 Reserved for future use
            36 Reserved for future use
            37 Reserved for future use
            38 Reserved for future use
            39 Reserved for future use
            40 Reserved for future use
            41 Reserved for future use
            42 Reserved for future use
            43 Synchronous Connection Complete Event
            44 Synchronous Connection Changed Event
            45 Sniff Subrating Event
            46 Extended Inquiry Result Event
            47 Encryption Key Refresh Complete Event
            48 IO Capability Request Event
            49 IO Capability Response Event
            50 User Confirmation Request Event
            51 User Passkey Request Event
            52 Remote OOB Data Request Event
            53 Simple Pairing Complete Event
            54 Reserved for future use
            55 Link Supervision Timeout Changed Event
            56 Enhanced Flush Complete Event
            57 Reserved for Future Use
            58 User Passkey Notification Event
            59 Keypress Notification Event
            60 Remote Host Supported Features Notification Event
            61 LE Meta Event
            62 Reserved for future use
            63 Reserved for future use

            Bit:    5  4  4  3  2  1  0  0
                    6  8  0  2  4  6  8  0
                 0x00 00 1F FF FF FF FF FF ~ Default.
                 0x20 00 9F FF FF FF FF FF ~ Default + Bit 47 ~ Encryption Key Refresh Complete Event + Bit 61 ~ LE Meta Event
        """

        events = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x9F, 0x00, 0x20];
        status = set_event_mask(transport, idx, events, 100);
        trace.trace(6, "Set Event Mask Command returns status: 0x%02X" % status);
        success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0) and success;
        """
            Bit LE Subevent Types
             0 LE Connection Complete Event
             1 LE Advertising Report Event
             2 LE Connection Update Complete Event
             3 LE Read Remote Features Complete Event
             4 LE Long Term Key Request Event
             5 LE Remote Connection Parameter Request Event
             6 LE Data Length Change Event
             7 LE Read Local P-256 Public Key Complete Event
             8 LE Generate DHKey Complete Event
             9 LE Enhanced Connection Complete Event
            10 LE Directed Advertising Report Event
            11 LE PHY Update Complete Event
            12 LE Extended Advertising Report Event
            13 LE Periodic Advertising Sync Established Event
            14 LE Periodic Advertising Report Event
            15 LE Periodic Advertising Sync Lost Event
            16 LE Extended Scan Timeout Event
            17 LE Extended Advertising Set Terminated Event
            18 LE Scan Request Received Event
            19 LE Channel Selection Algorithm Event
            20 LE Connectionless IQ Report event
            21 LE Connection IQ Report event
            22 LE CTE Request Failed event
            23 LE Periodic Advertising Sync Transfer Received event
            24 LE CIS Established event
            25 LE CIS Request event
            26 LE Create BIG Complete event
            27 LE Terminate BIG Complete event
            28 LE BIG Sync Established event
            29 LE BIG Sync Lost event
            30 LE Request Peer SCA Complete event
            31 LE Path Loss Threshold event
            32 LE Transmit Power Reporting event
            33 LE BIGInfo Advertising Report event

            Bit:    5  4  4  3  2  1  0  0
                    6  8  0  2  4  6  8  0
                 0x00 00 00 00 00 00 00 1F ~ Default.
                 0x00 00 00 03 FF F7 FF FF ~ All except 'LE Channel Selection Algorithm Event'
        """

        events = [0xFF, 0xFF, 0xF7, 0xFF, 0x03, 0x00, 0x00, 0x00];
        status = le_set_event_mask(transport, idx, events, 100);
        trace.trace(6, "LE Set Event Mask Command returns status: 0x%02X" % status);
        success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0) and success;
        """
            0x00 00 00 00 00 00 00 00 ~ Default.
        """
        events = [0 for _ in range(8)];

        status = set_event_mask_page_2(transport, idx, events, 100);
        trace.trace(6, "Set Event Mask Page2 Command returns status: 0x%02X" % status);
        success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0) and success;
    except Exception as e:
        import traceback
        traceback.print_exc()
        trace.trace(3, "Standby preamble steps failed: %s" % str(e));
        success = False;

    return success;

"""
    Calculate IRK from IR
"""
def __calculateIRK(transport, idx, key, trace):
    plaintext = [1 if i == 0 else 0 for i in range(16)];
    success, irk = __encrypt(transport, idx, key, plaintext, trace);
    return success, irk;

"""
    Generate a random static address from IRK
"""
def preamble_random_static_address(transport, idx, key, trace):
    success, rand = __random(transport, idx, trace);

    nrand = (toNumber(rand) & 0xFFFFFF) | 0xC00000;
    _success, localHash = __encrypt(transport, idx, key, toArray(nrand, 16), trace);
    success = success and _success;

    nlocalHash = toNumber(localHash) & 0xFFFFFF;
    address = nlocalHash | (nrand << 24);
    return success, toArray(address, 6);

"""
    Generate a private non-resolvable random address from IRK
"""
def preamble_random_non_resolvable_address(transport, idx, key, trace):
    success, rand = __random(transport, idx, trace);

    nrand = toNumber(rand) & 0x3FFFFF;
    _success, localHash = __encrypt(transport, idx, key, toArray(nrand, 16), trace);
    success = success and _success;

    nlocalHash = toNumber(localHash) & 0xFFFFFF;
    address = nlocalHash | (nrand << 24);
    return success, toArray(address, 6);

"""
    Calculates a Random Private Address based on the IR (passed to the function)

    The random address generation behavior is an extract from GAP [1] Section 2.1.2 and represents here the typical HCI sequences required from a Controller.
    The identity resolving key ‘irk’ is used in the test procedures in group ‘SEC’.

    key is the IR - Identity Root
"""
def preamble_random_address_calculated(transport, idx, key, trace):
    trace.trace(4, "Random Address Calculated preamble steps...");

    try:
        """
            Generate IRK from IR
        """
        success, irk = __calculateIRK(transport, idx, key, trace);
        trace.trace(7, "IRK: 0x%032X" % toNumber(irk));

        _success, address = preamble_random_static_address(transport, idx, irk, trace);
        success = success and _success;
        trace.trace(7, "Random address: 0x%012X" % toNumber(address));

    except Exception as e:
        trace.trace(3, "Random Address Calculated preamble failed: %s" % str(e));
        success = False;
        address = [0 for _ in range(6)];

    return (success, irk, address);

"""
    Calculates Encryption Keys based on the IR (identity root) and the ER (encryption root)

    Encryption keys are input to a Controller from [1](part H, section 2.4.2).
    The identity root, IR is referred to as 'ir' and has the default value 0x112233445566778899AABBCCDDEEFF00.
    The encryption root, ER is referred to as 'er' and has the default value 0x112233445566778899AABBCCDDEEFF00.
"""
def preamble_encryption_keys_calculated(transport, idx, trace):
    trace.trace(4, "Encryption Keys Calculated preamble steps...");

    try:
        success, div = __random(transport, idx, trace);

        _success, rand = __random(transport, idx, trace);
        success = success and _success;

        ir = er = 0x112233445566778899AABBCCDDEEFF00;

        _success, dhk = __encrypt(transport, idx, toArray(ir, 16), toArray(0x02, 16), trace);
        success = success and _success;

        _success, y   = __encrypt(transport, idx, dhk, rand, trace);
        success = success and _success;

        _success, ltk = __encrypt(transport, idx, toArray(er, 16), div, trace);
        success = success and _success;
        trace.trace(6, "Generated LTK: 0x%032X" % toNumber(ltk));

        ediv = toArray(toNumber(y) ^ toNumber(div), 16);
        ediv = ediv[:2]

    except Exception as e:
        trace.trace(3, "Encryption Keys Calculated preamble failed: %s" % str(e));
        success = False;
        rand = [0 for _ in range(8)];
        ediv = [0 for _ in range(2)];
        ltk  = [0 for _ in range(16)];

    return success, toNumber(rand), toNumber(ediv), ltk

def preamble_set_public_address(transport, idx, address, trace):
    trace.trace(4, "Set Public Address preamble steps...");

    try:
        status = write_bd_addr(transport, idx, toArray(address, 6), 100);
        trace.trace(6, "Write BD_ADDR Command returns status: 0x%02X" % status);
        success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0);
    except Exception as e:
        trace.trace(3, "Set Public Address preamble failed: %s" % str(e));
        success = False;

    return success;

"""
    The preamble_set_random_address function can be used to set three different kinds of random addresses.

    See [Vol 6] Part B, Section 1.3 -

    - A Static address (two MSBs are 11)
      - A static address is a 48-bit randomly generated address and shall meet the following requirements:
        • The two most significant bits of the address shall be equal to 1
        • At least one bit of the random part of the address shall be 0
        • At least one bit of the random part of the address shall be 1
    - A Private address
      - A non-resolvable Private adress (two MSBs are 00)
        - To generate a non-resolvable address, the device shall generate a 48-bit address with the following requirements:
          • The two most significant bits of the address shall be equal to 0
          • At least one bit of the random part of the address shall be 1
          • At least one bit of the random part of the address shall be 0
          • The address shall not be equal to the public address
      - A resolvable Private address (two MSBs are 01)
        - To generate a resolvable private address, the device must have either the Local Identity Resolving Key (IRK) or the Peer Identity Resolving Key (IRK).
          The resolvable private address shall be generated with the IRK and a randomly generated 24-bit number. The random number is known as prand and shall
          meet the following requirements:
          • The two most significant bits of prand shall be equal to 0 and 1.
          • At least one bit of the random part of prand shall be 0
          • At least one bit of the random part of prand shall be 1
"""
def preamble_set_random_address(transport, idx, address, trace):
    trace.trace(4, "Set Random Address preamble steps...");

    try:
        status = le_set_random_address(transport, idx, toArray(address, 6), 100);
        trace.trace(6, "LE Set Random Address Command returns status: 0x%02X" % status);
        success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0);
    except Exception as e:
        trace.trace(3, "Set Random Address preamble failed: %s" % str(e));
        success = False;

    return success;


"""
    When the IUT is in advertising state or peripheral role, a default value for the scanning, initiating or central address used is 0x123456789ABC.
    When the IUT is in scanning state, initiating state or central role, a default value for the address used for the state of advertising
    or the role of peripheral is 0x456789ABCDEF.

    When it is required to modify the Lower Tester address either in the company_assigned field, the company_id field,
    it has to be done by exchanging bytes 1 and 3 of company_assigned field or company_id field.
    If it is required to modify the Lower Tester address in the company_assigned and company_id fields,
    it has to be done by exchanging bytes 1 of company_assigned and company_id fields.
"""
def preamble_device_address_set(transport, idx, trace):
    trace.trace(4, "Device Address Set preamble steps...");

    try:
        """
            The Identity Root IR has the default value 0x112233445566778899AABBCCDDEEFF00
        """
        ir = 0x00112233445566778899AABBCCDDEEFF if idx == 0 else 0x112233445566778899AABBCCDDEEFF00;
        trace.trace(6, "Using default identity root value ir: 0x%032X" % ir);

        success, irk, randAddress = preamble_random_address_calculated(transport, idx, toArray(ir, 16), trace);
        trace.trace(6, "Generated IRK: 0x%032X" % toNumber(irk));
        trace.trace(6, "Generated random address %s" % formatAddress(randAddress));
        success = True;

        address = 0x123456789ABC if idx == 0 else 0x456789ABCDEF;
        success = success and preamble_set_public_address(transport, idx, address, trace);
        success = success and preamble_set_random_address(transport, idx, toNumber(randAddress), trace);

    except Exception as e:
        trace.trace(3, "Device address set preamble failed: %s" % str(e));
        success = False;
        irk = [0 for _ in range(16)];

    return (success, irk, randAddress);

"""
   The Bluetooth address (BD_ADDR) is 48 bit unique number. BD_ADDR ~ (NAP | UAP | LAP) - OUI ~ (NAP | UAP).
   The most significant  16 bits - the NAP - is a company specific id.
   The next significant   8 bits - the UAP - is a company specific id.
   The least significant 24 bits - the LAP - is a company assigned number.

   The upper half of a Bluetooth Address (most-significant 24 bits) is so called Organizationally Unique Identifier (OUI).
   It can be used to determine the manufacturer of a device (Bluetooth MAC Address Lookup form).
   OUI prefixes are assigned by the Institute of Electrical and Electronics Engineers (IEEE).

   NAP
      Non-significant Address Part (2 bytes). Contains first 16 bits of the OUI.
      The NAP value is used in Frequency Hopping Synchronization frames.
   UAP
      Upper Address Part (1 byte). Contains remaining 8 bits of the OUI.
      The UAP value is used for seeding in various Bluetooth specification algorithms.
   LAP
      Lower Address Part (3 bytes). This portion of Bluetooth Address is allocated by the vendor of device.
      The LAP value uniquely identifies a Bluetooth device as part of the Access Code in every transmitted frame.
      The LAP and the UAP make the significant address part (SAP) of the Bluetooth Address.
"""

"""
    Scramble the company_id part of the Bluetooth address.
"""
def address_scramble_OUI(address):
    return (address ^ 0xff00ff000000);

"""
    Scramble the company_assigned part of the Bluetooth address.
"""
def address_scramble_LAP(address):
    return (address ^ 0x000000ff00ff);

"""
    Scramble both the company_id part and the company_assigned part of the Bluetooth address.
"""
def address_exchange_OUI_LAP(address):
    return (address ^ 0xff00000000ff);

def preamble_specific_filter_accept_listed(transport, idx, addresses, trace):
    trace.trace(5, "Specific Filter Accept Listed preamble steps...");

    try:
        status = le_clear_filter_accept_list(transport, idx, 100);
        trace.trace(6, "LE Clear Filter Accept List Command returns status: 0x%02X" % status);
        success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0);

        for i in range(len(addresses)):
            address = toArray(addresses[i][1], 6);
            trace.trace(7, "Addding Device to Filter Accept List %s" % formatAddress(address, addresses[i][0]));
            status = le_add_device_to_filter_accept_list(transport, idx, addresses[i][0], address, 100);
            trace.trace(6, "LE Add Device to Filter Accept List Command returns status: 0x%02X" % status);
            success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0) and success;
    except Exception as e:
        trace.trace(3, "Specific Filter Accept Listed preamble failed: %s" % str(e));
        success = False;

    return success;

def preamble_buffer_size_read(transport, idx, trace):
    trace.trace(5, "Buffer Size Read preamble steps...");

    try:
        status, LeMaxLen, LeMaxNum = le_read_buffer_size(transport, idx, 100);
        trace.trace(6, "LE Read Buffer Size Command returns status: 0x%02X" % status);
        success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0);

        if LeMaxLen == 0 and LeMaxNum == 0:
            status, AclMaxLen, ScoMaxLen, AclMaxNum, ScoMaxNum = read_buffer_size(transport, idx, 100);
            trace.trace(6, "Read Buffer Size Command returns status: 0x%02X" % status);
            success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0) and success;
        """
            0x90 88 01 00 00 80 00 20 ~ 0x2000800000018890
        """
        events = [0x90, 0x88, 0x01, 0x00, 0x00, 0x80, 0x00, 0x20];

        status = set_event_mask(transport, idx, events, 100);
        trace.trace(6, "Set Event Mask Command returns status: 0x%02X" % status);
        success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0) and success;
    except Exception as e:
        trace.trace(3, "Buffer Size Read preamble failed: %s" % str(e));
        success = False;

    return success;

def preamble_ext_advertising_parameters_set(transport, idx, Handle, Properties, PrimMinInterval, PrimMaxInterval, PrimChannelMap, OwnAddrType, PeerAddrType, PeerAddress, FilterPolicy, TxPower, PrimAdvPhy, SecAdvMaxSkip, SecAdvPhy, Sid, ScanReqNotifyEnable, trace):
    trace.trace(5, "Extended Advertising Parameters Set preamble steps...");

    try:
        status = le_set_extended_advertising_parameters(transport, idx, Handle, Properties, PrimMinInterval, PrimMaxInterval, PrimChannelMap, OwnAddrType, PeerAddrType, \
                                                        PeerAddress, FilterPolicy, TxPower, PrimAdvPhy, SecAdvMaxSkip, SecAdvPhy, Sid, ScanReqNotifyEnable, 100);
        trace.trace(6, "LE Set Extended Advertising Parameters Command returns status: 0x%02X" % status);
        success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0);
    except Exception as e:
        trace.trace(3, "Extended Advertising Parameters Set preamble failed: %s" % str(e));
        success = False;

    return success;

def preamble_ext_advertising_data_set(transport, idx, Handle, Operation, FragPreference, advData, trace):
    trace.trace(5, "Extended Advertising Data Set preamble steps...");

    try:
        advertiseData = advData[ : ];
        if len(advData) > 251:
            advertiseData = advertiseData[:251];

        status = le_set_extended_advertising_data(transport, idx, Handle, Operation, FragPreference, advertiseData, 100);
        trace.trace(6, "LE Set Extended Advertising Data Command returns status: 0x%02X" % status);
        success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0);
    except Exception as e:
        trace.trace(3, "Extended Advertising Data Set preamble failed: %s" % str(e));
        success = False;

    return success;

def preamble_ext_scan_response_data_set(transport, idx, Handle, Operation, FragPreference, advData, trace):
    trace.trace(5, "Extended Scan Response Data Set preamble steps...");

    try:
        advertiseData = advData[ : ];
        if len(advData) > 251:
            advertiseData = advertiseData[:251];

        status = le_set_extended_scan_response_data(transport, idx, Handle, Operation, FragPreference, advertiseData, 100);
        trace.trace(6, "LE Set Extended Scan Response Data Command returns status: 0x%02X" % status);
        success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0);
    except Exception as e:
        trace.trace(3, "Extended Scan Response Data Set preamble failed: %s" % str(e));
        success = False;

    return success;

def preamble_ext_advertise_enable(transport, idx, enable, SHandle, SDuration, SMaxExtAdvEvts, trace):
    trace.trace(5, "Extended Advertising " + ("Enable" if enable else "Disable") + " preamble steps...");

    try:
        NumberOfSets = max(len(SHandle), len(SDuration), len(SMaxExtAdvEvts));
        if len(SHandle) < NumberOfSets:
            SHandle += [ 0 for _ in range(len(SHandle), NumberOfSets) ];
        if len(SDuration) < NumberOfSets:
            SDuration += [ 0 for _ in range(len(SDuration), NumberOfSets) ];
        if len(SMaxExtAdvEvts) < NumberOfSets:
            SMaxExtAdvEvts += [ 0 for _ in range(len(SMaxExtAdvEvts), NumberOfSets) ];

        status = le_set_extended_advertising_enable(transport, idx, enable, NumberOfSets, SHandle, SDuration, SMaxExtAdvEvts, 100);
        trace.trace(6, "LE Set Extended Advertising Enable Command returns status: 0x%02X" % status);
        success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0);
    except Exception as e:
        trace.trace(3, "Extended Advertising " + "Enable" if enable else "Disable" + " preamble failed: %s" % str(e));
        success = False;

    return success;

def preamble_scan_parameters_set(transport, idx, scanType, scanInterval, scanWindow, addrType, filterPolicy, trace):
    trace.trace(5, "Scan Parameters Set preamble steps...");

    try:
        status = le_set_scan_parameters(transport, idx, scanType, scanInterval, scanWindow, addrType, filterPolicy, 100);
        trace.trace(6, "LE Set Scan Parameters Command returns status: 0x%02X" % status);
        success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0);
    except Exception as e:
        trace.trace(3, "Scan Parameters Set preamble failed: %s" % str(e));
        success = False;

    return success;

def preamble_scan_enable(transport, idx, enable, filterDuplicate, trace):
    trace.trace(5, "Scanning " + ("Enable" if enable else "Disable") + " preamble steps...");

    try:
        status = le_set_scan_enable(transport, idx, enable, filterDuplicate, 100);
        trace.trace(6, "LE Set Scan Enable Command returns status: 0x%02X" % status);
        success = (status == 0);
        while not __getCommandCompleteEvent(transport, idx, trace):
            pass;
    except Exception as e:
        trace.trace(3, "Scanning " + ("Enable" if enable else "Disable") + " preamble failed: %s" % str(e));
        success = False;

    return success;

def preamble_passive_scanning(transport, idx, scanInterval, scanWindow, addrType, filterPolicy, trace):
    trace.trace(5, "Passive Scanning preamble steps...");

    success = preamble_scan_parameters_set(transport, idx, ScanType.PASSIVE, scanInterval, scanWindow, addrType, filterPolicy, trace);
    success = success and preamble_scan_enable(transport, idx, Scan.ENABLE, ScanFilterDuplicate.DISABLE, trace);
    return success;

def preamble_default_physical_channel(transport, idx, AllPhys, TxPhys, RxPhys, trace):
    trace.trace(5, "Default physical channels preamble steps...");

    try:
        status = le_set_default_phy(transport, idx, AllPhys, TxPhys, RxPhys, 100);
        success = __getCommandCompleteEvent(transport, idx, trace) and (status == 0);
    except Exception as e:
        trace.trace(3, "Default physical channels preamble failed: %s" % str(e));
        success = False;

    return success;

def public_address( address ):
    return ExtendedAddressType.PUBLIC, toArray(address, 6);

def random_address( address ):
    return ExtendedAddressType.RANDOM, toArray(address, 6);

def public_identity_address( address ):
    return ExtendedAddressType.RESOLVABLE_OR_PUBLIC, toArray(address, 6);

def random_identity_address( address ):
    return ExtendedAddressType.RESOLVABLE_OR_RANDOM, toArray(address, 6);
