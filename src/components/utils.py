# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

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
            0x200F: 'LE Read Filter Accept List Size',
            0x2010: 'LE Clear Filter Accept List',
            0x2011: 'LE Add Device To Filter Accept List',
            0x2012: 'LE Remove Device From Filter Accept List',
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

crc_table_24_ble = [
    0x000000, 0x01b4c0, 0x036980, 0x02dd40, 0x06d300, 0x0767c0, 0x05ba80, 0x040e40,
    0x0da600, 0x0c12c0, 0x0ecf80, 0x0f7b40, 0x0b7500, 0x0ac1c0, 0x081c80, 0x09a840,
    0x1b4c00, 0x1af8c0, 0x182580, 0x199140, 0x1d9f00, 0x1c2bc0, 0x1ef680, 0x1f4240,
    0x16ea00, 0x175ec0, 0x158380, 0x143740, 0x103900, 0x118dc0, 0x135080, 0x12e440,
    0x369800, 0x372cc0, 0x35f180, 0x344540, 0x304b00, 0x31ffc0, 0x332280, 0x329640,
    0x3b3e00, 0x3a8ac0, 0x385780, 0x39e340, 0x3ded00, 0x3c59c0, 0x3e8480, 0x3f3040,
    0x2dd400, 0x2c60c0, 0x2ebd80, 0x2f0940, 0x2b0700, 0x2ab3c0, 0x286e80, 0x29da40,
    0x207200, 0x21c6c0, 0x231b80, 0x22af40, 0x26a100, 0x2715c0, 0x25c880, 0x247c40,
    0x6d3000, 0x6c84c0, 0x6e5980, 0x6fed40, 0x6be300, 0x6a57c0, 0x688a80, 0x693e40,
    0x609600, 0x6122c0, 0x63ff80, 0x624b40, 0x664500, 0x67f1c0, 0x652c80, 0x649840,
    0x767c00, 0x77c8c0, 0x751580, 0x74a140, 0x70af00, 0x711bc0, 0x73c680, 0x727240,
    0x7bda00, 0x7a6ec0, 0x78b380, 0x790740, 0x7d0900, 0x7cbdc0, 0x7e6080, 0x7fd440,
    0x5ba800, 0x5a1cc0, 0x58c180, 0x597540, 0x5d7b00, 0x5ccfc0, 0x5e1280, 0x5fa640,
    0x560e00, 0x57bac0, 0x556780, 0x54d340, 0x50dd00, 0x5169c0, 0x53b480, 0x520040,
    0x40e400, 0x4150c0, 0x438d80, 0x423940, 0x463700, 0x4783c0, 0x455e80, 0x44ea40,
    0x4d4200, 0x4cf6c0, 0x4e2b80, 0x4f9f40, 0x4b9100, 0x4a25c0, 0x48f880, 0x494c40,
    0xda6000, 0xdbd4c0, 0xd90980, 0xd8bd40, 0xdcb300, 0xdd07c0, 0xdfda80, 0xde6e40,
    0xd7c600, 0xd672c0, 0xd4af80, 0xd51b40, 0xd11500, 0xd0a1c0, 0xd27c80, 0xd3c840,
    0xc12c00, 0xc098c0, 0xc24580, 0xc3f140, 0xc7ff00, 0xc64bc0, 0xc49680, 0xc52240,
    0xcc8a00, 0xcd3ec0, 0xcfe380, 0xce5740, 0xca5900, 0xcbedc0, 0xc93080, 0xc88440,
    0xecf800, 0xed4cc0, 0xef9180, 0xee2540, 0xea2b00, 0xeb9fc0, 0xe94280, 0xe8f640,
    0xe15e00, 0xe0eac0, 0xe23780, 0xe38340, 0xe78d00, 0xe639c0, 0xe4e480, 0xe55040,
    0xf7b400, 0xf600c0, 0xf4dd80, 0xf56940, 0xf16700, 0xf0d3c0, 0xf20e80, 0xf3ba40,
    0xfa1200, 0xfba6c0, 0xf97b80, 0xf8cf40, 0xfcc100, 0xfd75c0, 0xffa880, 0xfe1c40,
    0xb75000, 0xb6e4c0, 0xb43980, 0xb58d40, 0xb18300, 0xb037c0, 0xb2ea80, 0xb35e40,
    0xbaf600, 0xbb42c0, 0xb99f80, 0xb82b40, 0xbc2500, 0xbd91c0, 0xbf4c80, 0xbef840,
    0xac1c00, 0xada8c0, 0xaf7580, 0xaec140, 0xaacf00, 0xab7bc0, 0xa9a680, 0xa81240,
    0xa1ba00, 0xa00ec0, 0xa2d380, 0xa36740, 0xa76900, 0xa6ddc0, 0xa40080, 0xa5b440,
    0x81c800, 0x807cc0, 0x82a180, 0x831540, 0x871b00, 0x86afc0, 0x847280, 0x85c640,
    0x8c6e00, 0x8ddac0, 0x8f0780, 0x8eb340, 0x8abd00, 0x8b09c0, 0x89d480, 0x886040,
    0x9a8400, 0x9b30c0, 0x99ed80, 0x985940, 0x9c5700, 0x9de3c0, 0x9f3e80, 0x9e8a40,
    0x972200, 0x9696c0, 0x944b80, 0x95ff40, 0x91f100, 0x9045c0, 0x929880, 0x932c40
]


