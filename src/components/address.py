# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

from enum import IntEnum;
from components.utils import *;

class SimpleAddressType(IntEnum):
    PUBLIC               = 0       # Public Device Address (default)
    RANDOM               = 1       # Random Device Address

class ExtendedAddressType(IntEnum):
    PUBLIC               = 0       # Public Device Address (default)
    RANDOM               = 1       # Random Device Address
    RESOLVABLE_OR_PUBLIC = 2       # Controller generates Resolvable Private Address based on the local IRK from the resolving list.
                                   # If the resolving list contains no matching entry, use the public address.
    RESOLVABLE_OR_RANDOM = 3       # Controller generates Resolvable Private Address based on the local IRK from the resolving list.
                                   # If the resolving list contains no matching entry, use the random address from LE_Set_Random_Address.

class IdentityAddressType(IntEnum):
    PUBLIC               = 0       # Public Device Address.
    RANDOM               = 1       # Random Device Address.
    PUBLIC_IDENTITY      = 2       # Public Identity Address (Corresponds to peer’s Resolvable Private Address).
                                   # This value shall only be used by the Host if either the Host or the Controller does not support the LE Set Privacy Mode command.
    RANDOM_IDENTITY      = 3       # Random (static) Identity Address (Corresponds to peer’s Resolvable Private Address).
                                   # This value shall only be used by a Host if either the Host or the Controller does not support the LE Set Privacy Mode command.

class Address:

    def __init__(self, addressType, address=None):
        self.type = addressType;
        if not address is None:
            if isinstance( address, (list, tuple) ):
                self.address = list(address[ : ]);
            else:
                self.address = toArray(address, 6);
        else:
            self.address = toArray(0, 6);

    def isStaticRandom(self):
        return (self.address[5] & 0xC0) == 0xC0;
    
    def isResolvablePrivate(self):
        return (self.address[5] & 0xC0) == 0x40;
    
    def isNonResolvablePrivate(self):
        return (self.address[5] & 0xC0) == 0;
    
    def __str__(self):
        result = '{5:02X}:{4:02X}:{3:02X}:{2:02X}:{1:02X}:{0:02X}'.format(*self.address);
        if self.type is None:
            return result;
        elif ExtendedAddressType.PUBLIC == self.type:
            result += '(P)';
        elif ExtendedAddressType.RANDOM == self.type:
            result += '(R)';
        elif ExtendedAddressType.RESOLVABLE_OR_PUBLIC == self.type:
            result += '(p)';
        elif ExtendedAddressType.RESOLVABLE_OR_RANDOM == self.type:
            result += '(r)';
        elif 0xFE == self.type:
            result += '(u)'; # Random Device Address (Controller unable to resolve)
        elif 0xFF == self.type:
            result += '(a)'; # No address provided (anonymous advertisement)
        else:
            result += '(?)';
        return result;

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if (self.type is None) != (other.type is None):
                return False;
            return (self.type == other.type) and (self.address == other.address);
        return False;

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            if (self.type is None) != (other.type is None):
                return True;
            return (self.type != other.type) or (self.address != other.address);
        return True;
