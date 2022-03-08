# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

from enum import IntEnum;
from .utils import *;

class ADType(IntEnum):
    FLAGS                   =   1 # «Flags» Bluetooth Core Specification : Vol. 3, Part C, section 8.1.3 (v2.1 + EDR, 3.0 + HS and 4.0) Vol. 3, Part C, sections 11.1.3 and 18.1 (v4.0) Core Specification Supplement, Part A, section 1.3
    ILIST_UUIDS_16          =   2 # «Incomplete List of 16 - bit Service Class UUIDs» Bluetooth Core Specification : Vol. 3, Part C, section 8.1.1 (v2.1 + EDR, 3.0 + HS and 4.0) Vol. 3, Part C, sections 11.1.1 and 18.2 (v4.0) Core Specification Supplement, Part A, section 1.1
    CLIST_UUIDS_16          =   3 # «Complete List of 16 - bit Service Class UUIDs» Bluetooth Core Specification : Vol. 3, Part C, section 8.1.1 (v2.1 + EDR, 3.0 + HS and 4.0) Vol. 3, Part C, sections 11.1.1 and 18.2 (v4.0) Core Specification Supplement, Part A, section 1.1
    ILIST_UUIDS_32          =   4 # «Incomplete List of 32 - bit Service Class UUIDs» Bluetooth Core Specification : Vol. 3, Part C, section 8.1.1 (v2.1 + EDR, 3.0 + HS and 4.0) Vol. 3, Part C, section 18.2 (v4.0) Core Specification Supplement, Part A, section 1.1
    CLIST_UUIDS_32          =   5 # «Complete List of 32 - bit Service Class UUIDs» Bluetooth Core Specification : Vol. 3, Part C, section 8.1.1 (v2.1 + EDR, 3.0 + HS and 4.0) Vol. 3, Part C, section 18.2 (v4.0) Core Specification Supplement, Part A, section 1.1
    ILIST_UUIDS_128         =   6 # «Incomplete List of 128 - bit Service Class UUIDs» Bluetooth Core Specification : Vol. 3, Part C, section 8.1.1 (v2.1 + EDR, 3.0 + HS and 4.0) Vol. 3, Part C, sections 11.1.1 and 18.2 (v4.0) Core Specification Supplement, Part A, section 1.1
    CLIST_UUIDS_128         =   7 # «Complete List of 128 - bit Service Class UUIDs» Bluetooth Core Specification : Vol. 3, Part C, section 8.1.1 (v2.1 + EDR, 3.0 + HS and 4.0) Vol. 3, Part C, sections 11.1.1 and 18.2 (v4.0) Core Specification Supplement, Part A, section 1.1
    SHORTENED_LOCAL_NAME    =   8 # «Shortened Local Name» Bluetooth Core Specification : Vol. 3, Part C, section 8.1.2 (v2.1 + EDR, 3.0 + HS and 4.0) Vol. 3, Part C, sections 11.1.2 and 18.4 (v4.0) Core Specification Supplement, Part A, section 1.2
    COMPLETE_LOCAL_NAME     =   9 # «Complete Local Name» Bluetooth Core Specification : Vol. 3, Part C, section 8.1.2 (v2.1 + EDR, 3.0 + HS and 4.0) Vol. 3, Part C, sections 11.1.2 and 18.4 (v4.0) Core Specification Supplement, Part A, section 1.2
    TX_POWER_LEVEL          =  10 # «Tx Power Level» Bluetooth Core Specification : Vol. 3, Part C, section 8.1.5 (v2.1 + EDR, 3.0 + HS and 4.0) Vol. 3, Part C, sections 11.1.5 and 18.3 (v4.0) Core Specification Supplement, Part A, section 1.5
    DEVICE_CLASS            =  13 # «Class of Device» Bluetooth Core Specification : Vol. 3, Part C, section 8.1.6 (v2.1 + EDR, 3.0 + HS and 4.0) Vol. 3, Part C, sections 11.1.5 and 18.5 (v4.0) Core Specification Supplement, Part A, section 1.6
    PAIR_HASH_C             =  14 # «Simple Pairing Hash C» Bluetooth Core Specification : Vol. 3, Part C, section 8.1.6 (v2.1 + EDR, 3.0 + HS and 4.0) Vol. 3, Part C, sections 11.1.5 and 18.5 (v4.0) ​
    PAIR_RANDOM_R           =  15 # «Simple Pairing Randomizer R» Bluetooth Core Specification : Vol. 3, Part C, section 8.1.6 (v2.1 + EDR, 3.0 + HS and 4.0) Vol. 3, Part C, sections 11.1.5 and 18.5 (v4.0)
    SEC_MANAGER_TK          =  16 # «Security Manager TK Value» Bluetooth Core Specification : Vol. 3, Part C, sections 11.1.7 and 18.6 (v4.0) Core Specification Supplement, Part A, section 1.8
    SEC_MANAGER_OBF         =  17 # «Security Manager Out of Band Flags» Bluetooth Core Specification : Vol. 3, Part C, sections 11.1.6 and 18.7 (v4.0) Core Specification Supplement, Part A, section 1.7
    PERIPHERAL_CONNECT_INT       =  18 # «Peripheral Connection Interval Range» Bluetooth Core Specification : Vol. 3, Part C, sections 11.1.8 and 18.8 (v4.0) Core Specification Supplement, Part A, section 1.9
    SS_UUIDS_16             =  20 # «List of 16 - bit Service Solicitation UUIDs» Bluetooth Core Specification : Vol. 3, Part C, sections 11.1.9 and 18.9 (v4.0) Core Specification Supplement, Part A, section 1.10
    SS_UUIDS_128            =  21 # «List of 128 - bit Service Solicitation UUIDs» Bluetooth Core Specification : Vol. 3, Part C, sections 11.1.9 and 18.9 (v4.0) Core Specification Supplement, Part A, section 1.10
    SERVICE_DATA_16         =  22 # «Service Data» Bluetooth Core Specification : Vol. 3, Part C, sections 11.1.10 and 18.10 (v4.0)
    PUBLIC_ADDRESS          =  23 # «Public Target Address» Bluetooth Core Specification : Core Specification Supplement, Part A, section 1.13
    RANDOM_ADDRESS          =  24 # «Random Target Address» Bluetooth Core Specification : Core Specification Supplement, Part A, section 1.14
    APPEARANCE              =  25 # «Appearance» Bluetooth Core Specification : Core Specification Supplement, Part A, section 1.12
    ADVERTISE_INT           =  26 # ​«Advertising Interval» ​Bluetooth Core Specification : Core Specification Supplement, Part A, section 1.15​​​​
    DEVICE_ADDRESS          =  27 # «​LE Bluetooth Device Address» ​Core Specification Supplement, Part A, section 1.16
    DEVICE_ROLE             =  28 # «​LE Role» ​Core Specification Supplement, Part A, section 1.17
    PAIR_HASH_C256          =  29 # «​Simple Pairing Hash C - 256» ​Core Specification Supplement, Part A, section 1.6
    PAIR_RANDOM_R256        =  30 # «​Simple Pairing Randomizer R - 256» ​Core Specification Supplement, Part A, section 1.6
    SS_UUIDS_32             =  31 # ​«List of 32 - bit Service Solicitation UUIDs» ​Core Specification Supplement, Part A, section 1.10
    SERVICE_DATA_32         =  32 # ​«Service Data - 32 - bit UUID» ​Core Specification Supplement, Part A, section 1.11
    SERVICE_DATA_128        =  33 # ​«Service Data - 128 - bit UUID» ​Core Specification Supplement, Part A, section 1.11
    SEC_CONNECT_CONFIRM     =  34 # ​«​LE Secure Connections Confirmation Value» ​Core Specification Supplement Part A, Section 1.6
    SEC_CONNECT_RANDOM      =  35 # ​​«​LE Secure Connections Random Value» ​Core Specification Supplement Part A, Section 1.6​
    URI                     =  36 # ​​​«​URI» ​Bluetooth Core Specification : Core Specification Supplement, Part A, section 1.18
    INDOOR_POSITION         =  37 # ​«Indoor Positioning» ​Indoor Posiioning Service v1.0 or later
    DISCOVERY_DATA          =  38 # ​«Transport Discovery Data» ​Transport Discovery Service v1.0 or later​
    LE_SUPPORTED_FEATURES   =  39 # «LE Supported Features» Core Specification Supplement, Part A, Section 1.19
    CHANNEL_MAP_UPDATE      =  40 # «Channel Map Update Indication» Core Specification Supplement, Part A, Section 1.20
    INFO_DATA_3D            =  61 # ​​«3D Information Data» ​3D Synchronization Profile, v1.0 or later
    MANUFACTURER_DATA       = 255 # «Manufacturer Specific Data» Bluetooth Core Specification : Vol. 3, Part C, section 8.1.4 (v2.1 + EDR, 3.0 + HS and 4.0) Vol. 3, Part C, sections 11.1.4 and 18.11 (v4.0) Core Specification Supplement, Part A, section 1.4​

