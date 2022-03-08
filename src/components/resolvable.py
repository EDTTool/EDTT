# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

from enum import IntEnum;
from components.utils import *;
from components.basic_commands import *;
from components.address import *;
from components.events import *;

class AddressResolution(IntEnum):
    DISABLE = 0                    # Disable Private Address resolution
    ENABLE  = 1                    # Enable Private Address resolution

class PrivacyMode(IntEnum):
    NETWORK_PRIVACY = 0
    DEVICE_PRIVACY  = 1

class ResolvableAddresses:
    """
        Resolvable Addresses handles some aspects of Resolvable Private Addresses.
        - Clear List of Resolvable Private Addresses.
        - Add Device to List of Resolvable Private Addresses.
        - Remove Device from List of Resolvable Private Addresses.
        - Set timeout for changing a Resolvable Private Address.
        - Enable resolving of Private Resolvable Addresses.
        - Disable resolving of Private Resolvable Addresses.
    """
    """
        Constructor:
            transport - PTTT_nwtsim object
            idx       - Number; Device identifier
            trace     - Trace object
            localIRK  - Array of 16 Bytes holding the Local IRK or None if Local IRK is 16 zeros.
    """
    def __init__(self, transport, idx, trace, localIRK=None):
        self.transport = transport;
        self.idx = idx;
        self.trace = trace;
        self.localIRK = [ 0 for _ in range(16) ] if localIRK is None else localIRK[ : ];
        self.rawMode = True;

    def __verifyAndShowEvent(self, expectedEvent):
        event = get_event(self.transport, self.idx, 100);
        self.trace.trace(7, str(event));
        return event.event == expectedEvent;

    def __getCommandCompleteEvent(self):
        return not self.rawMode or self.__verifyAndShowEvent(Events.BT_HCI_EVT_CMD_COMPLETE);

    """
        Clear list of Resolvable Addresses
    """
    def clear(self):
        status = le_clear_resolving_list(self.transport, self.idx, 100);
        self.trace.trace(6, "LE Clear Resolving List Command returns status: 0x%02X" % status);
        return self.__getCommandCompleteEvent() and (status == 0);

    """
        Add entry to list of Resolvable Addresses

        peerAddress is an Address object; A SimpleAddressType Identity address
        peerIRK     is None or an array of 16 Bytes
    """
    def add(self, peerAddress, peerIRK=None):
        if peerIRK is None:
            peerIRK = [ 0 for _ in range(16) ];
        status = le_add_device_to_resolving_list(self.transport, self.idx, peerAddress.type, peerAddress.address, peerIRK, self.localIRK, 100);
        self.trace.trace(6, "LE Add Device to Resolving List Command returns status: 0x%02X" % status);
        return self.__getCommandCompleteEvent() and (status == 0);

    """
        Remove entry from list of Resolvable Addresses

        peerAddress is an Address object; A SimpleAddressType Identity address
    """
    def remove(self, peerAddress):
        status = le_remove_device_from_resolving_list(self.transport, self.idx, peerAddress.type, peerAddress.address, 100);
        self.trace.trace(6, "LE Remove Device from Resolving List Command returns status: 0x%02X" % status);
        return self.__getCommandCompleteEvent() and (status == 0);
    
    def __enable(self, enable):
        status = le_set_address_resolution_enable(self.transport, self.idx, enable, 100);
        self.trace.trace(6, "LE Set Address Resolution " + ("Enable" if enable else "Disable") + " Command returns status: 0x%02X" % status);
        return self.__getCommandCompleteEvent() and (status == 0);
    
    """
        Enable Address Resolution via list of Resolvable Addresses
    """
    def enable(self):
        return self.__enable(AddressResolution.ENABLE);

    """
        Disable Address Resolution via list of Resolvable Addresses
    """
    def disable(self):
        return self.__enable(AddressResolution.DISABLE);

    """
        Set Timeout for Address Resolution via list of Resolvable Addresses
    """
    def timeout(self, timeout):
        status = le_set_resolvable_private_address_timeout(self.transport, self.idx, timeout, 100);
        self.trace.trace(6, "LE Set Resolvable Private Address Timeout Command returns status: 0x%02X" % status);
        return self.__getCommandCompleteEvent() and (status == 0);

