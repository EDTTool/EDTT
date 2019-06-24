# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

from enum import IntEnum;
from components.utils import *;
from components.basic_commands import *;
from components.address import *;

class InitiatorFilterPolicy(IntEnum):
    FILTER_NONE            = 0     # White list is not used to determine which advertiser to connect to. Peer_Address_Type and Peer_Address shall be used.
    FILTER_WHITE_LIST_ONLY = 1     # White list is used to determine which advertiser to connect to. Peer_Address_Type and Peer_Address shall be ignored.

class Initiator:
    """
        A Initiator can create and destroy connections.
        - Set parameters for connection creation
        - Monitor connection status
        - Terminate connection
    """
    """
        Constructor:
            transport         - PTTT_nwtsim object
            initiator         - Number; Device identifier
            peer              - Number; Device identifier
            trace             - Trace object
            initiatorAddress  - ExtendedAddressType enum holding the address of the initiator (only the address type is used)
            peerAddress       - IdentityAddressType enum holding the address of the peer (both type and address are used)
            filterPolicy      - InitiatorFilterPolicy enum holding the type of scanning filter to apply
    """
    def __init__(self, transport, initiator, peer, trace, initiatorAddress, peerAddress, filterPolicy=InitiatorFilterPolicy.FILTER_NONE):
        self.transport = transport;
        self.initiator = initiator;
        self.peer = peer;
        self.trace = trace;
        self.initiatorAddress = initiatorAddress;
        self.peerAddress = peerAddress;
        self.filterPolicy = filterPolicy;
        
        self.RPAs = [ [ 0 for _ in range(6) ], [ 0 for _ in range(6) ] ];        
        self.handles = [-1, -1];
        self.reasons = [-1, -1];
        self.txPhys = self.rxPhys = -1;

        """
           Note: intervalMin shall not be greater than intervalMax.
                 supervisionTimeout in milliseconds shall be larger than (1 + latency) * intervalMax * 2, where intervalMax is in milliseconds.

                 With intervalMax =    6 -> supervisionTimeout >   12 * 1.25 ms =   15 ms (with a latency of zero)
                      intervalMax =   24 -> supervisionTimeout >   48 * 1.25 ms =   60 ms (with a latency of zero)
                      intervalMax = 3200 -> supervisionTimeout > 6400 * 1.25 ms = 8000 ms (with a latency of zero) 
        """
        self.scanInterval       = 32; # Scan Interval := 32 x 0.625 ms = 20 ms
        self.scanWindow         = 32; # Scan Window   := 32 x 0.625 ms = 20 ms
        self.intervalMin        = 24; # Minimum Connection interval := 24 x 1.25 ms = 30 ms
        self.intervalMax        = 24; # Maximum Connection interval := 24 x 1.25 ms = 30 ms
        self.latency            = 0;  # Don't allow peer to skip any connection events
        self.supervisionTimeout = 25; # Supervision timeout := 25 x 10 ms = 250 ms.
        self.minCeLen           = 0;  # Minimum Connection event interval = 0 x 0.625 ms = 0 ms
        self.maxCeLen           = 0;  # Maximum Connection event interval = 0 x 0.625 ms = 0 ms

        self.status             = 0;
        self.prevInterval       = 0;
        self.pre_connected = self.pre_updated = self.__rolesSwitched = False;

    """
        Private Event handles procedures... 

        Check for LE Connection Complete Event | LE Enhanced Connection Complete Event...
    """
    def __hasConnectionCompleteEvent(self, idx, timeout):

        handle = role = interval = -1;
        localRPA = [0 for _ in range(6)];

        success = has_event(self.transport, idx, timeout); 
        if success:
            eventTime, event, subEvent, eventData = get_event(self.transport, idx, 100);
            success = (subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_COMPLETE) or (subEvent == MetaEvents.BT_HCI_EVT_LE_ENH_CONN_COMPLETE);
            showEvent(event, eventData, self.trace);
            if success:
                self.status, handle, role, addressType, address, localRPA, peerRPA, interval = connectionComplete(eventData)[:8];
                success = (self.status == 0);
        return success, handle, role, localRPA, interval;

    """
        Check for Disconnect Complete Event...
    """
    def __hasDisconnectCompleteEvent(self, idx, timeout):

        handle = reason = -1;

        success = has_event(self.transport, idx, timeout);
        if success:        
            eventTime, event, subEvent, eventData = get_event(self.transport, idx, 100);
            success = (event == Events.BT_HCI_EVT_DISCONN_COMPLETE);
            showEvent(event, eventData, self.trace);
            if success:
                self.status, handle, reason = disconnectComplete(eventData);
                success = (self.status == 0);

        return success, handle, reason;

    """
        Check for LE PHY Update Complete Event...
    """
    def __hasPhysUpdateCompleteEvent(self, idx, timeout):
        
        txPhys = rxPhys = -1;

        success = has_event(self.transport, idx, timeout);
        if success:
            eventTime, event, subEvent, eventData = get_event(self.transport, idx, 100);
            success = subEvent == MetaEvents.BT_HCI_EVT_LE_PHY_UPDATE_COMPLETE;
            showEvent(event, eventData, self.trace);
            if success:
                self.status, handle, txPhys, rxPhys = physicalUpdated(eventData);
                success = (self.status == 0);

        return success, txPhys, rxPhys;

    """
        Check for LE Connection Parameter Update Request Event...
    """
    def __hasConnectionParamRequestEvent(self, idx, timeout):

        handle = minInterval = maxInterval = latency = supervisionTimeout = -1;

        success = has_event(self.transport, idx, timeout); 
        if success:
            eventTime, event, subEvent, eventData = get_event(self.transport, idx, 100);
            success = subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_PARAM_REQ;
            showEvent(event, eventData, self.trace);
            if success:
                handle, minInterval, maxInterval, latency, supervisionTimeout = remoteConnectionParameterRequest(eventData);

        return success, handle, minInterval, maxInterval, latency, supervisionTimeout;

    """
        Check for LE Connection Parameter Update Complete Event...
    """
    def __hasConnectionUpdateCompleteEvent(self, idx, timeout):
        status = handle = interval = latency = visionTimeout = -1;
        
        success = has_event(self.transport, idx, timeout);
        if success:
            eventTime, event, subEvent, eventData = get_event(self.transport, idx, 100);
            success = subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_UPDATE_COMPLETE;
            showEvent(event, eventData, self.trace);
            if success:                    
                status, handle, interval, latency, visionTimeout = connectionUpdated(eventData);
                success = (status == 0);

        return success, status, handle, interval, latency, visionTimeout;

    """
        Send Create Connection command...
    """
    def __initiating(self):

        try:
            le_create_connection(self.transport, self.initiator, self.scanInterval, self.scanWindow, self.filterPolicy, self.peerAddress.type, self.peerAddress.address, self.initiatorAddress.type, self.intervalMin, self.intervalMax, self.latency, self.supervisionTimeout, self.minCeLen, self.maxCeLen, 100);
            eventTime, event, subEvent, eventData = get_event(self.transport, self.initiator, 100);
            self.status = ord(eventData[0]);
            success = (event == Events.BT_HCI_EVT_CMD_STATUS) and (self.status == 0);
            self.trace.trace(6, "LE Create Connection Command returns status: 0x%02X" % self.status);
            showEvent(event, eventData, self.trace);
        except Exception as e: 
            self.trace.trace(3, "LE Create Connection Command failed: %s" % str(e));
            success = False;

        return success;

    """
        Send Disconnect command...
    """
    def __terminating(self, reason):

        try:
            disconnect(self.transport, self.initiator, self.handles[0], reason, 100);
            more = has_event(self.transport, self.initiator, 100);
            while more:
                eventTime, event, subEvent, eventData = get_event(self.transport, self.initiator, 100);
                if event == Events.BT_HCI_EVT_CMD_STATUS:
                    status, packets, opcode = struct.unpack('<BBH', eventData);
                    if opcode == HCICommands.BT_HCI_OP_DISCONNECT:
                        self.status = status;
                        self.trace.trace(6, "Disconnect Command returns status: 0x%02X" % self.status);
                        success = self.status == 0;
                        break; 
                showEvent(event, eventData, self.trace);
                more = has_event(self.transport, self.initiator, 100);

        except Exception as e: 
            self.trace.trace(3, "Disconnect Command failed: %s" % str(e));
            success = False;

        return success;

    """
        Send LE Connection Update command...
    """
    def __update(self, minInterval, maxInterval, latency, timeout):

        try:
            if 4 * timeout <= (1+latency) * maxInterval:
                timeout = (((1+latency) * maxInterval) + 7) / 4;

            self.status = le_connection_update(self.transport, self.initiator, self.handles[0], minInterval, maxInterval, latency, timeout, self.minCeLen, self.maxCeLen, 100);
            eventTime, event, subEvent, eventData = get_event(self.transport, self.initiator, 100);
            success = (event == Events.BT_HCI_EVT_CMD_STATUS) and (self.status == 0);
            self.trace.trace(6, "LE Connection Update Command returns status: 0x%02X" % self.status);
            showEvent(event, eventData, self.trace);
        except Exception as e: 
            self.trace.trace(3, "LE Connection Update Command failed: %s" % str(e));
            success = False;

        return success;

    """
        Send LE Set PHY command...
    """
    def __updatePhys(self, allPhys, txPhys, rxPhys, optionPhys):

        try:
            self.status = le_set_phy(self.transport, self.initiator, self.handles[0], allPhys, txPhys, rxPhys, optionPhys, 100);
            eventTime, event, subEvent, eventData = get_event(self.transport, self.initiator, 100);
            success = (event == Events.BT_HCI_EVT_CMD_STATUS) and (self.status == 0);
            self.trace.trace(6, "LE Set PHY Command returns status: 0x%02X" % self.status);
            showEvent(event, eventData, self.trace);
        except Exception as e: 
            self.trace.trace(3, "LE Set PHY Command failed: %s" % str(e));
            success = False;

        return success;

    def __updatedPhys(self):
        """
            Initiator should receive a LE_PHY_Update_Complete event to signal that the command has been effectuated (could be no change)...
        """
        success, txPhys, rxPhys = self.__hasPhysUpdateCompleteEvent(self.initiator, 1000);
                        
        if success and ((txPhys != self.txPhys) or (rxPhys != self.rxPhys)):
            self.txPhys = txPhys; self.rxPhys = rxPhys;
            """
                If Phys has changed - Peer should also receive a LE_PHY_Update_Complete event to signal that the command has been effectuated...
            """
            if not self.peer is None:
                success, txPhys, rxPhys = self.__hasPhysUpdateCompleteEvent(self.peer, 100);

        return success;

    """
        Carry out first part of the connect procedure...
    """
    def preConnect(self):
        self.pre_connected = self.__initiating();
        return self.pre_connected;

    """
        Carry out last part of the connect procedure...
    """
    def postConnect(self):
        success = self.pre_connected;
        """
            Both initiator and peer can receive a LE Connection Complete Event if connection succeeds...
        """
        if success:
            """
                Check for LE Connection Complete Event | LE Enhanced Connection Complete Event in initiator...
            """
            initiatorConnected, handle, role, localRPA, interval = self.__hasConnectionCompleteEvent(self.initiator, 300);
            if initiatorConnected:
                self.handles[0] = handle; self.prevInterval = interval;
                self.RPAs[0] = localRPA[ : ];
                self.trace.trace(7, "%s is %s" % ('UpperTester' if self.initiator == 0 else 'LowerTester', 'MASTER' if role == 0 else 'SLAVE'));
            """
                Check for LE Connection Complete Event | LE Enhanced Connection Complete Event in peer...
            """
            if not self.peer is None:
                peerConnected, handle, role, localRPA, interval = self.__hasConnectionCompleteEvent(self.peer, 100);
                if peerConnected:
                    self.handles[1] = handle;
                    self.RPAs[1] = localRPA[ : ];
                    self.trace.trace(7, "%s is %s" % ('UpperTester' if self.peer == 0 else 'LowerTester', 'MASTER' if role == 0 else 'SLAVE'));
            else:
                peerConnected = True;
            """
                Check for Disconnection Complete Event in initiator...
            """
            initiatorDisconnected, handle, reason = self.__hasDisconnectCompleteEvent(self.initiator, 200);
            if initiatorDisconnected:
                self.handles[0] = -1;
                initiatorConnected = False;

        return success and initiatorConnected and peerConnected;
        
    """
        Carry out the connect procedure...
    """
    def connect(self):
        success = self.preConnect();
        success = success and self.postConnect(); 
        if success:
            self.txPhys = self.rxPhys = 1;

        return success;

    """
        Disconnect...
    """
    def disconnect(self, reason):
        success = self.__terminating(reason) if not self.handles[0] == -1 else False;
        """
            Both initiator and peer can receive a Disconnection Complete Events...
        """
        if success:
            initiatorDisconnected, handle, reason = self.__hasDisconnectCompleteEvent(self.initiator, 100 * int((99 + 10 * self.prevInterval) / 100));
            if initiatorDisconnected:
                self.handles[0] = -1; self.reasons[0] = reason;
            
            if not self.peer is None:
                peerDisconnected, handle, reason = self.__hasDisconnectCompleteEvent(self.peer, 200);
                if peerDisconnected:
                    self.handles[1] = -1; self.reasons[1] = reason;
            else:
                peerDisconnected = True;
                        
        return success and initiatorDisconnected and peerDisconnected;

    """
        Update connection parameters...
    """
    def update(self, minInterval, maxInterval, latency, timeout):
        self.pre_updated = self.__update(minInterval, maxInterval, latency, timeout) if not self.handles[0] == -1 else False;
        return self.pre_updated;
    
    """
        Accept the request for connection parameters update, by responding to the LE Remote Connection Parameter Request Event...
    """
    def acceptUpdate(self):
        success = self.pre_updated;
        
        if success and not self.peer is None:
            """
                Verify that the peer receives a LE Remote Connection Parameter Request Event...
            """
            success, handle, minInterval, maxInterval, latency, timeout = self.__hasConnectionParamRequestEvent(self.peer, 3200);
            if success:
                """
                    Send a LL_CONNECTION_PARAM_RSP as a reaction to the LE Remote Connection Parameter Request Event...
                """
                status, handle = le_remote_connection_parameter_request_reply(self.transport, self.peer, handle, minInterval, maxInterval, latency, timeout, self.minCeLen, self.maxCeLen, 100);
                success = (status == 0);
                eventTime, event, subEvent, eventData = get_event(self.transport, self.peer, 100);
                showEvent(event, eventData, self.trace);
                success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);

        return success;

    """
        Reject the request for connection parameters update, by responding to the LE Remote Connection Parameter Request Event...
    """
    def rejectUpdate(self, reason):
        success = self.pre_updated;
        
        if success and not self.peer is None:
            """
                Verify that the peer receives a LE Remote Connection Parameter Request Event...
            """
            success, handle, minInterval, maxInterval, latency, timeout = self.__hasConnectionParamRequestEvent(self.peer, 3200);
            if success:
                """
                    Send a LL_REJECT_EXT_IND as a reaction to the LE Remote Connection Parameter Request Event...
                """
                status, handle = le_remote_connection_parameter_request_negative_reply(self.transport, self.peer, handle, reason, 100);
                success = status == 0;
                eventTime, event, subEvent, eventData = get_event(self.transport, self.peer, 100);
                showEvent(event, eventData, self.trace);
                success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);

        return success;

    def updated(self):
        success = self.pre_updated;

        if success:
            """
                Check for LE Connection Update Complete Event in initiator...
                NOTE: Timing depends on the connect interval in effect - update is usually 6 events after previous reponse event
            """
            initiatorUpdated, self.status, handle, interval, latency, timeout = self.__hasConnectionUpdateCompleteEvent(self.initiator, 100 * int((99 + 10 * self.prevInterval) / 100));
            initiatorUpdated = initiatorUpdated and (self.handles[0] == handle);           
            if initiatorUpdated:
                self.intervalMin = self.intervalMax = self.prevInterval = interval;
                self.latency = latency;
                self.supervisionTimeout = timeout;

            """
                Check for LE Connection Update Complete Event in peer...
            """
            if not self.peer is None:
                peerUpdated, status, handle, interval, latency, timeout = self.__hasConnectionUpdateCompleteEvent(self.peer, 200);
                peerUpdated = peerUpdated and (self.handles[1] == handle);
            else:
                peerUpdated = True;
            
            success = initiatorUpdated and peerUpdated;

        return success;
 
    def updatePhys(self, allPhys, txPhys, rxPhys, optionPhys):
        success = self.__updatePhys(allPhys, txPhys, rxPhys, optionPhys) if not self.handles[0] == -1 else False;
        
        if success:
            success = self.__updatedPhys();

        return success;

    """
        Switch roles of initiator and peer - used to let the peer do an update ...
    """
    def switchRoles(self):
        self.initiator, self.peer = self.peer, self.initiator;
        self.handles[0], self.handles[1] = self.handles[1], self.handles[0];
        self.__rolesSwitched ^= True;

    """
        Reset roles of initiator and peer - if they vere switched ...
    """
    def resetRoles(self):
        if self.__rolesSwitched:
            self.switchRoles();

    """
        Obtain local Resolvable Private Address from LE Enhanced Connection Complete Event ...
    """
    def localRPA(self):
        return self.RPAs[0];

    """
        Obtain peer Resolvable Private Address from LE Enhanced Connection Complete Event ...
    """
    def peerRPA(self):
        return self.RPAs[1];
