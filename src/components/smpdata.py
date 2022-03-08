# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

import string;
from enum import IntEnum;
from components.utils import *;

SMP_CID = 6;

class SMPCapability(IntEnum):
    SMP_CAP_DISPLAY_ONLY                 =   0 # Display Only
    SMP_CAP_DISPLAY_YES_NO               =   1 # Display Yes or No
    SMP_CAP_KEYBOARD_ONLY                =   2 # Keyboard Only
    SMP_CAP_NO_INPUT_NO_OUTPUT           =   3 # No Input and No Output
    SMP_CAP_KEYBOARD_DISPLAY             =   4 # Keyboard and Display

class SMPOOBFlag(IntEnum):
    SMP_OOB_NO_AUTH_DATA                 =   0 # OOB Authentication data not present
    SMP_OOB_AUTH_DATA_PRESENT            =   1 # OOB Authentication data from remote device present

class SMPBondingFlag(IntEnum):
    SMP_BOND_NONE                        =   0 # No Bondig requested
    SMP_BOND_REQUESTED                   =   1 # Bonding requested

class SMPMITMFlag(IntEnum):                    # MITM - 'Man In The Middle' attacks protection
    SMP_MITM_NONE                        =   0 # No MITM protection requested
    SMP_MITM_REQUESTED                   =   4 # MITM protection requested

class SMPSecureConnections(IntEnum):
    SMP_SC_NOT_SUPPORTED                 =   0 # Secure Connections Pairing not supported
    SMP_SC_SUPPORTED                     =   8 # Secure Connections Pairing supported

class SMPKeyPressNotifications(IntEnum):
    SMP_KPN_NONE                         =   0 # Do not exchange Keypress Notifications
    SMP_KPN_REQUESTED                    =  16 # Do exchange Keypress Notifications

class SMPSupportH7(IntEnum):
    SMP_CT2_NO_SUPPORT                   =   0 # No support for the h7 security function
    SMP_CT2_SUPPORTED                    =  32 # Support for the h7 security function present

class SMPPasskey(IntEnum):
    SMP_PASSKEY_ENTRY_STARTED            =   0 # Passkey entry started
    SMP_PASSKEY_DIGIT_ENTERED            =   1 # Passkey digit entered
    SMP_PASSKEY_DIGIT_ERASED             =   2 # Passkey digit erased
    SMP_PASSKEY_CLEARED                  =   3 # Passkey entry cleared
    SMP_PASSKEY_ENTRY_COMPLETE           =   4 # Passkey entry completed

class SMPKeyGeneration(IntEnum):
    SMP_KEY_GEN_JUST_WORKS               =   0 # Just Works
    SMP_KEY_GEN_NUM_COMPARE              =   1 # Numeric Comparison (Only for LE Secure Connections)
    SMP_KEY_GEN_PASSKEY                  =   2 # PassKey Entry
    SMP_KEY_GEN_OOB                      =   3 # Out of Band

class SMPDistribution(IntEnum):
    SMP_DST_ENCKEY                       =   1 # Distribute LTK, EDIV and Rand (LE legacy pairing); ignored (Secure Connections)
    SMP_DST_IDKEY                        =   2 # Distribute IRK and BD_ADDR
    SMP_DST_SIGNKEY                      =   4 # Distribute CSRK
    SMP_DST_LINKKEY                      =   8 # Derive Link Key from LTK (Secure Connections); ignored (no Secure Connections)

