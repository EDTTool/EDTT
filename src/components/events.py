# -*- coding: utf-8 -*-
import struct;
from enum import IntEnum;
from components.address import *;

class Events(IntEnum):
    BT_HCI_EVT_DISCONN_COMPLETE             = 5
    BT_HCI_EVT_ENCRYPT_CHANGE               = 8
    BT_HCI_EVT_REMOTE_VERSION_INFO          = 12
    BT_HCI_EVT_CMD_COMPLETE                 = 14
    BT_HCI_EVT_CMD_STATUS                   = 15
    BT_HCI_EVT_HARDWARE_ERROR               = 16
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

class CmdOpcodes(IntEnum):
    BT_HCI_OP_INQUIRY                       = 0x0401
    BT_HCI_OP_DISCONNECT                    = 0x0406
    BT_HCI_OP_READ_REMOTE_VERSION_INFO      = 0x041D
    BT_HCI_OP_SET_EVENT_MASK                = 0x0C01
    BT_HCI_OP_RESET                         = 0x0C03
    BT_HCI_OP_READ_TX_POWER_LEVEL           = 0x0C2D
    BT_HCI_OP_SET_CTL_TO_HOST_FLOW          = 0x0C31
    BT_HCI_OP_HOST_BUFFER_SIZE              = 0x0C33
    BT_HCI_OP_HOST_NUM_COMPLETED_PACKETS    = 0x0C35
    BT_HCI_OP_SET_EVENT_MASK_PAGE_2         = 0x0C63
    BT_HCI_OP_LE_READ_LE_HOST_SUPP          = 0x0C6C
    BT_HCI_OP_LE_WRITE_LE_HOST_SUPP         = 0x0C6D
    BT_HCI_OP_READ_AUTH_PAYLOAD_TIMEOUT     = 0x0C7B
    BT_HCI_OP_WRITE_AUTH_PAYLOAD_TIMEOUT    = 0x0C7C
    BT_HCI_OP_READ_LOCAL_VERSION_INFO       = 0x1001
    BT_HCI_OP_READ_SUPPORTED_COMMANDS       = 0x1002
    BT_HCI_OP_READ_LOCAL_FEATURES           = 0x1003
    BT_HCI_OP_READ_BUFFER_SIZE              = 0x1005
    BT_HCI_OP_READ_BD_ADDR                  = 0x1009
    BT_HCI_OP_READ_RSSI                     = 0x1405
    BT_HCI_OP_LE_SET_EVENT_MASK             = 0x2001
    BT_HCI_OP_LE_READ_BUFFER_SIZE           = 0x2002
    BT_HCI_OP_LE_READ_LOCAL_FEATURES        = 0x2003
    BT_HCI_OP_LE_SET_RANDOM_ADDRESS         = 0x2005
    BT_HCI_OP_LE_SET_ADV_PARAM              = 0x2006
    BT_HCI_OP_LE_READ_ADV_CHAN_TX_POWER     = 0x2007
    BT_HCI_OP_LE_SET_ADV_DATA               = 0x2008
    BT_HCI_OP_LE_SET_SCAN_RSP_DATA          = 0x2009
    BT_HCI_OP_LE_SET_ADV_ENABLE             = 0x200A
    BT_HCI_OP_LE_SET_SCAN_PARAM             = 0x200B
    BT_HCI_OP_LE_SET_SCAN_ENABLE            = 0x200C
    BT_HCI_OP_LE_CREATE_CONN                = 0x200D
    BT_HCI_OP_LE_CREATE_CONN_CANCEL         = 0x200E
    BT_HCI_OP_LE_READ_WL_SIZE               = 0x200F
    BT_HCI_OP_LE_CLEAR_WL                   = 0x2010
    BT_HCI_OP_LE_ADD_DEV_TO_WL              = 0x2011
    BT_HCI_OP_LE_REM_DEV_FROM_WL            = 0x2012
    BT_HCI_OP_LE_CONN_UPDATE                = 0x2013
    BT_HCI_OP_LE_SET_HOST_CHAN_CLASSIF      = 0x2014
    BT_HCI_OP_LE_READ_CHAN_MAP              = 0x2015
    BT_HCI_OP_LE_READ_REMOTE_FEATURES       = 0x2016
    BT_HCI_OP_LE_ENCRYPT                    = 0x2017
    BT_HCI_OP_LE_RAND                       = 0x2018
    BT_HCI_OP_LE_START_ENCRYPTION           = 0x2019
    BT_HCI_OP_LE_LTK_REQ_REPLY              = 0x201A
    BT_HCI_OP_LE_LTK_REQ_NEG_REPLY          = 0x201B
    BT_HCI_OP_LE_READ_SUPP_STATES           = 0x201C
    BT_HCI_OP_LE_RX_TEST                    = 0x201D
    BT_HCI_OP_LE_TX_TEST                    = 0x201E
    BT_HCI_OP_LE_TEST_END                   = 0x201F
    BT_HCI_OP_LE_CONN_PARAM_REQ_REPLY       = 0x2020
    BT_HCI_OP_LE_CONN_PARAM_REQ_NEG_REPLY   = 0x2021
    BT_HCI_OP_LE_SET_DATA_LEN               = 0x2022
    BT_HCI_OP_LE_READ_DEFAULT_DATA_LEN      = 0x2023
    BT_HCI_OP_LE_WRITE_DEFAULT_DATA_LEN     = 0x2024
    BT_HCI_OP_LE_P256_PUBLIC_KEY            = 0x2025
    BT_HCI_OP_LE_GENERATE_DHKEY             = 0x2026
    BT_HCI_OP_LE_ADD_DEV_TO_RL              = 0x2027
    BT_HCI_OP_LE_REM_DEV_FROM_RL            = 0x2028
    BT_HCI_OP_LE_CLEAR_RL                   = 0x2029
    BT_HCI_OP_LE_READ_RL_SIZE               = 0x202A
    BT_HCI_OP_LE_READ_PEER_RPA              = 0x202B
    BT_HCI_OP_LE_READ_LOCAL_RPA             = 0x202C
    BT_HCI_OP_LE_SET_ADDR_RES_ENABLE        = 0x202D
    BT_HCI_OP_LE_SET_RPA_TIMEOUT            = 0x202E
    BT_HCI_OP_LE_READ_MAX_DATA_LEN          = 0x202F
    BT_HCI_OP_LE_READ_PHY                   = 0x2030
    BT_HCI_OP_LE_SET_DEFAULT_PHY            = 0x2031
    BT_HCI_OP_LE_SET_PHY                    = 0x2032
    BT_HCI_OP_LE_ENH_RX_TEST                = 0x2033
    BT_HCI_OP_LE_ENH_TX_TEST                = 0x2034
    BT_HCI_OP_LE_SET_EXT_ADV_PARAM          = 0x2036
    BT_HCI_OP_LE_SET_EXT_ADV_DATA           = 0x2037
    BT_HCI_OP_LE_SET_EXT_SCAN_RSP_DATA      = 0x2038
    BT_HCI_OP_LE_SET_EXT_ADV_ENABLE         = 0x2039
    BT_HCI_OP_LE_READ_MAX_ADV_DATA_LEN      = 0x203A
    BT_HCI_OP_LE_READ_NUM_ADV_SETS          = 0x203B
    BT_HCI_OP_LE_REMOVE_ADV_SET             = 0x203C
    BT_HCI_OP_CLEAR_ADV_SETS                = 0x203D
    BT_HCI_OP_LE_SET_PER_ADV_PARAM          = 0x203E
    BT_HCI_OP_LE_SET_PER_ADV_DATA           = 0x203F
    BT_HCI_OP_LE_SET_PER_ADV_ENABLE         = 0x2040
    BT_HCI_OP_LE_SET_EXT_SCAN_PARAM         = 0x2041
    BT_HCI_OP_LE_SET_EXT_SCAN_ENABLE        = 0x2042
    BT_HCI_OP_LE_EXT_CREATE_CONN            = 0x2043
    BT_HCI_OP_LE_PER_ADV_CREATE_SYNC        = 0x2044
    BT_HCI_OP_LE_PER_ADV_CREATE_SYNC_CANCEL = 0x2045
    BT_HCI_OP_LE_PER_ADV_TERMINATE_SYNC     = 0x2046
    BT_HCI_OP_LE_ADD_DEV_TO_PER_ADV_LIST    = 0x2047
    BT_HCI_OP_LE_REM_DEV_FROM_PER_ADV_LIST  = 0x2048
    BT_HCI_OP_LE_CLEAR_PER_ADV_LIST         = 0x2049
    BT_HCI_OP_LE_READ_PER_ADV_LIST_SIZE     = 0x204A
    BT_HCI_OP_LE_READ_TX_POWER              = 0x204B
    BT_HCI_OP_LE_READ_RF_PATH_COMP          = 0x204C
    BT_HCI_OP_LE_WRITE_RF_PATH_COMP         = 0x204D
    BT_HCI_OP_LE_SET_PRIVACY_MODE           = 0x204E
    BT_HCI_OP_VS_WRITE_BD_ADDR              = 0xFC06

