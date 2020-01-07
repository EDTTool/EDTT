# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

import struct;
from enum import IntEnum;

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
    if ( value & 0x3FFFFFFFFFFFFFFF ):
        if ( value == 0x1FFFFFFFFFFF ):
            txt = 'Default';
        else:
            txt = '';
            for n in range(len(EventTexts)):
                if ( len(txt) ):
                    txt += ' | ';
                if ( value & (1<<n) ):
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
