# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

from enum import IntEnum;
from components.utils import *;
from components.basic_commands import *;
from components.address import *;
from components.events import *;

class Advertising(IntEnum):
    CONNECTABLE_UNDIRECTED     = 0 # Connectable undirected advertising (ADV_IND) (default).
    CONNECTABLE_HDC_DIRECTED   = 1 # Connectable high duty cycle directed advertising (ADV_DIRECT_IND, high duty cycle).
    SCANNABLE_UNDIRECTED       = 2 # Scannable undirected advertising (ADV_SCAN_IND).
    NON_CONNECTABLE_UNDIRECTED = 3 # Non connectable undirected advertising (ADV_NONCONN_IND).
    CONNECTABLE_LDC_DIRECTED   = 4 # Connectable low duty cycle directed advertising (ADV_DIRECT_IND, low duty cycle).

class Advertise(IntEnum):
    DISABLE = 0                    # Disable Advertising
    ENABLE  = 1                    # Enable Advertising

class AdvertisingFilterPolicy(IntEnum):
    FILTER_NONE                = 0 # Process scan and connection requests from all devices (i.e., the Filter Accept List is not in use) (default).
    FILTER_SCAN_REQUESTS       = 1 # Process connection requests from all devices and only scan requests from devices that are in the Filter Accept List.
    FILTER_CONNECTION_REQUESTS = 2 # Process scan requests from all devices and only connection requests from devices that are in the Filter Accept List.
    FILTER_BOTH_REQUESTS       = 3 # Process scan and connection requests only from devices in the Filter Accept List.

class AdvertiseChannel(IntEnum):
    CHANNEL_37   = 1               # Advertise on channel 37
    CHANNEL_38   = 2               # Advertise on channel 38
    CHANNEL_39   = 4               # Advertise on channel 39
    ALL_CHANNELS = 7               # Advertise on all three channels

class ExtAdvertiseType(IntEnum):
    CONNECTABLE              =  1  # bit 0 ~ Connectable advertising
    SCANNABLE                =  2  # bit 1 ~ Scannable advertising
    DIRECTED                 =  4  # bit 2 ~ Directed advertising
    CONNECTABLE_HDC_DIRECTED =  8  # bit 3 ~ High Duty Cycle Directed Connectable advertising (≤ 3.75 ms Advertising Interval)
    LEGACY                   = 16  # bit 4 ~ Use legacy advertising PDUs
    ANONYMOUS                = 32  # bit 5 ~ Omit advertiser's address from all PDUs ("anonymous advertising")
    INCLUDE_TX_POWER         = 64  # bit 6 ~ Include TxPower in the extended header of the advertising PDU