class SMPOpcode(IntEnum):
    SMP_PAIRING_REQUEST                  =   1 # Pairing Request  - Pairing Feature Exchange - IO Capability, OOB data flag, AuthReq, Max. Encryption Key Size, Initiator Key Distribution, Responder Key Distribution
    SMP_PAIRING_RESPONSE                 =   2 # Pairing Response - Pairing Feature Exchange - IO Capability, OOB data flag, AuthReq, Max. Encryption Key Size, Initiator Key Distribution, Responder Key Distribution
    SMP_PAIRING_CONFIRM                  =   3 # Pairing Confirm  - Pairing Confirmation value
    SMP_PAIRING_RANDOM                   =   4 # Pairing Random   - Pairing Random value
    SMP_PAIRING_FAILED                   =   5 # Pairing Failed   - Pairing Failed reason
    SMP_ENCRYPTION_INFORMATION           =   6 # Encryption Information - Long Term Key
    SMP_CENTRAL_IDENTIFICATION            =   7 # Central Identification  - Dsitribute EDIV and Rand for encrypting future connections
    SMP_IDENTITY_INFORMATION             =   8 # Identity Information   - Distribute the IRK
    SMP_IDENTITY_ADDRESS_INFORMATION     =   9 # Identity Address Information - Distribute Public or Static Random device address
    SMP_SIGNING_INFORMATION              =  10 # Signing Information    - Distribute the CSRK
    SMP_SECURITY_REQUEST                 =  11 # Security Request       - Initiate security with the requested properties
    SMP_PAIRING_PUBLIC_KEY               =  12 # Pairing Public Key     - Distribute Public Keys X and Y
    SMP_PAIRING_DHKEY_CHECK              =  13 # Pairing DHKey Check    - Distribute DHKey Check
    SMP_PAIRING_KEYPRESS_NOTIFICATION    =  14 # Keypress Notification  - Inform about keys entered or erased

class SMPError(IntEnum):
    SMP_ERROR_PASSKEY                    =   1 # The user input of passkey failed, for example, the user cancelled the operation
    SMP_ERROR_OOB                        =   2 # The OOB data is not available
    SMP_ERROR_AUTHENTICATION             =   3 # The pairing procedure cannot be performed as authentication requirements cannot be met due to IO capabilities of one or both devices
    SMP_ERROR_CONFIRM                    =   4 # The confirm value does not match the calculated compare value
    SMP_ERROR_PAIRING                    =   5 # Pairing is not supported by the device
    SMP_ERROR_ENCRYPTION                 =   6 # The resultant encryption key size is insufficient for the security requirements of this device
    SMP_ERROR_COMMAND                    =   7 # The SMP command received is not supported on this device
    SMP_ERROR_REASON                     =   8 # Pairing failed due to an unspecified reason
    SMP_ERROR_REPEATED_ATTEMPTS          =   9 # Pairing or authentication procedure is disallowed because too little time has elapsed since last pairing request or security request
    SMP_ERROR_INVALID_PARAMETERS         =  10 # The invalid parameters error code indicates that the command length is invalid or that a parameter is outside the specified range
    SMP_ERROR_DHKEY_CHECK                =  11 # Indicates to the remote device that the DHKey Check value received doesn't match the one calculated by the local device
    SMP_ERROR_NUMERIC_COMPARISON         =  12 # Indicates that the confirm values in the numeric comparison protocol do not match
    SMP_ERROR_PAIRING_IN_PROGRESS        =  13 # Indicates that the pairing over the LE transport failed due to a Pairing Request sent over the BR/EDR transport
    SMP_ERROR_CROSS_KEY_GENERATION       =  14 # Indicates that the BR/EDR Link Key generated on the BR/EDR transport cannot be used to derive and distribute keys for the LE transport

