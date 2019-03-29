# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

import struct;
import numpy;
from enum import IntEnum;

class Events(IntEnum):
    BT_HCI_EVT_NONE                         = 0
    BT_HCI_EVT_DISCONN_COMPLETE             = 5
    BT_HCI_EVT_ENCRYPT_CHANGE               = 8
    BT_HCI_EVT_REMOTE_VERSION_INFO          = 12
    BT_HCI_EVT_CMD_COMPLETE                 = 14
    BT_HCI_EVT_CMD_STATUS                   = 15
    BT_HCI_EVT_NUM_COMPLETED_PACKETS        = 19
    BT_HCI_EVT_DATA_BUF_OVERFLOW            = 26
    BT_HCI_EVT_ENCRYPT_KEY_REFRESH_COMPLETE = 48
    BT_HCI_EVT_LE_META_EVENT                = 62
    BT_HCI_EVT_AUTH_PAYLOAD_TIMEOUT_EXP     = 87

class MetaEvents(IntEnum):
    BT_HCI_EVT_LE_CONN_COMPLETE             = 1
    BT_HCI_EVT_LE_ADVERTISING_REPORT        = 2
    BT_HCI_EVT_LE_CONN_UPDATE_COMPLETE      = 3
    BT_HCI_EVT_LE_REMOTE_FEAT_COMPLETE      = 4
    BT_HCI_EVT_LE_LTK_REQUEST               = 5
    BT_HCI_EVT_LE_CONN_PARAM_REQ            = 6
    BT_HCI_EVT_LE_DATA_LEN_CHANGE           = 7
    BT_HCI_EVT_LE_P256_PUBLIC_KEY_COMPLETE  = 8
    BT_HCI_EVT_LE_GENERATE_DHKEY_COMPLETE   = 9
    BT_HCI_EVT_LE_ENH_CONN_COMPLETE         = 10
    BT_HCI_EVT_LE_DIRECT_ADV_REPORT         = 11
    BT_HCI_EVT_LE_PHY_UPDATE_COMPLETE       = 12
    BT_HCI_EVT_LE_EXT_ADVERTISING_REPORT    = 13
    BT_HCI_EVT_LE_PER_ADV_SYNC_ESTABLISHED  = 14
    BT_HCI_EVT_LE_PER_ADVERTISING_REPORT    = 15
    BT_HCI_EVT_LE_PER_ADV_SYNC_LOST         = 16
    BT_HCI_EVT_LE_SCAN_TIMEOUT              = 17
    BT_HCI_EVT_LE_ADV_SET_TERMINATED        = 18
    BT_HCI_EVT_LE_SCAN_REQ_RECEIVED         = 19
    BT_HCI_EVT_LE_CHAN_SEL_ALGO             = 20

opCodes = { 0x0401: 'Inquire',
            0x0406: 'Disconnect',
            0x041D: 'Read Remote Version Information',
            0x0C01: 'Set Event Mask',
            0x0C03: 'Reset',
            0x0C2D: 'Read Transmit Power Level',
            0x0C31: 'Set Controller To Host Flow Control',
            0x0C33: 'Host Buffer Size',
            0x0C35: 'Host Number Of Completed Packets',
            0x0C63: 'Set Event Mask Page 2',
            0x0C6C: 'Read LE Host Support',
            0x0C6D: 'Write LE Host Support',
            0x0C7B: 'Read Authenticated Payload Timeout',
            0x0C7C: 'Write Authenticated Payload Timeout',
            0x1001: 'Read Local Version Information',
            0x1002: 'Read Local Supported Commands',
            0x1003: 'Read Local Supported Features',
            0x1005: 'Read Buffer Size',
            0x1009: 'Read BD_ADDR',
            0x1405: 'Read RSSI',
            0x2001: 'LE Set Event Mask',
            0x2002: 'LE Read Buffer Size',
            0x2003: 'LE Read Local Supported Features',
            0x2005: 'LE Set Random Address',
            0x2006: 'LE Set Advertising Parameters',
            0x2007: 'LE Read Advertising Channel TX Power',
            0x2008: 'LE Set Advertising Data',
            0x2009: 'LE Set Scan Response Data',
            0x200A: 'LE Set Advertising Enable',
            0x200B: 'LE Set Scan Parameters',
            0x200C: 'LE Set Scan Enable',
            0x200D: 'LE Create Connection',
            0x200E: 'LE Create Connection Cancel',
            0x200F: 'LE Read White List Size',
            0x2010: 'LE Clear White List',
            0x2011: 'LE Add Device To White List',
            0x2012: 'LE Remove Device From White List',
            0x2013: 'LE Connection Update',
            0x2014: 'LE Set Host Channel Classification',
            0x2015: 'LE Read Channel Map',
            0x2016: 'LE Read Remote Features',
            0x2017: 'LE Encrypt',
            0x2018: 'LE Rand',
            0x2019: 'LE Start Encryption',
            0x201A: 'LE Long Term Key Request Reply',
            0x201B: 'LE Long Term Key Request Negative Reply',
            0x201C: 'LE Read Supported States',
            0x201D: 'LE Receiver Test',
            0x201E: 'LE Transmitter Test',
            0x201F: 'LE Test End',
            0x2020: 'LE Remote Connection Parameter Request Reply',
            0x2021: 'LE Remote Connection Parameter Request Negative Reply',
            0x2022: 'LE Set Data Length',
            0x2023: 'LE Read Suggested Default Data Length',
            0x2024: 'LE Write Suggested Default Data Length',
            0x2027: 'LE Add Device to Resolving List',
            0x2028: 'LE Remove Device From Resolving List',
            0x2029: 'LE Clear Resolving List',
            0x202A: 'LE Read Resolving List Size',
            0x202B: 'LE Read Peer Resolvable Address',
            0x202C: 'LE Read Local Resolvable Address',
            0x202D: 'LE Set Address Resolution Enable',
            0x202E: 'LE Set Resolvable Private Address Timeout',
            0x202F: 'LE Read Maximum Data Length',
            0x2030: 'LE Read PHY',
            0x2031: 'LE Set Default PHY',
            0x2032: 'LE Set PHY',
            0x2033: 'LE Enhanced Receiver Test',
            0x2034: 'LE Enhanced Transmitter Test',
            0x2036: 'LE Set Extended Advertising Parameters',
            0x2037: 'LE Set Extended Advertising Data',
            0x2038: 'LE Set Extended Scan Response Data',
            0x2039: 'LE Set Extended Advertising Enable',
            0x203A: 'LE Read Maximum Advertising Data Length',
            0x203B: 'LE Read Number of Supported Advertising Sets',
            0x203C: 'LE Remove Advertising Set',
            0x203D: 'LE Clear Advertising Sets',
            0x203E: 'LE Set Periodic Advertising Parameters',
            0x203F: 'LE Set Periodic Advertising Data',
            0x2040: 'LE Set Periodic Advertising Enable',
            0x2041: 'LE Set Extended Scan Parameters',
            0x2042: 'LE Set Extended Scan Enable',
            0x2043: 'LE Extended Create Connection',
            0x2044: 'LE Periodic Advertising Create Sync',
            0x2045: 'LE Periodic Advertising Create Sync Cancel',
            0x2046: 'LE Periodic Advertising Terminate Sync',
            0x2047: 'LE Add Device To Periodic Advertiser List',
            0x2048: 'LE Remove Device From Periodic Advertiser List',
            0x2049: 'LE Clear Periodic Advertiser List',
            0x204A: 'LE Read Periodic Advertiser List Size',
            0x204B: 'LE Read Transmit Power',
            0x204C: 'LE Read RF Path Compensation',
            0x204D: 'LE Write RF Path Compensation',
            0x204E: 'LE Set Privacy Mode',
            0xFC06: 'Write BD_ADDR' };