class ErrorCodes(IntEnum):
    BT_HCI_ERR_BAD_EVENT                    = 0x01
    BT_HCI_ERR_SIZE                         = 0x02
    BT_HCI_ERR_BAD_CONN_HANDLE              = 0x03
    BT_HCI_ERR_BAD_ENCRYPT_ENABLED          = 0x04
    BT_HCI_ERR_BAD_TX_POWER_LEVEL           = 0x05
    BT_HCI_ERR_BAD_LE_SUPPORTED_HOST        = 0x06
    BT_HCI_ERR_BAD_LE_SIMULTANEOUS_HOST     = 0x07
    BT_HCI_ERR_BAD_PAYLOAD_TIMEOUT          = 0x08
    BT_HCI_ERR_BAD_RSSI_VALUE               = 0x09
    BT_HCI_ERR_BAD_ADV_TX_POWER_LEVEL       = 0x0A
    BT_HCI_ERR_BAD_LIST_SIZE                = 0x0B
    BT_HCI_ERR_BAD_MAX_DATA_OCTETS          = 0x0C
    BT_HCI_ERR_BAD_MAX_DATA_TRANSMIT_TIME   = 0x0D
    BT_HCI_ERR_BAD_CHANNEL_MAP              = 0x0E
    BT_HCI_ERR_BAD_PHY_CHANNEL              = 0x0F
    BT_HCI_ERR_BAD_SELECTED_TX_POWER        = 0x10
    BT_HCI_ERR_BAD_MAX_DATA_LENGTH          = 0x11
    BT_HCI_ERR_BAD_SUPPORTED_ADV_SETS       = 0x12
    BT_HCI_ERR_BAD_RF_COMPENSATION_VALUE    = 0x13
    BT_HCI_ERR_BAD_COMMAND_STATUS_OPCODE    = 0x14
    BT_HCI_ERR_BAD_LINK_TYPE                = 0x15
    BT_HCI_ERR_BAD_CONNECTION_INTERVAL      = 0x16
    BT_HCI_ERR_BAD_CONNECTION_LATENCY       = 0x17
    BT_HCI_ERR_BAD_SUPERVISION_TIMEOUT      = 0x18
    BT_HCI_ERR_BAD_MASTER_CLOCK_ACCURACY    = 0x19
    BT_HCI_ERR_BAD_CONNECTION_ROLE          = 0x1A
    BT_HCI_ERR_BAD_ADDRESS_TYPE             = 0x1B
    BT_HCI_ERR_BAD_ADV_REPORT_EVENT         = 0x1C
    BT_HCI_ERR_BAD_ADV_DATA_LENGTH          = 0x1D
    BT_HCI_ERR_BAD_PARAMETER_INTERRELATION  = 0x1E
    BT_HCI_ERR_BAD_NO_ADVERTISING_REPORTS   = 0x1F
    BT_HCI_ERR_BAD_ADV_SID                  = 0x20
    BT_HCI_ERR_BAD_PERIODIC_ADV_INTERVAL    = 0x21
    BT_HCI_ERR_BAD_ADV_DATA_STATUS          = 0x22
    BT_HCI_ERR_BAD_ADV_UNUSED_VALUE         = 0x23
    BT_HCI_ERR_BAD_SYNC_HANDLE              = 0x24
    BT_HCI_ERR_BAD_ADVERTISING_HANDLE       = 0x25
    BT_HCI_ERR_BAD_CHANNEL_SEL_ALGORITHM    = 0x26

