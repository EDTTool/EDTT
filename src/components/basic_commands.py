# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

import struct;
from enum import IntEnum;
from itertools import chain;
from components.address import *;
from components.events import *;

class Commands(IntEnum):
    CMD_ECHO_REQ                                                  = 1
    CMD_ECHO_RSP                                                  = 2
    CMD_INQUIRE_REQ                                               = 3
    CMD_INQUIRE_RSP                                               = 4
    CMD_DISCONNECT_REQ                                            = 5
    CMD_DISCONNECT_RSP                                            = 6
    CMD_READ_REMOTE_VERSION_INFORMATION_REQ                       = 7
    CMD_READ_REMOTE_VERSION_INFORMATION_RSP                       = 8
    CMD_SET_EVENT_MASK_REQ                                        = 9
    CMD_SET_EVENT_MASK_RSP                                        = 10
    CMD_RESET_REQ                                                 = 11
    CMD_RESET_RSP                                                 = 12
    CMD_READ_TRANSMIT_POWER_LEVEL_REQ                             = 13
    CMD_READ_TRANSMIT_POWER_LEVEL_RSP                             = 14
    CMD_SET_CONTROLLER_TO_HOST_FLOW_CONTROL_REQ                   = 15
    CMD_SET_CONTROLLER_TO_HOST_FLOW_CONTROL_RSP                   = 16
    CMD_HOST_BUFFER_SIZE_REQ                                      = 17
    CMD_HOST_BUFFER_SIZE_RSP                                      = 18
    CMD_HOST_NUMBER_OF_COMPLETED_PACKETS_REQ                      = 19
    CMD_HOST_NUMBER_OF_COMPLETED_PACKETS_RSP                      = 20
    CMD_SET_EVENT_MASK_PAGE_2_REQ                                 = 21
    CMD_SET_EVENT_MASK_PAGE_2_RSP                                 = 22
    CMD_WRITE_LE_HOST_SUPPORT_REQ                                 = 23
    CMD_WRITE_LE_HOST_SUPPORT_RSP                                 = 24
    CMD_READ_AUTHENTICATED_PAYLOAD_TIMEOUT_REQ                    = 25
    CMD_READ_AUTHENTICATED_PAYLOAD_TIMEOUT_RSP                    = 26
    CMD_WRITE_AUTHENTICATED_PAYLOAD_TIMEOUT_REQ                   = 27
    CMD_WRITE_AUTHENTICATED_PAYLOAD_TIMEOUT_RSP                   = 28
    CMD_READ_LOCAL_VERSION_INFORMATION_REQ                        = 29
    CMD_READ_LOCAL_VERSION_INFORMATION_RSP                        = 30
    CMD_READ_LOCAL_SUPPORTED_COMMANDS_REQ                         = 31
    CMD_READ_LOCAL_SUPPORTED_COMMANDS_RSP                         = 32
    CMD_READ_LOCAL_SUPPORTED_FEATURES_REQ                         = 33
    CMD_READ_LOCAL_SUPPORTED_FEATURES_RSP                         = 34
    CMD_READ_BUFFER_SIZE_REQ                                      = 35
    CMD_READ_BUFFER_SIZE_RSP                                      = 36
    CMD_READ_BD_ADDR_REQ                                          = 37
    CMD_READ_BD_ADDR_RSP                                          = 38
    CMD_READ_RSSI_REQ                                             = 39
    CMD_READ_RSSI_RSP                                             = 40
    CMD_LE_SET_EVENT_MASK_REQ                                     = 41
    CMD_LE_SET_EVENT_MASK_RSP                                     = 42
    CMD_LE_READ_BUFFER_SIZE_REQ                                   = 43
    CMD_LE_READ_BUFFER_SIZE_RSP                                   = 44
    CMD_LE_READ_LOCAL_SUPPORTED_FEATURES_REQ                      = 45
    CMD_LE_READ_LOCAL_SUPPORTED_FEATURES_RSP                      = 46
    CMD_LE_SET_RANDOM_ADDRESS_REQ                                 = 47
    CMD_LE_SET_RANDOM_ADDRESS_RSP                                 = 48
    CMD_LE_SET_ADVERTISING_PARAMETERS_REQ                         = 49
    CMD_LE_SET_ADVERTISING_PARAMETERS_RSP                         = 50
    CMD_LE_READ_ADVERTISING_CHANNEL_TX_POWER_REQ                  = 51
    CMD_LE_READ_ADVERTISING_CHANNEL_TX_POWER_RSP                  = 52
    CMD_LE_SET_ADVERTISING_DATA_REQ                               = 53
    CMD_LE_SET_ADVERTISING_DATA_RSP                               = 54
    CMD_LE_SET_SCAN_RESPONSE_DATA_REQ                             = 55
    CMD_LE_SET_SCAN_RESPONSE_DATA_RSP                             = 56
    CMD_LE_SET_ADVERTISING_ENABLE_REQ                             = 57
    CMD_LE_SET_ADVERTISING_ENABLE_RSP                             = 58
    CMD_LE_SET_SCAN_PARAMETERS_REQ                                = 59
    CMD_LE_SET_SCAN_PARAMETERS_RSP                                = 60
    CMD_LE_SET_SCAN_ENABLE_REQ                                    = 61
    CMD_LE_SET_SCAN_ENABLE_RSP                                    = 62
    CMD_LE_CREATE_CONNECTION_REQ                                  = 63
    CMD_LE_CREATE_CONNECTION_RSP                                  = 64
    CMD_LE_CREATE_CONNECTION_CANCEL_REQ                           = 65
    CMD_LE_CREATE_CONNECTION_CANCEL_RSP                           = 66
    CMD_LE_READ_FILTER_ACCEPT_LIST_SIZE_REQ                               = 67
    CMD_LE_READ_FILTER_ACCEPT_LIST_SIZE_RSP                               = 68
    CMD_LE_CLEAR_FILTER_ACCEPT_LIST_REQ                                   = 69
    CMD_LE_CLEAR_FILTER_ACCEPT_LIST_RSP                                   = 70
    CMD_LE_ADD_DEVICE_TO_FILTER_ACCEPT_LIST_REQ                           = 71
    CMD_LE_ADD_DEVICE_TO_FILTER_ACCEPT_LIST_RSP                           = 72
    CMD_LE_REMOVE_DEVICE_FROM_FILTER_ACCEPT_LIST_REQ                      = 73
    CMD_LE_REMOVE_DEVICE_FROM_FILTER_ACCEPT_LIST_RSP                      = 74
    CMD_LE_CONNECTION_UPDATE_REQ                                  = 75
    CMD_LE_CONNECTION_UPDATE_RSP                                  = 76
    CMD_LE_SET_HOST_CHANNEL_CLASSIFICATION_REQ                    = 77
    CMD_LE_SET_HOST_CHANNEL_CLASSIFICATION_RSP                    = 78
    CMD_LE_READ_CHANNEL_MAP_REQ                                   = 79
    CMD_LE_READ_CHANNEL_MAP_RSP                                   = 80
    CMD_LE_READ_REMOTE_FEATURES_REQ                               = 81
    CMD_LE_READ_REMOTE_FEATURES_RSP                               = 82
    CMD_LE_ENCRYPT_REQ                                            = 83
    CMD_LE_ENCRYPT_RSP                                            = 84
    CMD_LE_RAND_REQ                                               = 85
    CMD_LE_RAND_RSP                                               = 86
    CMD_LE_START_ENCRYPTION_REQ                                   = 87
    CMD_LE_START_ENCRYPTION_RSP                                   = 88
    CMD_LE_LONG_TERM_KEY_REQUEST_REPLY_REQ                        = 89
    CMD_LE_LONG_TERM_KEY_REQUEST_REPLY_RSP                        = 90
    CMD_LE_LONG_TERM_KEY_REQUEST_NEGATIVE_REPLY_REQ               = 91
    CMD_LE_LONG_TERM_KEY_REQUEST_NEGATIVE_REPLY_RSP               = 92
    CMD_LE_READ_SUPPORTED_STATES_REQ                              = 93
    CMD_LE_READ_SUPPORTED_STATES_RSP                              = 94
    CMD_LE_RECEIVER_TEST_REQ                                      = 95
    CMD_LE_RECEIVER_TEST_RSP                                      = 96
    CMD_LE_TRANSMITTER_TEST_REQ                                   = 97
    CMD_LE_TRANSMITTER_TEST_RSP                                   = 98
    CMD_LE_TEST_END_REQ                                           = 99
    CMD_LE_TEST_END_RSP                                           = 100
    CMD_LE_REMOTE_CONNECTION_PARAMETER_REQUEST_REPLY_REQ          = 101
    CMD_LE_REMOTE_CONNECTION_PARAMETER_REQUEST_REPLY_RSP          = 102
    CMD_LE_REMOTE_CONNECTION_PARAMETER_REQUEST_NEGATIVE_REPLY_REQ = 103
    CMD_LE_REMOTE_CONNECTION_PARAMETER_REQUEST_NEGATIVE_REPLY_RSP = 104
    CMD_LE_SET_DATA_LENGTH_REQ                                    = 105
    CMD_LE_SET_DATA_LENGTH_RSP                                    = 106
    CMD_LE_READ_SUGGESTED_DEFAULT_DATA_LENGTH_REQ                 = 107
    CMD_LE_READ_SUGGESTED_DEFAULT_DATA_LENGTH_RSP                 = 108
    CMD_LE_WRITE_SUGGESTED_DEFAULT_DATA_LENGTH_REQ                = 109
    CMD_LE_WRITE_SUGGESTED_DEFAULT_DATA_LENGTH_RSP                = 110
    CMD_LE_READ_LOCAL_P_256_PUBLIC_KEY_COMMAND_REQ                = 111
    CMD_LE_READ_LOCAL_P_256_PUBLIC_KEY_COMMAND_RSP                = 112
    CMD_LE_GENERATE_DHKEY_COMMAND_REQ                             = 113
    CMD_LE_GENERATE_DHKEY_COMMAND_RSP                             = 114
    CMD_LE_ADD_DEVICE_TO_RESOLVING_LIST_REQ                       = 115
    CMD_LE_ADD_DEVICE_TO_RESOLVING_LIST_RSP                       = 116
    CMD_LE_REMOVE_DEVICE_FROM_RESOLVING_LIST_REQ                  = 117
    CMD_LE_REMOVE_DEVICE_FROM_RESOLVING_LIST_RSP                  = 118
    CMD_LE_CLEAR_RESOLVING_LIST_REQ                               = 119
    CMD_LE_CLEAR_RESOLVING_LIST_RSP                               = 120
    CMD_LE_READ_RESOLVING_LIST_SIZE_REQ                           = 121
    CMD_LE_READ_RESOLVING_LIST_SIZE_RSP                           = 122
    CMD_LE_READ_PEER_RESOLVABLE_ADDRESS_REQ                       = 123
    CMD_LE_READ_PEER_RESOLVABLE_ADDRESS_RSP                       = 124
    CMD_LE_READ_LOCAL_RESOLVABLE_ADDRESS_REQ                      = 125
    CMD_LE_READ_LOCAL_RESOLVABLE_ADDRESS_RSP                      = 126
    CMD_LE_SET_ADDRESS_RESOLUTION_ENABLE_REQ                      = 127
    CMD_LE_SET_ADDRESS_RESOLUTION_ENABLE_RSP                      = 128
    CMD_LE_SET_RESOLVABLE_PRIVATE_ADDRESS_TIMEOUT_REQ             = 129
    CMD_LE_SET_RESOLVABLE_PRIVATE_ADDRESS_TIMEOUT_RSP             = 130
    CMD_LE_READ_MAXIMUM_DATA_LENGTH_REQ                           = 131
    CMD_LE_READ_MAXIMUM_DATA_LENGTH_RSP                           = 132
    CMD_LE_READ_PHY_REQ                                           = 133
    CMD_LE_READ_PHY_RSP                                           = 134
    CMD_LE_SET_DEFAULT_PHY_REQ                                    = 135
    CMD_LE_SET_DEFAULT_PHY_RSP                                    = 136
    CMD_LE_SET_PHY_REQ                                            = 137
    CMD_LE_SET_PHY_RSP                                            = 138
    CMD_LE_ENHANCED_RECEIVER_TEST_REQ                             = 139
    CMD_LE_ENHANCED_RECEIVER_TEST_RSP                             = 140
    CMD_LE_ENHANCED_TRANSMITTER_TEST_REQ                          = 141
    CMD_LE_ENHANCED_TRANSMITTER_TEST_RSP                          = 142
    CMD_LE_SET_EXTENDED_ADVERTISING_PARAMETERS_REQ                = 143
    CMD_LE_SET_EXTENDED_ADVERTISING_PARAMETERS_RSP                = 144
    CMD_LE_SET_EXTENDED_ADVERTISING_DATA_REQ                      = 145
    CMD_LE_SET_EXTENDED_ADVERTISING_DATA_RSP                      = 146
    CMD_LE_SET_EXTENDED_SCAN_RESPONSE_DATA_REQ                    = 147
    CMD_LE_SET_EXTENDED_SCAN_RESPONSE_DATA_RSP                    = 148
    CMD_LE_SET_EXTENDED_ADVERTISING_ENABLE_REQ                    = 149
    CMD_LE_SET_EXTENDED_ADVERTISING_ENABLE_RSP                    = 150
    CMD_LE_READ_MAXIMUM_ADVERTISING_DATA_LENGTH_REQ               = 151
    CMD_LE_READ_MAXIMUM_ADVERTISING_DATA_LENGTH_RSP               = 152
    CMD_LE_READ_NUMBER_OF_SUPPORTED_ADVERTISING_SETS_REQ          = 153
    CMD_LE_READ_NUMBER_OF_SUPPORTED_ADVERTISING_SETS_RSP          = 154
    CMD_LE_REMOVE_ADVERTISING_SET_REQ                             = 155
    CMD_LE_REMOVE_ADVERTISING_SET_RSP                             = 156
    CMD_LE_CLEAR_ADVERTISING_SETS_REQ                             = 157
    CMD_LE_CLEAR_ADVERTISING_SETS_RSP                             = 158
    CMD_LE_SET_PERIODIC_ADVERTISING_PARAMETERS_REQ                = 159
    CMD_LE_SET_PERIODIC_ADVERTISING_PARAMETERS_RSP                = 160
    CMD_LE_SET_PERIODIC_ADVERTISING_DATA_REQ                      = 161
    CMD_LE_SET_PERIODIC_ADVERTISING_DATA_RSP                      = 162
    CMD_LE_SET_PERIODIC_ADVERTISING_ENABLE_REQ                    = 163
    CMD_LE_SET_PERIODIC_ADVERTISING_ENABLE_RSP                    = 164
    CMD_LE_SET_EXTENDED_SCAN_PARAMETERS_REQ                       = 165
    CMD_LE_SET_EXTENDED_SCAN_PARAMETERS_RSP                       = 166
    CMD_LE_SET_EXTENDED_SCAN_ENABLE_REQ                           = 167
    CMD_LE_SET_EXTENDED_SCAN_ENABLE_RSP                           = 168
    CMD_LE_EXTENDED_CREATE_CONNECTION_REQ                         = 169
    CMD_LE_EXTENDED_CREATE_CONNECTION_RSP                         = 170
    CMD_LE_PERIODIC_ADVERTISING_CREATE_SYNC_REQ                   = 171
    CMD_LE_PERIODIC_ADVERTISING_CREATE_SYNC_RSP                   = 172
    CMD_LE_PERIODIC_ADVERTISING_CREATE_SYNC_CANCEL_REQ            = 173
    CMD_LE_PERIODIC_ADVERTISING_CREATE_SYNC_CANCEL_RSP            = 174
    CMD_LE_PERIODIC_ADVERTISING_TERMINATE_SYNC_REQ                = 175
    CMD_LE_PERIODIC_ADVERTISING_TERMINATE_SYNC_RSP                = 176
    CMD_LE_ADD_DEVICE_TO_PERIODIC_ADVERTISER_LIST_REQ             = 177
    CMD_LE_ADD_DEVICE_TO_PERIODIC_ADVERTISER_LIST_RSP             = 178
    CMD_LE_REMOVE_DEVICE_FROM_PERIODIC_ADVERTISER_LIST_REQ        = 179
    CMD_LE_REMOVE_DEVICE_FROM_PERIODIC_ADVERTISER_LIST_RSP        = 180
    CMD_LE_CLEAR_PERIODIC_ADVERTISER_LIST_REQ                     = 181
    CMD_LE_CLEAR_PERIODIC_ADVERTISER_LIST_RSP                     = 182
    CMD_LE_READ_PERIODIC_ADVERTISER_LIST_SIZE_REQ                 = 183
    CMD_LE_READ_PERIODIC_ADVERTISER_LIST_SIZE_RSP                 = 184
    CMD_LE_READ_TRANSMIT_POWER_REQ                                = 185
    CMD_LE_READ_TRANSMIT_POWER_RSP                                = 186
    CMD_LE_READ_RF_PATH_COMPENSATION_REQ                          = 187
    CMD_LE_READ_RF_PATH_COMPENSATION_RSP                          = 188
    CMD_LE_WRITE_RF_PATH_COMPENSATION_REQ                         = 189
    CMD_LE_WRITE_RF_PATH_COMPENSATION_RSP                         = 190
    CMD_LE_SET_PRIVACY_MODE_REQ                                   = 191
    CMD_LE_SET_PRIVACY_MODE_RSP                                   = 192
    CMD_WRITE_BD_ADDR_REQ                                         = 193
    CMD_WRITE_BD_ADDR_RSP                                         = 194
    CMD_FLUSH_EVENTS_REQ                                          = 195
    CMD_FLUSH_EVENTS_RSP                                          = 196
    CMD_HAS_EVENT_REQ                                             = 197
    CMD_HAS_EVENT_RSP                                             = 198
    CMD_GET_EVENT_REQ                                             = 199
    CMD_GET_EVENT_RSP                                             = 200
    CMD_LE_DATA_FLUSH_REQ                                         = 201
    CMD_LE_DATA_FLUSH_RSP                                         = 202
    CMD_LE_DATA_READY_REQ                                         = 203
    CMD_LE_DATA_READY_RSP                                         = 204
    CMD_LE_DATA_WRITE_REQ                                         = 205
    CMD_LE_DATA_WRITE_RSP                                         = 206
    CMD_LE_DATA_READ_REQ                                          = 207
    CMD_LE_DATA_READ_RSP                                          = 208
    CMD_GATT_SERVICE_SET_REQ                                      = 209
    CMD_GATT_SERVICE_SET_RSP                                      = 210
    CMD_GATT_SERVICE_NOTIFY_REQ                                   = 211
    CMD_GATT_SERVICE_NOTIFY_RSP                                   = 212
    CMD_GATT_SERVICE_INDICATE_REQ                                 = 213
    CMD_GATT_SERVICE_INDICATE_RSP                                 = 214
    CMD_GAP_ADVERTISING_MODE_REQ                                  = 215
    CMD_GAP_ADVERTISING_MODE_RSP                                  = 216
    CMD_GAP_ADVERTISING_DATA_REQ                                  = 217
    CMD_GAP_ADVERTISING_DATA_RSP                                  = 218
    CMD_GAP_SCANNING_MODE_REQ                                     = 219
    CMD_GAP_SCANNING_MODE_RSP                                     = 220
    CMD_READ_STATIC_ADDRESSES_REQ                                 = 221
    CMD_READ_STATIC_ADDRESSES_RSP                                 = 222
    CMD_READ_KEY_HIERARCHY_ROOTS_REQ                              = 223
    CMD_READ_KEY_HIERARCHY_ROOTS_RSP                              = 224
    CMD_GAP_READ_IRK_REQ                                          = 225
    CMD_GAP_READ_IRK_RSP                                          = 226
    CMD_GAP_ROLE_REQ                                              = 227
    CMD_GAP_ROLE_RSP                                              = 228
    CMD_LE_ISO_DATA_FLUSH_REQ                                     = 229
    CMD_LE_ISO_DATA_FLUSH_RSP                                     = 230
    CMD_LE_ISO_DATA_READY_REQ                                     = 231
    CMD_LE_ISO_DATA_READY_RSP                                     = 232
    CMD_LE_ISO_DATA_WRITE_REQ                                     = 233
    CMD_LE_ISO_DATA_WRITE_RSP                                     = 234
    CMD_LE_ISO_DATA_READ_REQ                                      = 235
    CMD_LE_ISO_DATA_READ_RSP                                      = 236
    CMD_LE_SET_CIG_PARAMETERS_REQ                                 = 237
    CMD_LE_SET_CIG_PARAMETERS_RSP                                 = 238
    CMD_LE_SET_CIG_PARAMETERS_TEST_REQ                            = 239
    CMD_LE_SET_CIG_PARAMETERS_TEST_RSP                            = 240
    CMD_LE_CREATE_CIS_REQ                                         = 241
    CMD_LE_CREATE_CIS_RSP                                         = 242
    CMD_LE_REMOVE_CIG_REQ                                         = 243
    CMD_LE_REMOVE_CIG_RSP                                         = 244
    CMD_LE_ACCEPT_CIS_REQUEST_REQ                                 = 245
    CMD_LE_ACCEPT_CIS_REQUEST_RSP                                 = 246
    CMD_LE_REJECT_CIS_REQUEST_REQ                                 = 247
    CMD_LE_REJECT_CIS_REQUEST_RSP                                 = 248
    CMD_LE_SETUP_ISO_DATA_PATH_REQ                                = 249
    CMD_LE_SETUP_ISO_DATA_PATH_RSP                                = 250
    CMD_LE_REMOVE_ISO_DATA_PATH_REQ                               = 251
    CMD_LE_REMOVE_ISO_DATA_PATH_RSP                               = 252
    CMD_LE_SET_HOST_FEATURE_REQ                                   = 253
    CMD_LE_SET_HOST_FEATURE_RSP                                   = 254
    CMD_GET_IXIT_VALUE_REQ                                        = 255
    CMD_GET_IXIT_VALUE_RSP                                        = 256
    CMD_HCI_LE_ISO_TRANSMIT_TEST_REQ                              = 257
    CMD_HCI_LE_ISO_TRANSMIT_TEST_RSP                              = 258
    CMD_HCI_LE_ISO_RECEIVE_TEST_REQ                               = 259
    CMD_HCI_LE_ISO_RECEIVE_TEST_RSP                               = 260
    CMD_HCI_LE_ISO_READ_TEST_COUNTERS_REQ                         = 261
    CMD_HCI_LE_ISO_READ_TEST_COUNTERS_RSP                         = 262
    CMD_HCI_LE_ISO_TEST_END_REQ                                   = 263
    CMD_HCI_LE_ISO_TEST_END_RSP                                   = 264
    CMD_HCI_LE_REQUEST_PEER_SCA_REQ                               = 265
    CMD_HCI_LE_REQUEST_PEER_SCA_RSP                               = 266
    CMD_LE_READ_BUFFER_SIZE_V2_REQ                                = 267
    CMD_LE_READ_BUFFER_SIZE_V2_RSP                                = 268