# Bitwise reverse 1 byte
def rev_byte(input):
    result = 0
    for bit in range(8):
        if input & (1 << bit):
            result = result | (1 << (7-bit))
    return result

# Reverse the bits order in a 24 bit word
def rev_24(input):
    return rev_byte((input >> 0) & 0xff) << 16 | rev_byte((input >> 8) & 0xff) << 8 | rev_byte((input >> 16) & 0xff)

def BLECRCUpdate(crc, data):
    for i in range(len(data)):
        tbl_idx = (crc ^ data[i]) & 0xff
        crc = (crc_table_24_ble[tbl_idx] ^ (crc >> 8)) & 0xffffff
    return crc & 0xffffff

def calcBLECRC(crc_init, packet):
    return BLECRCUpdate(rev_24(crc_init), packet)

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
        [ 'Set Connection Encryption', 'Change Connection Link Key', 'Central Link Key', 'Remote Name Request', 'Remote Name Request Cancel', 'Read Remote Supported Features', 'Read Remote Extended Features', 'Read Remote Version Information' ],
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
        [ 'LE Set Scan Response Data', 'LE Set Advertising Enable', 'LE Set Scan Parameters', 'LE Set Scan Enable', 'LE Create Connection', 'LE Create Connection Cancel', 'LE Read Filter Accept List Size', 'LE Clear Filter Accept List' ],
        [ 'LE Add Device To Filter Accept List', 'LE Remove Device From Filter Accept List', 'LE Connection Update', 'LE Set Host Channel Classification', 'LE Read Channel Map', 'LE Read Remote Features', 'LE Encrypt', 'LE Rand' ],
        [ 'LE Start Encryption', 'LE Long Term Key Request Reply', 'LE Long Term Key Request Negative Reply', 'LE Read Supported States', 'LE Receiver Test', 'LE Transmitter Test', 'LE Test End', 'Reserved for Future Use' ],
        [ 'Reserved for Future Use', 'Reserved for Future Use', 'Reserved for Future Use', 'Enhanced Setup Synchronous Connection', 'Enhanced Accept Synchronous Connection', 'Read Local Supported Codecs', 'Set MWS Channel Parameters', 'Set External Frame Configuration' ],
        [ 'Set MWS Signaling', 'Set MWS Transport Layer', 'Set MWS Scan Frequency Table', 'Get MWS Transport Layer Configuration', 'Set MWS PATTERN Configuration', 'Set Triggered Clock Capture', 'Truncated Page', 'Truncated Page Cancel' ],
        [ 'Set Connectionless Peripheral Broadcast', 'Set Connectionless Peripheral Broadcast Receive', 'Start Synchronization Train', 'Receive Synchronization Train', 'Set Reserved LT_ADDR', 'Delete Reserved LT_ADDR', 'Set Connectionless Peripheral Broadcast Data', 'Read Synchronization Train Parameters' ],
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
        [ 'EV4 packets', 'EV5 packets', 'Reserved for Future Use', 'AFH capable peripheral', 'AFH classification peripheral', 'BR/EDR Not Supported', 'LE Supported (Controller)', '3-slot Enhanced Data Rate ACL packets' ],
        [ '5-slot Enhanced Data Rate ACL packets', 'Sniff subrating', 'Pause encryption', 'AFH capable central', 'AFH classification central', 'Enhanced Data Rate eSCO 2 Mb/s mode', 'Enhanced Data Rate eSCO 3 Mb/s mode', '3-slot Enhanced Data Rate eSCO packets' ],
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
        [ 'LE Encryption', 'Connection Parameters Request Procedure', 'Extended Reject Indication', 'Peripheral-initiated Features Exchange', 'LE Ping', 'LE Data Packet Length Extension', 'LL Privacy', 'Extended Scanner Filter Policies' ],
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
                     'Active Scanning State', 'Passive Scanning State', 'Initiating State', 'Connection State (Central Role)', 'Connection State (Peripheral Role)' ];
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
                   'Change Connection Link Key Complete Event', 'Central Link Key Complete Event', 'Read Remote Supported Features Complete Event', 'Read Remote Version Information Complete Event',
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
                    txt += EventTexts[n];
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
