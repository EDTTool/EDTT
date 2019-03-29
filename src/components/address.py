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
            self.address = toArray(0L, 6);

    def __str__(self):
        return formatAddress( self.address, self.type );

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return ((self.type & 1) == (other.type & 1)) and (self.address == other.address);
        return False;

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return ((self.type & 1) != (other.type & 1)) or (self.address != other.address);
        return True;