class HCICommands(IntEnum):
    BT_HCI_OP_INQUIRY                       = 0x401
    BT_HCI_OP_DISCONNECT                    = 0x406
    BT_HCI_OP_READ_REMOTE_VERSION_INFO      = 0x41D
    BT_HCI_OP_SET_EVENT_MASK                = 0xC01
    BT_HCI_OP_RESET                         = 0xC03
    BT_HCI_OP_READ_TX_POWER_LEVEL           = 0xC2D
    BT_HCI_OP_SET_CTL_TO_HOST_FLOW          = 0xC31
    BT_HCI_OP_HOST_BUFFER_SIZE              = 0xC33
    BT_HCI_OP_HOST_NUM_COMPLETED_PACKETS    = 0xC35
    BT_HCI_OP_SET_EVENT_MASK_PAGE_2         = 0xC63
    BT_HCI_OP_LE_WRITE_LE_HOST_SUPP         = 0xC6D
    BT_HCI_OP_READ_AUTH_PAYLOAD_TIMEOUT     = 0xC7B
    BT_HCI_OP_WRITE_AUTH_PAYLOAD_TIMEOUT    = 0xC7C
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
    BT_HCI_OP_LE_READ_FAL_SIZE               = 0x200F
    BT_HCI_OP_LE_CLEAR_FAL                   = 0x2010
    BT_HCI_OP_LE_ADD_DEV_TO_FAL              = 0x2011
    BT_HCI_OP_LE_REM_DEV_FROM_FAL            = 0x2012
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
    BT_HCI_OP_LE_READ_BUFFER_SIZE_V2        = 0x2060
    BT_HCI_OP_LE_SET_CIG_PARAMETERS         = 0x2062
    BT_HCI_OP_LE_SET_CIG_PARAMETERS_TEST    = 0x2063
    BT_HCI_OP_LE_CREATE_CIS                 = 0x2064
    BT_HCI_OP_LE_REMOVE_CIG                 = 0x2065
    BT_HCI_OP_LE_ACCEPT_CIS_REQUEST         = 0x2066
    BT_HCI_OP_LE_REJECT_CIS_REQUEST         = 0x2067
    BT_HCI_OP_LE_REQUEST_PEER_SCA           = 0x206D
    BT_HCI_OP_LE_SETUP_ISO_DATA_PATH        = 0x206E
    BT_HCI_OP_LE_REMOVE_ISO_DATA_PATH       = 0x206F
    BT_HCI_OP_LE_ISO_TRANSMIT_TEST          = 0x2070
    BT_HCI_OP_LE_ISO_RECEIVE_TEST           = 0x2071
    BT_HCI_OP_LE_ISO_READ_TEST_COUNTERS     = 0x2072
    BT_HCI_OP_LE_ISO_TEST_END               = 0x2073
    BT_HCI_OP_LE_SET_HOST_FEATURE           = 0x2074
    BT_HCI_OP_VS_WRITE_BD_ADDR              = 0xFC06

class Events(IntEnum):
    BT_HCI_EVT_NONE                         = 0
    BT_HCI_EVT_DISCONN_COMPLETE             = 5
    BT_HCI_EVT_ENCRYPT_CHANGE_V1            = 8
    BT_HCI_EVT_REMOTE_VERSION_INFO          = 12
    BT_HCI_EVT_CMD_COMPLETE                 = 14
    BT_HCI_EVT_CMD_STATUS                   = 15
    BT_HCI_EVT_NUM_COMPLETED_PACKETS        = 19
    BT_HCI_EVT_DATA_BUF_OVERFLOW            = 26
    BT_HCI_EVT_ENCRYPT_KEY_REFRESH_COMPLETE = 48
    BT_HCI_EVT_LE_META_EVENT                = 62
    BT_HCI_EVT_AUTH_PAYLOAD_TIMEOUT_EXP     = 87
    BT_HCI_EVT_ENCRYPT_CHANGE_V2            = 89


class MetaEvents(IntEnum):
    BT_HCI_EVT_LE_CONN_COMPLETE             = 1
    BT_HCI_EVT_LE_ADVERTISING_REPORT        = 2
    BT_HCI_EVT_LE_CONN_UPDATE_COMPLETE      = 3
    BT_HCI_EV_LE_REMOTE_FEAT_COMPLETE       = 4
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
    BT_HCI_EVT_LE_CIS_ESTABLISHED           = 25
    BT_HCI_EVT_LE_CIS_REQUEST               = 26
    BT_HCI_EVT_LE_REQUEST_PEER_SCA_COMPLETE = 31


class ProfileId(IntEnum):
    PROFILE_ID_GAP                          = 0
    PROFILE_ID_GATT                         = 1
    PROFILE_ID_HCI                          = 2
    PROFILE_ID_L2CAP                        = 3
    PROFILE_ID_LL                           = 4
    PROFILE_ID_SM                           = 5

class PhysicalChannel(IntEnum):
    LE_1M    = 1
    LE_2M    = 2
    LE_CODED = 3

class FragmentOperation(IntEnum):
    INTERMEDIATE_FRAGMENT = 0      # Intermediate fragment of fragmented extended advertising data
    FIRST_FRAGMENT        = 1      # First fragment of fragmented extended advertising data
    LAST_FRAGMENT         = 2      # Last fragment of fragmented extended advertising data
    COMPLETE_FRAGMENT     = 3      # Complete extended advertising data
    UNCHANGED_FRAGMENT    = 4      # Unchanged data (just update the Advertising DID)

class Ixit:
    """
    Definition of Implementation eXtra Information for Test (IXIT)
    """
    def __init__(self, profile_id, ref_major, ref_minor, value_fmt):
        self.profile_id = profile_id
        self.ref_major = ref_major
        self.ref_minor = ref_minor
        self.value_fmt = value_fmt

"""
The IXIT (Proforma for Bluetooth Conformance Test Suites) comes from Core.IXIT document
https://www.bluetooth.com/specifications/qualification-test-requirements/
"""
IXITS = {
    "TSPX_max_sdu_length": Ixit(ProfileId.PROFILE_ID_LL, 7, 1, 'H'),
    "TSPX_max_cis_nse":  Ixit(ProfileId.PROFILE_ID_LL, 7, 14, 'B'),
    "TSPX_max_cis_bn": Ixit(ProfileId.PROFILE_ID_LL, 7, 15, 'B'),
}

"""
BLUETOOTH CORE SPECIFICATION Version 5.2 | Vol 6, Part B, 4.6 FEATURE SUPPORT
"""
class FeatureSupport(IntEnum):
    ISOCHRONOUS_BROADCASTER = 30
    ISOCHRONOUS_CHANNELS = 32


def edtt_send_cmd(transport, idx, opcode, payload_fmt, payload_tuple):
    """Send EDTT command
    EDTT command PDU format
    0--------16--------------32--------+
    | Opcode | PayloadLength | Payload |
    +--------+---------------+---------+
    :param transport: bearer to be used
    :param idx: device index
    :param opcode: command opcode
    :param payload_fmt: command payload format used to serialize the data
    :param payload_tuple: payload as tuple
    :return:
    """
    req = struct.pack('<HH' + payload_fmt, opcode, struct.calcsize('<' + payload_fmt), *payload_tuple)
    transport.send(idx, req)


def edtt_wait_cmd_cmpl(transport, idx, opcode, payload_fmt, to):
    """Wait for command complete reception
    EDTT command complete PDU format
    0--------16--------------32--------+
    | Opcode | PayloadLength | Payload |
    +--------+---------------+---------+
    :param transport: bearer to be used
    :param idx: device index
    :param opcode: command complete opcode
    :param payload_fmt: command complete payload format used to deserialize the data
    :param to: timeout
    :return:
    """
    payload_fmt = '<' + payload_fmt  # specify endianess, avoid alignment
    exp_payload_len = struct.calcsize(payload_fmt)
    rsp_size = 4 + exp_payload_len
    rsp = transport.recv(idx, rsp_size, to)
    if rsp_size != len(rsp):
        raise Exception("Response too short (Expected %i bytes got %i bytes)" % (rsp_size, len(rsp)))

    # unpack and validate EDTT header first
    op, payload_len = struct.unpack_from('<HH', rsp)
    if op != opcode:
        raise Exception("Inappropriate command response received (%i)" % op)

    if payload_len != exp_payload_len:
        raise Exception("Payload length field corrupted (Expected %i got %i)" % (exp_payload_len, payload_len))

    # finally, unpack the payload
    return struct.unpack_from(payload_fmt, rsp, 4)


def echo(transport, idx, message, to):

    cmd = struct.pack('<HH', Commands.CMD_ECHO_REQ, len(message)) + message;
    transport.send(idx, cmd);

    packet = transport.recv(idx, len(cmd), to);

    if ( len(cmd) != len(packet) ):
        raise Exception("echo test failed: Response too short (Expected %i bytes got %i bytes)" % (len(cmd), len(packet)));

    RespCmd, RespLen = struct.unpack('<HH', packet[:4]);

    if ( RespCmd != Commands.CMD_ECHO_RSP ):
        raise Exception("echo test failed: Inappropriate command response received");

    if ( RespLen != len(message) ):
        raise Exception("echo test failed: Response length corrupted (%i)" % RespLen);

    if ( packet[4:] != message ):
        raise Exception("echo test failed: Message content corrupted (%s)" % packet[4:]);

    return packet[4:];