class Event:

    __metaFormats__ = { MetaEvents.BT_HCI_EVT_LE_CONN_COMPLETE:            'LE Connection Complete Event for handle {1:d} status 0x{0:02X} role {2:d} from {3:s} interval {4:d} latency {5:d} timeout {6:d} accuracy {7:d}',
                       MetaEvents.BT_HCI_EVT_LE_ADVERTISING_REPORT:        'LE Advertising Report Event event {0:d} from {1!s} with rssi {3:d} dBm.',
                       MetaEvents.BT_HCI_EVT_LE_CONN_UPDATE_COMPLETE:      'LE Connection Update Complete Event for handle {1:d} status 0x{0:02X} interval {2:d} latency {3:d} timeout {4:d}',
                       MetaEvents.BT_HCI_EVT_LE_REMOTE_FEAT_COMPLETE:      'LE Read Remote Features Complete Event for handle {1:d} status 0x{0:02X} features 0x{2:016X}',
                       MetaEvents.BT_HCI_EVT_LE_LTK_REQUEST:               'LE Long Term Key Request Event for handle {0:d} number 0x{1:016X} diversifier 0x{2:04X}',
                       MetaEvents.BT_HCI_EVT_LE_CONN_PARAM_REQ:            'LE Remote Connection Parameter Request Event for handle {0:d} interval [{1:d}, {2:d}] latency {3:d} timeout {4:d}',
                       MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE:           'LE Data Length Change Event for handle {0:d} Tx ({1:d}, {2:d}) Rx ({3:d}, {4:d})',
                       MetaEvents.BT_HCI_EVT_LE_P256_PUBLIC_KEY_COMPLETE:  'LE Read Local P-256 Public Key Complete Event status 0x{0:02X} key 0x{1:0128X}',
                       MetaEvents.BT_HCI_EVT_LE_GENERATE_DHKEY_COMPLETE:   'LE Generate DHKey Complete Event status 0x{0:02X} key 0x{1:064X}',
                       MetaEvents.BT_HCI_EVT_LE_ENH_CONN_COMPLETE:         'LE Enhanced Connection Complete Event for handle {1:d} status 0x{0:02X} role {2:d} address {3!s} localRPA {4!s} peerRPA {5!s} interval {6:d} latency {7:d} timeout {8:d} accuracy {9:d}',
                       MetaEvents.BT_HCI_EVT_LE_DIRECT_ADV_REPORT:         'LE Directed Advertising Report Event event {0:d} address {1!s}, direct adddress {2!s} rssi {3:d}',
                       MetaEvents.BT_HCI_EVT_LE_PHY_UPDATE_COMPLETE:       'LE PHY Update Complete Event for handle {1:d} status 0x{0:02X} Tx PHY {2:d} Rx PHY {3:d}',
                       MetaEvents.BT_HCI_EVT_LE_EXT_ADVERTISING_REPORT:    'LE Extended Advertising Report Event type {0:d} address {1!s} PHYs ({2:d}, {3:d}) SID {4:d} Tx power {5:+d} dBm. rssi {6:d} dBm. interval {7:d}',
                       MetaEvents.BT_HCI_EVT_LE_PER_ADV_SYNC_ESTABLISHED:  'LE Periodic Advertising Sync Established Event for handle {1:d} status 0x{0:02X} address {3!s} SID {2:d} PHY {4:d} interval {5:d} accuracy {6:d}',
                       MetaEvents.BT_HCI_EVT_LE_PER_ADVERTISING_REPORT:    'LE Periodic Advertising Report Event for handle {0:d} TX power {1:+d} dBm. rssi {2:+d} dBm. data status 0x{3:02X}',
                       MetaEvents.BT_HCI_EVT_LE_PER_ADV_SYNC_LOST:         'LE Periodic Advertising Sync Lost Event for handle {0:d}',
                       MetaEvents.BT_HCI_EVT_LE_SCAN_TIMEOUT:              'LE Scan Timeout Event',
                       MetaEvents.BT_HCI_EVT_LE_ADV_SET_TERMINATED:        'LE Advertising Set Terminated Event for Advertise handle {1:d} Connection handle {2:d} status 0x{0:02X} events {3:d}',
                       MetaEvents.BT_HCI_EVT_LE_SCAN_REQ_RECEIVED:         'LE Scan Request Received Event for handle {0:d} address {1!s}',
                       MetaEvents.BT_HCI_EVT_LE_CHAN_SEL_ALGO:             'LE Channel Selection Algorithm Event for handle {0:d} algorithm {1:d}' };

    __eventFormats__ = { Events.BT_HCI_EVT_DISCONN_COMPLETE:               'Disconnect Complete Event for handle {1:d} status 0x{0:02X} reason 0x{2:02X}',
                       Events.BT_HCI_EVT_ENCRYPT_CHANGE:                   'Encryption Change Event for handle {1:d} status 0x{0:02X} encryption enabled {2:d}',
                       Events.BT_HCI_EVT_REMOTE_VERSION_INFO:              'Read Remote Version Information Event for handle {1:d} status 0x{0:02X} manufacturer 0x{3:04X} version 0x{2:02X} subversion 0x{4:04X}',
                       Events.BT_HCI_EVT_CMD_COMPLETE:                     'Command Complete Event for opCode 0x{1:04X} status 0x{2:02X} packets 0x{0:02X}',
                       Events.BT_HCI_EVT_CMD_STATUS:                       'Command Status Event for opCode 0x{1:04X} status 0x{2:02X} packets 0x{0:02X}',
                       Events.BT_HCI_EVT_HARDWARE_ERROR:                   'Hardware Error Event error {0:d}',
                       Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS:            'Number of Completed Packets Event handles {0:d}',
                       Events.BT_HCI_EVT_DATA_BUF_OVERFLOW:                'Data Buffer Overflow Event link type {0:d}',
                       Events.BT_HCI_EVT_ENCRYPT_KEY_REFRESH_COMPLETE:     'Encryption Key Refresh Complete Event for handle {1:d} status 0x{0:02X}',
                       Events.BT_HCI_EVT_LE_META_EVENT:                    '',
                       Events.BT_HCI_EVT_AUTH_PAYLOAD_TIMEOUT_EXP:         'Authenticated Payload Timeout Expired Event for handle {0:d}' };

    __cceFormats__ = { CmdOpcodes.BT_HCI_OP_SET_EVENT_MASK:                'Command Complete Event for Set Event Mask status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_RESET:                         'Command Complete Event for Reset status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_READ_TX_POWER_LEVEL:           'Command Complete Event for Read Transmit Power Level status 0x{2:02X} handle {3:d} power level {4:+d} dBm.',
                       CmdOpcodes.BT_HCI_OP_SET_CTL_TO_HOST_FLOW:          'Command Complete Event for Set Controller To Host Flow Control status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_HOST_BUFFER_SIZE:              'Command Complete Event for Host Buffer Size status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_HOST_NUM_COMPLETED_PACKETS:    'Command Complete Event for Host Number Of Completed Packets',
                       CmdOpcodes.BT_HCI_OP_SET_EVENT_MASK_PAGE_2:         'Command Complete Event for Set Event Mask Page 2 status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_LE_HOST_SUPP:          'Command Complete Event for Read LE Host Support status 0x{2:02X} LE supported host {3:d} simultaneous LE host {4:d}',
                       CmdOpcodes.BT_HCI_OP_LE_WRITE_LE_HOST_SUPP:         'Command Complete Event for Write LE Host Support status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_RF_PATH_COMP: 		   'Command Complete Event for LE Read RF Path Compensation status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_READ_AUTH_PAYLOAD_TIMEOUT:     'Command Complete Event for Read Authenticated Payload Timeout status 0x{2:02X} handle {3:d} timeout {4:d} x 10 ms.',
                       CmdOpcodes.BT_HCI_OP_WRITE_AUTH_PAYLOAD_TIMEOUT:    'Command Complete Event for Write Authenticated Payload Timeout status 0x{2:02X} handle {3:d}',
                       CmdOpcodes.BT_HCI_OP_READ_LOCAL_VERSION_INFO:       'Command Complete Event for Read Local Version Information status 0x{2:02X} HCI version {3:d} HCI revision 0x{4:04X} LMP version {5:d} LMP subversion 0x{6:04X} manufacturer 0x{7:04X} ',
                       CmdOpcodes.BT_HCI_OP_READ_SUPPORTED_COMMANDS:       'Command Complete Event for Read Local Supported Commands status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_READ_LOCAL_FEATURES:           'Command Complete Event for Read Local Supported Features status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_READ_BUFFER_SIZE:              'Command Complete Event for Read Buffer Size status 0x{2:02X} ACL packet length {3:d} SYN packet length {4:d} ACL packets {5:d} SYN packets {6:d}',
                       CmdOpcodes.BT_HCI_OP_READ_BD_ADDR:                  'Command Complete Event for Read BD_ADDR status 0x{2:02X} address {3!s}',
                       CmdOpcodes.BT_HCI_OP_READ_RSSI:                     'Command Complete Event for Read RSSI status 0x{2:02X} handle {3:d} rssi {4:+d} dBm.',
                       CmdOpcodes.BT_HCI_OP_LE_SET_EVENT_MASK:             'Command Complete Event for LE Set Event Mask status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_BUFFER_SIZE:           'Command Complete Event for LE Read Buffer Size status 0x{2:02X} LE data packet length {3:d} LE data packets {4:d}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_LOCAL_FEATURES:        'Command Complete Event for LE Read Local Supported Features status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_RANDOM_ADDRESS:         'Command Complete Event for LE Set Random Address status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_ADV_PARAM:              'Command Complete Event for LE Set Advertising Parameters status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_ADV_CHAN_TX_POWER:     'Command Complete Event for LE Read Advertising Channel TX Power status 0x{2:02X} power level {3:+d} dBm.',
                       CmdOpcodes.BT_HCI_OP_LE_SET_ADV_DATA:               'Command Complete Event for LE Set Advertising Data status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_SCAN_RSP_DATA:          'Command Complete Event for LE Set Scan Response Data status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_ADV_ENABLE:             'Command Complete Event for LE Set Advertising Enable status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_SCAN_PARAM:             'Command Complete Event for LE Set Scan Parameters status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_SCAN_ENABLE:            'Command Complete Event for LE Set Scan Enable status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_CREATE_CONN_CANCEL:         'Command Complete Event for LE Create Connection Cancel status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_WL_SIZE:               'Command Complete Event for LE Read White List Size status 0x{2:02X} list size {3:d}',
                       CmdOpcodes.BT_HCI_OP_LE_CLEAR_WL:                   'Command Complete Event for LE Clear White List status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_ADD_DEV_TO_WL:              'Command Complete Event for LE Add Device To White List status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_REM_DEV_FROM_WL:            'Command Complete Event for LE Remove Device From White List status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_HOST_CHAN_CLASSIF:      'Command Complete Event for LE Set Host Channel Classification status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_CHAN_MAP:              'Command Complete Event for LE Read Channel Map status 0x{2:02X} handle {3:d} channel map 0x{4:010X}',
                       CmdOpcodes.BT_HCI_OP_LE_ENCRYPT:                    'Command Complete Event for LE Encrypt status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_RAND:                       'Command Complete Event for LE Rand status 0x{2:02X} number 0x{3:016X}',
                       CmdOpcodes.BT_HCI_OP_LE_LTK_REQ_REPLY:              'Command Complete Event for LE Long Term Key Request Reply status 0x{2:02X} handle {3:d}',
                       CmdOpcodes.BT_HCI_OP_LE_LTK_REQ_NEG_REPLY:          'Command Complete Event for LE Long Term Key Request Negative Reply status 0x{2:02X} handle {3:d}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_SUPP_STATES:           'Command Complete Event for LE Read Supported States status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_RX_TEST:                    'Command Complete Event for LE Receiver Test status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_TX_TEST:                    'Command Complete Event for LE Transmitter Test status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_TEST_END:                   'Command Complete Event for LE Test End status 0x{2:02X} packets {3:d}',
                       CmdOpcodes.BT_HCI_OP_LE_CONN_PARAM_REQ_REPLY:       'Command Complete Event for LE Remote Connection Parameter Request Reply status 0x{2:02X} handle {3:d}',
                       CmdOpcodes.BT_HCI_OP_LE_CONN_PARAM_REQ_NEG_REPLY:   'Command Complete Event for LE Remote Connection Parameter Request Negative Reply status 0x{2:02X} handle {3:d}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_DATA_LEN:               'Command Complete Event for LE Set Data Length status 0x{2:02X} handle {3:d}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_DEFAULT_DATA_LEN:      'Command Complete Event for LE Read Suggested Default Data Length status 0x{2:02X} max TX octets {3:d} max TX time {4:d}',
                       CmdOpcodes.BT_HCI_OP_LE_WRITE_DEFAULT_DATA_LEN:     'Command Complete Event for LE Write Suggested Default Data Length status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_ADD_DEV_TO_RL:              'Command Complete Event for LE Add Device To Resolving List status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_REM_DEV_FROM_RL:            'Command Complete Event for LE Remove Device From Resolving List status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_CLEAR_RL:                   'Command Complete Event for LE Clear Resolving List status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_RL_SIZE:               'Command Complete Event for LE Read Resolving List Size status 0x{2:02X} list size {3:d}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_PEER_RPA:              'Command Complete Event for LE Read Peer Resolvable Address status 0x{2:02X} address {3!s}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_LOCAL_RPA:             'Command Complete Event for LE Read Local Resolvable Address status 0x{2:02X} address {3!s}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_ADDR_RES_ENABLE:        'Command Complete Event for LE Set Address Resolution Enable status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_RPA_TIMEOUT:            'Command Complete Event for LE Set Resolvable Private Address Timeout status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_MAX_DATA_LEN:          'Command Complete Event for LE Read Maximum Data Length status 0x{2:02X} max TX octets {3:d} max TX time {4:d} max RX octets {5:d} max RX time {6:d}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_PHY:                   'Command Complete Event for LE Read PHY status 0x{2:02X} handle {3:d} TX phy {4:d} RX phy {5:d}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_DEFAULT_PHY:            'Command Complete Event for LE Set Default PHY status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_ENH_RX_TEST:                'Command Complete Event for LE Enhanced Receiver Test status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_ENH_TX_TEST:                'Command Complete Event for LE Enhanced Transmitter Test status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_EXT_ADV_PARAM:          'Command Complete Event for LE Set Extended Advertising Parameters status 0x{2:02X} power level {3:+d} dBm.',
                       CmdOpcodes.BT_HCI_OP_LE_SET_EXT_ADV_DATA:           'Command Complete Event for LE Set Extended Advertising Data status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_EXT_SCAN_RSP_DATA:      'Command Complete Event for LE Set Extended Scan Response Data status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_EXT_ADV_ENABLE:         'Command Complete Event for LE Set Extended Advertising Enable status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_MAX_ADV_DATA_LEN:      'Command Complete Event for LE Read Maximum Advertising Data Length status 0x{2:02X} max. data length {3:d}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_NUM_ADV_SETS:          'Command Complete Event for LE Read Number of Supported Advertising Sets status 0x{2:02X} supported sets {3:d}',
                       CmdOpcodes.BT_HCI_OP_LE_REMOVE_ADV_SET:             'Command Complete Event for LE Remove Advertising Set status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_CLEAR_ADV_SETS:                'Command Complete Event for LE Clear Advertising Sets status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_PER_ADV_PARAM:          'Command Complete Event for LE Set Periodic Advertising Parameters status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_PER_ADV_DATA:           'Command Complete Event for LE Set Periodic Advertising Data status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_PER_ADV_ENABLE:         'Command Complete Event for LE Set Periodic Advertising Enable status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_EXT_SCAN_PARAM:         'Command Complete Event for LE Set Extended Scan Parameters status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_EXT_SCAN_ENABLE:        'Command Complete Event for LE Set Extended Scan Enable status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_PER_ADV_CREATE_SYNC_CANCEL: 'Command Complete Event for LE Periodic Advertising Create Sync Cancel status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_PER_ADV_TERMINATE_SYNC:     'Command Complete Event for LE Periodic Advertising Terminate Sync status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_ADD_DEV_TO_PER_ADV_LIST:    'Command Complete Event for LE Add Device To Periodic Advertiser List status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_REM_DEV_FROM_PER_ADV_LIST:  'Command Complete Event for LE Remove Device From Periodic Advertiser List status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_CLEAR_PER_ADV_LIST:         'Command Complete Event for LE Clear Periodic Advertiser List status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_PER_ADV_LIST_SIZE:     'Command Complete Event for LE Read Periodic Advertiser List Size status 0x{2:02X} list size {3:d}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_TX_POWER:              'Command Complete Event for LE Read Transmit Power status 0x{2:02X} TX power range [{3:+d}, {4:+d}] dBm.',
                       CmdOpcodes.BT_HCI_OP_LE_READ_RF_PATH_COMP:          'Command Complete Event for LE Read RF Path Compensation status 0x{2:02X} TX path compensation {3:+d} x 0.1 dB. RX path compensation {4:+d} x 0.1 dB.',
                       CmdOpcodes.BT_HCI_OP_LE_WRITE_RF_PATH_COMP:         'Command Complete Event for LE Write RF Path Compensation status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_PRIVACY_MODE:           'Command Complete Event for LE Set Privacy Mode status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_VS_WRITE_BD_ADDR:              'Command Complete Event for Write BD_ADDR status 0x{2:02X}' };

    __cseFormats__ = { CmdOpcodes.BT_HCI_OP_INQUIRY:                       'Command Status Event for Inquire status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_DISCONNECT:                    'Command Status Event for Disconnect status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_READ_REMOTE_VERSION_INFO:      'Command Status Event for Read Remote Version Information status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_CREATE_CONN:                'Command Status Event for LE Create Connection status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_CONN_UPDATE:                'Command Status Event for LE Connection Update status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_READ_REMOTE_FEATURES:       'Command Status Event for LE Read Remote Features status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_START_ENCRYPTION:           'Command Status Event for LE Start Encryption status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_P256_PUBLIC_KEY:            'Command Status Event for LE Read Local P-256 Public Key Command status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_GENERATE_DHKEY:             'Command Status Event for LE Generate DHKey Command status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_SET_PHY:                    'Command Status Event for LE Set PHY status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_EXT_CREATE_CONN:            'Command Status Event for LE Extended Create Connection status 0x{2:02X}',
                       CmdOpcodes.BT_HCI_OP_LE_PER_ADV_CREATE_SYNC:        'Command Status Event for LE Periodic Advertising Create Sync status 0x{2:02X}' };


    def __init__(self, event, data, time=None):
        self.event = event;
        self.data  = data[:];
        self.values = None;
        self.errors = set([]);
        self.time = time;
        self.size = len(self.data);
        self.subEvent = struct.unpack('B', self.data[:1])[0] if self.size > 0 and self.event == Events.BT_HCI_EVT_LE_META_EVENT else 0;

    def __asNumber(self, data):
        value = 0;
        for part in reversed(data):
            value <<= 8;
            value += part;
        return value;

    def __checkSize(self, size):
        if self.size != size:
            if self.size == 4:
                  # Unknown command response
                  return False
            self.errors.add(ErrorCodes.BT_HCI_ERR_SIZE);
        return self.size >= size;

    def __checkMinSize(self, size):
        if not self.size >= size:
            self.errors.add(ErrorCodes.BT_HCI_ERR_SIZE);
        return self.size >= size;

    def __checkConnectionHandle(self, handle):
        if not (0 <= handle <= 0xEFF):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_CONN_HANDLE);

    def __checkEncryptionEnabled(self, enabled):
        if not (0 <= enabled <= 2):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_ENCRYPT_ENABLED);

    def __checkTXPowerLevel(self, level):
        if not (-30 <= level <= 20):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_TX_POWER_LEVEL);

    def __checkLESupportedHost(self, value):
        if not (0 <= value <= 1):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_LE_SUPPORTED_HOST);

    def __checkLESimultaneousHost(self, value):
        if not (0 == value):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_LE_SIMULTANEOUS_HOST);

    def __checkPayloadTimeout(self, timeout):
        if not (0 < timeout):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_PAYLOAD_TIMEOUT);

    def __checkRSSI(self, rssi):
        if not ((-127 <= rssi <= 20) or (rssi == 127)):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_RSSI_VALUE);

    def __checkAdvTXPowerLevel(self, level):
        if not (-20 <= level <= 10):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_ADV_TX_POWER_LEVEL);

    def __checkListSize(self, size):
        if not (1 <= size):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_LIST_SIZE);

    def __checkMaxDataOctets(self, octets):
        if not (0x001B <= octets <= 0x00FB):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_MAX_DATA_OCTETS);

    def __checkMaxDataTransmitTime(self, time):
        if not (0x0148 <= time <= 0x4290):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_MAX_DATA_TRANSMIT_TIME);

    def __checkChannelMap(self, map):
        if not (map <= 0x1FFFFFFFFF):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_CHANNEL_MAP);

    def __checkPhy(self, phy, legal=[1,2,3]):
        if not (phy in legal):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_PHY_CHANNEL);

    def __checkSelectedTXPower(self, power, minPower=-127, maxPower=126):
        if not (minPower <= power <= maxPower):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_SELECTED_TX_POWER);

    def __checkMaxAdvDataLength(self, length):
        if not (0x001F <= length <= 0x0672):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_MAX_DATA_LENGTH);

    def __checkSupportedAdvSets(self, sets):
        if not (1 <= sets <= 240):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_SUPPORTED_ADV_SETS);

    def __checkRFPathCompensation(self, value):
        if not (-1280 <= value <= 1280):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_RF_COMPENSATION_VALUE);

    def __checkLinkType(self, linkType):
        if not (0 <= linkType <= 1):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_LINK_TYPE);

    def __checkConnectionInterval(self, interval):
        if not (0x0006 <= interval <= 0x0C80):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_CONNECTION_INTERVAL);

    def __checkConnectionLatency(self, latency):
        if not (0x0000 <= latency <= 0x01F3):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_CONNECTION_LATENCY);

    def __checkSupervisionTimeout(self, timeout):
        if not (0x000A <= timeout <= 0x0C80):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_SUPERVISION_TIMEOUT);

    def __checkMasterClockAccuracy(self, accuracy):
        if not (0 <= accuracy <= 7):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_MASTER_CLOCK_ACCURACY);

    def __checkConnectionRole(self, role):
        if not (0 <= role <= 1):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_CONNECTION_ROLE);

    def __checkAddressType(self, type, legalTypes=[0,1,2,3]):
        if not (type in legalTypes):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_ADDRESS_TYPE);

    def __checkAdvEvent(self, event, minEvent=0, maxEvent=4):
        if not (minEvent <= event <= maxEvent):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_ADV_REPORT_EVENT);

    def __checkAdvDataLength(self, length, maxLength=31):
        if not (0 <= length <= maxLength):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_ADV_DATA_LENGTH);

    def __checkSid(self, sid, legal):
        if not (sid in legal):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_ADV_SID);

    def __checkSyncHandle(self, handle):
        if not (0 <= handle <= 0xEFF):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_SYNC_HANDLE);

    def __checkPeriodicAdvInterval(self, interval):
        if not (6 <= interval):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_PERIODIC_ADV_INTERVAL);

    def __checkAdvDataStatus(self, status):
        if not (0 <= status <= 2):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_ADV_DATA_STATUS);

    def __checkAdvertisingHandle(self, handle):
        if not (0 <= handle <= 0xEF):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_ADVERTISING_HANDLE);

    def __checkChannelAlgorithm(self, algorithm):
        if not (0 <= algorithm <= 1):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_CHANNEL_SEL_ALGORITHM);

    def __checkAdvertisingReports(self, reports, minReports=1, maxReports=25):
        if not (minReports <= reports <= maxReports):
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_NO_ADVERTISING_REPORTS);


    def __disconnectComplete(self):
        if self.__checkSize(4):
            status, handle, reason = struct.unpack('<BHB', self.data[:4]);
            self.__checkConnectionHandle(handle);
        else:
            status = handle = reason = 0;
        return status, handle, reason;

    def __encryptionChange(self):
        if self.__checkSize(4):
            status, handle, enabled = struct.unpack('<BHB', self.data[:4]);
            self.__checkConnectionHandle(handle);
            self.__checkEncryptionEnabled(enabled);
        else:
            status = handle = enabled = 0;
        return status, handle, enabled;

    def __RemoteVersionComplete(self):
        if self.__checkSize(8):
            status, handle, version, manufacturer, subVersion = struct.unpack('<BHBHH', self.data[:8]);
            self.__checkConnectionHandle(handle);
        else:
            status = handle = version = manufacturer = subVersion = 0;
        return status, handle, version, manufacturer, subVersion;

    """ ================================================================================

          The following private methods are all sub-sets of the Command Complete Event

        ================================================================================ """

    def __readTXPowerLevel(self):
        if self.__checkSize(7):
            handle, level = struct.unpack('<Hb', self.data[4:7]);
            self.__checkConnectionHandle(handle);
            self.__checkTXPowerLevel(level);
        else:
            handle = level = 0;
        return handle, level

    def __readLEHostSupport(self):
        if self.__checkSize(6):
            supported, simultaneous = struct.unpack('<BB', self.data[4:6]);
            self.__checkLESupportedHost(supported);
            self.__checkLESimultaneousHost(simultaneous);
        else:
            supported = simultaneous = 0;
        return supported, simultaneous;

    def __readAuthPayloadTimeout(self):
        if self.__checkSize(8):
            handle, timeout = struct.unpack('<HH', self.data[4:8]);
            self.__checkConnectionHandle(handle);
            self.__checkPayloadTimeout(timeout);
            self.__checkConnectionHandle(handle);
            self.__checkPayloadTimeout(timeout);
        else:
            handle = timeout = 0;
        return handle, timeout;

    def __writeAuthPayloadTimeout(self):
        if self.__checkSize(6):
            handle = struct.unpack('<H', self.data[4:6])[0];
            self.__checkConnectionHandle(handle);
        else:
            handle = 0;
        return (handle,);

    def __readLocalVersionInformation(self):
        if self.__checkSize(12):
            hciVersion, hciRevision, lmpVersion, manufacturer, lmpSubversion = struct.unpack('<BHBHH', self.data[4:12]);
        else:
            hciVersion = hciRevision = lmpVersion = lmpSubversion = manufacturer = 0;
        return hciVersion, hciRevision, lmpVersion, lmpSubversion, manufacturer;

    def __readLocalSupportedCommands(self):
        if self.__checkSize(68):
            commands = struct.unpack('<64B', self.data[4:68]);
        else:
            commands = [0 for _ in range(64)];
        return (commands,);

    def __readLocalSupportedFeatures(self):
        if self.__checkSize(12):
            features = struct.unpack('<8B', self.data[4:12]);
        else:
            features = [0 for _ in range(8)];
        return (features,);

    def __readBufferSize(self):
        if self.__checkSize(11):
            aclLength, synLength, aclPackets, synPackets = struct.unpack('<HBHH', self.data[4:11]);
        else:
            aclLength = synLength = aclPackets = synPackets = 0
        return aclLength, synLength, aclPackets, synPackets;

    def __readBDAddress(self):
        if self.__checkSize(10):
            address = struct.unpack('<6B', self.data[4:10]);
        else:
            address = None;
        return (Address(None, address),);

    def __readRssi(self):
        if self.__checkSize(7):
            handle, rssi = struct.unpack('<Hb', self.data[4:7]);
            self.__checkConnectionHandle(handle);
            self.__checkRSSI(rssi);
        else:
            handle = rssi = 0;
        return handle, rssi;

    def __leReadBufferSize(self):
        if self.__checkSize(7):
            dpLength, dpCount = struct.unpack('<HB', self.data[4:7]);
        else:
            dpLength = dpCount = 0;
        return dpLength, dpCount;

    def __leReadLocalSupportedFeatures(self):
        if self.__checkSize(12):
            features = struct.unpack('<8B', self.data[4:12]);
        else:
            features = [0 for _ in range(8)];
        return (features,);

    def __leReadAdvChannelTXPower(self):
        if self.__checkSize(5):
            power = struct.unpack('<b', self.data[4:5])[0];
            self.__checkAdvTXPowerLevel(power);
        else:
            power = 0;
        return (power,);

    def __leReadListSize(self):
        if self.__checkSize(5):
            size = struct.unpack('<B', self.data[4:5])[0];
            self.__checkListSize(size);
        else:
            size = 0;
        return (size,);

    def __leReadChannelMap(self):
        if self.__checkSize(11):
            handle = struct.unpack('<H', self.data[4:6])[0];
            chnMap = struct.unpack('<5B', self.data[6:11]);
            chnMapNo = self.__asNumber(chnMap);
            self.__checkConnectionHandle(handle);
            self.__checkChannelMap(chnMapNo);
        else:
            handle = chnMapNo = 0;
        return handle, chnMapNo;

    def __leEncrypt(self):
        if self.__checkSize(20):
            encData = struct.unpack('<16B', self.data[4:20]);
        else:
            encData = [0 for _ in range(16)];
        return (encData,);

    def __leRand(self):
        if self.__checkSize(12):
            number = struct.unpack('<8B', self.data[4:12]);
        else:
            number = [0 for _ in range(8)];
        return (self.__asNumber(number),);

    def __leLTKRequestReply(self):
        if self.__checkSize(6):
            handle = struct.unpack('<H', self.data[4:6])[0];
            self.__checkConnectionHandle(handle);
        else:
            handle = 0;
        return (handle,);

    def __leReadSupportedStates(self):
        if self.__checkSize(12):
            states = struct.unpack('<8B', self.data[4:12]);
        else:
            states = [0 for _ in range(8)];
        return (self.__asNumber(states),);

    def __leTestEnd(self):
        if self.__checkSize(6):
            packets = struct.unpack('<H', self.data[4:6])[0];
        else:
            packets = 0;
        return (packets,);

    def __leRemoteConnectionParameterRequest(self):
        if self.__checkSize(6):
            handle = struct.unpack('<H', self.data[4:6])[0];
            self.__checkConnectionHandle(handle);
        else:
            handle = 0;
        return (handle,);

    def __leSetDataLength(self):
        if self.__checkSize(6):
            handle = struct.unpack('<H', self.data[4:6])[0];
            self.__checkConnectionHandle(handle);
        else:
            handle = 0;
        return (handle,);

    def __leReadDefaultDataLength(self):
        if self.__checkSize(8):
            maxOctets, maxTime = struct.unpack('<HH', self.data[4:8]);
            self.__checkMaxDataOctets(maxOctets);
            self.__checkMaxDataTransmitTime(maxTime);
        else:
            maxOctets = maxTime = 0;
        return maxOctets, maxTime;

    def __leReadResolvingListSize(self):
        if self.__checkSize(5):
            size = struct.unpack('<B', self.data[4:5])[0];
        else:
            size = 0;
        return (size,);

    def __leReadResolvableAddress(self):
        if self.__checkSize(10):
            address = struct.unpack('<6B', self.data[4:10]);
        else:
            address = None;
        return (Address(None, address),);

    def __leReadMaximumDataLength(self):
        if self.__checkSize(12):
            maxTXOctets, maxTXTime, maxRXOctets, maxRXTime = struct.unpack('<HHHH', self.data[4:12]);
            self.__checkMaxDataOctets(maxTXOctets);
            self.__checkMaxDataTransmitTime(maxTXTime);
            self.__checkMaxDataOctets(maxRXOctets);
            self.__checkMaxDataTransmitTime(maxRXTime);
        else:
            maxTXOctets = maxTXTime = maxRXOctets = maxRXTime = 0;
        return maxTXOctets, maxTXTime, maxRXOctets, maxRXTime;

    def __leReadPHY(self):
        if self.__checkSize(8):
            handle, txPHY, rxPHY = struct.unpack('<HBB', self.data[4:8]);
            self.__checkConnectionHandle(handle);
            self.__checkPhy(txPHY);
            self.__checkPhy(rxPHY);
        else:
            handle = txPHY = rxPHY = 0;
        return handle, txPHY, rxPHY;

    def __leSetExtAdvParameters(self):
        if self.__checkSize(5):
            power = struct.unpack('<b', self.data[4:5])[0];
            self.__checkSelectedTXPower(power);
        else:
            power = 0;
        return (power,);

    def __leReadMaxAdvDataLength(self):
        if self.__checkSize(6):
            maxLength = struct.unpack('<H', self.data[4:6])[0];
            self.__checkMaxAdvDataLength(maxLength);
        else:
            maxLength = 0;
        return (maxLength,);

    def __leReadNoOfSupportedAdvSets(self):
        if self.__checkSize(5):
            maxSets = struct.unpack('<B', self.data[4:5])[0];
            self.__checkSupportedAdvSets(maxSets);
        else:
            maxSets = 0;
        return (maxSets,);

    def __leReadTransmitPower(self):
        if self.__checkSize(6):
            minPower, maxPower = struct.unpack('<bb', self.data[4:6]);
            self.__checkSelectedTXPower(minPower);
            self.__checkSelectedTXPower(maxPower);
        else:
            minPower = maxPower = 0;
        return minPower, maxPower;

    def __leReadRFPathCompensation(self):
        if self.__checkSize(8):
            txPCValue, rxPCValue = struct.unpack('<hh', self.data[4:8]);
            self.__checkRFPathCompensation(txPCValue);
            self.__checkRFPathCompensation(rxPCValue);
        else:
            txPCValue = rxPCValue = 0;
        return txPCValue, rxPCValue;

    """ ================================================================================

           The above private methods were all sub-sets of the Command Complete Event

        ================================================================================ """

    def __commandComplete(self):
        if self.size >= 4:
            numPackets, opCode, status = struct.unpack('<BHB', self.data[:4]);
            if opCode in self.__cceFuncs__:
                return (numPackets, opCode, status) + self.__cceFuncs__[opCode](self);
        else:
            numPackets = opCode = status = 0;
        self.__checkSize(4);
        return numPackets, opCode, status;

    def __commandStatus(self):
        if self.__checkSize(4):
            status, numPackets, opCode = struct.unpack('<BBH', self.data[:4]);
            if not (opCode in CmdOpcodes._value2member_map_):
                self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_COMMAND_STATUS_OPCODE);
        else:
            numPackets = opCode = status = 0;
        return numPackets, opCode, status;

    def __hardwareError(self):
        if self.__checkSize(1):
            error = struct.unpack('<B', self.data[:1])[0];
        else:
            error = 0;
        return (error,);

    def __completedPackets(self):
        numHandles = struct.unpack('<B', self.data[:1])[0] if self.size > 0 else 0;
        if self.__checkSize(1 + 4*numHandles):
            if numHandles > 0:
                handles = struct.unpack('<' + str(numHandles) + 'H', self.data[1:1+2*numHandles]);
                packets = struct.unpack('<' + str(numHandles) + 'H', self.data[1+2*numHandles:]);
            else:
                handles = [];
                packets = [];
            for handle in handles:
                self.__checkConnectionHandle(handle);
        else:
            handles = [];
            packets = [];
        return numHandles, handles, packets;

    def __dataBufferOverflow(self):
        if self.__checkSize(1):
            linkType = struct.unpack('<B', self.data[:1])[0];
            self.__checkLinkType(linkType);
        else:
            linkType = 0;
        return (linkType,);

    def __encryptionKeyRefreshComplete(self):
        if self.__checkSize(3):
            status, handle = struct.unpack('<BH', self.data[:3]);
            self.__checkConnectionHandle(handle);
        else:
            status = handle = 0;
        return status, handle;

    def __authenticatedPayloadTimeout(self):
        if self.__checkSize(2):
            handle = struct.unpack('<H', self.data[:2])[0];
            self.__checkConnectionHandle(handle);
        else:
            handle = 0;
        return (handle,);

    def __connectionComplete(self):
        if self.__checkSize(19):
            status, handle, role, addressType = struct.unpack('<BHBB', self.data[1:6]);
            address = struct.unpack('<6B', self.data[6:12]);
            interval, latency, timeout, accuracy = struct.unpack('<HHHB', self.data[12:19]);
            self.__checkConnectionHandle(handle);
            self.__checkConnectionRole(role);
            self.__checkAddressType(addressType, [0,1]);
            self.__checkConnectionInterval(interval);
            self.__checkConnectionLatency(latency);
            self.__checkSupervisionTimeout(timeout);
            self.__checkMasterClockAccuracy(accuracy);
        else:
            status = handle = role = addressType = interval = latency = timeout = accuracy = 0;
            address = None;
        return status, handle, role, Address(addressType, address), interval, latency, timeout, accuracy;

    def __advertisingReport(self):
        if self.__checkMinSize(12):
            reports, event, addressType = struct.unpack('<BBB', self.data[1:4]);
            address = struct.unpack('<6B', self.data[4:10]);
            dataSize = struct.unpack('<B', self.data[10:11])[0];
            if self.__checkSize(12 + dataSize):
                if dataSize > 0:
                    data = list(struct.unpack('<' + str(dataSize) + 'B', self.data[11:11+dataSize]));
                else:
                    data = [];
                rssi = struct.unpack('b', self.data[11+dataSize:12+dataSize])[0];
            else:
                rssi, data = 0, [];
            self.__checkAdvEvent(event);
            self.__checkAddressType(addressType);
            self.__checkAdvDataLength(dataSize);
            self.__checkRSSI(rssi);
        else:
            event, addressType, rssi, address, data = 0, 0, 0, None, [];
        return event, Address(addressType, address), data, rssi;

    def __connectionUpdateComplete(self):
        if self.__checkSize(10):
            status, handle, interval, latency, timeout = struct.unpack('<BHHHH', self.data[1:10]);
            self.__checkConnectionHandle(handle);
            self.__checkConnectionInterval(interval);
            self.__checkConnectionLatency(latency);
            self.__checkSupervisionTimeout(timeout);
        else:
            status = handle = interval = latency = timeout = 0;
        return status, handle, interval, latency, timeout;

    def __remoteFeaturesComplete(self):
        if self.__checkSize(12):
            status, handle = struct.unpack('<BH', self.data[1:4]);
            features = struct.unpack('<8B', self.data[4:12]);
            self.__checkConnectionHandle(handle);
        else:
            status, handle, features = 0, 0, [0 for _ in range(8)];
        return status, handle, self.__asNumber(features);

    def __leLTKRequest(self):
        if self.__checkSize(13):
            handle = struct.unpack('<H', self.data[1:3])[0];
            number = struct.unpack('<8B', self.data[3:11]);
            diversifier = struct.unpack('<H', self.data[11:13])[0];
            self.__checkConnectionHandle(handle);
        else:
            handle, number, diversifier = 0, [0 for _ in range(8)], 0;
        return handle, self.__asNumber(number), diversifier;

    def __connectionParameterRequest(self):
        if self.__checkSize(11):
            handle, minInterval, maxInterval, latency, timeout = struct.unpack('<HHHHH', self.data[1:11]);
            self.__checkConnectionHandle(handle);
            self.__checkConnectionInterval(minInterval);
            self.__checkConnectionInterval(maxInterval);
            self.__checkConnectionLatency(latency);
            self.__checkSupervisionTimeout(timeout);
            if not (minInterval <= maxInterval):
                self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_PARAMETER_INTERRELATION);
        else:
            handle = minInterval = maxInterval = latency = timeout = 0;
        return handle, minInterval, maxInterval, latency, timeout;

    def __dataLengthChange(self):
        if self.__checkSize(11):
            handle, maxTxOctets, maxTxTime, maxRxOctets, maxRxTime = struct.unpack('<HHHHH', self.data[1:11]);
            self.__checkConnectionHandle(handle);
            self.__checkMaxDataOctets(maxTxOctets);
            self.__checkMaxDataTransmitTime(maxTxTime);
            self.__checkMaxDataOctets(maxRxOctets);
            self.__checkMaxDataTransmitTime(maxRxTime);
        else:
            handle = maxTxOctets = maxTxTime = maxRxOctets = maxRxTime = 0;
        return handle, maxTxOctets, maxTxTime, maxRxOctets, maxRxTime;

    def __publicKeyComplete(self):
        if self.__checkSize(66):
            status = struct.unpack('<B', self.data[1:2])[0];
            key = struct.unpack('<64B', self.data[2:66]);
        else:
            status, key = 0, [0 for _ in range(64)];
        return status, self.__asNumber(key);

    def __generateDHKeyComplete(self):
        if self.__checkSize(34):
            status = struct.unpack('<B', self.data[1:2])[0];
            key = struct.unpack('<32B', self.data[2:34]);
        else:
            status, key = 0, [0 for _ in range(32)];
        return status, self.__asNumber(key);

    def __enhancedConnectionComplete(self):
        if self.__checkSize(31):
            status, handle, role, addressType = struct.unpack('<BHBB', self.data[1:6]);
            peerAddress = struct.unpack('<6B', self.data[6:12]);
            localResolvableAddress = struct.unpack('<6B', self.data[12:18]);
            peerResolvableAddress = struct.unpack('<6B', self.data[18:24]);
            interval, latency, timeout, accuracy = struct.unpack('<HHHB', self.data[24:31]);
            if status == 0:
                self.__checkConnectionHandle(handle);
                self.__checkConnectionRole(role);
                self.__checkAddressType(addressType);
                self.__checkConnectionInterval(interval);
                self.__checkConnectionLatency(latency);
                self.__checkSupervisionTimeout(timeout);
                self.__checkMasterClockAccuracy(accuracy);
        else:
            status = handle = role = addressType = interval = latency = timeout = accuracy = 0;
            peerAddress = localResolvableAddress = peerResolvableAddress = None;
        return status, handle, role, Address(addressType, peerAddress), Address(None, localResolvableAddress), Address(None, peerResolvableAddress), \
               interval, latency, timeout, accuracy;

    def __directAdvertisingReport(self):
        if self.__checkSize(18):
            reports, event, addressType = struct.unpack('<BBB', self.data[1:4]);
            address = struct.unpack('<6B', self.data[4:10]);
            directAddressType = struct.unpack('<B', self.data[10:11])[0];
            directAddress = struct.unpack('<6B', self.data[11:17]);
            rssi = struct.unpack('<b', self.data[17:18])[0];
            self.__checkAdvertisingReports(reports);
            self.__checkAdvEvent(event, 1, 1);
            self.__checkAddressType(addressType);
            self.__checkAddressType(directAddressType, [1]);
            self.__checkRSSI(rssi);
        else:
            event = addressType = directAddressType = rssi = 0;
            address = directAddress = None;
        return event, Address(addressType, address), Address(directAddressType, directAddress), rssi;

    def __phyUpdateComplete(self):
        if self.__checkSize(6):
            status, handle, txPhysical, rxPhysical = struct.unpack('<BHBB', self.data[1:6]);
            self.__checkConnectionHandle(handle);
            self.__checkPhy(txPhysical);
            self.__checkPhy(rxPhysical);
        else:
            status = handle = txPhysical = rxPhysical = 0;
        return status, handle, txPhysical, rxPhysical;

    def __extendedAdvertisingReport(self):
        if self.__checkMinSize(26):
            reports, eventType, addressType = struct.unpack('<BHB', self.data[1:5]);
            address = struct.unpack('<6B', self.data[5:11]);
            priPHY, secPHY, sid, txPower, rssi, interval, dirAddressType = struct.unpack('<BBBbbHB', self.data[11:19]);
            dirAddress = struct.unpack('<6B', self.data[19:25]);
            dataSize = struct.unpack('<B', self.data[25:26])[0];
            if self.__checkSize(26 + dataSize):
                if dataSize > 0:
                    data = list(struct.unpack('<' + str(dataSize) + 'B', self.data[26:26+dataSize]));
                else:
                    data = [];
            else:
                data = [];
            self.__checkAdvertisingReports(reports, 1, 10);
            self.__checkAdvEvent(eventType, 0, 0x7F);
            self.__checkAddressType(addressType, [0,1,2,3,255]);
            self.__checkPhy(priPHY, [1,3]);
            self.__checkPhy(secPHY, [0,1,2,3]);
            self.__checkSid(sid, [_ for _ in range(16)] + [255]);
            self.__checkSelectedTXPower(txPower, -127, 127);
            self.__checkRSSI(rssi);
            self.__checkPeriodicAdvInterval(interval);
            self.__checkAddressType(dirAddressType, [0,1,2,3,254]);
            self.__checkAdvDataLength(dataSize, 229);
        else:
            eventType = addressType = priPHY = secPHY = sid = txPower = rssi = interval = dirAddressType = 0;
            address, dirAddress, data = None, None, [];
        return eventType, Address(addressType, address), priPHY, secPHY, sid, txPower, rssi, interval, Address(dirAddressType, dirAddress), data;

    def __periodicAdvertisingSync(self):
        if self.__checkSize(16):
            status, handle, sid, addressType = struct.unpack('<BHBB', self.data[1:6]);
            address = struct.unpack('<6B', self.data[6:12]);
            phy, interval, accuracy = struct.unpack('<BHB', self.data[12:16]);
            self.__checkSyncHandle(handle);
            self.__checkSid(sid, [_ for _ in range(16)]);
            self.__checkAddressType(addressType);
            self.__checkPhy(phy);
            self.__checkPeriodicAdvInterval(interval);
            self.__checkMasterClockAccuracy(accuracy);
        else:
            status = handle = sid = addressType = phy = interval = accuracy = 0;
            address = None;
        return status, handle, sid, Address(addressType, address), phy, interval, accuracy;

    def __periodicAdvertisingReport(self):
        if self.__checkMinSize(8):
            handle, txPower, rssi, unUsed, dataStatus, dataSize = struct.unpack('<HbbBBB', self.data[1:8]);
            if self.__checkSize(8 + dataSize):
                if dataSize > 0:
                    data = list(struct.unpack('<' + str(dataSize) + 'B', self.data[8:8+dataSize]));
                else:
                    data = [];
                self.__checkSyncHandle(handle);
                self.__checkSelectedTXPower(txPower, -127, 127);
                self.__checkRSSI(rssi);
                self.__checkAdvDataStatus(dataStatus);
                self.__checkAdvDataLength(dataSize, 248);
                if not (unUsed == 0xFF):
                    self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_ADV_UNUSED_VALUE);
            else:
                data = [];
        else:
            handle, txPower, rssi, dataStatus, data = 0, 0, 0, 0, [];
        return handle, txPower, rssi, dataStatus, data;

    def __periodicAdvertisingSyncLost(self):
        if self.__checkSize(3):
            handle = struct.unpack('<H', self.data[1:3])[0];
            self.__checkSyncHandle(handle);
        else:
            handle = 0;
        return (handle,);

    def __scanTimeout(self):
        self.__checkSize(1);
        return (None,);

    def __advertiseSetTerminated(self):
        if self.__checkSize(6):
            status, advertiseHandle, connectionHandle, completedEvents = struct.unpack('<BBHB', self.data[1:6]);
            self.__checkAdvertisingHandle(advertiseHandle);
            self.__checkConnectionHandle(connectionHandle);
        else:
            status = advertiseHandle = connectionHandle = completedEvents = 0;
        return status, advertiseHandle, connectionHandle, completedEvents;

    def __scanRequestReceived(self):
        if self.__checkSize(9):
            handle, addressType = struct.unpack('<BB', self.data[1:3]);
            address = struct.unpack('<6B', self.data[3:9]);
            self.__checkAdvertisingHandle(handle);
            self.__checkAddressType(addressType);
        else:
            handle, addressType, address = 0, 0, None;
        return handle, Address(addressType, address);

    def __channnelSelectionAlgorithm(self):
        if self.__checkSize(4):
            handle, algorithm = struct.unpack('<HB', self.data[1:4]);
            self.__checkConnectionHandle(handle);
            self.__checkChannelAlgorithm(algorithm);
        else:
            handle = algorithm = 0;
        return handle, algorithm;

    def __metaEvent(self):
        if self.subEvent in self.__metaFuncs__:
            return self.__metaFuncs__[self.subEvent](self);
        else:
            raise Exception('LE Meta Event with invalid sub-event 0x%02X' % subEvent);

    def decode(self):
        if not self.values is None:
            return self.values;
        elif self.event in self.__eventFuncs__:
            self.values = self.__eventFuncs__[self.event](self);
            if not len(self.errors) == 0:
                raise Exception('Illegal values in event data! Event: 0x%02X,0x%02X Errors: %s' % (self.event, self.subEvent, self.errors));
            return self.values;
        else:
            self.errors.add(ErrorCodes.BT_HCI_ERR_BAD_EVENT);
            raise Exception('Illegal Event with event code 0x%02X' % self.event);

    def isCommandComplete(self):
        return self.event == Events.BT_HCI_EVT_CMD_COMPLETE;

    def isCommandStatus(self):
        return self.event == Events.BT_HCI_EVT_CMD_STATUS;

    def __str__(self):
        if self.event in self.__eventFormats__:
            if self.values is None:
                self.decode();
            if Events.BT_HCI_EVT_LE_META_EVENT != self.event:
                if Events.BT_HCI_EVT_CMD_COMPLETE == self.event and self.values[1] in self.__cceFormats__:
                    return self.__cceFormats__[self.values[1]].format(*self.values);
                elif Events.BT_HCI_EVT_CMD_STATUS == self.event and self.values[1] in self.__cseFormats__:
                    return self.__cseFormats__[self.values[1]].format(*self.values);
                else:
                    return self.__eventFormats__[self.event].format(*self.values);
            else:
                if self.subEvent in self.__metaFormats__:
                    return self.__metaFormats__[self.subEvent].format(*self.values);
                else:
                    raise Exception('LE Meta Event with invalid sub-event 0x%02X' % self.subEvent);
        else:
            raise Exception('Illegal Event with event code 0x%02X' % event);


    __metaFuncs__  = { MetaEvents.BT_HCI_EVT_LE_CONN_COMPLETE:            __connectionComplete,
                       MetaEvents.BT_HCI_EVT_LE_ADVERTISING_REPORT:       __advertisingReport,
                       MetaEvents.BT_HCI_EVT_LE_CONN_UPDATE_COMPLETE:     __connectionUpdateComplete,
                       MetaEvents.BT_HCI_EVT_LE_REMOTE_FEAT_COMPLETE:     __remoteFeaturesComplete,
                       MetaEvents.BT_HCI_EVT_LE_LTK_REQUEST:              __leLTKRequest,
                       MetaEvents.BT_HCI_EVT_LE_CONN_PARAM_REQ:           __connectionParameterRequest,
                       MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE:          __dataLengthChange,
                       MetaEvents.BT_HCI_EVT_LE_P256_PUBLIC_KEY_COMPLETE: __publicKeyComplete,
                       MetaEvents.BT_HCI_EVT_LE_GENERATE_DHKEY_COMPLETE:  __generateDHKeyComplete,
                       MetaEvents.BT_HCI_EVT_LE_ENH_CONN_COMPLETE:        __enhancedConnectionComplete,
                       MetaEvents.BT_HCI_EVT_LE_DIRECT_ADV_REPORT:        __directAdvertisingReport,
                       MetaEvents.BT_HCI_EVT_LE_PHY_UPDATE_COMPLETE:      __phyUpdateComplete,
                       MetaEvents.BT_HCI_EVT_LE_EXT_ADVERTISING_REPORT:   __extendedAdvertisingReport,
                       MetaEvents.BT_HCI_EVT_LE_PER_ADV_SYNC_ESTABLISHED: __periodicAdvertisingSync,
                       MetaEvents.BT_HCI_EVT_LE_PER_ADVERTISING_REPORT:   __periodicAdvertisingReport,
                       MetaEvents.BT_HCI_EVT_LE_PER_ADV_SYNC_LOST:        __periodicAdvertisingSyncLost,
                       MetaEvents.BT_HCI_EVT_LE_SCAN_TIMEOUT:             __scanTimeout,
                       MetaEvents.BT_HCI_EVT_LE_ADV_SET_TERMINATED:       __advertiseSetTerminated,
                       MetaEvents.BT_HCI_EVT_LE_SCAN_REQ_RECEIVED:        __scanRequestReceived,
                       MetaEvents.BT_HCI_EVT_LE_CHAN_SEL_ALGO:            __channnelSelectionAlgorithm };

    __eventFuncs__ = { Events.BT_HCI_EVT_DISCONN_COMPLETE:                __disconnectComplete,
                       Events.BT_HCI_EVT_ENCRYPT_CHANGE:                  __encryptionChange,
                       Events.BT_HCI_EVT_REMOTE_VERSION_INFO:             __RemoteVersionComplete,
                       Events.BT_HCI_EVT_CMD_COMPLETE:                    __commandComplete,
                       Events.BT_HCI_EVT_CMD_STATUS:                      __commandStatus,
                       Events.BT_HCI_EVT_HARDWARE_ERROR:                  __hardwareError,
                       Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS:           __completedPackets,
                       Events.BT_HCI_EVT_DATA_BUF_OVERFLOW:               __dataBufferOverflow,
                       Events.BT_HCI_EVT_ENCRYPT_KEY_REFRESH_COMPLETE:    __encryptionKeyRefreshComplete,
                       Events.BT_HCI_EVT_LE_META_EVENT:                   __metaEvent,
                       Events.BT_HCI_EVT_AUTH_PAYLOAD_TIMEOUT_EXP:        __authenticatedPayloadTimeout };

    __cceFuncs__ =   { CmdOpcodes.BT_HCI_OP_READ_TX_POWER_LEVEL:          __readTXPowerLevel,
                       CmdOpcodes.BT_HCI_OP_LE_READ_LE_HOST_SUPP:         __readLEHostSupport,
                       CmdOpcodes.BT_HCI_OP_READ_AUTH_PAYLOAD_TIMEOUT:    __readAuthPayloadTimeout,
                       CmdOpcodes.BT_HCI_OP_WRITE_AUTH_PAYLOAD_TIMEOUT:   __writeAuthPayloadTimeout,
                       CmdOpcodes.BT_HCI_OP_READ_LOCAL_VERSION_INFO:      __readLocalVersionInformation,
                       CmdOpcodes.BT_HCI_OP_READ_SUPPORTED_COMMANDS:      __readLocalSupportedCommands,
                       CmdOpcodes.BT_HCI_OP_READ_LOCAL_FEATURES:          __readLocalSupportedFeatures,
                       CmdOpcodes.BT_HCI_OP_READ_BUFFER_SIZE:             __readBufferSize,
                       CmdOpcodes.BT_HCI_OP_READ_BD_ADDR:                 __readBDAddress,
                       CmdOpcodes.BT_HCI_OP_READ_RSSI:                    __readRssi,
                       CmdOpcodes.BT_HCI_OP_LE_READ_BUFFER_SIZE:          __leReadBufferSize,
                       CmdOpcodes.BT_HCI_OP_LE_READ_LOCAL_FEATURES: 	  __leReadLocalSupportedFeatures,
                       CmdOpcodes.BT_HCI_OP_LE_READ_ADV_CHAN_TX_POWER: 	  __leReadAdvChannelTXPower,
                       CmdOpcodes.BT_HCI_OP_LE_READ_WL_SIZE:              __leReadListSize,
                       CmdOpcodes.BT_HCI_OP_LE_READ_CHAN_MAP:             __leReadChannelMap,
                       CmdOpcodes.BT_HCI_OP_LE_ENCRYPT:                   __leEncrypt,
                       CmdOpcodes.BT_HCI_OP_LE_RAND:                      __leRand,
                       CmdOpcodes.BT_HCI_OP_LE_LTK_REQ_REPLY:             __leLTKRequestReply,
                       CmdOpcodes.BT_HCI_OP_LE_LTK_REQ_NEG_REPLY:         __leLTKRequestReply,
                       CmdOpcodes.BT_HCI_OP_LE_READ_SUPP_STATES:          __leReadSupportedStates,
                       CmdOpcodes.BT_HCI_OP_LE_TEST_END:                  __leTestEnd,
                       CmdOpcodes.BT_HCI_OP_LE_CONN_PARAM_REQ_REPLY:      __leRemoteConnectionParameterRequest,
                       CmdOpcodes.BT_HCI_OP_LE_CONN_PARAM_REQ_NEG_REPLY:  __leRemoteConnectionParameterRequest,
                       CmdOpcodes.BT_HCI_OP_LE_SET_DATA_LEN:              __leSetDataLength,
                       CmdOpcodes.BT_HCI_OP_LE_READ_DEFAULT_DATA_LEN:     __leReadDefaultDataLength,
                       CmdOpcodes.BT_HCI_OP_LE_READ_RL_SIZE:              __leReadListSize,
                       CmdOpcodes.BT_HCI_OP_LE_READ_PEER_RPA:             __leReadResolvableAddress,
                       CmdOpcodes.BT_HCI_OP_LE_READ_LOCAL_RPA:            __leReadResolvableAddress,
                       CmdOpcodes.BT_HCI_OP_LE_READ_MAX_DATA_LEN:         __leReadMaximumDataLength,
                       CmdOpcodes.BT_HCI_OP_LE_READ_PHY:                  __leReadPHY,
                       CmdOpcodes.BT_HCI_OP_LE_SET_EXT_ADV_PARAM:         __leSetExtAdvParameters,
                       CmdOpcodes.BT_HCI_OP_LE_READ_MAX_ADV_DATA_LEN:     __leReadMaxAdvDataLength,
                       CmdOpcodes.BT_HCI_OP_LE_READ_NUM_ADV_SETS:         __leReadNoOfSupportedAdvSets,
                       CmdOpcodes.BT_HCI_OP_LE_READ_PER_ADV_LIST_SIZE:    __leReadListSize,
                       CmdOpcodes.BT_HCI_OP_LE_READ_TX_POWER:             __leReadTransmitPower,
                       CmdOpcodes.BT_HCI_OP_LE_READ_RF_PATH_COMP:         __leReadRFPathCompensation };