class Advertiser:
    """
        An Advertiser handles all aspects of advertising.
        - Set Advertising parameters including Advertising data.
        - Set Scan response data.
        - Enable Advertising.
        - Disable Advertising.
    """
    """
        Constructor:
            transport     - EDTTT object
            idx           - Number; Device identifier
            trace         - Trace object
            channels      - AdvertiseChannels enum holding the channel or channels to advertise on
            advertiseType - Advertising enum holding the type of advertising to emit
            ownAddress    - Address object with an ExtendedAddressType address (only the address type is used)
            peerAddress   - Address object with a SimpleAddressType address (both address type and address are used)
            filterPolicy  - AdvertisingFilterPolicy enum
            advertiseData - Array of Bytes holding advertise data
            responseData  - Array of Bytes holding response data
    """
    def __init__(self, transport, idx, trace, channels, advertiseType, ownAddress, peerAddress, filterPolicy=AdvertisingFilterPolicy.FILTER_NONE, \
                       advertiseData=None, responseData=None):
        self.transport = transport;
        self.idx = idx;
        self.trace = trace;
        self.channels = channels;
        self.advertiseType = advertiseType;
        """
            Own_Address_Type parameter indicates the type of address being used in the advertising packets.

            If Own_Address_Type equals 0x02 or 0x03, the Peer_Address parameter contains the peer’s Identity Address and
            the Peer_Address_Type parameter contains the Peer’s Identity Type (i.e. 0x00 or 0x01).
            These parameters are used to locate the corresponding local IRK in the resolving list; this IRK is used to generate
            the own address used in the advertisement.

            If Own_Address_Type equals 0x02 or 0x03, the Controller generates the peer’s Resolvable Private Address using the
            peer’s IRK corresponding to the peer’s Identity Address contained in the Peer_Address parameter and peer’s Identity
            Address Type (i.e. 0x00 or 0x01) contained in the Peer_Address_Type parameter.

            If directed advertising is performed, i.e. when Advertising_Type is set to 0x01 (ADV_DIRECT_IND, high duty cycle) or
            0x04 (ADV_DIRECT_IND, low duty cycle mode), then the Peer_Address_Type and Peer_Address shall be valid.
        """
        self.ownAddress = ownAddress;
        self.peerAddress = peerAddress;

        self.advertiseData = [] if advertiseData is None else advertiseData[ : ];
        self.responseData = [] if responseData is None else responseData[ : ];
        """
            The Advertising_Interval_Min shall be less than or equal to the Advertising_Interval_Max.
            The Advertising_Interval_Min and Advertising_Interval_Max should not be the same value to enable the Controller to
            determine the best advertising interval given other activities.

            For high duty cycle directed advertising, i.e. when Advertising_Type is 0x01 (ADV_DIRECT_IND, high duty cycle),
            the Advertising_Interval_Min and Advertising_Interval_Max parameters are not used and shall be ignored.
        """
        self.minInterval = 32; # Minimum Advertise Interval = 32 x 0.625 ms = 20.00 ms
        self.maxInterval = 32; # Maximum Advertise Interval = 32 x 0.625 ms = 20.00 ms
        self.filterPolicy = filterPolicy;
        self.status = 0;

    def __verifyAndShowEvent(self, expectedEvent):
        event = get_event(self.transport, self.idx, 200);
        self.trace.trace(7, str(event));
        return event.event == expectedEvent;

    def __getCommandCompleteEvent(self):
        return self.__verifyAndShowEvent(Events.BT_HCI_EVT_CMD_COMPLETE);

    def __confined_array(self, data, limit):
        dataSize = len(data) if len(data) <= limit else limit;
        dataCopy = data[ : ];
        if len(data) < limit:
            dataCopy += [0 for _ in range(limit - dataSize)];
        elif len(data) > limit:
            dataCopy = dataCopy[:limit];
        return dataSize, dataCopy;

    def __set_advertise_parameters(self):

        self.status = le_set_advertising_parameters(self.transport, self.idx, self.minInterval, self.maxInterval, self.advertiseType, self.ownAddress.type, \
                                                    self.peerAddress.type, self.peerAddress.address, self.channels, self.filterPolicy, 200);
        self.trace.trace(6, "LE Set Advertising Parameters Command returns status: 0x%02X" % self.status);
        return self.__getCommandCompleteEvent() and (self.status == 0);

    def __set_advertise_data(self):

        dataSize, advertiseData = self.__confined_array(self.advertiseData, 31);

        self.status = le_set_advertising_data(self.transport, self.idx, dataSize, advertiseData, 200);
        self.trace.trace(6, "LE Set Advertising Data Command returns status: 0x%02X" % self.status);
        return self.__getCommandCompleteEvent() and (self.status == 0);

    def __set_scan_response(self):

        dataSize, responseData = self.__confined_array(self.responseData, 31);
            
        self.status = le_set_scan_response_data(self.transport, self.idx, dataSize, responseData, 200);
        self.trace.trace(6, "LE Set Scan Response Data Command returns status: 0x%02X" % self.status);
        return self.__getCommandCompleteEvent() and (self.status == 0);

    def __advertise_enable(self, enable):
    
        self.status = le_set_advertising_enable(self.transport, self.idx, enable, 200);
        self.trace.trace(6, "LE Set Advertising Enable Command (%s) returns status: 0x%02X" % ("Enabling" if enable else "Disabling", self.status));
        return self.__getCommandCompleteEvent() and (self.status == 0);

    """
        Enable advertising - start emitting Advertise packages
    """
    def enable(self, sameSetup=False):
        if not sameSetup:
            success = self.__set_advertise_parameters();
            success = success and self.__set_advertise_data();
            success = success and self.__set_scan_response();
        else:
            success = True;
        success = success and self.__advertise_enable(Advertise.ENABLE);
        return success;

    """
        Disable advertising - stop emitting Advertise packages
    """
    def disable(self):
        return self.__advertise_enable(Advertise.DISABLE);

    """
        Check for a advertise timeout - when using connectable high duty cycle directed advertising
    """
    def timeout(self, timeout=200):
        self.status = 0;
        if has_event(self.transport, self.idx, timeout)[0]:
            event = get_event(self.transport, self.idx, 200);
            self.trace.trace(7, str(event));
            if (event.subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_COMPLETE) or (event.subEvent == MetaEvents.BT_HCI_EVT_LE_ENH_CONN_COMPLETE):
                self.status = event.decode()[0];
        return self.status == 0x3C;