"""
    This command causes the BR/EDR Controller to enter Inquiry Mode. Inquiry Mode is used to discover other nearby BR/EDR
    Controllers. The LAP input parameter contains the LAP from which the inquiry access code shall be derived when the inquiry
    procedure is made. The Inquiry_Length parameter specifies the total duration of the Inquiry Mode and, when this time
    expires, Inquiry will be halted. When Extended_Inquiry_Length is greater than zero, the duration of the Inquiry Mode may
    be changed to (Inquiry_Length + Extended_Inquiry_Length). The Num_Responses parameter specifies the number of responses
    that can be received before the Inquiry is halted. Inquiry Result, Inquiry Result with RSSI, or Extended Inquiry Result
    events will be sent to report the details of nearby BR/EDR Controllers that have responded to this inquiry. The Inquiry
    Complete event is sent to report that Inquiry Mode has ended.
"""
def inquire(transport, idx, lap, length, NumRsp, to):

    cmd = struct.pack('<HHH3B', Commands.CMD_INQUIRE_REQ, 7, HCICommands.BT_HCI_OP_INQUIRY, *lap);
    cmd += struct.pack('<BB', length, NumRsp);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("Inquire command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status, = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_INQUIRE_RSP ):
        raise Exception("Inquire command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("Inquire command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The Disconnect command is used to terminate an existing connection.
"""
def disconnect(transport, idx, handle, reason, to):

    cmd = struct.pack('<HHHHB', Commands.CMD_DISCONNECT_REQ, 5, HCICommands.BT_HCI_OP_DISCONNECT, handle, reason);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("Disconnect command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_DISCONNECT_RSP ):
        raise Exception("Disconnect command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("Disconnect command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    This command will obtain the values for the version information for the remote device identified by the Connection_Handle
    parameter.
"""
def read_remote_version_information(transport, idx, handle, to):

    cmd = struct.pack('<HHHH', Commands.CMD_READ_REMOTE_VERSION_INFORMATION_REQ, 4, HCICommands.BT_HCI_OP_READ_REMOTE_VERSION_INFO, handle);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("Read Remote Version Information command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_READ_REMOTE_VERSION_INFORMATION_RSP ):
        raise Exception("Read Remote Version Information command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("Read Remote Version Information command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The Set_Event_Mask command is used to control which events are generated by the HCI for the Host. If the bit in the
    Event_Mask is set to a one, then the event associated with that bit will be enabled. For an LE Controller, the \93LE Meta
    Event\94 bit in the Event_Mask shall enable or disable all LE events in the LE Meta Event (see Section 7.7.65).
"""
def set_event_mask(transport, idx, events, to):

    cmd = struct.pack('<HHH8B', Commands.CMD_SET_EVENT_MASK_REQ, 10, HCICommands.BT_HCI_OP_SET_EVENT_MASK, *events);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("Set Event Mask command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_SET_EVENT_MASK_RSP ):
        raise Exception("Set Event Mask command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("Set Event Mask command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The Reset command will reset the Controller and the Link Manager on the BR/ EDR Controller, the PAL on an AMP Controller,
    or the Link Layer on an LE Controller. If the Controller supports both BR/EDR and LE then the Reset command shall reset
    the Link Manager, Baseband and Link Layer. The Reset command shall not affect the used HCI transport layer since the HCI
    transport layers may have reset mechanisms of their own. After the reset is completed, the current operational state will
    be lost, the Controller will enter standby mode and the Controller will automatically revert to the default values for the
    parameters for which default values are defined in the specification.
"""
def reset(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_RESET_REQ, 2, HCICommands.BT_HCI_OP_RESET);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("Reset command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_RESET_RSP ):
        raise Exception("Reset command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("Reset command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    This command reads the values for the Transmit_Power_Level parameter for the specified Connection_Handle. The
    Connection_Handle shall be a Connection_Handle for an ACL connection.
"""
def read_transmit_power_level(transport, idx, handle, levelType, to):

    cmd = struct.pack('<HHHHB', Commands.CMD_READ_TRANSMIT_POWER_LEVEL_REQ, 5, HCICommands.BT_HCI_OP_READ_TX_POWER_LEVEL, handle, levelType);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 8, to);

    if ( 8 != len(packet) ):
        raise Exception("Read Transmit Power Level command failed: Response too short (Expected %i bytes got %i bytes)" % (8, len(packet)));

    RespCmd, RespLen, status, handle, TxPowerLevel = struct.unpack('<HHBHb', packet);

    if ( RespCmd != Commands.CMD_READ_TRANSMIT_POWER_LEVEL_RSP ):
        raise Exception("Read Transmit Power Level command failed: Inappropriate command response received");

    if ( RespLen != 4 ):
        raise Exception("Read Transmit Power Level command failed: Response length field corrupted (%i)" % RespLen);

    return status, handle, TxPowerLevel;

"""
    This command is used by the Host to turn flow control on or off for data and/or voice sent in the direction from the
    Controller to the Host.
"""
def set_controller_to_host_flow_control(transport, idx, FlowEnable, to):

    cmd = struct.pack('<HHHB', Commands.CMD_SET_CONTROLLER_TO_HOST_FLOW_CONTROL_REQ, 3, HCICommands.BT_HCI_OP_SET_CTL_TO_HOST_FLOW, FlowEnable);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("Set Controller To Host Flow Control command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_SET_CONTROLLER_TO_HOST_FLOW_CONTROL_RSP ):
        raise Exception("Set Controller To Host Flow Control command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("Set Controller To Host Flow Control command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The Host_Buffer_Size command is used by the Host to notify the Controller about the maximum size of the data portion of
    HCI ACL and synchronous Data Packets sent from the Controller to the Host.
"""
def host_buffer_size(transport, idx, AclMtu, ScoMtu, AclPkts, ScoPkts, to):

    cmd = struct.pack('<HHHHBHH', Commands.CMD_HOST_BUFFER_SIZE_REQ, 9, HCICommands.BT_HCI_OP_HOST_BUFFER_SIZE, AclMtu, ScoMtu, AclPkts, ScoPkts);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("Host Buffer Size command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_HOST_BUFFER_SIZE_RSP ):
        raise Exception("Host Buffer Size command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("Host Buffer Size command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The Host_Number_Of_Completed_Packets command is used by the Host to indicate to the Controller the number of HCI Data
    Packets that have been completed for each Connection_Handle since the previous Host_Number_Of_Completed_Packets command
    was sent to the Controller.
"""
def host_number_of_completed_packets(transport, idx, NumHandles, HHandle, HCount, to):
    cmd = struct.pack('<HHHB' + 'HH' * NumHandles, Commands.CMD_HOST_NUMBER_OF_COMPLETED_PACKETS_REQ, 7 + 4 * NumHandles,
                      HCICommands.BT_HCI_OP_HOST_NUM_COMPLETED_PACKETS, NumHandles, *list(chain(*list(zip(HHandle, HCount)))));

    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("Host Number Of Completed Packets command failed: Response too short (Expected %i bytes got %i bytes)" % (4, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HH', packet);

    if ( RespCmd != Commands.CMD_HOST_NUMBER_OF_COMPLETED_PACKETS_RSP ):
        raise Exception("Host Number Of Completed Packets command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("Host Number Of Completed Packets command failed: Response length field corrupted (%i)" % RespLen);


"""
    The Set_Event_Mask_Page_2 command is used to control which events are generated by the HCI for the Host. The
    Event_Mask_Page_2 is a logical extension to the Event_Mask parameter of the Set_Event_Mask command.
"""
def set_event_mask_page_2(transport, idx, EventsPage2, to):

    cmd = struct.pack('<HHH8B', Commands.CMD_SET_EVENT_MASK_PAGE_2_REQ, 10, HCICommands.BT_HCI_OP_SET_EVENT_MASK_PAGE_2, *EventsPage2);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("Set Event Mask Page 2 command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_SET_EVENT_MASK_PAGE_2_RSP ):
        raise Exception("Set Event Mask Page 2 command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("Set Event Mask Page 2 command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The Write_LE_Host_Support command is used to set the LE Supported (Host) and Simultaneous LE and BR/EDR to Same Device
    Capable (Host) Link Manager Protocol feature bits. These Link Manager Protocol feature bits are used by a remote Host. See
    [Vol 2] Part C, Section 3.2.
"""
def write_le_host_support(transport, idx, suppLe, simul, to):

    cmd = struct.pack('<HHHBB', Commands.CMD_WRITE_LE_HOST_SUPPORT_REQ, 4, HCICommands.BT_HCI_OP_LE_WRITE_LE_HOST_SUPP, suppLe, simul);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("Write LE Host Support command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_WRITE_LE_HOST_SUPPORT_RSP ):
        raise Exception("Write LE Host Support command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("Write LE Host Support command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    This command reads the Authenticated_Payload_Timeout (authenticatedPayloadTO, see [Vol 2] Part B, Section Appendix B for
    BR/EDR connections and [Vol 6] Part B, Section 5.4 for LE connections) parameter in the Primary Controller on the
    specified Connection_Handle.
"""
def read_authenticated_payload_timeout(transport, idx, handle, to):

    cmd = struct.pack('<HHHH', Commands.CMD_READ_AUTHENTICATED_PAYLOAD_TIMEOUT_REQ, 4, HCICommands.BT_HCI_OP_READ_AUTH_PAYLOAD_TIMEOUT, handle);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 9, to);

    if ( 9 != len(packet) ):
        raise Exception("Read Authenticated Payload Timeout command failed: Response too short (Expected %i bytes got %i bytes)" % (9, len(packet)));

    RespCmd, RespLen, status, handle, AuthPayloadTimeout = struct.unpack('<HHBHH', packet);

    if ( RespCmd != Commands.CMD_READ_AUTHENTICATED_PAYLOAD_TIMEOUT_RSP ):
        raise Exception("Read Authenticated Payload Timeout command failed: Inappropriate command response received");

    if ( RespLen != 5 ):
        raise Exception("Read Authenticated Payload Timeout command failed: Response length field corrupted (%i)" % RespLen);

    return status, handle, AuthPayloadTimeout;

"""
    This command writes the Authenticated_Payload_Timeout (authenticatedPayloadTO, see [Vol 2] Part B, Section Appendix B and
    [Vol 6] Part B, Section 5.4 for the LE connection) parameter in the Primary Controller for the specified
    Connection_Handle.
"""
def write_authenticated_payload_timeout(transport, idx, handle, AuthPayloadTimeout, to):

    cmd = struct.pack('<HHHHH', Commands.CMD_WRITE_AUTHENTICATED_PAYLOAD_TIMEOUT_REQ, 6, HCICommands.BT_HCI_OP_WRITE_AUTH_PAYLOAD_TIMEOUT, handle, AuthPayloadTimeout);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 7, to);

    if ( 7 != len(packet) ):
        raise Exception("Write Authenticated Payload Timeout command failed: Response too short (Expected %i bytes got %i bytes)" % (7, len(packet)));

    RespCmd, RespLen, status, handle = struct.unpack('<HHBH', packet);

    if ( RespCmd != Commands.CMD_WRITE_AUTHENTICATED_PAYLOAD_TIMEOUT_RSP ):
        raise Exception("Write Authenticated Payload Timeout command failed: Inappropriate command response received");

    if ( RespLen != 3 ):
        raise Exception("Write Authenticated Payload Timeout command failed: Response length field corrupted (%i)" % RespLen);

    return status, handle;

"""
    This command reads the values for the version information for the local Controller. The HCI Version information defines
    the version information of the HCI layer. The LMP/PAL Version information defines the version of the LMP or PAL. The
    Manufacturer_Name information indicates the manufacturer of the local device. The HCI Revision and LMP/PAL Subversion are
    implementation dependent.
"""
def read_local_version_information(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_READ_LOCAL_VERSION_INFORMATION_REQ, 2, HCICommands.BT_HCI_OP_READ_LOCAL_VERSION_INFO);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 13, to);

    if ( 13 != len(packet) ):
        raise Exception("Read Local Version Information command failed: Response too short (Expected %i bytes got %i bytes)" % (13, len(packet)));

    RespCmd, RespLen, status, HCIVersion, HCIRevision, LMPVersion, manufacturer, LMPSubversion = struct.unpack('<HHBBHBHH', packet);

    if ( RespCmd != Commands.CMD_READ_LOCAL_VERSION_INFORMATION_RSP ):
        raise Exception("Read Local Version Information command failed: Inappropriate command response received");

    if ( RespLen != 9 ):
        raise Exception("Read Local Version Information command failed: Response length field corrupted (%i)" % RespLen);

    return status, HCIVersion, HCIRevision, LMPVersion, manufacturer, LMPSubversion;

"""
    This command reads the list of HCI commands supported for the local Controller. This command shall return the
    Supported_Commands configuration parameter. It is implied that if a command is listed as supported, the feature underlying
    that command is also supported.
"""
def read_local_supported_commands(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_READ_LOCAL_SUPPORTED_COMMANDS_REQ, 2, HCICommands.BT_HCI_OP_READ_SUPPORTED_COMMANDS);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 69, to);

    if ( 69 != len(packet) ):
        raise Exception("Read Local Supported Commands command failed: Response too short (Expected %i bytes got %i bytes)" % (69, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet[:5]);
    commands = struct.unpack('<64B', packet[5:]);

    if ( RespCmd != Commands.CMD_READ_LOCAL_SUPPORTED_COMMANDS_RSP ):
        raise Exception("Read Local Supported Commands command failed: Inappropriate command response received");

    if ( RespLen != 65 ):
        raise Exception("Read Local Supported Commands command failed: Response length field corrupted (%i)" % RespLen);

    return status, commands;

"""
    This command requests a list of the supported features for the local BR/EDR Controller. This command will return a list of
    the LMP features. For details see [Vol 2] Part C, Link Manager Protocol Specification.
"""
def read_local_supported_features(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_READ_LOCAL_SUPPORTED_FEATURES_REQ, 2, HCICommands.BT_HCI_OP_READ_LOCAL_FEATURES);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 13, to);

    if ( 13 != len(packet) ):
        raise Exception("Read Local Supported Features command failed: Response too short (Expected %i bytes got %i bytes)" % (13, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet[:5]);
    features = struct.unpack('<8B', packet[5:]);

    if ( RespCmd != Commands.CMD_READ_LOCAL_SUPPORTED_FEATURES_RSP ):
        raise Exception("Read Local Supported Features command failed: Inappropriate command response received");

    if ( RespLen != 9 ):
        raise Exception("Read Local Supported Features command failed: Response length field corrupted (%i)" % RespLen);

    return status, features;

"""
    The Read_Buffer_Size command is used to read the maximum size of the data portion of HCI ACL and synchronous Data Packets
    sent from the Host to the Controller. The Host will segment the data to be transmitted from the Host to the Controller
    according to these sizes, so that the HCI Data Packets will contain data with up to these sizes. The Read_Buffer_Size
    command also returns the total number of HCI ACL and synchronous Data Packets that can be stored in the data buffers of
    the Controller. The Read_Buffer_Size command must be issued by the Host before it sends any data to the Controller.
"""
def read_buffer_size(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_READ_BUFFER_SIZE_REQ, 2, HCICommands.BT_HCI_OP_READ_BUFFER_SIZE);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);
    assert 5 == len(packet), f"Received invalid length packet {len(packet)}"

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_READ_BUFFER_SIZE_RSP ):
        raise Exception("Read Buffer Size command failed: Inappropriate command response received");

    if RespLen == 1:
        # Unsupported command
        return status

    assert RespLen != 8, f"Response length field corrupted ({RespLen})"

    packet = transport.recv(idx, 7, to)
    assert 7 == len(packet), f"Received invalid length packet {len(packet)}"

    AclMaxLen, ScoMaxLen, AclMaxNum, ScoMaxNum = struct.unpack('<HBHH', packet);

    return status, AclMaxLen, ScoMaxLen, AclMaxNum, ScoMaxNum

"""
    On an LE Controller, this command shall read the Public Device Address as defined in [Vol 6] Part B, Section 1.3. If this
    Controller does not have a Public Device Address, the value 0x000000000000 shall be returned. On a BR/EDR/LE Controller,
    the public address shall be the same as the BD_ADDR.
"""
def read_bd_addr(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_READ_BD_ADDR_REQ, 2, HCICommands.BT_HCI_OP_READ_BD_ADDR);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 11, to);

    if ( 11 != len(packet) ):
        raise Exception("Read BD_ADDR command failed: Response too short (Expected %i bytes got %i bytes)" % (11, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet[:5]);
    BdaddrVal = struct.unpack('<6B', packet[5:]);

    if ( RespCmd != Commands.CMD_READ_BD_ADDR_RSP ):
        raise Exception("Read BD_ADDR command failed: Inappropriate command response received");

    if ( RespLen != 7 ):
        raise Exception("Read BD_ADDR command failed: Response length field corrupted (%i)" % RespLen);

    return status, BdaddrVal;

"""
    This command reads the Received Signal Strength Indication (RSSI) value from a Controller.
"""
def read_rssi(transport, idx, handle, to):

    cmd = struct.pack('<HHHH', Commands.CMD_READ_RSSI_REQ, 4, HCICommands.BT_HCI_OP_READ_RSSI, handle);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 8, to);

    if ( 8 != len(packet) ):
        raise Exception("Read RSSI command failed: Response too short (Expected %i bytes got %i bytes)" % (8, len(packet)));

    RespCmd, RespLen, status, handle, rssi = struct.unpack('<HHBHb', packet);

    if ( RespCmd != Commands.CMD_READ_RSSI_RSP ):
        raise Exception("Read RSSI command failed: Inappropriate command response received");

    if ( RespLen != 4 ):
        raise Exception("Read RSSI command failed: Response length field corrupted (%i)" % RespLen);

    return status, handle, rssi;

"""
    The LE_Set_Event_Mask command is used to control which LE events are generated by the HCI for the Host.
"""
def le_set_event_mask(transport, idx, events, to):

    cmd = struct.pack('<HHH8B', Commands.CMD_LE_SET_EVENT_MASK_REQ, 10, HCICommands.BT_HCI_OP_LE_SET_EVENT_MASK, *events);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Event Mask command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_EVENT_MASK_RSP ):
        raise Exception("LE Set Event Mask command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Event Mask command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Read_Buffer_Size command is used to read the maximum size of the data portion of HCI LE ACL Data Packets sent from
    the Host to the Controller. The Host will segment the data transmitted to the Controller according to these values, so
    that the HCI Data Packets will contain data with up to this size. The LE_Read_Buffer_Size command also returns the total
    number of HCI LE ACL Data Packets that can be stored in the data buffers of the Controller. The LE_Read_Buffer_Size
    command must be issued by the Host before it sends any data to an LE Controller (see Section 4.1.1).
"""
def le_read_buffer_size(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_READ_BUFFER_SIZE_REQ, 2, HCICommands.BT_HCI_OP_LE_READ_BUFFER_SIZE);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 8, to);

    if ( 8 != len(packet) ):
        raise Exception("LE Read Buffer Size command failed: Response too short (Expected %i bytes got %i bytes)" % (8, len(packet)));

    RespCmd, RespLen, status, LeMaxLen, LeMaxNum = struct.unpack('<HHBHB', packet);

    if ( RespCmd != Commands.CMD_LE_READ_BUFFER_SIZE_RSP ):
        raise Exception("LE Read Buffer Size command failed: Inappropriate command response received");

    if ( RespLen != 4 ):
        raise Exception("LE Read Buffer Size command failed: Response length field corrupted (%i)" % RespLen);

    return status, LeMaxLen, LeMaxNum;

"""
    The LE_Read_Buffer_Size command is used to read the maximum size of the data portion of HCI LE ACL Data Packets sent from
    the Host to the Controller. The Host will segment the data transmitted to the Controller according to these values, so
    that the HCI Data Packets will contain data with up to this size. The LE_Read_Buffer_Size command also returns the total
    number of HCI LE ACL Data Packets that can be stored in the data buffers of the Controller. The LE_Read_Buffer_Size
    command must be issued by the Host before it sends any data to an LE Controller (see Section 4.1.1).
"""
def le_read_buffer_size_v2(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_READ_BUFFER_SIZE_V2_REQ, 2, HCICommands.BT_HCI_OP_LE_READ_BUFFER_SIZE_V2);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 11, to);

    if ( 11 != len(packet) ):
        raise Exception("LE Read Buffer Size V2 command failed: Response too short (Expected %i bytes got %i bytes)" % (11, len(packet)));

    RespCmd, RespLen, status, LeMaxLen, LeMaxNum, IsoMaxLen, IsoMaxNum = struct.unpack('<HHBHBHB', packet);

    if ( RespCmd != Commands.CMD_LE_READ_BUFFER_SIZE_V2_RSP ):
        raise Exception("LE Read Buffer Size V2 command failed: Inappropriate command response received");

    if ( RespLen != 7 ):
        raise Exception("LE Read Buffer Size V2 command failed: Response length field corrupted (%i)" % RespLen);

    return status, LeMaxLen, LeMaxNum, IsoMaxLen, IsoMaxNum;

"""
    This command requests the list of the supported LE features for the Controller.
"""
def le_read_local_supported_features(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_READ_LOCAL_SUPPORTED_FEATURES_REQ, 2, HCICommands.BT_HCI_OP_LE_READ_LOCAL_FEATURES);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 13, to);

    if ( 13 != len(packet) ):
        raise Exception("LE Read Local Supported Features command failed: Response too short (Expected %i bytes got %i bytes)" % (13, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet[:5]);
    features = struct.unpack('<8B', packet[5:]);

    if ( RespCmd != Commands.CMD_LE_READ_LOCAL_SUPPORTED_FEATURES_RSP ):
        raise Exception("LE Read Local Supported Features command failed: Inappropriate command response received");

    if ( RespLen != 9 ):
        raise Exception("LE Read Local Supported Features command failed: Response length field corrupted (%i)" % RespLen);

    return status, features;

"""
    The LE_Set_Random_Address command is used by the Host to set the LE Random Device Address in the Controller (see [Vol 6]
    Part B, Section 1.3).
"""
def le_set_random_address(transport, idx, BdaddrVal, to):

    cmd = struct.pack('<HHH6B', Commands.CMD_LE_SET_RANDOM_ADDRESS_REQ, 8, HCICommands.BT_HCI_OP_LE_SET_RANDOM_ADDRESS, *BdaddrVal);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Random Address command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_RANDOM_ADDRESS_RSP ):
        raise Exception("LE Set Random Address command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Random Address command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Set_Advertising_Parameters command is used by the Host to set the advertising parameters.
"""
def le_set_advertising_parameters(transport, idx, MinInterval, MaxInterval, paramType, OwnAddrType, DirectAddrType, AVal, ChannelMap, FilterPolicy, to):

    cmd = struct.pack('<HHHHHBBB6B', Commands.CMD_LE_SET_ADVERTISING_PARAMETERS_REQ, 17, HCICommands.BT_HCI_OP_LE_SET_ADV_PARAM, MinInterval, MaxInterval, paramType, OwnAddrType, DirectAddrType, *AVal);
    cmd += struct.pack('<BB', ChannelMap, FilterPolicy);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Advertising Parameters command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_ADVERTISING_PARAMETERS_RSP ):
        raise Exception("LE Set Advertising Parameters command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Advertising Parameters command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Read_Advertising_Channel_TX_Power command is used by the Host to read the transmit power level used for LE
    advertising channel packets.
"""
def le_read_advertising_channel_tx_power(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_READ_ADVERTISING_CHANNEL_TX_POWER_REQ, 2, HCICommands.BT_HCI_OP_LE_READ_ADV_CHAN_TX_POWER);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 6, to);

    if ( 6 != len(packet) ):
        raise Exception("LE Read Advertising Channel TX Power command failed: Response too short (Expected %i bytes got %i bytes)" % (6, len(packet)));

    RespCmd, RespLen, status, TxPowerLevel = struct.unpack('<HHBb', packet);

    if ( RespCmd != Commands.CMD_LE_READ_ADVERTISING_CHANNEL_TX_POWER_RSP ):
        raise Exception("LE Read Advertising Channel TX Power command failed: Inappropriate command response received");

    if ( RespLen != 2 ):
        raise Exception("LE Read Advertising Channel TX Power command failed: Response length field corrupted (%i)" % RespLen);

    return status, TxPowerLevel;

"""
    The LE_Set_Advertising_Data command is used to set the data used in advertising packets that have a data field.
"""
def le_set_advertising_data(transport, idx, dataLen, data, to):

    cmd = struct.pack('<HHHB31B', Commands.CMD_LE_SET_ADVERTISING_DATA_REQ, 34, HCICommands.BT_HCI_OP_LE_SET_ADV_DATA, dataLen, *data);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Advertising Data command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_ADVERTISING_DATA_RSP ):
        raise Exception("LE Set Advertising Data command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Advertising Data command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    This command is used to provide data used in Scanning Packets that have a data field.
"""
def le_set_scan_response_data(transport, idx, dataLen, data, to):

    cmd = struct.pack('<HHHB31B', Commands.CMD_LE_SET_SCAN_RESPONSE_DATA_REQ, 34, HCICommands.BT_HCI_OP_LE_SET_SCAN_RSP_DATA, dataLen, *data);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Scan Response Data command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_SCAN_RESPONSE_DATA_RSP ):
        raise Exception("LE Set Scan Response Data command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Scan Response Data command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Set_Advertising_Enable command is used to request the Controller to start or stop advertising. The Controller
    manages the timing of advertisements as per the advertising parameters given in the LE_Set_Advertising_Parameters command.
"""
def le_set_advertising_enable(transport, idx, enable, to):

    cmd = struct.pack('<HHHB', Commands.CMD_LE_SET_ADVERTISING_ENABLE_REQ, 3, HCICommands.BT_HCI_OP_LE_SET_ADV_ENABLE, enable);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Advertising Enable command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_ADVERTISING_ENABLE_RSP ):
        raise Exception("LE Set Advertising Enable command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Advertising Enable command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Set_Scan_Parameters command is used to set the scan parameters. The LE_Scan_Type parameter controls the type of
    scan to perform.
"""
def le_set_scan_parameters(transport, idx, ScanType, interval, window, AddrType, FilterPolicy, to):

    cmd = struct.pack('<HHHBHHBB', Commands.CMD_LE_SET_SCAN_PARAMETERS_REQ, 9, HCICommands.BT_HCI_OP_LE_SET_SCAN_PARAM, ScanType, interval, window, AddrType, FilterPolicy);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Scan Parameters command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_SCAN_PARAMETERS_RSP ):
        raise Exception("LE Set Scan Parameters command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Scan Parameters command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Set_Scan_Enable command is used to start scanning. Scanning is used to discover advertising devices nearby.
"""
def le_set_scan_enable(transport, idx, enable, FilterDup, to):

    cmd = struct.pack('<HHHBB', Commands.CMD_LE_SET_SCAN_ENABLE_REQ, 4, HCICommands.BT_HCI_OP_LE_SET_SCAN_ENABLE, enable, FilterDup);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Scan Enable command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_SCAN_ENABLE_RSP ):
        raise Exception("LE Set Scan Enable command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Scan Enable command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Create_Connection command is used to create a Link Layer connection to a connectable advertiser.
"""
def le_create_connection(transport, idx, ScanInterval, ScanWindow, FilterPolicy, PeerAddrType, AVal, OwnAddrType, ConnIntervalMin, ConnIntervalMax, ConnLatency, SupervisionTimeout, MinCeLen, MaxCeLen, to):

    cmd = struct.pack('<HHHHHBB6B', Commands.CMD_LE_CREATE_CONNECTION_REQ, 27, HCICommands.BT_HCI_OP_LE_CREATE_CONN, ScanInterval, ScanWindow, FilterPolicy, PeerAddrType, *AVal);
    cmd += struct.pack('<BHHHHHH', OwnAddrType, ConnIntervalMin, ConnIntervalMax, ConnLatency, SupervisionTimeout, MinCeLen, MaxCeLen);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Create Connection command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_CREATE_CONNECTION_RSP ):
        raise Exception("LE Create Connection command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Create Connection command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Create_Connection_Cancel command is used to cancel the LE_Create_Connection or LE_Extended_Create_Connection
    commands. This command shall only be issued after the LE_Create_Connection or LE_Extended_Create_Connection commands have
    been issued, a Command Status event has been received for the LE Create Connection or LE_Extended_Create_Connection
    commands, and before the LE Connection Complete or LE Enhanced Connection Complete events.
"""
def le_create_connection_cancel(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_CREATE_CONNECTION_CANCEL_REQ, 2, HCICommands.BT_HCI_OP_LE_CREATE_CONN_CANCEL);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Create Connection Cancel command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_CREATE_CONNECTION_CANCEL_RSP ):
        raise Exception("LE Create Connection Cancel command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Create Connection Cancel command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Read_Filter_Accept_List_Size command is used to read the total number of Filter Accept List entries that can be stored in the
    Controller.
"""
def le_read_filter_accept_list_size(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_READ_FILTER_ACCEPT_LIST_SIZE_REQ, 2, HCICommands.BT_HCI_OP_LE_READ_FAL_SIZE);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 6, to);

    if ( 6 != len(packet) ):
        raise Exception("LE Read Filter Accept List Size command failed: Response too short (Expected %i bytes got %i bytes)" % (6, len(packet)));

    RespCmd, RespLen, status, FalSize = struct.unpack('<HHBB', packet);

    if ( RespCmd != Commands.CMD_LE_READ_FILTER_ACCEPT_LIST_SIZE_RSP ):
        raise Exception("LE Read Filter Accept List Size command failed: Inappropriate command response received");

    if ( RespLen != 2 ):
        raise Exception("LE Read Filter Accept List Size command failed: Response length field corrupted (%i)" % RespLen);

    return status, FalSize;

"""
    The LE_Clear_Filter_Accept_List command is used to clear the Filter Accept List stored in the Controller.
"""
def le_clear_filter_accept_list(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_CLEAR_FILTER_ACCEPT_LIST_REQ, 2, HCICommands.BT_HCI_OP_LE_CLEAR_FAL);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Clear Filter Accept List command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_CLEAR_FILTER_ACCEPT_LIST_RSP ):
        raise Exception("LE Clear Filter Accept List command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Clear Filter Accept List command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Add_Device_To_Filter_Accept_List command is used to add a single device to the Filter Accept List stored in the Controller.
"""
def le_add_device_to_filter_accept_list(transport, idx, AddrType, AVal, to):

    cmd = struct.pack('<HHHB6B', Commands.CMD_LE_ADD_DEVICE_TO_FILTER_ACCEPT_LIST_REQ, 9, HCICommands.BT_HCI_OP_LE_ADD_DEV_TO_FAL, AddrType, *AVal);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Add Device To Filter Accept List command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_ADD_DEVICE_TO_FILTER_ACCEPT_LIST_RSP ):
        raise Exception("LE Add Device To Filter Accept List command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Add Device To Filter Accept List command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Remove_Device_From_Filter_Accept_List command is used to remove a single device from the Filter Accept List stored in the
    Controller.
"""
def le_remove_device_from_filter_accept_list(transport, idx, AddrType, AVal, to):

    cmd = struct.pack('<HHHB6B', Commands.CMD_LE_REMOVE_DEVICE_FROM_FILTER_ACCEPT_LIST_REQ, 9, HCICommands.BT_HCI_OP_LE_REM_DEV_FROM_FAL, AddrType, *AVal);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Remove Device From Filter Accept List command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_REMOVE_DEVICE_FROM_FILTER_ACCEPT_LIST_RSP ):
        raise Exception("LE Remove Device From Filter Accept List command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Remove Device From Filter Accept List command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Connection_Update command is used to change the Link Layer connection parameters of a connection. This command may
    be issued on both the central and peripheral.
"""
def le_connection_update(transport, idx, handle, ConnIntervalMin, ConnIntervalMax, ConnLatency, SupervisionTimeout, MinCeLen, MaxCeLen, to):

    cmd = struct.pack('<HHHHHHHHHH', Commands.CMD_LE_CONNECTION_UPDATE_REQ, 16, HCICommands.BT_HCI_OP_LE_CONN_UPDATE, handle, ConnIntervalMin, ConnIntervalMax, ConnLatency, SupervisionTimeout, MinCeLen, MaxCeLen);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Connection Update command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_CONNECTION_UPDATE_RSP ):
        raise Exception("LE Connection Update command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Connection Update command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Set_Host_Channel_Classification command allows the Host to specify a channel classification for data channels based
    on its \93local information\94. This classification persists until overwritten with a subsequent
    LE_Set_Host_Channel_Classification command or until the Controller is reset using the Reset command (see [Vol 6] Part B,
    Section 4.5.8.1).
"""
def le_set_host_channel_classification(transport, idx, ChMap, to):

    cmd = struct.pack('<HHH5B', Commands.CMD_LE_SET_HOST_CHANNEL_CLASSIFICATION_REQ, 7, HCICommands.BT_HCI_OP_LE_SET_HOST_CHAN_CLASSIF, *ChMap);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Host Channel Classification command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_HOST_CHANNEL_CLASSIFICATION_RSP ):
        raise Exception("LE Set Host Channel Classification command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Host Channel Classification command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Read_Channel_Map command returns the current Channel_Map for the specified Connection_Handle.
"""
def le_read_channel_map(transport, idx, handle, to):

    cmd = struct.pack('<HHHH', Commands.CMD_LE_READ_CHANNEL_MAP_REQ, 4, HCICommands.BT_HCI_OP_LE_READ_CHAN_MAP, handle);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 12, to);

    if ( 12 != len(packet) ):
        raise Exception("LE Read Channel Map command failed: Response too short (Expected %i bytes got %i bytes)" % (12, len(packet)));

    RespCmd, RespLen, status, handle = struct.unpack('<HHBH', packet[:7]);
    ChMap = struct.unpack('<5B', packet[7:]);

    if ( RespCmd != Commands.CMD_LE_READ_CHANNEL_MAP_RSP ):
        raise Exception("LE Read Channel Map command failed: Inappropriate command response received");

    if ( RespLen != 8 ):
        raise Exception("LE Read Channel Map command failed: Response length field corrupted (%i)" % RespLen);

    return status, handle, int.from_bytes(ChMap, 'little', signed=False)

"""
    This command requests, from the remote device identified by the connection handle, the features used on the connection and
    the features supported by the remote device. For details see [Vol 6] Part B, Section 4.6.
"""
def le_read_remote_features(transport, idx, handle, to):

    cmd = struct.pack('<HHHH', Commands.CMD_LE_READ_REMOTE_FEATURES_REQ, 4, HCICommands.BT_HCI_OP_LE_READ_REMOTE_FEATURES, handle);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Read Remote Features command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_READ_REMOTE_FEATURES_RSP ):
        raise Exception("LE Read Remote Features command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Read Remote Features command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Encrypt command is used to request the Controller to encrypt the Plaintext_Data in the command using the Key given
    in the command and returns the Encrypted_Data to the Host.
"""
def le_encrypt(transport, idx, key, plaintext, to):
    def pad_or_slice(L, n):
        L = list(L)
        if len(L) < n:
            return L + ([0] * (n - len(L)))
        else:
            return L[:n]

    key = pad_or_slice(key, 16)
    plaintext = pad_or_slice(plaintext, 16)

    cmd = struct.pack('<HHH16B', Commands.CMD_LE_ENCRYPT_REQ, 34, HCICommands.BT_HCI_OP_LE_ENCRYPT, *key);
    cmd += struct.pack('<16B', *plaintext);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 21, to);

    if ( 21 != len(packet) ):
        raise Exception("LE Encrypt command failed: Response too short (Expected %i bytes got %i bytes)" % (21, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet[:5]);
    EncData = struct.unpack('<16B', packet[5:]);

    if ( RespCmd != Commands.CMD_LE_ENCRYPT_RSP ):
        raise Exception("LE Encrypt command failed: Inappropriate command response received");

    if ( RespLen != 17 ):
        raise Exception("LE Encrypt command failed: Response length field corrupted (%i)" % RespLen);

    return status, EncData;

"""
    The LE_Rand command is used to request the Controller to generate 8 octets of random data to be sent to the Host. The
    Random_Number shall be generated according to [Vol 2] Part H, Section 2 if the LE Feature (LE Encryption) is supported.
"""
def le_rand(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_RAND_REQ, 2, HCICommands.BT_HCI_OP_LE_RAND);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 13, to);

    if ( 13 != len(packet) ):
        raise Exception("LE Rand command failed: Response too short (Expected %i bytes got %i bytes)" % (13, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet[:5]);
    rand = struct.unpack('<8B', packet[5:]);

    if ( RespCmd != Commands.CMD_LE_RAND_RSP ):
        raise Exception("LE Rand command failed: Inappropriate command response received");

    if ( RespLen != 9 ):
        raise Exception("LE Rand command failed: Response length field corrupted (%i)" % RespLen);

    return status, rand;


def le_start_encryption(transport, idx, handle, rand, ediv, ltk, to):
    """The LE_Start_Encryption command is used to authenticate the given encryption key associated with the remote
    device specified by the Connection_Handle, and once authenticated will encrypt the connection.
    :param transport: bearer to be used
    :param idx: device index
    :param handle: connection handle
    :param rand: random number
    :param ediv: encrypted diversifier
    :param ltk: 16 byte long term key array
    :param to: Receiver timeout
    :return: status
    """
    edtt_send_cmd(transport, idx, Commands.CMD_LE_START_ENCRYPTION_REQ, 'HHQH16B',
                  (HCICommands.BT_HCI_OP_LE_START_ENCRYPTION, handle, rand, ediv, *ltk))
    return edtt_wait_cmd_cmpl(transport, idx, Commands.CMD_LE_START_ENCRYPTION_RSP, 'B', to)[0]


"""
    The LE_Long_Term_Key_Request_Reply command is used to reply to an LE Long Term Key Request event from the Controller, and
    specifies the Long_Term_Key parameter that shall be used for this Connection_Handle. The Long_Term_Key is used as defined
    in [Vol 6] Part B, Section 5.1.3.
"""
def le_long_term_key_request_reply(transport, idx, handle, ltk, to):

    cmd = struct.pack('<HHHH16B', Commands.CMD_LE_LONG_TERM_KEY_REQUEST_REPLY_REQ, 20, HCICommands.BT_HCI_OP_LE_LTK_REQ_REPLY, handle, *ltk);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 7, to);

    if ( 7 != len(packet) ):
        raise Exception("LE Long Term Key Request Reply command failed: Response too short (Expected %i bytes got %i bytes)" % (7, len(packet)));

    RespCmd, RespLen, status, handle = struct.unpack('<HHBH', packet);

    if ( RespCmd != Commands.CMD_LE_LONG_TERM_KEY_REQUEST_REPLY_RSP ):
        raise Exception("LE Long Term Key Request Reply command failed: Inappropriate command response received");

    if ( RespLen != 3 ):
        raise Exception("LE Long Term Key Request Reply command failed: Response length field corrupted (%i)" % RespLen);

    return status, handle;

"""
    The LE_Long_Term_Key_Request_Negative_Reply command is used to reply to an LE Long Term Key Request event from the
    Controller if the Host cannot provide a Long Term Key for this Connection_Handle.
"""
def le_long_term_key_request_negative_reply(transport, idx, handle, to):

    cmd = struct.pack('<HHHH', Commands.CMD_LE_LONG_TERM_KEY_REQUEST_NEGATIVE_REPLY_REQ, 4, HCICommands.BT_HCI_OP_LE_LTK_REQ_NEG_REPLY, handle);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 7, to);

    if ( 7 != len(packet) ):
        raise Exception("LE Long Term Key Request Negative Reply command failed: Response too short (Expected %i bytes got %i bytes)" % (7, len(packet)));

    RespCmd, RespLen, status, handle = struct.unpack('<HHBH', packet);

    if ( RespCmd != Commands.CMD_LE_LONG_TERM_KEY_REQUEST_NEGATIVE_REPLY_RSP ):
        raise Exception("LE Long Term Key Request Negative Reply command failed: Inappropriate command response received");

    if ( RespLen != 3 ):
        raise Exception("LE Long Term Key Request Negative Reply command failed: Response length field corrupted (%i)" % RespLen);

    return status, handle;

"""
    The LE_Read_Supported_States command reads the states and state combinations that the link layer supports. See [Vol 6]
    Part B, Section 1.1.1. LE_States is an 8-octet bit field. If a bit is set to 1 then this state or state combination is
    supported by the Controller. Multiple bits in LE_States may be set to 1 to indicate support for multiple state and state
    combinations.
"""
def le_read_supported_states(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_READ_SUPPORTED_STATES_REQ, 2, HCICommands.BT_HCI_OP_LE_READ_SUPP_STATES);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 13, to);

    if ( 13 != len(packet) ):
        raise Exception("LE Read Supported States command failed: Response too short (Expected %i bytes got %i bytes)" % (13, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet[:5]);
    LeStates = struct.unpack('<8B', packet[5:]);

    if ( RespCmd != Commands.CMD_LE_READ_SUPPORTED_STATES_RSP ):
        raise Exception("LE Read Supported States command failed: Inappropriate command response received");

    if ( RespLen != 9 ):
        raise Exception("LE Read Supported States command failed: Response length field corrupted (%i)" % RespLen);

    return status, LeStates;

"""
    This command is used to start a test where the DUT receives test reference packets at a fixed interval. The tester
    generates the test reference packets.
"""
def le_receiver_test(transport, idx, RxCh, to):

    cmd = struct.pack('<HHHB', Commands.CMD_LE_RECEIVER_TEST_REQ, 3, HCICommands.BT_HCI_OP_LE_RX_TEST, RxCh);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Receiver Test command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_RECEIVER_TEST_RSP ):
        raise Exception("LE Receiver Test command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Receiver Test command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    This command is used to start a test where the DUT generates test reference packets at a fixed interval. The Controller
    shall transmit at maximum power.
"""
def le_transmitter_test(transport, idx, TxCh, TestDataLen, PktPayload, to):

    cmd = struct.pack('<HHHBBB', Commands.CMD_LE_TRANSMITTER_TEST_REQ, 5, HCICommands.BT_HCI_OP_LE_TX_TEST, TxCh, TestDataLen, PktPayload);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Transmitter Test command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_TRANSMITTER_TEST_RSP ):
        raise Exception("LE Transmitter Test command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Transmitter Test command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    This command is used to stop any test which is in progress. The Number_Of_Packets for a transmitter test shall be reported
    as 0x0000. The Number_Of_Packets is an unsigned number and contains the number of received packets.
"""
def le_test_end(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_TEST_END_REQ, 2, HCICommands.BT_HCI_OP_LE_TEST_END);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 7, to);

    if ( 7 != len(packet) ):
        raise Exception("LE Test End command failed: Response too short (Expected %i bytes got %i bytes)" % (7, len(packet)));

    RespCmd, RespLen, status, RxPktCount = struct.unpack('<HHBH', packet);

    if ( RespCmd != Commands.CMD_LE_TEST_END_RSP ):
        raise Exception("LE Test End command failed: Inappropriate command response received");

    if ( RespLen != 3 ):
        raise Exception("LE Test End command failed: Response length field corrupted (%i)" % RespLen);

    return status, RxPktCount;

"""
    Both the central Host and the peripheral Host use this command to reply to the HCI LE Remote Connection Parameter Request event.
    This indicates that the Host has accepted the remote device\92s request to change connection parameters.
"""
def le_remote_connection_parameter_request_reply(transport, idx, handle, IntervalMin, IntervalMax, latency, timeout, MinCeLen, MaxCeLen, to):

    cmd = struct.pack('<HHHHHHHHHH', Commands.CMD_LE_REMOTE_CONNECTION_PARAMETER_REQUEST_REPLY_REQ, 16, HCICommands.BT_HCI_OP_LE_CONN_PARAM_REQ_REPLY, handle, IntervalMin, IntervalMax, latency, timeout, MinCeLen, MaxCeLen);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 7, to);

    if ( 7 != len(packet) ):
        raise Exception("LE Remote Connection Parameter Request Reply command failed: Response too short (Expected %i bytes got %i bytes)" % (7, len(packet)));

    RespCmd, RespLen, status, handle = struct.unpack('<HHBH', packet);

    if ( RespCmd != Commands.CMD_LE_REMOTE_CONNECTION_PARAMETER_REQUEST_REPLY_RSP ):
        raise Exception("LE Remote Connection Parameter Request Reply command failed: Inappropriate command response received");

    if ( RespLen != 3 ):
        raise Exception("LE Remote Connection Parameter Request Reply command failed: Response length field corrupted (%i)" % RespLen);

    return status, handle;

"""
    Both the central Host and the peripheral Host use this command to reply to the HCI LE Remote Connection Parameter Request event.
    This indicates that the Host has rejected the remote device\92s request to change connection parameters. The reason for the
    rejection is given in the Reason parameter.
"""
def le_remote_connection_parameter_request_negative_reply(transport, idx, handle, reason, to):

    cmd = struct.pack('<HHHHB', Commands.CMD_LE_REMOTE_CONNECTION_PARAMETER_REQUEST_NEGATIVE_REPLY_REQ, 5, HCICommands.BT_HCI_OP_LE_CONN_PARAM_REQ_NEG_REPLY, handle, reason);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 7, to);

    if ( 7 != len(packet) ):
        raise Exception("LE Remote Connection Parameter Request Negative Reply command failed: Response too short (Expected %i bytes got %i bytes)" % (7, len(packet)));

    RespCmd, RespLen, status, handle = struct.unpack('<HHBH', packet);

    if ( RespCmd != Commands.CMD_LE_REMOTE_CONNECTION_PARAMETER_REQUEST_NEGATIVE_REPLY_RSP ):
        raise Exception("LE Remote Connection Parameter Request Negative Reply command failed: Inappropriate command response received");

    if ( RespLen != 3 ):
        raise Exception("LE Remote Connection Parameter Request Negative Reply command failed: Response length field corrupted (%i)" % RespLen);

    return status, handle;

"""
    The LE_Set_Data_Length command allows the Host to suggest maximum transmission packet size and maximum packet transmission
    time (connMaxTxOctets and connMaxTxTime - see [Vol 6] Part B, Section 4.5.10) to be used for a given connection. The
    Controller may use smaller or larger values based on local information.
"""
def le_set_data_length(transport, idx, handle, TxOctets, TxTime, to):

    cmd = struct.pack('<HHHHHH', Commands.CMD_LE_SET_DATA_LENGTH_REQ, 8, HCICommands.BT_HCI_OP_LE_SET_DATA_LEN, handle, TxOctets, TxTime);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 7, to);

    if ( 7 != len(packet) ):
        raise Exception("LE Set Data Length command failed: Response too short (Expected %i bytes got %i bytes)" % (7, len(packet)));

    RespCmd, RespLen, status, handle = struct.unpack('<HHBH', packet);

    if ( RespCmd != Commands.CMD_LE_SET_DATA_LENGTH_RSP ):
        raise Exception("LE Set Data Length command failed: Inappropriate command response received");

    if ( RespLen != 3 ):
        raise Exception("LE Set Data Length command failed: Response length field corrupted (%i)" % RespLen);

    return status, handle;

"""
    The LE_Read_Suggested_Default_Data_Length command allows the Host to read the Host's suggested values
    (SuggestedMaxTxOctets and SuggestedMaxTxTime) for the Controller's maximum transmitted number of payload octets and
    maximum packet transmission time to be used for new connections (see [Vol 6] Part B, Section 4.5.10).
"""
def le_read_suggested_default_data_length(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_READ_SUGGESTED_DEFAULT_DATA_LENGTH_REQ, 2, HCICommands.BT_HCI_OP_LE_READ_DEFAULT_DATA_LEN);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 9, to);

    if ( 9 != len(packet) ):
        raise Exception("LE Read Suggested Default Data Length command failed: Response too short (Expected %i bytes got %i bytes)" % (9, len(packet)));

    RespCmd, RespLen, status, MaxTxOctets, MaxTxTime = struct.unpack('<HHBHH', packet);

    if ( RespCmd != Commands.CMD_LE_READ_SUGGESTED_DEFAULT_DATA_LENGTH_RSP ):
        raise Exception("LE Read Suggested Default Data Length command failed: Inappropriate command response received");

    if ( RespLen != 5 ):
        raise Exception("LE Read Suggested Default Data Length command failed: Response length field corrupted (%i)" % RespLen);

    return status, MaxTxOctets, MaxTxTime;

"""
    The LE_Write_Suggested_Default_Data_Length command allows the Host to specify its suggested values for the Controller's
    maximum transmission number of payload octets and maximum packet transmission time to be used for new connections. The
    Controller may use smaller or larger values for connInitialMaxTxOctets and connInitialMaxTxTime based on local information
    (see [Vol 6] Part B, Section 4.5.10).
"""
def le_write_suggested_default_data_length(transport, idx, MaxTxOctets, MaxTxTime, to):

    cmd = struct.pack('<HHHHH', Commands.CMD_LE_WRITE_SUGGESTED_DEFAULT_DATA_LENGTH_REQ, 6, HCICommands.BT_HCI_OP_LE_WRITE_DEFAULT_DATA_LEN, MaxTxOctets, MaxTxTime);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Write Suggested Default Data Length command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_WRITE_SUGGESTED_DEFAULT_DATA_LENGTH_RSP ):
        raise Exception("LE Write Suggested Default Data Length command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Write Suggested Default Data Length command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Read_Local_P-256_Public_Key command is used to return the local P-256 public key from the Controller. The
    Controller shall generate a new P-256 public/private key pair upon receipt of this command. The keys returned via this
    command shall not be used when Secure Connections is used over the BR/EDR transport.
"""
def le_read_local_p_256_public_key_command(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_READ_LOCAL_P_256_PUBLIC_KEY_COMMAND_REQ, 2, HCICommands.BT_HCI_OP_LE_P256_PUBLIC_KEY);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Read Local P-256 Public Key Command command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_READ_LOCAL_P_256_PUBLIC_KEY_COMMAND_RSP ):
        raise Exception("LE Read Local P-256 Public Key Command command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Read Local P-256 Public Key Command command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Generate_DHKey command is used to initiate generation of a Diffie-Hellman key in the Controller for use over the LE
    transport. This command takes the remote P-256 public key as input. The Diffie-Hellman key generation uses the private key
    generated by LE_Read_Local_P256_Public_Key command. The Diffie-Hellman key returned via this command shall not be
    generated using any keys used for Secure Connections over the BR/EDR transport.
"""
def le_generate_dhkey_command(transport, idx, key, to):

    cmd = struct.pack('<HHH64B', Commands.CMD_LE_GENERATE_DHKEY_COMMAND_REQ, 66, HCICommands.BT_HCI_OP_LE_GENERATE_DHKEY, *key);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Generate DHKey Command command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_GENERATE_DHKEY_COMMAND_RSP ):
        raise Exception("LE Generate DHKey Command command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Generate DHKey Command command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Add_Device_To_Resolving_List command is used to add one device to the list of address translations used to resolve
    Resolvable Private Addresses in the Controller.
"""
def le_add_device_to_resolving_list(transport, idx, PeerIdAddrType, AVal, PeerIrk, LocalIrk, to):

    cmd = struct.pack('<HHHB6B', Commands.CMD_LE_ADD_DEVICE_TO_RESOLVING_LIST_REQ, 41, HCICommands.BT_HCI_OP_LE_ADD_DEV_TO_RL, PeerIdAddrType, *AVal);
    cmd += struct.pack('<16B', *PeerIrk);
    cmd += struct.pack('<16B', *LocalIrk);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Add Device To Resolving List command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_ADD_DEVICE_TO_RESOLVING_LIST_RSP ):
        raise Exception("LE Add Device To Resolving List command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Add Device To Resolving List command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Remove_Device_From_Resolving_List command is used to remove one device from the list of address translations used
    to resolve Resolvable Private Addresses in the Controller.
"""
def le_remove_device_from_resolving_list(transport, idx, PeerIdAddrType, AVal, to):

    cmd = struct.pack('<HHHB6B', Commands.CMD_LE_REMOVE_DEVICE_FROM_RESOLVING_LIST_REQ, 9, HCICommands.BT_HCI_OP_LE_REM_DEV_FROM_RL, PeerIdAddrType, *AVal);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Remove Device From Resolving List command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_REMOVE_DEVICE_FROM_RESOLVING_LIST_RSP ):
        raise Exception("LE Remove Device From Resolving List command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Remove Device From Resolving List command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Clear_Resolving_List command is used to remove all devices from the list of address translations used to resolve
    Resolvable Private Addresses in the Controller.
"""
def le_clear_resolving_list(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_CLEAR_RESOLVING_LIST_REQ, 2, HCICommands.BT_HCI_OP_LE_CLEAR_RL);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Clear Resolving List command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_CLEAR_RESOLVING_LIST_RSP ):
        raise Exception("LE Clear Resolving List command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Clear Resolving List command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Read_Resolving_List_Size command is used to read the total number of address translation entries in the resolving
    list that can be stored in the Controller. Note: The number of entries that can be stored is not fixed and the Controller
    can change it at any time (e.g. because the memory used to store the list can also be used for other purposes).
"""
def le_read_resolving_list_size(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_READ_RESOLVING_LIST_SIZE_REQ, 2, HCICommands.BT_HCI_OP_LE_READ_RL_SIZE);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 6, to);

    if ( 6 != len(packet) ):
        raise Exception("LE Read Resolving List Size command failed: Response too short (Expected %i bytes got %i bytes)" % (6, len(packet)));

    RespCmd, RespLen, status, RlSize = struct.unpack('<HHBB', packet);

    if ( RespCmd != Commands.CMD_LE_READ_RESOLVING_LIST_SIZE_RSP ):
        raise Exception("LE Read Resolving List Size command failed: Inappropriate command response received");

    if ( RespLen != 2 ):
        raise Exception("LE Read Resolving List Size command failed: Response length field corrupted (%i)" % RespLen);

    return status, RlSize;

"""
    The LE_Read_Peer_Resolvable_Address command is used to get the current peer Resolvable Private Address being used for the
    corresponding peer Public and Random (static) Identity Address. The peer\92s resolvable address being used may change after
    the command is called.
"""
def le_read_peer_resolvable_address(transport, idx, PeerIdAddrType, AVal, to):

    cmd = struct.pack('<HHHB6B', Commands.CMD_LE_READ_PEER_RESOLVABLE_ADDRESS_REQ, 9, HCICommands.BT_HCI_OP_LE_READ_PEER_RPA, PeerIdAddrType, *AVal);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 11, to);

    if ( 11 != len(packet) ):
        raise Exception("LE Read Peer Resolvable Address command failed: Response too short (Expected %i bytes got %i bytes)" % (11, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet[:5]);
    PeerRpaVal = struct.unpack('<6B', packet[5:]);

    if ( RespCmd != Commands.CMD_LE_READ_PEER_RESOLVABLE_ADDRESS_RSP ):
        raise Exception("LE Read Peer Resolvable Address command failed: Inappropriate command response received");

    if ( RespLen != 7 ):
        raise Exception("LE Read Peer Resolvable Address command failed: Response length field corrupted (%i)" % RespLen);

    return status, list(PeerRpaVal);

"""
    The LE_Read_Local_Resolvable_Address command is used to get the current local Resolvable Private Address being used for
    the corresponding peer Identity Address. The local\92s resolvable address being used may change after the command is called.
"""
def le_read_local_resolvable_address(transport, idx, PeerIdAddrType, AVal, to):

    cmd = struct.pack('<HHHB6B', Commands.CMD_LE_READ_LOCAL_RESOLVABLE_ADDRESS_REQ, 9, HCICommands.BT_HCI_OP_LE_READ_LOCAL_RPA, PeerIdAddrType, *AVal);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 11, to);

    if ( 11 != len(packet) ):
        raise Exception("LE Read Local Resolvable Address command failed: Response too short (Expected %i bytes got %i bytes)" % (11, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet[:5]);
    LocalRpaVal = struct.unpack('<6B', packet[5:]);

    if ( RespCmd != Commands.CMD_LE_READ_LOCAL_RESOLVABLE_ADDRESS_RSP ):
        raise Exception("LE Read Local Resolvable Address command failed: Inappropriate command response received");

    if ( RespLen != 7 ):
        raise Exception("LE Read Local Resolvable Address command failed: Response length field corrupted (%i)" % RespLen);

    return status, list(LocalRpaVal);

"""
    The LE_Set_Address_Resolution_Enable command is used to enable resolution of Resolvable Private Addresses in the
    Controller. This causes the Controller to use the resolving list whenever the Controller receives a local or peer
    Resolvable Private Address.
"""
def le_set_address_resolution_enable(transport, idx, enable, to):

    cmd = struct.pack('<HHHB', Commands.CMD_LE_SET_ADDRESS_RESOLUTION_ENABLE_REQ, 3, HCICommands.BT_HCI_OP_LE_SET_ADDR_RES_ENABLE, enable);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Address Resolution Enable command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_ADDRESS_RESOLUTION_ENABLE_RSP ):
        raise Exception("LE Set Address Resolution Enable command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Address Resolution Enable command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Set_Resolvable_Private_Address_Timeout command set the length of time the Controller uses a Resolvable Private
    Address before a new resolvable private address is generated and starts being used.
"""
def le_set_resolvable_private_address_timeout(transport, idx, RpaTimeout, to):

    cmd = struct.pack('<HHHH', Commands.CMD_LE_SET_RESOLVABLE_PRIVATE_ADDRESS_TIMEOUT_REQ, 4, HCICommands.BT_HCI_OP_LE_SET_RPA_TIMEOUT, RpaTimeout);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Resolvable Private Address Timeout command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_RESOLVABLE_PRIVATE_ADDRESS_TIMEOUT_RSP ):
        raise Exception("LE Set Resolvable Private Address Timeout command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Resolvable Private Address Timeout command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Read_Maximum_Data_Length command allows the Host to read the Controller\92s maximum supported payload octets and
    packet duration times for transmission and reception (supportedMaxTxOctets and supportedMaxTxTime, supportedMaxRxOctets,
    and supportedMaxRxTime, see [Vol 6] Part B, Section 4.5.10).
"""
def le_read_maximum_data_length(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_READ_MAXIMUM_DATA_LENGTH_REQ, 2, HCICommands.BT_HCI_OP_LE_READ_MAX_DATA_LEN);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 13, to);

    if ( 13 != len(packet) ):
        raise Exception("LE Read Maximum Data Length command failed: Response too short (Expected %i bytes got %i bytes)" % (13, len(packet)));

    RespCmd, RespLen, status, MaxTxOctets, MaxTxTime, MaxRxOctets, MaxRxTime = struct.unpack('<HHBHHHH', packet);

    if ( RespCmd != Commands.CMD_LE_READ_MAXIMUM_DATA_LENGTH_RSP ):
        raise Exception("LE Read Maximum Data Length command failed: Inappropriate command response received");

    if ( RespLen != 9 ):
        raise Exception("LE Read Maximum Data Length command failed: Response length field corrupted (%i)" % RespLen);

    return status, MaxTxOctets, MaxTxTime, MaxRxOctets, MaxRxTime;

"""
    The LE_Read_PHY command is used to read the current transmitter PHY and receiver PHY on the connection identified by the
    Connection_Handle.
"""
def le_read_phy(transport, idx, handle, to):

    cmd = struct.pack('<HHHH', Commands.CMD_LE_READ_PHY_REQ, 4, HCICommands.BT_HCI_OP_LE_READ_PHY, handle);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 9, to);

    if ( 9 != len(packet) ):
        raise Exception("LE Read PHY command failed: Response too short (Expected %i bytes got %i bytes)" % (9, len(packet)));

    RespCmd, RespLen, status, handle, TxPhy, RxPhy = struct.unpack('<HHBHBB', packet);

    if ( RespCmd != Commands.CMD_LE_READ_PHY_RSP ):
        raise Exception("LE Read PHY command failed: Inappropriate command response received");

    if ( RespLen != 5 ):
        raise Exception("LE Read PHY command failed: Response length field corrupted (%i)" % RespLen);

    return status, handle, TxPhy, RxPhy;

"""
    The LE_Set_Default_PHY command allows the Host to specify its preferred values for the transmitter PHY and receiver PHY to
    be used for all subsequent connections over the LE transport.
"""
def le_set_default_phy(transport, idx, AllPhys, TxPhys, RxPhys, to):

    cmd = struct.pack('<HHHBBB', Commands.CMD_LE_SET_DEFAULT_PHY_REQ, 5, HCICommands.BT_HCI_OP_LE_SET_DEFAULT_PHY, AllPhys, TxPhys, RxPhys);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Default PHY command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_DEFAULT_PHY_RSP ):
        raise Exception("LE Set Default PHY command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Default PHY command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Set_PHY command is used to set the PHY preferences for the connection identified by the Connection_Handle. The
    Controller might not be able to make the change (e.g. because the peer does not support the requested PHY) or may decide
    that the current PHY is preferable.
"""
def le_set_phy(transport, idx, handle, AllPhys, TxPhys, RxPhys, PhyOpts, to):

    cmd = struct.pack('<HHHHBBBH', Commands.CMD_LE_SET_PHY_REQ, 9, HCICommands.BT_HCI_OP_LE_SET_PHY, handle, AllPhys, TxPhys, RxPhys, PhyOpts);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set PHY command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_PHY_RSP ):
        raise Exception("LE Set PHY command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set PHY command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    This command is used to start a test where the DUT receives test reference packets at a fixed interval. The tester
    generates the test reference packets.
"""
def le_enhanced_receiver_test(transport, idx, RxCh, phy, ModIndex, to):

    cmd = struct.pack('<HHHBBB', Commands.CMD_LE_ENHANCED_RECEIVER_TEST_REQ, 5, HCICommands.BT_HCI_OP_LE_ENH_RX_TEST, RxCh, phy, ModIndex);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Enhanced Receiver Test command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_ENHANCED_RECEIVER_TEST_RSP ):
        raise Exception("LE Enhanced Receiver Test command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Enhanced Receiver Test command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    This command is used to start a test where the DUT generates test reference packets at a fixed interval. The Controller
    shall transmit at maximum power.
"""
def le_enhanced_transmitter_test(transport, idx, TxCh, TestDataLen, PktPayload, phy, to):

    cmd = struct.pack('<HHHBBBB', Commands.CMD_LE_ENHANCED_TRANSMITTER_TEST_REQ, 6, HCICommands.BT_HCI_OP_LE_ENH_TX_TEST, TxCh, TestDataLen, PktPayload, phy);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Enhanced Transmitter Test command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_ENHANCED_TRANSMITTER_TEST_RSP ):
        raise Exception("LE Enhanced Transmitter Test command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Enhanced Transmitter Test command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Set_Extended_Advertising_Parameters command is used by the Host to set the advertising parameters.
"""
def le_set_extended_advertising_parameters(transport, idx, handle, props, PrimMinInterval, PrimMaxInterval, PrimChannelMap, OwnAddrType, PeerAddrType, AVal, FilterPolicy, TxPower, PrimAdvPhy, SecAdvMaxSkip, SecAdvPhy, sid, ScanReqNotifyEnable, to):

    cmd = struct.pack('<HHHBH3B', Commands.CMD_LE_SET_EXTENDED_ADVERTISING_PARAMETERS_REQ, 27, HCICommands.BT_HCI_OP_LE_SET_EXT_ADV_PARAM, handle, props, *PrimMinInterval);
    cmd += struct.pack('<3B', *PrimMaxInterval);
    cmd += struct.pack('<BBB6B', PrimChannelMap, OwnAddrType, PeerAddrType, *AVal);
    cmd += struct.pack('<BbBBBBB', FilterPolicy, TxPower, PrimAdvPhy, SecAdvMaxSkip, SecAdvPhy, sid, ScanReqNotifyEnable);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Extended Advertising Parameters command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_EXTENDED_ADVERTISING_PARAMETERS_RSP ):
        raise Exception("LE Set Extended Advertising Parameters command failed: Inappropriate command response received");

    if ( status == 0x01 ):
        # Unsupported command, no Selected_TX_Power in response
        if ( RespLen != 1 ):
            raise Exception("LE Set Extended Advertising Parameters command failed: Response length field corrupted (%i)" % RespLen);
        return status

    if ( RespLen != 2 ):
        raise Exception("LE Set Extended Advertising Parameters command failed: Response length field corrupted (%i)" % RespLen);

    # Read out the last byte of the message
    packet = transport.recv(idx, 1, to);
    if ( 1 != len(packet) ):
        raise Exception("LE Set Extended Advertising Parameters command failed: Response too short (Expected %i bytes got %i bytes)" % (6, 5));

    return status;

"""
    The LE_Set_Extended_Advertising_Data command is used to set the data used in advertising PDUs that have a data field. This
    command may be issued at any time after an advertising set identified by the Advertising_Handle parameter has been created
    using the LE Set Extended Advertising Parameters Command (see Section 7.8.53), regardless of whether advertising in that
    set is enabled or disabled.
"""
def le_set_extended_advertising_data(transport, idx, handle, op, FragPref, data, to):

    cmd = struct.pack('<HHHBBBB' + str(len(data)) + 'B', Commands.CMD_LE_SET_EXTENDED_ADVERTISING_DATA_REQ, len(data) + 6, HCICommands.BT_HCI_OP_LE_SET_EXT_ADV_DATA, handle, op, FragPref, len(data), *data);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Extended Advertising Data command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_EXTENDED_ADVERTISING_DATA_RSP ):
        raise Exception("LE Set Extended Advertising Data command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Extended Advertising Data command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""

"""
def le_set_extended_scan_response_data(transport, idx, handle, op, FragPref, data, to):

    cmd = struct.pack('<HHHBBBB' + str(len(data)) + 'B', Commands.CMD_LE_SET_EXTENDED_SCAN_RESPONSE_DATA_REQ, len(data) + 6, HCICommands.BT_HCI_OP_LE_SET_EXT_SCAN_RSP_DATA, handle, op, FragPref, len(data), *data);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Extended Scan Response Data command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_EXTENDED_SCAN_RESPONSE_DATA_RSP ):
        raise Exception("LE Set Extended Scan Response Data command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Extended Scan Response Data command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Set_Extended_Advertising_Enable command is used to request the Controller to enable or disable one or more
    advertising sets using the advertising sets identified by the Advertising_Handle[i] parameter. The Controller manages the
    timing of advertisements in accordance with the advertising parameters given in the LE_Set_Extended_Advertising_Parameters
    command. The Number_of_Sets parameter is the number of advertising sets contained in the parameter arrays. If Enable and
    Number_of_Sets are both set to 0x00, then all advertising sets are disabled.
"""
def le_set_extended_advertising_enable(transport, idx, enable, SetNum, SHandle, SDuration, SMaxExtAdvEvts, to):
    cmd = struct.pack('<HHHBB' + 'BHB' * SetNum,
                      Commands.CMD_LE_SET_EXTENDED_ADVERTISING_ENABLE_REQ, 4 + 4 * SetNum,
                      HCICommands.BT_HCI_OP_LE_SET_EXT_ADV_ENABLE, enable, SetNum, *list(chain(*list(zip(SHandle, SDuration, SMaxExtAdvEvts)))))

    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Extended Advertising Enable command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_EXTENDED_ADVERTISING_ENABLE_RSP ):
        raise Exception("LE Set Extended Advertising Enable command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Extended Advertising Enable command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Read_Maximum_Advertising_Data_Length command is used to read the maximum length of data supported by the Controller
    for use as advertisement data or scan response data in an advertising event or as periodic advertisement data.
"""
def le_read_maximum_advertising_data_length(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_READ_MAXIMUM_ADVERTISING_DATA_LENGTH_REQ, 2, HCICommands.BT_HCI_OP_LE_READ_MAX_ADV_DATA_LEN);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);
    assert 5 == len(packet), f"Received invalid length packet {len(packet)}"

    RespCmd, RespLen, status = struct.unpack('<HHB', packet)

    if ( RespCmd != Commands.CMD_LE_READ_MAXIMUM_ADVERTISING_DATA_LENGTH_RSP ):
        raise Exception("LE Read Maximum Advertising Data Length command failed: Inappropriate command response received");

    if RespLen == 1:
        # Unsupported command.
        return status

    assert RespLen == 3, f"Response length field corrupted ({RespLen})"

    packet = transport.recv(idx, 2, to)
    assert 2 == len(packet), f"Received invalid length packet {len(packet)}"

    MaxAdvDataLen, = struct.unpack('<H', packet)
    return status, MaxAdvDataLen

"""
    The LE_Read_Number_of_Supported_Advertising_Sets command is used to read the maximum number of advertising sets supported
    by the advertising Controller at the same time. Note: The number of advertising sets that can be supported is not fixed
    and the Controller can change it at any time because the memory used to store advertising sets can also be used for other
    purposes.
"""
def le_read_number_of_supported_advertising_sets(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_READ_NUMBER_OF_SUPPORTED_ADVERTISING_SETS_REQ, 2, HCICommands.BT_HCI_OP_LE_READ_NUM_ADV_SETS);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);
    assert 5 == len(packet), f"Received invalid length packet {len(packet)}"

    RespCmd, RespLen, status = struct.unpack('<HHB', packet)

    if ( RespCmd != Commands.CMD_LE_READ_NUMBER_OF_SUPPORTED_ADVERTISING_SETS_RSP ):
        raise Exception("LE Read Number of Supported Advertising Sets command failed: Inappropriate command response received");

    if RespLen == 1:
        # Unsupported command.
        return status

    assert RespLen != 2, f"Response length field corrupted ({RespLen})"

    packet = transport.recv(idx, 1, to)
    assert 1 == len(packet), f"Received invalid length packet {len(packet)}"

    NumSets = struct.unpack('<B', packet)
    return status, NumSets

"""
    The LE_Remove_Advertising_Set command is used to remove an advertising set from the Controller.
"""
def le_remove_advertising_set(transport, idx, handle, to):

    cmd = struct.pack('<HHHB', Commands.CMD_LE_REMOVE_ADVERTISING_SET_REQ, 3, HCICommands.BT_HCI_OP_LE_REMOVE_ADV_SET, handle);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Remove Advertising Set command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_REMOVE_ADVERTISING_SET_RSP ):
        raise Exception("LE Remove Advertising Set command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Remove Advertising Set command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Clear_Advertising_Sets command is used to remove all existing advertising sets from the Controller.
"""
def le_clear_advertising_sets(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_CLEAR_ADVERTISING_SETS_REQ, 2, HCICommands.BT_HCI_OP_CLEAR_ADV_SETS);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Clear Advertising Sets command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_CLEAR_ADVERTISING_SETS_RSP ):
        raise Exception("LE Clear Advertising Sets command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Clear Advertising Sets command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Set_Periodic_Advertising_Parameters command is used by the Host to set the parameters for periodic advertising.
"""
def le_set_periodic_advertising_parameters(transport, idx, handle, MinInterval, MaxInterval, props, to):

    cmd = struct.pack('<HHHBHHH', Commands.CMD_LE_SET_PERIODIC_ADVERTISING_PARAMETERS_REQ, 9, HCICommands.BT_HCI_OP_LE_SET_PER_ADV_PARAM, handle, MinInterval, MaxInterval, props);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Periodic Advertising Parameters command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_PERIODIC_ADVERTISING_PARAMETERS_RSP ):
        raise Exception("LE Set Periodic Advertising Parameters command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Periodic Advertising Parameters command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Set_Periodic_Advertising_Data command is used to set the data used in periodic advertising PDUs. This command may
    be issued at any time after the advertising set identified by the Advertising_Handle parameter has been configured for
    periodic advertising using the LE_Set_Periodic_Advertising_Parameters Command (see Section 7.8.61), regardless of whether
    advertising in that set is enabled or disabled. If the advertising set has not been configured for periodic advertising,
    then the Controller shall return the error code Command Disallowed (0x0C).
"""
def le_set_periodic_advertising_data(transport, idx, handle, op, dataLen, data, to):

    cmd = struct.pack('<HHHBBB251B', Commands.CMD_LE_SET_PERIODIC_ADVERTISING_DATA_REQ, 256, HCICommands.BT_HCI_OP_LE_SET_PER_ADV_DATA, handle, op, dataLen, *data);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Periodic Advertising Data command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_PERIODIC_ADVERTISING_DATA_RSP ):
        raise Exception("LE Set Periodic Advertising Data command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Periodic Advertising Data command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Set_Periodic_Advertising_Enable command is used to request the Controller to enable or disable the periodic
    advertising for the advertising set specified by the Advertising_Handle parameter (ordinary advertising is not affected).
"""
def le_set_periodic_advertising_enable(transport, idx, enable, handle, to):

    cmd = struct.pack('<HHHBB', Commands.CMD_LE_SET_PERIODIC_ADVERTISING_ENABLE_REQ, 4, HCICommands.BT_HCI_OP_LE_SET_PER_ADV_ENABLE, enable, handle);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Periodic Advertising Enable command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_PERIODIC_ADVERTISING_ENABLE_RSP ):
        raise Exception("LE Set Periodic Advertising Enable command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Periodic Advertising Enable command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Set_Extended_Scan_Parameters command is used to set the extended scan parameters to be used on the advertising
    channels.
"""
def le_set_extended_scan_parameters(transport, idx, OwnAddrType, FilterPolicy, phys, PType, PInterval, PWindow, to):

    cmd = struct.pack('<HHHBBB' + 'BHH' * phys, Commands.CMD_LE_SET_EXTENDED_SCAN_PARAMETERS_REQ, 5 + 5 * phys,
                      HCICommands.BT_HCI_OP_LE_SET_EXT_SCAN_PARAM, OwnAddrType, FilterPolicy, phys,
                      *list(chain(*list(zip(PType, PInterval, PWindow)))))

    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Extended Scan Parameters command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_EXTENDED_SCAN_PARAMETERS_RSP ):
        raise Exception("LE Set Extended Scan Parameters command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Extended Scan Parameters command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Set_Extended_Scan_Enable command is used to enable or disable scanning.
"""
def le_set_extended_scan_enable(transport, idx, enable, FilterDup, duration, period, to):

    cmd = struct.pack('<HHHBBHH', Commands.CMD_LE_SET_EXTENDED_SCAN_ENABLE_REQ, 8, HCICommands.BT_HCI_OP_LE_SET_EXT_SCAN_ENABLE, enable, FilterDup, duration, period);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Extended Scan Enable command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_EXTENDED_SCAN_ENABLE_RSP ):
        raise Exception("LE Set Extended Scan Enable command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Extended Scan Enable command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Extended_Create_Connection command is used to create a Link Layer connection to a connectable advertiser.
    LE_Extended_Create_Connection command can be used in place of LE_Create_Connection command.
"""
def le_extended_create_connection(transport, idx, FilterPolicy, OwnAddrType, PeerAddrType, AVal, phys, PInterval, PWindow, PConnIntervalMin, PConnIntervalMax, PConnLatency, PSupervisionTimeout, PMinCeLen, PMaxCeLen, to):

    PHYCount = bin(phys).count("1")

    cmd = struct.pack('<HHHBBB6BB' + 'HHHHHHHH' * PHYCount, Commands.CMD_LE_EXTENDED_CREATE_CONNECTION_REQ, 12 + 16 * PHYCount,
                      HCICommands.BT_HCI_OP_LE_EXT_CREATE_CONN, FilterPolicy, OwnAddrType, PeerAddrType, *AVal, phys,
                      *list(chain(*list(zip(PInterval, PWindow, PConnIntervalMin, PConnIntervalMax, PConnLatency, PSupervisionTimeout, PMinCeLen, PMaxCeLen)))))

    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Extended Create Connection command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_EXTENDED_CREATE_CONNECTION_RSP ):
        raise Exception("LE Extended Create Connection command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Extended Create Connection command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Periodic_Advertising_Create_Sync command is used to synchronize with periodic advertising from an advertiser and
    begin receiving periodic advertising packets.
"""
def le_periodic_advertising_create_sync(transport, idx, FilterPolicy, sid, AddrType, AVal, skip, SyncTimeout, unused, to):

    cmd = struct.pack('<HHHBBB6B', Commands.CMD_LE_PERIODIC_ADVERTISING_CREATE_SYNC_REQ, 16, HCICommands.BT_HCI_OP_LE_PER_ADV_CREATE_SYNC, FilterPolicy, sid, AddrType, *AVal);
    cmd += struct.pack('<HHB', skip, SyncTimeout, unused);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Periodic Advertising Create Sync command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_PERIODIC_ADVERTISING_CREATE_SYNC_RSP ):
        raise Exception("LE Periodic Advertising Create Sync command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Periodic Advertising Create Sync command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Periodic_Advertising_Create_Sync_Cancel command is used to cancel the LE_Periodic_Advertising_Create_Sync command
    while it is pending.
"""
def le_periodic_advertising_create_sync_cancel(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_PERIODIC_ADVERTISING_CREATE_SYNC_CANCEL_REQ, 2, HCICommands.BT_HCI_OP_LE_PER_ADV_CREATE_SYNC_CANCEL);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Periodic Advertising Create Sync Cancel command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_PERIODIC_ADVERTISING_CREATE_SYNC_CANCEL_RSP ):
        raise Exception("LE Periodic Advertising Create Sync Cancel command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Periodic Advertising Create Sync Cancel command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Periodic_Advertising_Terminate_Sync command is used to stop reception of the periodic advertising identified by the
    Sync_Handle parameter.
"""
def le_periodic_advertising_terminate_sync(transport, idx, handle, to):

    cmd = struct.pack('<HHHH', Commands.CMD_LE_PERIODIC_ADVERTISING_TERMINATE_SYNC_REQ, 4, HCICommands.BT_HCI_OP_LE_PER_ADV_TERMINATE_SYNC, handle);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Periodic Advertising Terminate Sync command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_PERIODIC_ADVERTISING_TERMINATE_SYNC_RSP ):
        raise Exception("LE Periodic Advertising Terminate Sync command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Periodic Advertising Terminate Sync command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Add_Device_To_Periodic_Advertiser_List command is used to add a single device to the Periodic Advertiser list
    stored in the Controller. Any additions to the Periodic Advertiser list take effect immediately. If the device is already
    on the list, the Controller shall return the error code Invalid HCI Command Parameters (0x12).
"""
def le_add_device_to_periodic_advertiser_list(transport, idx, AddrType, AVal, sid, to):

    cmd = struct.pack('<HHHB6B', Commands.CMD_LE_ADD_DEVICE_TO_PERIODIC_ADVERTISER_LIST_REQ, 10, HCICommands.BT_HCI_OP_LE_ADD_DEV_TO_PER_ADV_LIST, AddrType, *AVal);
    cmd += struct.pack('<B', sid);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Add Device To Periodic Advertiser List command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_ADD_DEVICE_TO_PERIODIC_ADVERTISER_LIST_RSP ):
        raise Exception("LE Add Device To Periodic Advertiser List command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Add Device To Periodic Advertiser List command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Remove_Device_From_Periodic_Advertiser_List command is used to remove one device from the list of Periodic
    Advertisers stored in the Controller. Removals from the Periodic Advertisers List take effect immediately.
"""
def le_remove_device_from_periodic_advertiser_list(transport, idx, AddrType, AVal, sid, to):

    cmd = struct.pack('<HHHB6B', Commands.CMD_LE_REMOVE_DEVICE_FROM_PERIODIC_ADVERTISER_LIST_REQ, 10, HCICommands.BT_HCI_OP_LE_REM_DEV_FROM_PER_ADV_LIST, AddrType, *AVal);
    cmd += struct.pack('<B', sid);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Remove Device From Periodic Advertiser List command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_REMOVE_DEVICE_FROM_PERIODIC_ADVERTISER_LIST_RSP ):
        raise Exception("LE Remove Device From Periodic Advertiser List command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Remove Device From Periodic Advertiser List command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Clear_Periodic_Advertiser_List command is used to remove all devices from the list of Periodic Advertisers in the
    Controller.
"""
def le_clear_periodic_advertiser_list(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_CLEAR_PERIODIC_ADVERTISER_LIST_REQ, 2, HCICommands.BT_HCI_OP_LE_CLEAR_PER_ADV_LIST);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Clear Periodic Advertiser List command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_CLEAR_PERIODIC_ADVERTISER_LIST_RSP ):
        raise Exception("LE Clear Periodic Advertiser List command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Clear Periodic Advertiser List command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Read_Periodic_Advertiser_List_Size command is used to read the total number of Periodic Advertiser list entries
    that can be stored in the Controller. Note: The number of entries that can be stored is not fixed and the Controller can
    change it at any time (e.g., because the memory used to store the list can also be used for other purposes).
"""
def le_read_periodic_advertiser_list_size(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_READ_PERIODIC_ADVERTISER_LIST_SIZE_REQ, 2, HCICommands.BT_HCI_OP_LE_READ_PER_ADV_LIST_SIZE);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);
    assert 5 == len(packet), f"Received invalid length packet {len(packet)}"

    RespCmd, RespLen, status = struct.unpack('<HHB', packet)

    if ( RespCmd != Commands.CMD_LE_READ_PERIODIC_ADVERTISER_LIST_SIZE_RSP ):
        raise Exception("LE Read Periodic Advertiser List Size command failed: Inappropriate command response received");

    if RespLen == 1:
        # Unsupported command.
        return status

    assert RespLen != 2, f"Response length field corrupted ({RespLen})"

    packet = transport.recv(idx, 1, to)
    assert 1 == len(packet), f"Received invalid length packet {len(packet)}"

    ListSize = struct.unpack('<B', packet)
    return status, ListSize;

"""
    The LE_Read_Transmit_Power command is used to read the minimum and maximum transmit powers supported by the Controller.
"""
def le_read_transmit_power(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_READ_TRANSMIT_POWER_REQ, 2, HCICommands.BT_HCI_OP_LE_READ_TX_POWER);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 7, to);

    if ( 7 != len(packet) ):
        raise Exception("LE Read Transmit Power command failed: Response too short (Expected %i bytes got %i bytes)" % (7, len(packet)));

    RespCmd, RespLen, status, MinTxPower, MaxTxPower = struct.unpack('<HHBbb', packet);

    if ( RespCmd != Commands.CMD_LE_READ_TRANSMIT_POWER_RSP ):
        raise Exception("LE Read Transmit Power command failed: Inappropriate command response received");

    if ( RespLen != 3 ):
        raise Exception("LE Read Transmit Power command failed: Response length field corrupted (%i)" % RespLen);

    return status, MinTxPower, MaxTxPower;

"""
    The LE_Read_RF_Path_Compensation command is used to read the RF Path Compensation Values parameter used in the Tx Power
    Level and RSSI calculation.
"""
def le_read_rf_path_compensation(transport, idx, to):

    cmd = struct.pack('<HHH', Commands.CMD_LE_READ_RF_PATH_COMPENSATION_REQ, 2, HCICommands.BT_HCI_OP_LE_READ_RF_PATH_COMP);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);
    assert 5 == len(packet), f"Received invalid length packet {len(packet)}"

    RespCmd, RespLen, status = struct.unpack('<HHB', packet)

    if ( RespCmd != Commands.CMD_LE_READ_RF_PATH_COMPENSATION_RSP ):
        raise Exception("LE Read RF Path Compensation command failed: Inappropriate command response received");

    if RespLen == 1:
        # Unsupported command.
        return status

    assert RespLen != 5, f"Response length field corrupted ({RespLen})"

    packet = transport.recv(idx, 4, to)
    assert 4 == len(packet), f"Received invalid length packet {len(packet)}"

    TxPathComp, RxPathComp  = struct.unpack('<HH', packet)
    return status, TxPathComp, RxPathComp

"""
    The LE_Write_RF_Path_Compensation command is used to indicate the RF path gain or loss between the RF transceiver and the
    antenna contributed by intermediate components. A positive value means a net RF path gain and a negative value means a net
    RF path loss. The RF Tx Path Compensation Value parameter shall be used by the Controller to calculate radiative Tx Power
    Level used in the TxPower field in the Extended Header using the following equation: Radiative Tx Power Level = Tx Power
    Level at RF transceiver output + RF Tx Path Compensation Value For example, if the Tx Power Level is +4 (dBm) at RF
    transceiver output and the RF Path Compensation Value is -1.5 (dB), the radiative Tx Power Level is +4+(-1.5) = 2.5 (dBm).
"""
def le_write_rf_path_compensation(transport, idx, TxPathComp, RxPathComp, to):

    cmd = struct.pack('<HHHhh', Commands.CMD_LE_WRITE_RF_PATH_COMPENSATION_REQ, 6, HCICommands.BT_HCI_OP_LE_WRITE_RF_PATH_COMP, TxPathComp, RxPathComp);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Write RF Path Compensation command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_WRITE_RF_PATH_COMPENSATION_RSP ):
        raise Exception("LE Write RF Path Compensation command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Write RF Path Compensation command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The LE_Set_Privacy_Mode command is used to allow the Host to specify the privacy mode to be used for a given entry on the
    resolving list. The effect of this setting is specified in [Vol 6] Part B, Section 4.7.
"""
def le_set_privacy_mode(transport, idx, IdAddrType, AVal, mode, to):

    cmd = struct.pack('<HHHB6B', Commands.CMD_LE_SET_PRIVACY_MODE_REQ, 10, HCICommands.BT_HCI_OP_LE_SET_PRIVACY_MODE, IdAddrType, *AVal);
    cmd += struct.pack('<B', mode);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Set Privacy Mode command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_SET_PRIVACY_MODE_RSP ):
        raise Exception("LE Set Privacy Mode command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Set Privacy Mode command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    The Write_BD_ADDR command is used to set the Public address of the Device.
"""
def write_bd_addr(transport, idx, BdaddrVal, to):

    cmd = struct.pack('<HHH6B', Commands.CMD_WRITE_BD_ADDR_REQ, 8, HCICommands.BT_HCI_OP_VS_WRITE_BD_ADDR, *BdaddrVal);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("Write BD_ADDR command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_WRITE_BD_ADDR_RSP ):
        raise Exception("Write BD_ADDR command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("Write BD_ADDR command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    Flush the events queue
"""
def flush_events(transport, idx, to):

    cmd = struct.pack('<HH', Commands.CMD_FLUSH_EVENTS_REQ, 0);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 4, to);

    if ( 4 != len(packet) ):
        raise Exception("Flush Events command failed: Response too short (Expected %i bytes got %i bytes)" % (4, len(packet)));

    RespCmd, RespLen = struct.unpack('<HH', packet);

    if ( RespCmd != Commands.CMD_FLUSH_EVENTS_RSP ):
        raise Exception("Flush Events command failed: Inappropriate command response received");

    if ( RespLen != 0 ):
        raise Exception("Flush Events command failed: Response length field corrupted (%i)" % RespLen);


"""
    Check whether an event is available in the events queue
"""
def has_event(transport, idx, to):

    while to >= 0:
        start_t = transport.last_t

        cmd = struct.pack('<HH', Commands.CMD_HAS_EVENT_REQ, 0);
        transport.send(idx, cmd);

        packet = transport.recv(idx, 5, 100);

        if ( 5 != len(packet) ):
            raise Exception("Has Event command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

        RespCmd, RespLen, count = struct.unpack('<HHB', packet);

        if ( RespCmd != Commands.CMD_HAS_EVENT_RSP ):
            raise Exception("Has Event command failed: Inappropriate command response received");

        if ( RespLen != 1 ):
            raise Exception("Has Event command failed: Response length field corrupted (%i)" % RespLen);

        if count > 0:
            break;

        to_tmp = 100 - int((transport.last_t - start_t) / 1000);
        to -= 100;
        if to >= 0 and to_tmp > 0:
            transport.wait(to_tmp);

    return count > 0, count;

"""
    Get event(s) from the events queue
"""
def get_event(transport, idx, to, multiple=False):

    cmd = struct.pack('<HHB', Commands.CMD_GET_EVENT_REQ, 1, 1 if multiple else 0);
    transport.send(idx, cmd);

    nBytes = 3 if multiple else 10;
    packet = transport.recv(idx, nBytes, to);

    if nBytes != len(packet):
        raise Exception("Get Event command failed: Response too short (Expected %i bytes got %i bytes)" % (nBytes, len(packet)));

    if multiple:
        RespCmd, count = struct.unpack('<HB', packet);
        if RespCmd != Commands.CMD_GET_EVENT_RSP:
            raise Exception("Get Event command failed: Inappropriate command response received");

        events = [];
        while count > 0:
            packet = transport.recv(idx, 8, to);
            RespLen, time, event, eventLen = struct.unpack('<HIBB', packet);
            data = "" if eventLen == 0 else transport.recv(idx, eventLen, to);

            if RespLen != (6 + eventLen):
                raise Exception("Get Event command failed: Response length field corrupted (%i)" % RespLen);

            events += [Event(event, data, time)];
            count -= 1;

        return events;
    else:
        RespCmd, RespLen, time, event, eventLen = struct.unpack('<HHIBB', packet[:10]);
        data = "" if RespLen <= 6 else transport.recv(idx, RespLen - 6, to);

        if RespCmd != Commands.CMD_GET_EVENT_RSP:
            raise Exception("Get Event command failed: Inappropriate command response received (%i)" % RespCmd);

        if RespLen != 6 + eventLen:
            raise Exception("Get Event command failed: Response length field corrupted (%i)" % RespLen);

        transport.Trace.btsnoop.send_event(idx, packet, data)

        return Event(event, data, time);

"""
    Flush the Data queue
"""
def le_data_flush(transport, idx, to):

    cmd = struct.pack('<HH', Commands.CMD_LE_DATA_FLUSH_REQ, 0);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 4, to);

    if ( 4 != len(packet) ):
        raise Exception("LE Data Flush command failed: Response too short (Expected %i bytes got %i bytes)" % (4, len(packet)));

    RespCmd, RespLen = struct.unpack('<HH', packet);

    if ( RespCmd != Commands.CMD_LE_DATA_FLUSH_RSP ):
        raise Exception("LE Data Flush command failed: Inappropriate command response received");

    if ( RespLen != 0 ):
        raise Exception("LE Data Flush command failed: Response length field corrupted (%i)" % RespLen);


"""
    Check whether data is available in the data queue
"""
def le_data_ready(transport, idx, to):

    while to >= 0:
        cmd = struct.pack('<HH', Commands.CMD_LE_DATA_READY_REQ, 0);
        transport.send(idx, cmd);

        packet = transport.recv(idx, 5, 100);

        if ( 5 != len(packet) ):
            raise Exception("LE Data Ready command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

        RespCmd, RespLen, empty = struct.unpack('<HHB', packet);

        if ( RespCmd != Commands.CMD_LE_DATA_READY_RSP ):
            raise Exception("LE Data Ready command failed: Inappropriate command response received");

        if ( RespLen != 1 ):
            raise Exception("LE Data Ready command failed: Response length field corrupted (%i)" % RespLen);

        if empty != 1:
            break;

        to -= 100;
        if to >= 0:
            transport.wait(100);

    return empty != 1;

"""
    Write Data packet
"""
def le_data_write(transport, idx, handle, PbFlags, BcFlags, data, to):

    handle &= 0x0fff;
    handle |= (PbFlags | (BcFlags << 2)) << 12;
    cmd = struct.pack('<HHHH' + str(len(data)) + 'B', Commands.CMD_LE_DATA_WRITE_REQ, 4 + len(data), handle, len(data), *data);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 5, to);

    if ( 5 != len(packet) ):
        raise Exception("LE Data Write command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)));

    RespCmd, RespLen, status = struct.unpack('<HHB', packet);

    if ( RespCmd != Commands.CMD_LE_DATA_WRITE_RSP ):
        raise Exception("LE Data Write command failed: Inappropriate command response received");

    if ( RespLen != 1 ):
        raise Exception("LE Data Write command failed: Response length field corrupted (%i)" % RespLen);

    return status;

"""
    Read Data packet
"""
def le_data_read(transport, idx, to):

    cmd = struct.pack('<HH', Commands.CMD_LE_DATA_READ_REQ, 0);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 12, to);

    if ( 12 != len(packet) ):
        raise Exception("LE Data Read command failed: Response too short (Expected %i bytes got %i bytes)" % (12, len(packet)));

    RespCmd, RespLen, time, handle, dataLen = struct.unpack('<HHIHH', packet[:12]);
    if RespLen > 8:
        packet = transport.recv(idx, RespLen - 8, to);
    if dataLen > 0:
        data = struct.unpack('<' + str(dataLen) + 'B', packet);
    else:
        data = [];

    if ( RespCmd != Commands.CMD_LE_DATA_READ_RSP ):
        raise Exception("LE Data Read command failed: Inappropriate command response received");

    if ( RespLen != 8 + dataLen ):
        raise Exception("LE Data Read command failed: Response length field corrupted (%i)" % RespLen);

    PbFlags = (handle >> 12) & 0x03;
    BcFlags = (handle >> 14) & 0x03;
    handle &= 0x0fff;

    transport.Trace.btsnoop.send_monitor_acl_rx(idx, handle, dataLen, packet)

    return time, handle, PbFlags, BcFlags, data;

"""
    Switch GATT Service Set
"""
def switch_gatt_service_set(transport, idx, serviceSet, to):

    cmd = struct.pack('<HHB', Commands.CMD_GATT_SERVICE_SET_REQ, 1, serviceSet);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 4, to);

    if ( 4 != len(packet) ):
        raise Exception("Switch GATT Service Set command failed: Response too short (Expected %i bytes got %i bytes)" % (4, len(packet)));

    RespCmd, RespLen = struct.unpack('<HH', packet);

    if ( RespCmd != Commands.CMD_GATT_SERVICE_SET_RSP ):
        raise Exception("Switch GATT Service Set command failed: Inappropriate command response received");

    if ( RespLen != 0 ):
        raise Exception("Switch GATT Service Set command failed: Response length field corrupted (%i)" % RespLen);

"""
    Invoke GATT Service Set Notifications
"""
def gatt_service_notify(transport, idx, to):

    cmd = struct.pack('<HH', Commands.CMD_GATT_SERVICE_NOTIFY_REQ, 0);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 4, to);

    if ( 4 != len(packet) ):
        raise Exception("Invoke GATT Service Set Notifications command failed: Response too short (Expected %i bytes got %i bytes)" % (4, len(packet)));

    RespCmd, RespLen = struct.unpack('<HH', packet);

    if ( RespCmd != Commands.CMD_GATT_SERVICE_NOTIFY_RSP ):
        raise Exception("Invoke GATT Service Set Notifications command failed: Inappropriate command response received");

    if ( RespLen != 0 ):
        raise Exception("Invoke GATT Service Set Notifications command failed: Response length field corrupted (%i)" % RespLen);

"""
    Invoke GATT Service Set Indications
"""
def gatt_service_indicate(transport, idx, to):

    cmd = struct.pack('<HH', Commands.CMD_GATT_SERVICE_INDICATE_REQ, 0);
    transport.send(idx, cmd);

    packet = transport.recv(idx, 4, to);

    if ( 4 != len(packet) ):
        raise Exception("Invoke GATT Service Set Indications command failed: Response too short (Expected %i bytes got %i bytes)" % (4, len(packet)));

    RespCmd, RespLen = struct.unpack('<HH', packet);

    if ( RespCmd != Commands.CMD_GATT_SERVICE_INDICATE_RSP ):
        raise Exception("Invoke GATT Service Set Indications command failed: Inappropriate command response received");

    if ( RespLen != 0 ):
        raise Exception("Invoke GATT Service Set Indications command failed: Response length field corrupted (%i)" % RespLen);

"""
    Flush the ISO Data queue
"""
def le_iso_data_flush(transport, idx, to):

    cmd = struct.pack('<HH', Commands.CMD_LE_ISO_DATA_FLUSH_REQ, 0)
    transport.send(idx, cmd)

    packet = transport.recv(idx, 4, to)

    if ( 4 != len(packet) ):
        raise Exception("LE ISO Data Flush command failed: Response too short (Expected %i bytes got %i bytes)" % (4, len(packet)))

    RespCmd, RespLen = struct.unpack('<HH', packet)

    if ( RespCmd != Commands.CMD_LE_ISO_DATA_FLUSH_RSP ):
        raise Exception("LE ISO Data Flush command failed: Inappropriate command response received")

    if ( RespLen != 0 ):
        raise Exception("LE ISO Data Flush command failed: Response length field corrupted (%i)" % RespLen)

"""
    Check whether ISO data is available in the data queue
"""
def le_iso_data_ready(transport, idx, to):

    while to >= 0:
        cmd = struct.pack('<HH', Commands.CMD_LE_ISO_DATA_READY_REQ, 0)
        transport.send(idx, cmd)

        packet = transport.recv(idx, 5, 100);

        if ( 5 != len(packet) ):
            raise Exception("LE ISO Data Ready command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)))

        RespCmd, RespLen, empty = struct.unpack('<HHB', packet)

        if ( RespCmd != Commands.CMD_LE_ISO_DATA_READY_RSP ):
            raise Exception("LE ISO Data Ready command failed: Inappropriate command response received")

        if ( RespLen != 1 ):
            raise Exception("LE ISO Data Ready command failed: Response length field corrupted (%i)" % RespLen)

        if empty != 1:
            break

        to -= 100;
        if to >= 0:
            transport.wait(100)

    return empty != 1



def le_iso_data_write_rsp(transport, idx, to):
    packet = transport.recv(idx, 5, to)

    if ( 5 != len(packet) ):
        raise Exception("LE ISO Data Write command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)))

    RespCmd, RespLen, status = struct.unpack('<HHB', packet)

    if ( RespCmd != Commands.CMD_LE_ISO_DATA_WRITE_RSP ):
        raise Exception("LE ISO Data Write command failed: Inappropriate command response received")

    if ( RespLen != 1 ):
        raise Exception("LE ISO Data Write command failed: Response length field corrupted (%i)" % RespLen)

    return status

"""
    Write ISO Data packet
"""
def le_iso_data_write(transport, idx, handle, PbFlags, TsFlag, data, to):

    handle &= 0x0fff
    handle |= ((PbFlags | (TsFlag << 2)) << 12) & 0x7fff

    cmd = struct.pack('<HHHH' + str(len(data)) + 'B', Commands.CMD_LE_ISO_DATA_WRITE_REQ, 4 + len(data), handle, len(data), *data)
    transport.send(idx, cmd)

    if ( to == 0 ):
        return 0

    return le_iso_data_write_rsp(transport, idx, to)

"""
    Read ISO Data packet
"""
def le_iso_data_read(transport, idx, to):

    cmd = struct.pack('<HH', Commands.CMD_LE_ISO_DATA_READ_REQ, 0)
    transport.send(idx, cmd)

    packet = transport.recv(idx, 12, to)

    if ( 12 != len(packet) ):
        raise Exception("LE ISO Data Read command failed: Response too short (Expected %i bytes got %i bytes)" % (12, len(packet)))

    RespCmd, RespLen, time, handle, dataLen = struct.unpack('<HHIHH', packet[:12])
    if RespLen > 8:
        packet = transport.recv(idx, RespLen - 8, to)
    if dataLen > 0:
        data = struct.unpack('<' + str(dataLen) + 'B', packet)
    else:
        data = []

    if ( RespCmd != Commands.CMD_LE_ISO_DATA_READ_RSP ):
        raise Exception("LE ISO Data Read command failed: Inappropriate command response received")

    if ( RespLen != 8 + dataLen ):
        raise Exception("LE ISO Data Read command failed: Response length field corrupted (%i)" % RespLen)

    transport.Trace.btsnoop.send_monitor_iso_rx(idx, handle, dataLen, packet)

    PbFlags = (handle >> 12) & 0x03
    TsFlag  = (handle >> 14) & 0x01
    handle &= 0x0fff

    return time, handle, PbFlags, TsFlag, data

"""
    The HCI_LE_Set_CIG_Parameters command is used by a central's Host to
    set the parameters of one or more CISes that are associated with a CIG in the
    Controller.
"""
def le_set_cig_parameters(transport, idx, CigId, SduIntervalMToS, SduIntervalSToM, PeripheralsClockAccuracy, Packing,
                          Framing, MaxTransportLatencyMToS, MaxTransportLatencySToM, CisCount, CisId, MaxSduMToS, MaxSduSToM,
                          PhyMToS, PhySToM, RtnMToS, RtnSToM, to):
    cmd_parameters = [HCICommands.BT_HCI_OP_LE_SET_CIG_PARAMETERS, CigId, *toArray(SduIntervalMToS, 3),
                      *toArray(SduIntervalSToM, 3), PeripheralsClockAccuracy, Packing, Framing, MaxTransportLatencyMToS,
                      MaxTransportLatencySToM, CisCount]
    for i in range(CisCount):
        cmd_parameters += [CisId[i], MaxSduMToS[i], MaxSduSToM[i], PhyMToS[i], PhySToM[i], RtnMToS[i], RtnSToM[i]]

    edtt_send_cmd(transport, idx, Commands.CMD_LE_SET_CIG_PARAMETERS_REQ, 'HB3B3BBBBHHB' + CisCount * 'BHHBBBB',
                  cmd_parameters)

    status, cigId, cisCount, *cisConnectionHandle = \
        edtt_wait_cmd_cmpl(transport, idx, Commands.CMD_LE_SET_CIG_PARAMETERS_RSP, f'BBB{CisCount}H', to)

    return status, cigId, cisCount, cisConnectionHandle

"""
    The command is used by a central's Host to set the parameters of one or more
    CISes that are associated with a CIG in the Controller. Should only be used for
    testing purposes.
"""
def le_set_cig_parameters_test(transport, idx, CigId, SduIntervalMToS, SduIntervalSToM, FtMToS, FtSToM, IsoInterval, PeripheralsClockAccuracy,
                               Packing, Framing, CisCount, CisId, Nse, MaxSduMToS, MaxSduSToM, MaxPduMToS, MaxPduSToM,
                               PhyMToS, PhySToM, BnMToS, BnSToM, to):
    cmd_parameters = [HCICommands.BT_HCI_OP_LE_SET_CIG_PARAMETERS_TEST, CigId, *toArray(SduIntervalMToS, 3),
                      *toArray(SduIntervalSToM, 3), FtMToS, FtSToM, IsoInterval, PeripheralsClockAccuracy, Packing, Framing,
                      CisCount]
    for i in range(CisCount):
        cmd_parameters += [CisId[i], Nse[i], MaxSduMToS[i], MaxSduSToM[i], MaxPduMToS[i], MaxPduSToM[i], PhyMToS[i],
                           PhySToM[i], BnMToS[i], BnSToM[i]]

    edtt_send_cmd(transport, idx, Commands.CMD_LE_SET_CIG_PARAMETERS_TEST_REQ,
                  'HB3B3BBBHBBBB' + CisCount * 'BBHHHHBBBB', cmd_parameters)

    status, cigId, cisCount, *cisConnectionHandle = \
        edtt_wait_cmd_cmpl(transport, idx, Commands.CMD_LE_SET_CIG_PARAMETERS_TEST_RSP, f'BBB{CisCount}H', to)

    return status, cigId, cisCount, cisConnectionHandle

"""
    The HCI_LE_Create_CIS command is used by the central's Host to create one
    or more CISes using the connections identified by the ACL_Connection_Handle[i]
    parameter array.
"""
def le_create_cis(transport, idx, CisCount, CisConnectionHandle, AclConnectionHandle, to):
    cmd_parameters = [HCICommands.BT_HCI_OP_LE_CREATE_CIS, CisCount]
    for i in range(CisCount):
        cmd_parameters += [CisConnectionHandle[i], AclConnectionHandle[i]]

    edtt_send_cmd(transport, idx, Commands.CMD_LE_CREATE_CIS_REQ, 'HB' + CisCount * 'HH', cmd_parameters)

    return edtt_wait_cmd_cmpl(transport, idx, Commands.CMD_LE_CREATE_CIS_RSP, 'B', to)[0]

"""
    The HCI_LE_Remove_CIG command is used by the central's Host to remove
    all the CISes associated with the CIG identified by CIG_ID.
"""
def le_remove_cig(transport, idx, CigId, to):

    cmd = struct.pack('<HHHB', Commands.CMD_LE_REMOVE_CIG_REQ, 3, HCICommands.BT_HCI_OP_LE_REMOVE_CIG, CigId)
    transport.send(idx, cmd)

    packet = transport.recv(idx, 6, to)

    if ( 6 != len(packet) ):
        raise Exception("LE Remove CIG command failed: Response too short (Expected %i bytes got %i bytes)" % (6, len(packet)))

    RespCmd, RespLen, status, cigId = struct.unpack('<HHBB', packet)

    if ( RespCmd != Commands.CMD_LE_REMOVE_CIG_RSP ):
        raise Exception("LE Remove CIG command failed: Inappropriate command response received")

    if ( RespLen != 2 ):
        raise Exception("LE Remove CIG command failed: Response length field corrupted (%i)" % RespLen)

    return status, cigId

"""
    The HCI_LE_Accept_CIS_Request command is used by the peripheral's Host to
    inform the Controller to accept the request for the CIS that is identified by the
    Connection_Handle.
"""
def le_accept_cis_request(transport, idx, ConnectionHandle, to):

    ConnectionHandle &= 0x0fff

    cmd = struct.pack('<HHHH', Commands.CMD_LE_ACCEPT_CIS_REQUEST_REQ, 4, HCICommands.BT_HCI_OP_LE_ACCEPT_CIS_REQUEST,
                      ConnectionHandle)
    transport.send(idx, cmd)

    packet = transport.recv(idx, 5, to)

    if ( 5 != len(packet) ):
        raise Exception("LE Accept CIS Request command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)))

    RespCmd, RespLen, status = struct.unpack('<HHB', packet)

    if ( RespCmd != Commands.CMD_LE_ACCEPT_CIS_REQUEST_RSP ):
        raise Exception("LE Accept CIS Request command failed: Inappropriate command response received")

    if ( RespLen != 1 ):
        raise Exception("LE Accept CIS Request command failed: Response length field corrupted (%i)" % RespLen)

    return status

"""
    The HCI_LE_Reject_CIS_Request command is used by the peripheral's Host to
    inform the Controller to reject the request for the CIS that is identified by the
    Connection_Handle.
"""
def le_reject_cis_request(transport, idx, ConnectionHandle, Reason, to):

    ConnectionHandle &= 0x0fff

    cmd = struct.pack('<HHHHB', Commands.CMD_LE_REJECT_CIS_REQUEST_REQ, 5, HCICommands.BT_HCI_OP_LE_REJECT_CIS_REQUEST,
                      ConnectionHandle, Reason)
    transport.send(idx, cmd)

    packet = transport.recv(idx, 7, to)

    if ( 7 != len(packet) ):
        raise Exception("LE Reject CIS Request command failed: Response too short (Expected %i bytes got %i bytes)" % (7, len(packet)))

    RespCmd, RespLen, status, connectionHandle = struct.unpack('<HHBH', packet)

    if ( RespCmd != Commands.CMD_LE_REJECT_CIS_REQUEST_RSP ):
        raise Exception("LE Reject CIS Request command failed: Inappropriate command response received")

    if ( RespLen != 3 ):
        raise Exception("LE Reject CIS Request command failed: Response length field corrupted (%i)" % RespLen)

    return status, connectionHandle


def le_request_peer_sca(transport, idx, acl_conn_handle, to):
    """
    The command is used to read the Sleep Clock Accuracy (SCA) of the peer device.
    :param transport: bearer to be used
    :param idx: device index
    :param acl_conn_handle: Connection handle of the ACL
    :param to: Receiver timeout
    :return: command status
    """
    cmd_parameters = [HCICommands.BT_HCI_OP_LE_REQUEST_PEER_SCA, acl_conn_handle]
    edtt_send_cmd(transport, idx, Commands.CMD_HCI_LE_REQUEST_PEER_SCA_REQ, 'HH', cmd_parameters)

    return edtt_wait_cmd_cmpl(transport, idx, Commands.CMD_HCI_LE_REQUEST_PEER_SCA_RSP, 'B', to)[0]


"""
    The HCI_LE_Setup_ISO_Data_Path command is used to identify and create
    the isochronous data path between the Host and the Controller for an
    established CIS or BIS identified by the Connection_Handle parameter.
"""
def le_setup_iso_data_path(transport, idx, ConnectionHandle, DataPathDirection, DataPathId, CodecId, ControllerDelay,
                           CodecConfigurationLength, CodecConfiguration, to):

    ConnectionHandle &= 0x0fff

    cmd = struct.pack('<HHHHBB5B3BB' + str(CodecConfigurationLength) + 'B',
                      Commands.CMD_LE_SETUP_ISO_DATA_PATH_REQ, 15 + (CodecConfigurationLength * 1), HCICommands.BT_HCI_OP_LE_SETUP_ISO_DATA_PATH,
                      ConnectionHandle, DataPathDirection, DataPathId, *CodecId, *toArray(ControllerDelay, 3), CodecConfigurationLength, *CodecConfiguration)
    transport.send(idx, cmd)

    packet = transport.recv(idx, 7, to)

    if ( 7 != len(packet) ):
        raise Exception("LE Setup ISO Data Path command failed: Response too short (Expected %i bytes got %i bytes)" % (7, len(packet)))

    RespCmd, RespLen, status, connectionHandle = struct.unpack('<HHBH', packet)

    if ( RespCmd != Commands.CMD_LE_SETUP_ISO_DATA_PATH_RSP ):
        raise Exception("LE Setup ISO Data Path command failed: Inappropriate command response received")

    if ( RespLen != 3 ):
        raise Exception("LE Setup ISO Data Path command failed: Response length field corrupted (%i)" % RespLen)

    return status, connectionHandle

"""
    The HCI_LE_Remove_ISO_Data_Path command is used to remove the input
    and/or output data path(s) associated with a CIS or BIS identified by the
    Connection_Handle parameter.
"""
def le_remove_iso_data_path(transport, idx, ConnectionHandle, DataPathDirection, to):

    ConnectionHandle &= 0x0fff

    cmd = struct.pack('<HHHHB',
                      Commands.CMD_LE_REMOVE_ISO_DATA_PATH_REQ, 5, HCICommands.BT_HCI_OP_LE_REMOVE_ISO_DATA_PATH,
                      ConnectionHandle, DataPathDirection)
    transport.send(idx, cmd)

    packet = transport.recv(idx, 7, to)

    if ( 7 != len(packet) ):
        raise Exception("LE Remove ISO Data Path command failed: Response too short (Expected %i bytes got %i bytes)" % (7, len(packet)))

    RespCmd, RespLen, status, connectionHandle = struct.unpack('<HHBH', packet)

    if ( RespCmd != Commands.CMD_LE_REMOVE_ISO_DATA_PATH_RSP ):
        raise Exception("LE Remove ISO Data Path command failed: Inappropriate command response received")

    if ( RespLen != 3 ):
        raise Exception("LE Remove ISO Data Path command failed: Response length field corrupted (%i)" % RespLen)

    return status, connectionHandle

"""
    The HCI_LE_Set_Host_Feature command is used by the Host to set or clear a bit
    controlled by the Host in the Link Layer FeatureSet stored in the Controller.
"""
def le_set_host_feature(transport, idx, BitNumber, BitValue, to):

    cmd = struct.pack('<HHHBB', Commands.CMD_LE_SET_HOST_FEATURE_REQ, 4, HCICommands.BT_HCI_OP_LE_SET_HOST_FEATURE, BitNumber, BitValue)
    transport.send(idx, cmd)

    packet = transport.recv(idx, 5, to)

    if ( 5 != len(packet) ):
        raise Exception("LE Set Host Feature command failed: Response too short (Expected %i bytes got %i bytes)" % (5, len(packet)))

    RespCmd, RespLen, status = struct.unpack('<HHB', packet)

    if ( RespCmd != Commands.CMD_LE_SET_HOST_FEATURE_RSP ):
        raise Exception("LE Set Host Feature command failed: Inappropriate command response received")

    if ( RespLen != 1 ):
        raise Exception("LE Set Host Feature command failed: Response length field corrupted (%i)" % RespLen)

    return status


def get_ixit_value(transport, idx, ixit, to):
    """Request IXIT value from test device
    :param transport: bearer to be used
    :param idx: device index
    :param ixit: IXIT to read
    :param to: Receiver timeout
    :return: IXIT value
    """
    edtt_send_cmd(transport, idx, Commands.CMD_GET_IXIT_VALUE_REQ, 'BBB',
                  (ixit.profile_id, ixit.ref_major, ixit.ref_minor))
    return edtt_wait_cmd_cmpl(transport, idx, Commands.CMD_GET_IXIT_VALUE_RSP, ixit.value_fmt, to)[0]


def hci_le_iso_transmit_test(transport, idx, connection_handle, payload_type, to):
    """
    The command is used to configure an established CIS or BIS specified by the Connection_Handle parameter, and
    transmit test payloads which are generated by the Controller.
    :param transport: bearer to be used
    :param idx: device index
    :param connection_handle: CIS or BIS connection handle
    :param payload_type: defines the configuration of SDUs in the payload.
    :param to: Receiver timeout
    :return: (status, connection_handle)
    """
    edtt_send_cmd(transport, idx, Commands.CMD_HCI_LE_ISO_TRANSMIT_TEST_REQ, 'HHB',
                  (HCICommands.BT_HCI_OP_LE_ISO_TRANSMIT_TEST, connection_handle, payload_type))
    return edtt_wait_cmd_cmpl(transport, idx, Commands.CMD_HCI_LE_ISO_TRANSMIT_TEST_RSP, 'BH', to)


def hci_le_iso_receive_test(transport, idx, connection_handle, payload_type, to):
    """
    The command is used to configure an established CIS or a synchronized BIG specified by the Connection_Handle
    parameter to receive payloads.
    :param transport: bearer to be used
    :param idx: device index
    :param connection_handle: CIS or BIS connection handle
    :param payload_type: defines the configuration of SDUs in the payload.
    :param to: Receiver timeout
    :return: (status, connection_handle)
    """
    edtt_send_cmd(transport, idx, Commands.CMD_HCI_LE_ISO_RECEIVE_TEST_REQ, 'HHB',
                  (HCICommands.BT_HCI_OP_LE_ISO_RECEIVE_TEST, connection_handle, payload_type))
    return edtt_wait_cmd_cmpl(transport, idx, Commands.CMD_HCI_LE_ISO_RECEIVE_TEST_RSP, 'BH', to)


def hci_le_iso_read_test_counters_test(transport, idx, connection_handle, to):
    """
    The command is used to read the test counters in the Controller which is configured in ISO Receive Test mode for a
    CIS or BIS specified by the Connection_Handle. Reading the test counters does not reset the test counters.
    :param transport: bearer to be used
    :param idx: device index
    :param connection_handle: CIS or BIS connection handle
    :param to: Receiver timeout
    :return: (status, connection_handle, received_sdu_count, missed_sdu_count, failed_sdu_count)
    """
    edtt_send_cmd(transport, idx, Commands.CMD_HCI_LE_ISO_READ_TEST_COUNTERS_REQ, 'HH',
                  (HCICommands.BT_HCI_OP_LE_ISO_READ_TEST_COUNTERS, connection_handle))
    return edtt_wait_cmd_cmpl(transport, idx, Commands.CMD_HCI_LE_ISO_READ_TEST_COUNTERS_RSP, 'BHIII', to)


def hci_le_iso_test_end(transport, idx, connection_handle, to):
    """The command is used to terminate the ISO Transmit and/or Receive Test mode for a CIS or BIS specified by the
    Connection_Handle parameter but does not terminate the CIS or BIS.
    :param transport: bearer to be used
    :param idx: device index
    :param connection_handle: CIS or BIS connection handle
    :param to: Receiver timeout
    :return: (status, connection_handle, received_sdu_count, missed_sdu_count, failed_sdu_count)
    """
    edtt_send_cmd(transport, idx, Commands.CMD_HCI_LE_ISO_TEST_END_REQ, 'HH', (HCICommands.BT_HCI_OP_LE_ISO_TEST_END,
                                                                               connection_handle))
    return edtt_wait_cmd_cmpl(transport, idx, Commands.CMD_HCI_LE_ISO_TEST_END_RSP, 'BHIII', to)