class ADRole(IntEnum):
    ONLY_PERIPHERAL         =   0 # Only Peripheral Role supported
    ONLY_CENTRAL            =   1 # Only Central Role supported
    PERIPHERAL_PREFERRED    =   2 # Peripheral and Central Role supported, Peripheral Role preferred for connection establishment
    CENTRAL_PREFERRED       =   3 # Peripheral and Central Role supported, Central Role preferred for connection establishment

class ADFlag(IntEnum):
    LE_LIMITED_DISCOVERABLE =   1 # LE Limited Discoverable Mode
    LE_GENERAL_DISCOVERABLE =   2 # LE General Discoverable Mode
    BR_EDR_NOT_SUPPORTED    =   4 # BR/EDR Not Supported. Bit 37 of LMP Feature Mask Definitions.
    LE_BR_EDR_CAPABLE_CTRL  =   8 # Simultaneous LE and BR/EDR to Same Device Capable (Controller). Bit 49 of LMP Feature Mask Definitions.
    LE_BR_EDR_CAPABLE_HOST  =  16 # Simultaneous LE and BR/EDR to Same Device Capable (Host).       Bit 66 of LMP Feature Mask Definitions.
    LE_FLAGS_ALL            =  31 # All flags set

"""
    Appearance is a 16 bit number divided into a Category (most significant 10 bits) and a Sub-category (least significant 6 bits)

    Category Category Name      Sub-category Sub-category Name                Appearance Value
           0 Unknown                       0 Unknown                                         0
           1 Phone                         0 Generic Phone                                  64
           2 Computer                      0 Generic Computer                              128
           3 Watch                         0 Generic Watch                                 192
                                           1 Sports Watch                                  193
           4 Clock                         0 Generic Clock                                 256
           5 Display                       0 Generic Display                               320
           6 Remote Control                0 Generic Remote Control                        384
           7 Eye-glasses                   0 Generic Eye-glasses                           448
           8 Tag                           0 Generic Tag                                   512
           9 Keyring                       0 Generic Keyring                               576
          10 Media Player                  0 Generic Media Player                          640
          11 Barcode Scanner               0 Generic Barcode Scanner                       704
          12 Thermometer                   0 Generic Thermometer                           768
                                           1 Ear Thermometer                               769
          13 Heart rate Sensor             0 Generic Heart rate Sensor                     832
                                           1 Heart rate Belt                               833
          14 Blood Pressure                0 Generic Blood Pressure                        896
                                           1 Blood Pressure Arm                            897
                                           2 Blood Pressure Wrist                          898
          15 Human Interface Device (HID)  0 Generic Human Interface Device                960
                                           1 Keyboard                                      961
                                           2 Mouse                                         962
                                           3 Joystick                                      963
                                           4 Gamepad                                       964
                                           5 Digitizer Tablet                              965
                                           6 Card Reader                                   966
                                           7 Digital Pen                                   967
                                           8 Barcode Scanner                               968
          16 Glucoose Meter                0 Generic Glucoose Meter                       1024
          17 Running Walking Sensor        0 Generic Running Walking Sensor               1088
                                           1 In-Shoe Running Walking Sensor               1089
                                           2 On-Shoe Running Walking Sensor               1090
                                           3 On-Hip  Running Walking Sensor               1091
          18 Cycling                       0 Generic Cycling                              1152
                                           1 Cycling Computer                             1153
                                           2 Speed Sensor                                 1154
                                           3 Cadence Sensor                               1155
                                           4 Power Sensor                                 1156
                                           5 Speed and Cadence Sensor                     1157
          49 Pulse Oximeter                0 Generic Pulse Oximeter                       3136
                                           1 Fingertip                                    3137
                                           2 Wrist Worn                                   3138
          50 Weight Scale                  0 Generic Weight Scale                         3200
          51 Personal Mobility Device      0 Generic Personal Mobility Device             3264
                                           1 Powered Weelchair                            3265
                                           2 Mobility Scooter                             3266
          52 Continuous Glucoose Monitor   0 Generic Continuous Glucoose Monitor          3328
          53 Insulin Pump                  0 Generic Insulin Pump                         3392
                                           1 Durable Insulin Pump                         3393
                                           4 Patch   Insulin Pump                         3396
                                           8 Insulin Pen                                  3400
          54 Medication Delivery           0 Generic Medication Delivery                  3456
          81 Outdoor Sports Activity       0 Generic Outdoor Sports Activity              5184
                                           1 Location Display Device                      5185
                                           2 Location and Navigation Display Device       5186
                                           3 Location Pod                                 5187
                                           4 Location and Navigation Pod                  5188
"""