class SMPData:

    def __init__(self):
        self.data = [];

    def encode(self, opcode, *args):
      #
      # encode ( SMPOpcode.SMP_PAIRING_REQUEST, <io_capability>, <oob_flag>, <auth_req>, <max_enq_key_size>, <init_key_dist>, <resp_key_dist> )
      #          where <io_capability> 1 octet, <oob_flag> 1 octet, <auth_req> 1 octet, <max_enq_key_size> 1 octet, <init_key_dist> 1 octet, <resp_key_dist> 1 octet
      #
        if   ( opcode == SMPOpcode.SMP_PAIRING_REQUEST ):
            self.data = [ opcode ] + list( args[:6] );
      #
      # encode ( SMPOpcode.SMP_PAIRING_RESPONSE, <io_capability>, <oob_flag>, <auth_req>, <max_enq_key_size>, <init_key_dist>, <resp_key_dist> )
      #          where <io_capability> 1 octet, <oob_flag> 1 octet, <auth_req> 1 octet, <max_enq_key_size> 1 octet, <init_key_dist> 1 octet, <resp_key_dist> 1 octet
      #
        elif ( opcode == SMPOpcode.SMP_PAIRING_RESPONSE ):
            self.data = [ opcode ] + list( args[:6] );
      #
      # encode ( SMPOpcode.SMP_PAIRING_CONFIRM, <confirm_value> )
      #       where <confirm_value> 16 octets
      #
        elif ( opcode == SMPOpcode.SMP_PAIRING_CONFIRM ):
            self.data = [ opcode ] + toArray( args[0], 16 );
      #
      # encode ( SMPOpcode.SMP_PAIRING_RANDOM, <random_value> )
      #       where <random_value> 16 octets
      #
        elif ( opcode == SMPOpcode.SMP_PAIRING_RANDOM ):
            self.data = [ opcode ] + toArray( args[0], 16 );
      #
      # encode ( SMPOpcode.SMP_PAIRING_FAILED, <reason> )
      #       where <reason> 1 octet
      #
        elif ( opcode == SMPOpcode.SMP_PAIRING_FAILED ):
            self.data = [ opcode ] + [ args[0] ];
      #
      # encode ( SMPOpcode.SMP_ENCRYPTION_INFORMATION, <ltk> )
      #       where <ltk> 16 octets
      #
        elif ( opcode == SMPOpcode.SMP_ENCRYPTION_INFORMATION ):
            self.data = [ opcode ] + toArray( args[0], 16 );
      #
      # encode ( SMPOpcode.SMP_CENTRAL_IDENTIFICATION, <ediv>, <rand> )
      #       where <ediv> 2 octets; <rand> 8 octets
      #
        elif ( opcode == SMPOpcode.SMP_CENTRAL_IDENTIFICATION ):
            self.data = [ opcode ] + toArray( args[0], 2 ) + toArray( args[1], 8 );
      #
      # encode ( SMPOpcode.SMP_IDENTITY_INFORMATION, <irk> )
      #       where <irk> 16 octets
      #
        elif ( opcode == SMPOpcode.SMP_IDENTITY_INFORMATION ):
            self.data = [ opcode ] + toArray( args[0], 16 );
      #
      # encode ( SMPOpcode.SMP_IDENTITY_ADDRESS_INFORMATION, <address_type>, <address> )
      #       where <address_type> 1 octet; <address> 6 octets
      #
        elif ( opcode == SMPOpcode.SMP_IDENTITY_ADDRESS_INFORMATION ):
            self.data = [ opcode ] + [ args[0] ] + toArray( args[1], 6 );
      #
      # encode ( SMPOpcode.SMP_SIGNING_INFORMATION, <csrk> )
      #       where <csrk> 16 octets
      #
        elif ( opcode == SMPOpcode.SMP_SIGNING_INFORMATION ):
            self.data = [ opcode ] + toArray( args[0], 16 );
      #
      # encode ( SMPOpcode.SMP_SECURITY_REQUEST, <properties> )
      #       where <properties> 1 octet
      #
        elif ( opcode == SMPOpcode.SMP_SECURITY_REQUEST ):
            self.data = [ opcode ] + [ args[0] ];
      #
      # encode ( SMPOpcode.SMP_PAIRING_PUBLIC_KEY, <key_X>, <key_Y> )
      #       where <key_X> 32 octets; <key_Y> 32 octets
      #
        elif ( opcode == SMPOpcode.SMP_PAIRING_PUBLIC_KEY ):
            self.data = [ opcode ] + toArray( args[0], 32 ) + toArray( args[1], 32 );
      #
      # encode ( SMPOpcode.SMP_PAIRING_DHKEY_CHECK, <check_value> )
      #       where <check_value> 16 octets
      #
        elif ( opcode == SMPOpcode.SMP_PAIRING_DHKEY_CHECK ):
            self.data = [ opcode ] + toArray( args[0], 16 );
      #
      # encode ( SMPOpcode.SMP_PAIRING_KEYPRESS_NOTIFICATION, <type> )
      #       where <type> 1 octet
      #
        elif ( opcode == SMPOpcode.SMP_PAIRING_KEYPRESS_NOTIFICATION ):
            self.data = [ opcode ] + [ args[0] ];
      #
      # The first two octets in the L2CAP PDU contains the length of the entire L2CAP PDU in octets, excluding the Length and CID fields.
      #
        if len(self.data) > 0:
            self.data = toArray( len(self.data), 2 ) + toArray( SMP_CID, 2 ) + self.data;
        return self.data;
            
    def decode(self, data):
        self.data = data[:];
        size = toNumber( data[:2] );
        cid = toNumber( data[2:4] );
        opcode = SMPOpcode(data[4]);

        result = { "opcode": opcode };
      #
      # decode ( SMPOpcode.SMP_PAIRING_REQUEST, <io_capability>, <oob_flag>, <auth_req>, <max_enq_key_size>, <init_key_dist>, <resp_key_dist> )
      #          where <io_capability> 1 octet, <oob_flag> 1 octet, <auth_req> 1 octet, <max_enq_key_size> 1 octet, <init_key_dist> 1 octet, <resp_key_dist> 1 octet
      #
        if   ( opcode == SMPOpcode.SMP_PAIRING_REQUEST ):
            result["capability"] = data[5];
            result["oob"] = data[6];
            result["auth"] = data[7];
            result["max_key_size"] = data[8];
            result["init_key_dist"] = data[9];
            result["resp_key_dist"] = data[10];
      #
      # decode ( SMPOpcode.SMP_PAIRING_RESPONSE, <io_capability>, <oob_flag>, <auth_req>, <max_enq_key_size>, <init_key_dist>, <resp_key_dist> )
      #          where <io_capability> 1 octet, <oob_flag> 1 octet, <auth_req> 1 octet, <max_enq_key_size> 1 octet, <init_key_dist> 1 octet, <resp_key_dist> 1 octet
      #
        elif ( opcode == SMPOpcode.SMP_PAIRING_RESPONSE ):
            result["capability"] = data[5];
            result["oob"] = data[6];
            result["auth"] = data[7];
            result["max_key_size"] = data[8];
            result["init_key_dist"] = data[9];
            result["resp_key_dist"] = data[10];
      #
      # decode ( SMPOpcode.SMP_PAIRING_CONFIRM, <confirm_value> )
      #       where <confirm_value> 16 octets
      #
        elif ( opcode == SMPOpcode.SMP_PAIRING_CONFIRM ):
            result["value"] = toNumber( data[5:21] );
      #
      # decode ( SMPOpcode.SMP_PAIRING_RANDOM, <random_value> )
      #       where <random_value> 16 octets
      #
        elif ( opcode == SMPOpcode.SMP_PAIRING_RANDOM ):
            result["value"] = toNumber( data[5:21] );
      #
      # decode ( SMPOpcode.SMP_PAIRING_FAILED, <reason> )
      #       where <reason> 1 octet
      #
        elif ( opcode == SMPOpcode.SMP_PAIRING_FAILED ):
            result["reason"] = (SMPError)(data[5]);
      #
      # decode ( SMPOpcode.SMP_ENCRYPTION_INFORMATION, <ltk> )
      #       where <ltk> 16 octets
      #
        elif ( opcode == SMPOpcode.SMP_ENCRYPTION_INFORMATION ):
            result["ltk"] = toNumber( data[5:21] );
      #
      # decode ( SMPOpcode.SMP_CENTRAL_IDENTIFICATION, <ediv>, <rand> )
      #       where <ediv> 2 octets; <rand> 8 octets
      #
        elif ( opcode == SMPOpcode.SMP_CENTRAL_IDENTIFICATION ):
            result["ediv"] = toNumber( data[5:7] );
            result["rand"] = toNumber( data[7:15] );
      #
      # decode ( SMPOpcode.SMP_IDENTITY_INFORMATION, <irk> )
      #       where <irk> 16 octets
      #
        elif ( opcode == SMPOpcode.SMP_IDENTITY_INFORMATION ):
            result["irk"] = toNumber( data[5:21] );
      #
      # decode ( SMPOpcode.SMP_IDENTITY_ADDRESS_INFORMATION, <address_type>, <address> )
      #       where <address_type> 1 octet; <address> 6 octets
      #
        elif ( opcode == SMPOpcode.SMP_IDENTITY_ADDRESS_INFORMATION ):
            result["type"] = data[5];
            result["address"] = toNumber( data[6:12] );
      #
      # decode ( SMPOpcode.SMP_SIGNING_INFORMATION, <csrk> )
      #       where <csrk> 16 octets
      #
        elif ( opcode == SMPOpcode.SMP_SIGNING_INFORMATION ):
            result["csrk"] = toNumber( data[5:21] );
      #
      # decode ( SMPOpcode.SMP_PAIRING_PUBLIC_KEY, <key_X>, <key_Y> )
      #       where <key_X> 32 octets; <key_Y> 32 octets
      #
        elif ( opcode == SMPOpcode.SMP_PAIRING_PUBLIC_KEY ):
            result["key_X"] = toNumber( data[5:37] );
            result["key_Y"] = toNumber( data[37:69] );
      #
      # decode ( SMPOpcode.SMP_PAIRING_DHKEY_CHECK, <check_value> )
      #       where <check_value> 16 octets
      #
        elif ( opcode == SMPOpcode.SMP_PAIRING_DHKEY_CHECK ):
            result["value"] = toNumber( data[5:21] );
      #
      # decode ( SMPOpcode.SMP_PAIRING_KEYPRESS_NOTIFICATION, <type> )
      #       where <type> 1 octet
      #
        elif ( opcode == SMPOpcode.SMP_PAIRING_KEYPRESS_NOTIFICATION ):
            result["change"] = (SMPPasskey)(data[5]);

        return result;

    def error(self, code):
        errorTexts = {
            SMPError.SMP_ERROR_PASSKEY:
                "The user input of passkey failed.",
            SMPError.SMP_ERROR_OOB:
                "The OOB data is not available.",
            SMPError.SMP_ERROR_AUTHENTICATION:
                "The pairing procedure cannot be performed as authentication requirements cannot be met.",
            SMPError.SMP_ERROR_CONFIRM:
                "The confirm value does not match the calculated compare value.",
            SMPError.SMP_ERROR_PAIRING:
                "Pairing is not supported by the device.",
            SMPError.SMP_ERROR_ENCRYPTION:
                "The resultant encryption key size is insufficient for the security requirements.",
            SMPError.SMP_ERROR_COMMAND:
                "The SMP command received is not supported.",
            SMPError.SMP_ERROR_REASON:
                "Pairing failed due to an unspecified reason.",
            SMPError.SMP_ERROR_REPEATED_ATTEMPTS:
                "Pairing or authentication procedure is disallowed because too little time has elapsed since last pairing- or security-request.",
            SMPError.SMP_ERROR_INVALID_PARAMETERS:
                "The command length is invalid or a parameter is outside the specified range.",
            SMPError.SMP_ERROR_DHKEY_CHECK:
                "The DHKey Check value received doesn't match the one calculated.",
            SMPError.SMP_ERROR_NUMERIC_COMPARISON:
                "The confirm values in the numeric comparison protocol do not match.",
            SMPError.SMP_ERROR_PAIRING_IN_PROGRESS:
                "The pairing over LE transport failed due to a Pairing Request sent over the BR/EDR transport.",
            SMPError.SMP_ERROR_CROSS_KEY_GENERATION:
                "The BR/EDR Link Key generated on the BR/EDR transport cannot be used to derive and distribute keys for the LE transport."
        };
        if code in errorTexts:
            return errorTexts[code];
        else:
            return "Unknown error code (%d)" % code;