def formatAddress(address, addressType=None):
    result = '';
    for part in reversed(address):
        if ( len(result) ):
            result += ':';
        result += '%02X' % part;
    if ( not addressType is None ):
        result += '(R)' if ( (addressType & 1) == 1 ) else '(P)';
    return result;

def formatChannelMap(channelMap):
    value = 0;
    for part in reversed(channelMap):
        value <<= 8;
        value += part;
    return '%010X' % value;

def formatArray(intArray):
    result = '';
    for part in intArray:
        if ( len(result) ):
            result += ' ';
        result += '%02X' % part;
    return result;

def formatPattern(pattern):
    PatternTexts = [ 'Pseudo-Random bit sequence 9', 'Pattern of alternating bits ‘11110000’', 'Pattern of alternating bits ‘10101010’', 'Pseudo-Random bit sequence 15',
                     'Pattern of All ‘1’ bits', 'Pattern of All ‘0’ bits', 'Pattern of alternating bits ‘00001111’', 'Pattern of alternating bits ‘0101’' ];
    return PatternTexts[pattern] if ( pattern in range(len(PatternTexts)) ) else 'Unknown pattern!';

def showCommands(commands, trace):
    CommandTexts = [
        [ 'Inquiry', 'Inquiry Cancel', 'Periodic Inquiry Mode', 'Exit Periodic Inquiry Mode', 'Create Connection', 'Disconnect', 'Add SCO Connection (deprecated)', 'Create Connection Cancel' ],
        [ 'Accept Connection Request', 'Reject Connection Request', 'Link Key Request Reply', 'Link Key Request Negative Reply', 'PIN Code Request Reply', 'PIN Code Request Negative Reply', 'Change Connection Packet Type', 'Authentication Requested' ],
        [ 'Set Connection Encryption', 'Change Connection Link Key', 'Master Link Key', 'Remote Name Request', 'Remote Name Request Cancel', 'Read Remote Supported Features', 'Read Remote Extended Features', 'Read Remote Version Information' ],
        [ 'Read Clock Offset', 'Read LMP Handle', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use' ],
        [ 'Reserved for Future Use', 'Hold Mode', 'Sniff Mode', 'Exit Sniff Mode', 'Reserved for Future Use', 'Reserved for Future Use', 'QoS Setup', 'Role Discovery' ],
        [ 'Switch Role', 'Read Link Policy Settings', 'Write Link Policy Settings', 'Read Default Link Policy Settings', 'Write Default Link Policy Settings', 'Flow Specification', 'Set Event Mask', 'Reset' ],
        [ 'Set Event Filter', 'Flush', 'Read PIN Type', 'Write PIN Type', 'Create New Unit Key', 'Read Stored Link Key', 'Write Stored Link Key', 'Delete Stored Link Key' ],
        [ 'Write Local Name', 'Read Local Name', 'Read Connection Accept Timeout', 'Write Connection Accept Timeout', 'Read Page Timeout', 'Write Page Timeout', 'Read Scan Enable', 'Write Scan Enable' ],
        [ 'Read Page Scan Activity', 'Write Page Scan Activity', 'Read Inquiry Scan Activity', 'Write Inquiry Scan Activity', 'Read Authentication Enable', 'Write Authentication Enable', 'Read Encryption Mode (deprecated)', 'Write Encryption Mode (deprecated)' ],
        [ 'Read Class Of Device', 'Write Class Of Device', 'Read Voice Setting', 'Write Voice Setting', 'Read Automatic Flush Timeout', 'Write Automatic Flush Timeout', 'Read Num Broadcast Retransmissions', 'Write Num Broadcast Retransmissions' ],
        [ 'Read Hold Mode Activity', 'Write Hold Mode Activity', 'Read Transmit Power Level', 'Read Synchronous Flow Control Enable', 'Write Synchronous Flow Control Enable', 'Set Controller To Host Flow Control', 'Host Buffer Size', 'Host Number Of Completed Packets' ],
        [ 'Read Link Supervision Timeout', 'Write Link Supervision Timeout', 'Read Number of Supported IAC', 'Read Current IAC LAP', 'Write Current IAC LAP', 'Read Page Scan Mode Period (deprecated)', 'Write Page Scan Mode Period (deprecated)', 'Read Page Scan Mode (deprecated)' ],
        [ 'Write Page Scan Mode (deprecated)', 'Set AFH Host Channel Classification', 'Reserved for Future Use', 'Reserved for Future Use', 'Read Inquiry Scan Type', 'Write Inquiry Scan Type', 'Read Inquiry Mode', 'Write Inquiry Mode' ],
        [ 'Read Page Scan Type', 'Write Page Scan Type', 'Read AFH Channel Assessment Mode', 'Write AFH Channel Assessment Mode', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use' ],
        [ 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use', 'Read Local Version Information', 'Reserved for Future Use', 'Read Local Supported Features', 'Read Local Extended Features', 'Read Buffer Size' ],
        [ 'Read Country Code [Deprecated]', 'Read BD ADDR', 'Read Failed Contact Counter', 'Reset Failed Contact Counter', 'Read Link Quality', 'Read RSSI', 'Read AFH Channel Map', 'Read Clock' ],
        [ 'Read Loopback Mode', 'Write Loopback Mode', 'Enable Device Under Test Mode', 'Setup Synchronous Connection Request', 'Accept Synchronous Connection Request', 'Reject Synchronous Connection Request', 'Reserved for Future Use', 'Reserved for Future Use' ],
        [ 'Read Extended Inquiry Response', 'Write Extended Inquiry Response', 'Refresh Encryption Key', 'Reserved for Future Use', 'Sniff Subrating', 'Read Simple Pairing Mode', 'Write Simple Pairing Mode', 'Read Local OOB Data' ],
        [ 'Read Inquiry Response Transmit Power Level', 'Write Inquiry Transmit Power Level', 'Read Default Erroneous Data Reporting', 'Write Default Erroneous Data Reporting', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use', 'IO Capability Request Reply' ],
        [ 'User Confirmation Request Reply', 'User Confirmation Request Negative Reply', 'User Passkey Request Reply', 'User Passkey Request Negative Reply', 'Remote OOB Data Request Reply', 'Write Simple Pairing Debug Mode', 'Enhanced Flush', 'Remote OOB Data Request Negative Reply' ],
        [ 'Reserved for Future Use', 'Reserved for Future Use', 'Send Keypress Notification', 'IO Capability Request Negative Reply', 'Read Encryption Key Size', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use' ],
        [ 'Create Physical Link', 'Accept Physical Link', 'Disconnect Physical Link', 'Create Logical Link', 'Accept Logical Link', 'Disconnect Logical Link', 'Logical Link Cancel', 'Flow Spec Modify' ],
        [ 'Read Logical Link Accept Timeout', 'Write Logical Link Accept Timeout', 'Set Event Mask Page 2', 'Read Location Data', 'Write Location Data', 'Read Local AMP Info', 'Read Local AMP_ASSOC', 'Write Remote AMP_ASSOC' ],
        [ 'Read Flow Control Mode', 'Write Flow Control Mode', 'Read Data Block Size', 'Reserved for Future Use', 'Reserved for Future Use', 'Enable AMP Receiver Reports', 'AMP Test End', 'AMP Test' ],
        [ 'Read Enhanced Transmit Power Level', 'Reserved for Future Use', 'Read Best Effort Flush Timeout', 'Write Best Effort Flush Timeout', 'Short Range Mode', 'Read LE Host Support', 'Write LE Host Support', 'Reserved for Future Use' ],
        [ 'LE Set Event Mask', 'LE Read Buffer Size', 'LE Read Local Supported Features', 'Reserved for Future Use', 'LE Set Random Address', 'LE Set Advertising Parameters', 'LE Read Advertising Channel TX Power', 'LE Set Advertising Data' ],
        [ 'LE Set Scan Response Data', 'LE Set Advertising Enable', 'LE Set Scan Parameters', 'LE Set Scan Enable', 'LE Create Connection', 'LE Create Connection Cancel', 'LE Read White List Size', 'LE Clear White List' ],
        [ 'LE Add Device To White List', 'LE Remove Device From White List', 'LE Connection Update', 'LE Set Host Channel Classification', 'LE Read Channel Map', 'LE Read Remote Features', 'LE Encrypt', 'LE Rand' ],
        [ 'LE Start Encryption', 'LE Long Term Key Request Reply', 'LE Long Term Key Request Negative Reply', 'LE Read Supported States', 'LE Receiver Test', 'LE Transmitter Test', 'LE Test End', 'Reserved for Future Use' ],
        [ 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use', 'Enhanced Setup Synchronous Connection', 'Enhanced Accept Synchronous Connection', 'Read Local Supported Codecs', 'Set MWS Channel Parameters', 'Set External Frame Configuration' ],
        [ 'Set MWS Signaling', 'Set MWS Transport Layer', 'Set MWS Scan Frequency Table', 'Get MWS Transport Layer Configuration', 'Set MWS PATTERN Configuration', 'Set Triggered Clock Capture', 'Truncated Page', 'Truncated Page Cancel' ],
        [ 'Set Connectionless Slave Broadcast', 'Set Connectionless Slave Broadcast Receive', 'Start Synchronization Train', 'Receive Synchronization Train', 'Set Reserved LT_ADDR', 'Delete Reserved LT_ADDR', 'Set Connectionless Slave Broadcast Data', 'Read Synchronization Train Parameters' ],
        [ 'Write Synchronization Train Parameters', 'Remote OOB Extended Data Request Reply', 'Read Secure Connections Host Support', 'Write Secure Connections Host Support', 'Read Authenticated Payload Timeout', 'Write Authenticated Payload Timeout', 'Read Local OOB Extended Data', 'Write Secure Connections Test Mode' ],
        [ 'Read Extended Page Timeout', 'Write Extended Page Timeout', 'Read Extended Inquiry Length', 'Write Extended Inquiry Length', 'LE Remote Connection Parameter Request Reply', 'LE Remote Connection Parameter Request Negative Reply', 'LE Set Data Length', 'LE Read Suggested Default Data Length' ],
        [ 'LE Write Suggested Default Data Length', 'LE Read Local P-256 Public Key', 'LE Generate DH Key', 'LE Add Device To Resolving List', 'LE Remove Device From Resolving List', 'LE Clear Resolving List', 'LE Read Resolving List Size', 'LE Read Peer Resolvable Address' ],
        [ 'LE Read Local Resolvable Address', 'LE Set Address Resolution Enable', 'LE Set Resolvable Private Address Timeout', 'LE Read Maximum Data Length', 'LE Read PHY Command', 'LE Set Default PHY Command', 'LE Set PHY Command', 'LE Enhanced Receiver Test Command' ],
        [ 'LE Enhanced Transmitter Test Command', 'LE Set Advertising Set Random Address Command', 'LE Set Extended Advertising Parameters Command', 'LE Set Extended Advertising Data Command', 'LE Set Extended Scan Response Data Command', 'LE Set Extended Advertising Enable Command', 'LE Read Maximum Advertising Data Length Command', 'LE Read Number of Supported Advertising Sets Command' ],
        [ 'LE Remove Advertising Set Command', 'LE Clear Advertising Sets Command', 'LE Set Periodic Advertising Parameters Command', 'LE Set Periodic Advertising Data Command', 'LE Set Periodic Advertising Enable Command', 'LE Set Extended Scan Parameters Command', 'LE Set Extended Scan Enable Command', 'LE Extended Create Connection Command' ],
        [ 'LE Periodic Advertising Create Sync Command', 'LE Periodic Advertising Create Sync Cancel Command', 'LE Periodic Advertising Terminate Sync Command', 'LE Add Device To Periodic Advertiser List Command', 'LE Remove Device From Periodic Advertiser List Command', 'LE Clear Periodic Advertiser List Command', 'LE Read Periodic Advertiser List Size Command', 'LE Read Transmit Power Command' ],
        [ 'LE Read RF Path Compensation Command', 'LE Write RF Path Compensation Command', 'LE Set Privacy Mode', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use' ]
    ];

    for n in range(len(CommandTexts)):
        fmt = '%2i %s';
        for i in range(8):
            txt = 'SUPPORTED' if ( commands[n] & (1<<i) ) else 'NOT SUPPORTED';
            if ( i ):
               trace.trace(8, fmt % CommandTexts[n][i] + ' ' + txt);
            else:
               trace.trace(8, fmt % (n, CommandTexts[n][i] + ' ' + txt)); 
            fmt = '   %s';

def showFeatures(features, trace):
    FeatureTexts = [
        [ '3 slot packets', '5 slot packets', 'Encryption', 'Slot offset', 'Timing accuracy', 'Role switch', 'Hold mode', 'Sniff mode' ],
        [ 'Reserved for Future Use', 'Power control requests', 'Channel quality driven data rate (CQDDR)', 'SCO link', 'HV2 packets', 'HV3 packets', 'µ-law log synchronous data', 'A-law log synchronous data' ],
        [ 'CVSD synchronous data', 'Paging parameter negotiation', 'Power control', 'Transparent synchronous data', 'Flow control lag (least significant bit)', 'Flow control lag (middle bit)', 'Flow control lag (most significant bit)', 'Broadcast Encryption' ],
        [ 'Reserved for Future Use', 'Enhanced Data Rate ACL 2 Mb/s mode', 'Enhanced Data Rate ACL 3 Mb/s mode', 'Enhanced inquiry scan', 'Interlaced inquiry scan', 'Interlaced page scan', 'RSSI with inquiry results', 'Extended SCO link (EV3 packets)' ],
        [ 'EV4 packets', 'EV5 packets', 'Reserved for Future Use', 'AFH capable slave', 'AFH classification slave', 'BR/EDR Not Supported', 'LE Supported (Controller)', '3-slot Enhanced Data Rate ACL packets' ],
        [ '5-slot Enhanced Data Rate ACL packets', 'Sniff subrating', 'Pause encryption', 'AFH capable master', 'AFH classification master', 'Enhanced Data Rate eSCO 2 Mb/s mode', 'Enhanced Data Rate eSCO 3 Mb/s mode', '3-slot Enhanced Data Rate eSCO packets' ],
        [ 'Extended Inquiry Response', 'Simultaneous LE and BR/EDR to Same Device Capable (Controller)', 'Reserved for Future Use', 'Secure Simple Pairing', 'Encapsulated PDU', 'Erroneous Data Reporting', 'Non-flushable Packet Boundary Flag', 'Reserved for Future Use' ],
        [ 'Link Supervision Timeout Changed Event', 'Inquiry TX Power Level', 'Enhanced Power Control', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use' ]
    ];

    for n in range(len(FeatureTexts)):
        fmt = '%2i %s';
        for i in range(8):
            txt = 'SUPPORTED' if ( features[n] & (1<<i) ) else 'NOT SUPPORTED';
            if ( i ):
                trace.trace(8, fmt % FeatureTexts[n][i] + ' ' + txt);
            else:
                trace.trace(8, fmt % (n, FeatureTexts[n][i] + ' ' + txt)); 
            fmt = '   %s';

def showLEFeatures(features, trace):
    LEFeatureTexts = [
        [ 'LE Encryption', 'Connection Parameters Request Procedure', 'Extended Reject Indication', 'Slave-initiated Features Exchange', 'LE Ping', 'LE Data Packet Length Extension', 'LL Privacy', 'Extended Scanner Filter Policies' ],
        [ 'LE 2M PHY', 'Stable Modulation Index - Transmitter', 'Stable Modulation Index - Receiver', 'LE Coded PHY', 'LE Extended Advertising', 'LE Periodic Advertising', 'Channel Selection Algorithm #2', 'LE Power Class 1' ],
        [ 'Minimum Number of Used Channels Procedure', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use' ],
    ];
        
    for n in range(len(LEFeatureTexts)):
        fmt = '%2i %s';
        for i in range(8):
            txt = 'SUPPORTED' if ( features[n] & (1<<i) ) else 'NOT SUPPORTED';
            if ( i ):
                trace.trace(8, fmt % LEFeatureTexts[n][i] + ' ' + txt);
            else:
                trace.trace(8, fmt % (n, LEFeatureTexts[n][i] + ' ' + txt)); 
            fmt = '   %s';

def showLEStates(states, trace):
    LEStateTexts = [ 'Scannable Advertising State', 'Connectable Advertising State', 'Non-connectable Advertising State', 'High Duty Cycle Directed Advertising State', 'Low Duty Cycle Directed Advertising State',
                     'Active Scanning State', 'Passive Scanning State', 'Initiating State', 'Connection State (Master Role)', 'Connection State (Slave Role)' ];
    LEStateMap   = [ [   4,   1,   2,   8,  64,  32, 128, 512 ],
                     [  68,  65,  66,  72,  36,  33,  34,  40 ],
                     [ 132, 129, 260, 257, 516, 513, 192, 160 ],
                     [ 320, 288, 576, 544, 384,  16,  80,  48 ],
                     [ 130, 136, 144, 258, 264, 272, 514, 520 ],
                     [ 528, 640,   0,   0,   0,   0,   0,   0 ] ];

    for n in range(len(LEStateMap)):
        fmt = '%2i %s';
        for i in range(8):
            if ( LEStateMap[n][i] ):
                txt = '';
                for j in range(len(LEStateTexts)):
                    if ( LEStateMap[n][i] & (1<<j) ):
                        if ( len(txt) ):
                             txt += ' | '
                        txt += LEStateTexts[j];
                txt += ' SUPPORTED' if ( states[n] & (1<<i) ) else ' NOT SUPPORTED';
                if ( i ):
                    trace.trace(8, fmt % txt);
                else:
                    trace.trace(8, fmt % (n, txt));
            fmt = '   %s';

def showEventMask(eventMask, trace):
    """
        0x0000000000000000 ~ No events specified.
    """
    EventTexts = [ 'Inquiry Complete Event', 'Inquiry Result Event', 'Connection Complete Event', 'Connection Request Event',
                   'Disconnection Complete Event', 'Authentication Complete Event', 'Remote Name Request Complete Event', 'Encryption Change Event',
                   'Change Connection Link Key Complete Event', 'Master Link Key Complete Event', 'Read Remote Supported Features Complete Event', 'Read Remote Version Information Complete Event',
                   'QoS Setup Complete Event', 'Reserved', 'Reserved', 'Hardware Error Event',
                   'Flush Occurred Event', 'Role Change Event', 'Reserved', 'Mode Change Event',
                   'Return Link Keys Event', 'PIN Code Request Event', 'Link Key Request Event', 'Link Key Notification Event',
                   'Loopback Command Event', 'Data Buffer Overflow Event', 'Max Slots Change Event', 'Read Clock Offset Complete Event',
                   'Connection Packet Type Changed Event', 'QoS Violation Event', 'Page Scan Mode Change Event [deprecated]', 'Page Scan Repetition Mode Change Event',
                   'Flow Specification Complete Event', 'Inquiry Result with RSSI Event', 'Read Remote Extended Features Complete Event', 'Reserved',
                   'Reserved', 'Reserved', 'Reserved', 'Reserved',
                   'Reserved', 'Reserved', 'Reserved', 'Synchronous Connection Complete Event',
                   'Synchronous Connection Changed Event', 'Sniff Subrating Event', 'Extended Inquiry Result Event', 'Encryption Key Refresh Complete Event',
                   'IO Capability Request Event', 'IO Capability Request Reply Event', 'User Confirmation Request Event', 'User Passkey Request Event',
                   'Remote OOB Data Request Event','Simple Pairing Complete Event', 'Reserved', 'Link Supervision Timeout Changed Event',
                   'Enhanced Flush Complete Event', 'Reserved', 'User Passkey Notification Event', 'Keypress Notification Event',
                   'Remote Host Supported Features Notification Event', 'LE Meta-Event' ];
    """
        0x00001FFFFFFFFFFF ~ Default.
        0xC000000000000000 ~ Reserved for future use."
    """
    value = 0;
    for part in reversed(eventMask):
        value <<= 8;
        value += part;
    if ( value & 0x3FFFFFFFFFFFFFFFL ):
        if ( value == 0x1FFFFFFFFFFFL ):
            txt = 'Default';
        else:
            txt = '';
            for n in range(len(EventTexts)):
                if ( len(txt) ):
                    txt += ' | ';
                if ( value & (1L<<n) ):
                    txt += LEEventTexts[n];
    else:
        txt = 'No events specified';
    trace.trace(8, txt);
    
def showLEEventMask(eventMask, trace):
    """
        0x0000000000000000 ~ No LE events specified.
    """
    LEEventTexts = [ 'LE Connection Complete Event', 'LE Advertising Report Event', 'LE Connection Update Complete Event', 'LE Read Remote Used Features Complete Event',
                     'LE Long Term Key Request Event', 'LE Remote Connection Parameter Request Event' ];
    """
        0x000000000000001F ~ Default.
        0xFFFFFFFFFFFFFFC0 ~ Reserved for future use.
    """
    value = 0;
    for part in reversed(eventMask):
        value <<= 8;
        value += part;
    if ( value & 0x1f ):
        if ( value == 0x1f ):
            txt = 'Default';
        else:
            txt = '';
            for n in range(len(LEEventTexts)):
                if ( len(txt) ):
                    txt += ' | ';
                if ( value & (1<<n) ):
                    txt += LEEventTexts[n];
    else:
        txt = 'No LE events specified';
    trace.trace(8, txt);

def eventNone(eventData, trace):
    trace.trace(8, 'No event received!');

def eventDisconnect(eventData, trace):
    status, handle, reason = struct.unpack('<BHB', eventData[:4]);
    trace.trace(7, 'Disconnect Complete Event for Handle 0x%04X status 0x%02X reason 0x%02X' % (handle, status, reason));
    
def eventEncryptionChange(eventData, trace):
    status, handle, enabled = struct.unpack('<BHB', eventData[:4]);
    trace.trace(7, 'Encryption Change Event for Handle 0x%04X status 0x%02X enabled 0x%02X' % (handle, status, enabled));

def eventRemoteVersion(eventData, trace):
    status, handle, version, manufacturer, subVersion = struct.unpack('<BHBHH', eventData[:8]);
    trace.trace(7, 'Read Remote Version Information Event for Handle 0x%04X status 0x%02X version 0x%02X manufacturer 0x%04X' % (handle, status, version, manufacturer));

def eventCommandComplete(eventData, trace):
    numPackets, opCode, status = struct.unpack('<BHB', eventData[:4]);
    if opCode in opCodes:
        trace.trace(7, 'Command Complete Event for opCode 0x%04X (%s) status 0x%02X' % (opCode, opCodes[opCode], status));
    else:    
        trace.trace(7, 'Command Complete Event for opCode 0x%04X (Unknown) status 0x%02X' % (opCode, status));

def eventCommandStatus(eventData, trace):
    status, numPackets, opCode = struct.unpack('<BBH', eventData[:4]);
    if opCode in opCodes:
        trace.trace(7, 'Command Status Event for opCode 0x%04X (%s) status 0x%02X' % (opCode, opCodes[opCode], status));
    else:
        trace.trace(7, 'Command Status Event for opCode 0x%04X (Unknown) status 0x%02X' % (opCode, status));

def eventCompletedPackets(eventData, trace):
    numHandles = struct.unpack('<B', eventData[:1])[0];
    if numHandles > 0:
        handles = struct.unpack('<' + str(numHandles) + 'H', eventData[1:1+2*numHandles]);
        packets = struct.unpack('<' + str(numHandles) + 'H', eventData[1+2*numHandles:]);
        trace.trace(7, 'Number of Completed Packets Event handles %d: handle[0]=%d packets[0]=%d' % (numHandles, handles[0], packets[0]));
    else:
        trace.trace(7, 'Number of Completed Packets Event handles %d' % numHandles);
    
def eventBufferOverflow(eventData, trace):
    linkType = struct.unpack('<B', eventData[:1])[0];
    trace.trace(7, 'Data Buffer Overflow Event link type %d' % linkType);
    
def eventEncryptKeyRefresh(eventData, trace):
    status, handle = struct.unpack('<BH', eventData[:3]);
    trace.trace(7, 'Encryption Key Refresh Complete Event for Handle 0x%04X status 0x%02X' % (handle, status));
    
def eventConnected(eventData, trace):
    status, handle, role, addressType = struct.unpack('<BHBB', eventData[:5]);
    address = struct.unpack('<6B', eventData[5:11]);
    interval, latency, timeout, accuracy = struct.unpack('<HHHB', eventData[11:18]);
    trace.trace(7, 'LE Connection Complete Event for Handle 0x%04X status 0x%02X role 0x%02X (%s)' % (handle, status, role, ('MASTER' if (role == 0) else 'SLAVE')));
    
def eventAdvertisingReport(eventData, trace):
    reports, event, addressType = struct.unpack('<BBB', eventData[:3]);
    address = struct.unpack('<6B', eventData[3:9]);
    dataSize = struct.unpack('<B', eventData[9:10])[0];
    trace.trace(7, 'LE Advertising Report Event with %d report(s) event 0x%02X from %s with %d data bytes' % (reports, event, formatAddress(address, addressType), dataSize));
    
def eventConnectionUpdate(eventData, trace):
    status, handle, interval, latency, timeout = struct.unpack('<BHHHH', eventData[:9]);
    trace.trace(7, 'LE Connection Update Complete Event for Handle 0x%04X status 0x%02X' % (handle, status));
    
def eventRemoteFeatures(eventData, trace):
    status, handle = struct.unpack('<BH', eventData[:3]);
    features = struct.unpack('<8B', eventData[3:11]);
    trace.trace(7, 'LE Read Remote Features Complete Event for Handle 0x%04X status 0x%02X' % (handle, status));
    
def eventLTKRequest(eventData, trace):
    handle = struct.unpack('<H', eventData[:2])[0];
    number = struct.unpack('<8B', eventData[2:10]);
    diversifier = struct.unpack('<H', eventData[10:12])[0];
    trace.trace(7, 'LE Long Term Key Request Event for Handle 0x%04X number 0x%016X diversifier 0x%04X' % (handle, toNumber(number), diversifier));

def eventConnectionParameters(eventData, trace):
    handle, minInterval, maxInterval, latency, timeout = struct.unpack('<HHHHH', eventData[:10]);
    trace.trace(7, 'LE Remote Connection Parameter Request Event for Handle 0x%04X interval [%d, %d] latency %d timeout %d' % (handle, minInterval, maxInterval, latency, timeout));

def eventDataLengthChange(eventData, trace):
    handle, maxTxOctets, maxTxTime, maxRxOctets, maxRxTime = struct.unpack('<HHHHH', eventData[:10]);
    trace.trace(7, 'LE Data Length Change Event for Handle 0x%04X Tx (%d, %d) Rx (%d, %d)' % (handle, maxTxOctets, maxTxTime, maxRxOctets, maxRxTime));
    
def eventPublicKey(eventData, trace):
    status = struct.unpack('<B', eventData[:1])[0];
    key = struct.unpack('<64B', eventData[1:65]);
    trace.trace(7, 'LE Read Local P-256 Public Key Complete Event status 0x%02X key 0x%0128X' % (status, toNumber(key)));
    
def eventGeneratedDHKey(eventData, trace):
    status = struct.unpack('<B', eventData[:1])[0];
    key = struct.unpack('<32B', eventData[1:33]);
    trace.trace(7, 'LE Generate DHKey Complete Event status 0x%02X key 0x%064X' % (status, toNumber(key)));
    
def eventEnhancedConnection(eventData, trace):
    emptyAddress = numpy.asarray([ 0 for _ in range(6) ]);
    status, handle, role, addressType = struct.unpack('<BHBB', eventData[:5]);
    peerAddress = struct.unpack('<6B', eventData[5:11]);
    localResolvableAddress = numpy.asarray(struct.unpack('<6B', eventData[11:17]));
    peerResolvableAddress = numpy.asarray(struct.unpack('<6B', eventData[17:23]));
    interval, latency, timeout, accuracy = struct.unpack('<HHHB', eventData[23:30]);
    if (localResolvableAddress == emptyAddress).all() and (peerResolvableAddress == emptyAddress).all():
        trace.trace(7, 'LE Enhanced Connection Complete Event for Handle 0x%04X status 0x%02X Peer Address %s(%d) role 0x%02X (%s)' % (handle, status, formatAddress(peerAddress), addressType, role, ('MASTER' if (role == 0) else 'SLAVE')));
    else:
        trace.trace(7, 'LE Enhanced Connection Complete Event for Handle 0x%04X status 0x%02X Peer Address %s(%d) RPAs %s and %s role 0x%02X (%s)' % (handle, status, formatAddress(peerAddress), addressType, formatAddress(localResolvableAddress), formatAddress(peerResolvableAddress), role, ('MASTER' if (role == 0) else 'SLAVE')));

def eventDirectAdvertisingReport(eventData, trace):
    reports = struct.unpack('<B', eventData[:1])[0];
    trace.trace(7, 'LE Directed Advertising Report Event with %d report(s)' % reports);
    
def eventPhysicalUpdated(eventData, trace):
    status, handle, txPhysical, rxPhysical = struct.unpack('<BHBB', eventData[:5]);
    trace.trace(7, 'LE PHY Update Complete Event for Handle 0x%04X status 0x%02X Tx PHY %d Rx PHY %d' % (handle, status, txPhysical, rxPhysical));
    
def eventExtendedAdvertisingReport(eventData, trace):
    reports = struct.unpack('<B', eventData[:1])[0];
    trace.trace(7, 'LE Extended Advertising Report Event with %d report(s)' % reports);
    
def eventPeriodicAdvertisingSync(eventData, trace):
    status, handle = struct.unpack('<BH', eventData[:3]);
    trace.trace(7, 'LE Periodic Advertising Sync Established Event for Handle 0x%04X status 0x%02X' % (handle, status));
    
def eventPeriodicAdvertisingReport(eventData, trace):
    handle, txPower, RSSI, dontCare, dataStatus, dataLength = struct.unpack('<HBBBBB', eventData[:7]);
    trace.trace(7, 'LE Periodic Advertising Report Event for Handle 0x%04X TX Power %d RSSI %d Data Status 0x%02X Data Length %d' % (handle, txPower, RSSI, dataStatus, dataLength));
    
def eventPeriodicAdvertisingSyncLost(eventData, trace):
    handle = struct.unpack('<H', eventData[:2])[0];
    trace.trace(7, 'LE Periodic Advertising Sync Lost Event for Handle 0x%04X' % handle);
    
def eventScanTimeout(eventData, trace):
    trace.trace(7, 'LE Scan Timeout Event');
    
def eventAdvertiseSetTerminated(eventData, trace):
    status, advertiseHandle, connectionHandle, completedEvents = struct.unpack('<BBHB', eventData[:5]);
    trace.trace(7, 'LE Advertising Set Terminated Event for Advertise Handle 0x%04X Connection Handle 0x%04X status 0x%02X events %d' % (advertiseHandle, connectionHandle, completedEvents));
    
def eventScanRequestReceived(eventData, trace):
    handle, addressType = struct.unpack('<BB', eeventData[:2]);
    address = struct.unpack('<6B', eventData[2:]);
    trace.trace(7, 'LE Scan Request Received Event for Handle 0x%02X address %s' % (handle, formatAddress(address, addressType)));
    
def eventChannnelSeltionAlgorithm(eventData, trace):
    handle, algorithm = struct.unpack('<HB', eventData[:3]);
    trace.trace(7, 'LE Channel Selection Algorithm Event for Handle 0x%04X algorithm 0x%02X' % (handle, algorithm));
    
def eventLEMeta(eventData, trace):
    selections = { MetaEvents.BT_HCI_EVT_LE_CONN_COMPLETE:            eventConnected,
                   MetaEvents.BT_HCI_EVT_LE_ADVERTISING_REPORT:       eventAdvertisingReport,
                   MetaEvents.BT_HCI_EVT_LE_CONN_UPDATE_COMPLETE:     eventConnectionUpdate,
                   MetaEvents.BT_HCI_EVT_LE_REMOTE_FEAT_COMPLETE:     eventRemoteFeatures,
                   MetaEvents.BT_HCI_EVT_LE_LTK_REQUEST:              eventLTKRequest,
                   MetaEvents.BT_HCI_EVT_LE_CONN_PARAM_REQ:           eventConnectionParameters,
                   MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE:          eventDataLengthChange,
                   MetaEvents.BT_HCI_EVT_LE_P256_PUBLIC_KEY_COMPLETE: eventPublicKey,
                   MetaEvents.BT_HCI_EVT_LE_GENERATE_DHKEY_COMPLETE:  eventGeneratedDHKey,
                   MetaEvents.BT_HCI_EVT_LE_ENH_CONN_COMPLETE:        eventEnhancedConnection,
                   MetaEvents.BT_HCI_EVT_LE_DIRECT_ADV_REPORT:        eventDirectAdvertisingReport,
                   MetaEvents.BT_HCI_EVT_LE_PHY_UPDATE_COMPLETE:      eventPhysicalUpdated,
                   MetaEvents.BT_HCI_EVT_LE_EXT_ADVERTISING_REPORT:   eventExtendedAdvertisingReport,
                   MetaEvents.BT_HCI_EVT_LE_PER_ADV_SYNC_ESTABLISHED: eventPeriodicAdvertisingSync,
                   MetaEvents.BT_HCI_EVT_LE_PER_ADVERTISING_REPORT:   eventPeriodicAdvertisingReport,
                   MetaEvents.BT_HCI_EVT_LE_PER_ADV_SYNC_LOST:        eventPeriodicAdvertisingSyncLost,
                   MetaEvents.BT_HCI_EVT_LE_SCAN_TIMEOUT:             eventScanTimeout,
                   MetaEvents.BT_HCI_EVT_LE_ADV_SET_TERMINATED:       eventAdvertiseSetTerminated,
                   MetaEvents.BT_HCI_EVT_LE_SCAN_REQ_RECEIVED:        eventScanRequestReceived,
                   MetaEvents.BT_HCI_EVT_LE_CHAN_SEL_ALGO:            eventChannnelSeltionAlgorithm }; 
    subEvent = struct.unpack('<B', eventData[:1])[0];
    if subEvent in selections:
        selections[subEvent](eventData[1:], trace);
    else:
        trace.trace(7, 'LE Meta Event with invalid sub-event 0x%02X' & subEvent);

def eventAuthenticationTimeout(eventData, trace):
    handle = struct.unpack('<H', eventData[:2])[0];
    trace.trace(7, 'Authenticated Payload Timeout Expired Event for Handle 0x%04X' % handle);
    
def showEvent(event, eventData, trace):
    selections = { Events.BT_HCI_EVT_NONE: eventNone,
                   Events.BT_HCI_EVT_DISCONN_COMPLETE:                eventDisconnect,
                   Events.BT_HCI_EVT_ENCRYPT_CHANGE:                  eventEncryptionChange,
                   Events.BT_HCI_EVT_REMOTE_VERSION_INFO:             eventRemoteVersion,
                   Events.BT_HCI_EVT_CMD_COMPLETE:                    eventCommandComplete,
                   Events.BT_HCI_EVT_CMD_STATUS:                      eventCommandStatus,
                   Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS:           eventCompletedPackets,
                   Events.BT_HCI_EVT_DATA_BUF_OVERFLOW:               eventBufferOverflow,
                   Events.BT_HCI_EVT_ENCRYPT_KEY_REFRESH_COMPLETE:    eventEncryptKeyRefresh,
                   Events.BT_HCI_EVT_LE_META_EVENT:                   eventLEMeta,
                   Events.BT_HCI_EVT_AUTH_PAYLOAD_TIMEOUT_EXP:        eventAuthenticationTimeout };
    if event in selections:
        selections[event](eventData, trace);
    else:
        trace.trace(7, 'Illegal Event with event code 0x%02X' % event);
    
"""
   Note: Assumes that reports are 1 - doesn't have to be the case
"""
def directedAdvertiseReport(eventData):
    reports = struct.unpack('<B', eventData[1:2])[0];
    eventType, addressType = struct.unpack('<BB', eventData[2:4]);
    address = struct.unpack('<6B', eventData[4:10]);
    dirAddressType = struct.unpack('<B', eventData[10:11])[0];
    dirAddress = struct.unpack('<6B', eventData[11:17]);
    rssi = struct.unpack('<B', eventData[17:18])[0];
    return reports, eventType, addressType, address, dirAddressType, dirAddress, rssi;

"""
   Note: Assumes that reports are 1 - doesn't have to be the case
"""
def advertiseReport(eventData):
    reports = struct.unpack('<B', eventData[1:2])[0];
    eventType, addressType = struct.unpack('<BB', eventData[2:4]);
    address = struct.unpack('<6B', eventData[4:10]);
    dataSize = struct.unpack('<B', eventData[10:11])[0];
    data = [];
    if dataSize > 0:
        data += struct.unpack('<' + str(dataSize) + 'B', eventData[11:11+dataSize]);
    rssi = struct.unpack('<B', eventData[11+dataSize:12+dataSize])[0];
    return reports, eventType, addressType, address, data, rssi;

"""
    Parse either of 'LE Connection Complete Event' or 'LE Enhanced Connection Complete Event'
"""
def connectionComplete(eventData):
    subEvent = struct.unpack('<B', eventData[:1])[0];
    status, handle, role, addressType = struct.unpack('<BHBB', eventData[1:6]);
    address = struct.unpack('<6B', eventData[6:12]);
    if (subEvent == MetaEvents.BT_HCI_EVT_LE_ENH_CONN_COMPLETE):
        localRPA = struct.unpack('<6B', eventData[12:18]);
        peerRPA = struct.unpack('<6B', eventData[18:24]);
        interval, latency, timeout, accuracy = struct.unpack('<HHHB', eventData[24:31]);
    else:
        localRPA = [0 for _ in range(6)];
        peerRPA = [0 for _ in range(6)];
        interval, latency, timeout, accuracy = struct.unpack('<HHHB', eventData[12:19]);
    return status, handle, role, addressType, address, localRPA, peerRPA, interval, latency, timeout, accuracy;

def disconnectComplete(eventData):
    status, handle, reason = struct.unpack('<BHB', eventData[:4]);
    return status, handle, reason;

def connectionUpdated(eventData):
    subEvent = struct.unpack('<B', eventData[:1])[0];
    status, handle, interval, latency, timeout = struct.unpack('<BHHHH', eventData[1:10]);
    return status, handle, interval, latency, timeout;

def remoteConnectionParameterRequest(eventData):
    subEvent = struct.unpack('<B', eventData[:1])[0];
    handle, minInterval, maxInterval, latency, timeout = struct.unpack('<HHHHH', eventData[1:11]);
    return handle, minInterval, maxInterval, latency, timeout;

def remoteFeatures(eventData):
    subEvent = struct.unpack('<B', eventData[:1])[0];
    status, handle = struct.unpack('<BH', eventData[1:4]);
    features = struct.unpack('<8B', eventData[4:12]);	
    return status, handle, features;

def remoteVersion(eventData):
    status, handle, version, manufacturerID, subVersion = struct.unpack('<BHBHH', eventData[:8]);
    return status, handle, version, manufacturerID, subVersion;
    
def channelSelectionAlgorithm(eventData):
    status, handle, algorithm = struct.unpack('<BHB', eventData[:4]);
    return status, handle, algorithm;

def physicalUpdated(eventData):
    subEvent = struct.unpack('<B', eventData[:1])[0];
    status, handle, txPhys, rxPhys = struct.unpack('<BHBB', eventData[1:6]);
    return status, handle, txPhys, rxPhys;

def completedPackets(eventData):
    numHandles = struct.unpack('<B', eventData[:1])[0];
    if numHandles > 0:
        handles = struct.unpack('<' + str(numHandles) + 'H', eventData[1:1+2*numHandles]);
        packets = struct.unpack('<' + str(numHandles) + 'H', eventData[1+2*numHandles:]);
    else:
        handles = [];
        packets = [];
    return numHandles, handles, packets;

def dataLengthChanged(eventData):
    handle, maxTxOctets, maxTxTime, maxRxOctets, maxRxTime = struct.unpack('<HHHHH', eventData[1:]);
    return handle, maxTxOctets, maxTxTime, maxRxOctets, maxRxTime;

def toNumber(intArray):
    value = 0;
    for part in reversed(intArray):
        value <<= 8;
        value += part;
    return value;

def toArray(number, size):
    array = [0 for _ in range(size)];

    for i in range(size):
        array[i] = number & 0xFF;
        number >>= 8;
    return array;