__schemeNames__ = {
    'aaa':                      [ 0X02 ],
    'aaas':                     [ 0X03 ],
    'about':                    [ 0X04 ],
    'acap':                     [ 0X05 ],
    'acct':                     [ 0X06 ],
    'cap':                      [ 0X07 ],
    'cid':                      [ 0X08 ],
    'coap':                     [ 0X09 ],
    'coaps':                    [ 0X0A ],
    'crid':                     [ 0X0B ],
    'data':                     [ 0X0C ],
    'dav':                      [ 0X0D ],
    'dict':                     [ 0X0E ],
    'dns':                      [ 0X0F ],
    'file':                     [ 0X10 ],
    'ftp':                      [ 0X11 ],
    'geo':                      [ 0X12 ],
    'go':                       [ 0X13 ],
    'gopher':                   [ 0X14 ],
    'h323':                     [ 0X15 ],
    'http':                     [ 0X16 ],
    'https':                    [ 0X17 ],
    'iax':                      [ 0X18 ],
    'icap':                     [ 0X19 ],
    'im':                       [ 0X1A ],
    'imap':                     [ 0X1B ],
    'info':                     [ 0X1C ],
    'ipp':                      [ 0X1D ],
    'ipps':                     [ 0X1E ],
    'iris':                     [ 0X1F ],
    'iris.beep':                [ 0X20 ],
    'iris.xpc':                 [ 0X21 ],
    'iris.xpcs':                [ 0X22 ],
    'iris.lwz':                 [ 0X23 ],
    'jabber':                   [ 0X24 ],
    'ldap':                     [ 0X25 ],
    'mailto':                   [ 0X26 ],
    'mid':                      [ 0X27 ],
    'msrp':                     [ 0X28 ],
    'msrps':                    [ 0X29 ],
    'mtqp':                     [ 0X2A ],
    'mupdate':                  [ 0X2B ],
    'news':                     [ 0X2C ],
    'nfs':                      [ 0X2D ],
    'ni':                       [ 0X2E ],
    'nih':                      [ 0X2F ],
    'nntp':                     [ 0X30 ],
    'opaquelocktoken':          [ 0X31 ],
    'pop':                      [ 0X32 ],
    'pres':                     [ 0X33 ],
    'reload':                   [ 0X34 ],
    'rtsp':                     [ 0X35 ],
    'rtsps':                    [ 0X36 ],
    'rtspu':                    [ 0X37 ],
    'service':                  [ 0X38 ],
    'session':                  [ 0X39 ],
    'shttp':                    [ 0X3A ],
    'sieve':                    [ 0X3B ],
    'sip':                      [ 0X3C ],
    'sips':                     [ 0X3D ],
    'sms':                      [ 0X3E ],
    'snmp':                     [ 0X3F ],
    'soap.beep':                [ 0X40 ],
    'soap.beeps':               [ 0X41 ],
    'stun':                     [ 0X42 ],
    'stuns':                    [ 0X43 ],
    'tag':                      [ 0X44 ],
    'tel':                      [ 0X45 ],
    'telnet':                   [ 0X46 ],
    'tftp':                     [ 0X47 ],
    'thismessage':              [ 0X48 ],
    'tn3270':                   [ 0X49 ],
    'tip':                      [ 0X4A ],
    'turn':                     [ 0X4B ],
    'turns':                    [ 0X4C ],
    'tv':                       [ 0X4D ],
    'urn':                      [ 0X4E ],
    'vemmi':                    [ 0X4F ],
    'ws':                       [ 0X50 ],
    'wss':                      [ 0X51 ],
    'xcon':                     [ 0X52 ],
    'xcon-userid':              [ 0X53 ],
    'xmlrpc.beep':              [ 0X54 ],
    'xmlrpc.beeps':             [ 0X55 ],
    'xmpp':                     [ 0X56 ],
    'z39.50r':                  [ 0X57 ],
    'z39.50s':                  [ 0X58 ],
    'acr':                      [ 0X59 ],
    'adiumxtra':                [ 0X5A ],
    'afp':                      [ 0X5B ],
    'afs':                      [ 0X5C ],
    'aim':                      [ 0X5D ],
    'apt':                      [ 0X5E ],
    'attachment':               [ 0X5F ],
    'aw':                       [ 0X60 ],
    'barion':                   [ 0X61 ],
    'beshare':                  [ 0X62 ],
    'bitcoin':                  [ 0X63 ],
    'bolo':                     [ 0X64 ],
    'callto':                   [ 0X65 ],
    'chrome':                   [ 0X66 ],
    'chrome-extension':         [ 0X67 ],
    'com-eventbrite-attendee':  [ 0X68 ],
    'content':                  [ 0X69 ],
    'cvs':                      [ 0X6A ],
    'dlna-playsingle':          [ 0X6B ],
    'dlna-playcontainer':       [ 0X6C ],
    'dtn':                      [ 0X6D ],
    'dvb':                      [ 0X6E ],
    'ed2k':                     [ 0X6F ],
    'facetime':                 [ 0X70 ],
    'feed':                     [ 0X71 ],
    'feedready':                [ 0X72 ],
    'finger':                   [ 0X73 ],
    'fish':                     [ 0X74 ],
    'gg':                       [ 0X75 ],
    'git':                      [ 0X76 ],
    'gizmoproject':             [ 0X77 ],
    'gtalk':                    [ 0X78 ],
    'ham':                      [ 0X79 ],
    'hcp':                      [ 0X7A ],
    'icon':                     [ 0X7B ],
    'ipn':                      [ 0X7C ],
    'irc':                      [ 0X7D ],
    'irc6':                     [ 0X7E ],
    'ircs':                     [ 0X7F ],
    'itms':                     [ 0XC2, 0X80 ],
    'jar':                      [ 0XC2, 0X81 ],
    'jms':                      [ 0XC2, 0X82 ],
    'keyparc':                  [ 0XC2, 0X83 ],
    'lastfm':                   [ 0XC2, 0X84 ],
    'ldaps':                    [ 0XC2, 0X85 ],
    'magnet':                   [ 0XC2, 0X86 ],
    'maps':                     [ 0XC2, 0X87 ],
    'market':                   [ 0XC2, 0X88 ],
    'message':                  [ 0XC2, 0X89 ],
    'mms':                      [ 0XC2, 0X8A ],
    'ms-help':                  [ 0XC2, 0X8B ],
    'ms-settings-power':        [ 0XC2, 0X8C ],
    'msnim':                    [ 0XC2, 0X8D ],
    'mumble':                   [ 0XC2, 0X8E ],
    'mvn':                      [ 0XC2, 0X8F ],
    'notes':                    [ 0XC2, 0X90 ],
    'oid':                      [ 0XC2, 0X91 ],
    'palm':                     [ 0XC2, 0X92 ],
    'paparazzi':                [ 0XC2, 0X93 ],
    'pkcs11':                   [ 0XC2, 0X94 ],
    'platform':                 [ 0XC2, 0X95 ],
    'proxy':                    [ 0XC2, 0X96 ],
    'psyc':                     [ 0XC2, 0X97 ],
    'query':                    [ 0XC2, 0X98 ],
    'res':                      [ 0XC2, 0X99 ],
    'resource':                 [ 0XC2, 0X9A ],
    'rmi':                      [ 0XC2, 0X9B ],
    'rsync':                    [ 0XC2, 0X9C ],
    'rtmfp':                    [ 0XC2, 0X9D ],
    'rtmp':                     [ 0XC2, 0X9E ],
    'secondlife':               [ 0XC2, 0X9F ],
    'sftp':                     [ 0XC2, 0XA0 ],
    'sgn':                      [ 0XC2, 0XA1 ],
    'skype':                    [ 0XC2, 0XA2 ],
    'smb':                      [ 0XC2, 0XA3 ],
    'smtp':                     [ 0XC2, 0XA4 ],
    'soldat':                   [ 0XC2, 0XA5 ],
    'spotify':                  [ 0XC2, 0XA6 ],
    'ssh':                      [ 0XC2, 0XA7 ],
    'steam':                    [ 0XC2, 0XA8 ],
    'submit':                   [ 0XC2, 0XA9 ],
    'svn':                      [ 0XC2, 0XAA ],
    'teamspeak':                [ 0XC2, 0XAB ],
    'teliaeid':                 [ 0XC2, 0XAC ],
    'things':                   [ 0XC2, 0XAD ],
    'udp':                      [ 0XC2, 0XAE ],
    'unreal':                   [ 0XC2, 0XAF ],
    'ut2004':                   [ 0XC2, 0XB0 ],
    'ventrilo':                 [ 0XC2, 0XB1 ],
    'view-source':              [ 0XC2, 0XB2 ],
    'webcal':                   [ 0XC2, 0XB3 ],
    'wtai':                     [ 0XC2, 0XB4 ],
    'wyciwyg':                  [ 0XC2, 0XB5 ],
    'xfire':                    [ 0XC2, 0XB6 ],
    'xri':                      [ 0XC2, 0XB7 ],
    'ymsgr':                    [ 0XC2, 0XB8 ],
    'example':                  [ 0XC2, 0XB9 ],
    'ms-settings-cloudstorage': [ 0XC2, 0XBA ]
};

class ADData:

    def __init__(self):
        self.data = [];

    def encode(self, adType, *args):
      #
      # ADType.TX_POWER_LEVEL, <power_level>; where <power_level> [ -127, +127 ] dBm.
      #
        if ( adType == ADType.TX_POWER_LEVEL ):
            self.data = [ 2, adType, args[0] if args[0] >= 0 else 256+args[0] ];
      #
      # ADType.FLAGS, <flags>           where <flags> [ 0, 31 ]
      # ADType.SEC_MANAGER_OBF, <flags> where <flags> [ 0, 15 ]
      # ADType.DEVICE_ROLE, <role>      where <role>  [ 0, 3 ]
      #
        elif ( adType == ADType.FLAGS or adType == ADType.SEC_MANAGER_OBF or adType == ADType.DEVICE_ROLE ):
            self.data = [ 2, adType, args[0] ];
      #
      # ADType.ILIST_UUIDS_16, <uuid_A>, <uuid_B>, ...
      # ADTYpe,CLIST_UUIDS_16, <uuid_A>, <uuid_B>, ...
      # ADType.SS_UUIDS_16,    <uuid_A>, <uuid_B>, ...
      #
        elif ( adType == ADType.ILIST_UUIDS_16 or adType == ADType.CLIST_UUIDS_16 or adType == ADType.SS_UUIDS_16 ):
            self.data = [ 1+2*len(args), adType ];
            for arg in args:
                self.data += toArray(arg, 2);
      #
      # ADType.ILIST_UUIDS_32, <uuid_A>, <uuid_B>, ...
      # ADTYpe,CLIST_UUIDS_32, <uuid_A>, <uuid_B>, ...
      # ADType.SS_UUIDS_32,    <uuid_A>, <uuid_B>, ...
      #
        elif ( adType == ADType.ILIST_UUIDS_32 or adType == ADType.CLIST_UUIDS_32 or adType == ADType.SS_UUIDS_32 ):
            self.data = [ 1+4*len(args), adType ];
            for arg in args:
                self.data += toArray(arg, 4);
      #
      # ADType.ILIST_UUIDS_128, <uuid_A>, <uuid_B>, ...
      # ADTYpe,CLIST_UUIDS_128, <uuid_A>, <uuid_B>, ...
      # ADType.SS_UUIDS_128,    <uuid_A>, <uuid_B>, ...
      #
        elif ( adType == ADType.ILIST_UUIDS_128 or adType == ADType.CLIST_UUIDS_128 or adType == ADType.SS_UUIDS_128 ):
            self.data = [ 1+16*len(args), adType ];
            for arg in args:
                self.data += toArray(arg, 16);
      #
      # ADType.SHORTENED_LOCAL_NAME, <unicode_name>
      # ADType.COMPLETE_LOCAL_NAME,  <unicode_name>
      #
        elif ( adType == ADType.SHORTENED_LOCAL_NAME or adType == ADType.COMPLETE_LOCAL_NAME ):
            name = args[0].encode('UTF-8');
            if len(name) > 29:
                name = name[:29];
            self.data = [ 1+len(name), adType ] + [ _ for _ in name ];
      #
      # ADType.DEVICE_CLASS, <device_class>
      #
        elif ( adType == ADType.DEVICE_CLASS ):
            self.data = [ 4, adType ] + toArray(args[0], 3);
      #
      # ADType.PAIR_HASH_C,    <hash_value>
      # ADType.PAIR_RANDOM_R,  <random_value>
      # ADType.SEC_MANAGER_TK, <tk_value>
      #
        elif ( adType == ADType.PAIR_HASH_C or adType == ADType.PAIR_RANDOM_R or adType == ADType.SEC_MANAGER_TK ):
            self.data = [ 17, adType ] + toArray(args[0], 16);
      #
      # ADType.PERIPHERAL_CONNECT_INT, <min_interval>, <max_interval>
      #
        elif ( adType == ADType.PERIPHERAL_CONNECT_INT ):
            self.data = [ 5, adType ] + toArray(args[0], 2) + toArray(args[1], 2);
      #
      # ADType.SERVICE_DATA_16, <service_uuid>, [<service_data>...]
      #
        elif ( adType == ADType.SERVICE_DATA_16 ):
            self.data = [ 2+len(args), adType ] + toArray(args[0],2);
            if len(args) > 1:
                for arg in args[1:]:
                    self.data += [ arg ];
      #
      # ADType.SERVICE_DATA_32, <service_uuid>, [<service_data>...]
      #
        elif ( adType == ADType.SERVICE_DATA_32 ):
            self.data = [ 4+len(args), adType ] + toArray(args[0], 4);
            if len(args) > 1:
                for arg in args[1:]:
                    self.data += [ arg ];
      #
      # ADType.SERVICE_DATA_128, <service_uuid>, [<service_data>...]
      #
        elif ( adType == ADType.SERVICE_DATA_128 ):
            self.data = [ 16+len(args), adType ] + toArray(args[0], 16);
            if len(args) > 1:
                for arg in args[1:]:
                    self.data += [ arg ];
      #
      # ADType.PUBLIC_ADDRESS, <address_A>, <address_B>, ...
      # ADType.RANDOM_ADDRESS, <address_A>, <address_B>, ...
      #
        elif ( adType == ADType.PUBLIC_ADDRESS or adType == ADType.RANDOM_ADDRESS ):
            self.data = [ 1+6*len(args), adType ];
            for arg in args:
                self.data += toArray(arg, 6);
      #
      # ADType.APPEARANCE,    <apperance>
      # ADType.ADVERTISE_INT, <interval>
      #
        elif ( adType == ADType.APPEARANCE or adType == ADType.ADVERTISE_INT ):
            self.data = [ 3, adType ] + toArray(args[0], 2);
      #
      # ADType.DEVICE_ADDRESS, <address>, <public_or_random>
      #
        elif ( adType == ADType.DEVICE_ADDRESS ):
            self.data = [ 8, adType ] + toArray(args[0], 6) + [ args[1] and 1 ];
      #
      # ADType.LE_SUPPORTED_FEATURES, <features>
      #
        elif ( adType == ADType.LE_SUPPORTED_FEATURES ):
            self.data = [ 4, adType ] + toArray(args[0], 3);
      #
      # ADType.CHANNEL_MAP_UPDATE, <channel_map>, <instant>
      #
        elif ( adType == ADType.CHANNEL_MAP_UPDATE ):
            self.data = [ 8, adType ] + toArray(args[0], 5) + toArray(args[1], 2);
      #
      # ADType.MANUFACTURER_DATA, <manufacturer>, <data>...
      #
        elif ( adType == ADType.MANUFACTURER_DATA ):
            self.data = [ 2+len(args), adType ] + toArray(args[0], 2);
            if len(args) > 1:
                for arg in args[1:]:
                    self.data += [ arg ];
      #
      # ADType.URI, <unicode_uri>
      #
        elif ( adType == ADType.URI ):
            nPos = args[0].find(':');
            if nPos > -1 and args[0][:nPos] in __schemeNames__:
                rest = args[0][(nPos+1):].encode('UTF-8');
                self.data = [ 1+len(__schemeNames__[args[0][:nPos]])+len(rest),
                        adType ] + __schemeNames__[args[0][:nPos]] + [ _ for _ in rest ];
            else:
                rest = args[0].encode('UTF-8');
                self.data = [ 2+len(rest), adType ] + [ 1 ] + [ _ for _ in rest ];

        return self.data;

    def decode(self, data):
        result = { };
        size = len(data);

        n = 0;
        while n < size:    
            length = data[n];
            length -= 1; n += 1
            if length > 0:
                if data[n] in ADType._value2member_map_:
                    adType = ADType(data[n]);
                    n += 1;
                  #
                  # ADType.TX_POWER_LEVEL, <power_level>; where <power_level> [ -127, +127 ] dBm.
                  #
                    if ( adType == ADType.TX_POWER_LEVEL ):
                        result[adType] = data[n] if data[n] < 128 else data[n]-256;
                  #
                  # ADType.FLAGS, <flags>           where <flags> [ 0, 31 ]
                  # ADType.SEC_MANAGER_OBF, <flags> where <flags> [ 0, 15 ]
                  # ADType.DEVICE_ROLE, <role>      where <role>  [ 0, 3 ]
                  #
                    elif ( adType == ADType.FLAGS or adType == ADType.SEC_MANAGER_OBF or adType == ADType.DEVICE_ROLE ):
                        result[adType] = data[n];
                  #
                  # ADType.ILIST_UUIDS_16, <uuid_A>, <uuid_B>, ...
                  # ADTYpe,CLIST_UUIDS_16, <uuid_A>, <uuid_B>, ...
                  # ADType.SS_UUIDS_16,    <uuid_A>, <uuid_B>, ...
                  #
                    elif ( adType == ADType.ILIST_UUIDS_16 or adType == ADType.CLIST_UUIDS_16 or adType == ADType.SS_UUIDS_16 ):
                        result[adType] = [];
                        for i in range(n, n+length, 2):
                            result[adType] += [ toNumber( data[i:i+2] ) ];
                  #
                  # ADType.ILIST_UUIDS_32, <uuid_A>, <uuid_B>, ...
                  # ADTYpe,CLIST_UUIDS_32, <uuid_A>, <uuid_B>, ...
                  # ADType.SS_UUIDS_32,    <uuid_A>, <uuid_B>, ...
                  #
                    elif ( adType == ADType.ILIST_UUIDS_32 or adType == ADType.CLIST_UUIDS_32 or adType == ADType.SS_UUIDS_32 ):
                        result[adType] = [];
                        for i in range(n, n+length, 4):
                            result[adType] += [ toNumber( data[i:i+4] ) ];
                  #
                  # ADType.ILIST_UUIDS_128, <uuid_A>, <uuid_B>, ...
                  # ADTYpe,CLIST_UUIDS_128, <uuid_A>, <uuid_B>, ...
                  # ADType.SS_UUIDS_128,    <uuid_A>, <uuid_B>, ...
                  #
                    elif ( adType == ADType.ILIST_UUIDS_128 or adType == ADType.CLIST_UUIDS_128 or adType == ADType.SS_UUIDS_128 ):
                        result[adType] = [];
                        for i in range(n, n+length, 16):
                            result[adType] += [ toNumber( data[i:i+16] ) ];
                  #
                  # ADType.SHORTENED_LOCAL_NAME, <unicode_name>
                  # ADType.COMPLETE_LOCAL_NAME,  <unicode_name>
                  #
                    elif ( adType == ADType.SHORTENED_LOCAL_NAME or adType == ADType.COMPLETE_LOCAL_NAME ):
                        name = bytes(data[n:n+length])
                        result[adType] = name.decode('utf-8');
                  #
                  # ADType.DEVICE_CLASS, <device_class>
                  #
                    elif ( adType == ADType.DEVICE_CLASS ):
                        result[adType] = toNumber( data[n:n+length] );
                  #
                  # ADType.PAIR_HASH_C,    <hash_value>
                  # ADType.PAIR_RANDOM_R,  <random_value>
                  # ADType.SEC_MANAGER_TK, <tk_value>
                  #
                    elif ( adType == ADType.PAIR_HASH_C or adType == ADType.PAIR_RANDOM_R or adType == ADType.SEC_MANAGER_TK ):
                        result[adType] = toNumber( data[n:n+length] );
                  #
                  # ADType.PERIPHERAL_CONNECT_INT, <min_interval>, <max_interval>
                  #
                    elif ( adType == ADType.PERIPHERAL_CONNECT_INT ):
                        result[adType] = [];
                        for i in range(n, n+length, 2):
                            result[adType] += [ toNumber( data[i:i+2] ) ];
                  #
                  # ADType.SERVICE_DATA_16, <service_uuid>, [<service_data>...]
                  #
                    elif ( adType == ADType.SERVICE_DATA_16 ):
                        result[adType] = { "uuid": toNumber( data[n:n+2] ), "data": data[n+2:n+length] };
                  #
                  # ADType.SERVICE_DATA_32, <service_uuid>, [<service_data>...]
                  #
                    elif ( adType == ADType.SERVICE_DATA_32 ):
                        result[adType] = { "uuid": toNumber( data[n:n+4] ), "data": data[n+4:n+length] };
                  #
                  # ADType.SERVICE_DATA_128, <service_uuid>, [<service_data>...]
                  #
                    elif ( adType == ADType.SERVICE_DATA_128 ):
                        result[adType] = { "uuid": toNumber( data[n:n+16] ), "data": data[n+16:n+length] };
                  #
                  # ADType.PUBLIC_ADDRESS, <address_A>, <address_B>, ...
                  # ADType.RANDOM_ADDRESS, <address_A>, <address_B>, ...
                  #
                    elif ( adType == ADType.PUBLIC_ADDRESS or adType == ADType.RANDOM_ADDRESS ):
                        result[adType] = [];
                        for i in range(n, n+length, 6):
                            result[adType] += [ toNumber( data[i:i+6] ) ];
                  #
                  # ADType.APPEARANCE,    <apperance>
                  # ADType.ADVERTISE_INT, <interval>
                  #
                    elif ( adType == ADType.APPEARANCE or adType == ADType.ADVERTISE_INT ):
                        result[adType] = toNumber( data[n:n+2] );
                  #
                  # ADType.DEVICE_ADDRESS, <address>, <public_or_random>
                  #
                    elif ( adType == ADType.DEVICE_ADDRESS ):
                        result[adType] = { "address": toNumber( data[n:n+6] ), "type": data[n+6] };
                  #
                  # ADType.LE_SUPPORTED_FEATURES, <features>
                  #
                    elif ( adType == ADType.LE_SUPPORTED_FEATURES ):
                        result[adType] = data[n:n+length];
                  #
                  # ADType.CHANNEL_MAP_UPDATE, <channel_map>, <instant>
                  #
                    elif ( adType == ADType.CHANNEL_MAP_UPDATE ):
                        result[adType] = { "map": toNumber( data[n:n+5] ), "instant": toNumber( data[n+5:n+7] ) };
                  #
                  # ADType.MANUFACTURER_DATA, <manufacturer>, <data>...
                  #
                    elif ( adType == ADType.MANUFACTURER_DATA ):
                        result[adType] = { "manufacturer": toNumber( data[n:n+2] ), "data": data[n+2:n+length] };
                  #
                  # ADType.URI, <unicode_uri>
                  #
                    elif ( adType == ADType.URI ):
                        name = [ chr(_) for _ in data[n:n+length] ];
                        name = ''.join(name).decode('utf-8');
                        codePoint = ord(name[0]);
                        name = name[1:];
                        if codePoint > 1:
                            for scheme, code in __schemeNames__.items():
                                if codePoint == code[-1]:
                                    name = scheme + ':' + name;
                                    break;
                        result[adType] = name;
                    else:
                        result[adType] = data[n:n+length];
                    n += length;
                else:
                    adType = data[n];
                    n += 1;
                    result[adType] = data[n:n+length];
                    n += length;

        return result;

    def asBytes(self):
        return [int(_) for _ in self.data];
