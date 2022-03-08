# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

import string;
from enum import IntEnum;
from components.utils import *;

ATT_CID = 4;

class ATTProperty(IntEnum):
    ATT_PROP_BROADCAST                   =   1
    ATT_PROP_READ                        =   2
    ATT_PROP_WRITE_WITHOUT_RESPONSE      =   4
    ATT_PROP_WRITE                       =   8
    ATT_PROP_NOTIFY                      =  16
    ATT_PROP_INDICATE                    =  32
    ATT_PROP_AUTHENTICATED_SIGNED_WRITES =  64
    ATT_PROP_EXTENDED_PROPERTIES         = 128

class ATTPermission(IntEnum):
    ATT_PERM_NONE                        =   0
    ATT_PERM_READ                        =   1
    ATT_PERM_WRITE                       =   2
    ATT_PERM_READ_ENCRYPT                =   4
    ATT_PERM_WRITE_ENCRYPT               =   8
    ATT_PERM_READ_AUTHEN                 =  16
    ATT_PERM_WRITE_AUTHEN                =  32
    ATT_PERM_WRITE_PREPARED              =  64
    ATT_PERM_READ_AUTHOR                 = 128
    ATT_PERM_WRITE_AUTHOR                = 256
    ATT_PERM_ANY_READ                    = ATT_PERM_READ | ATT_PERM_READ_ENCRYPT | ATT_PERM_READ_AUTHEN | ATT_PERM_READ_AUTHOR
    ATT_PERM_ANY_WRITE                   = ATT_PERM_WRITE | ATT_PERM_WRITE_ENCRYPT | ATT_PERM_WRITE_AUTHEN | ATT_PERM_WRITE_PREPARED | ATT_PERM_WRITE_AUTHOR

#
# The Opcode field has the following bits:
#    Bits:
#     0-5: Method
#       6: Command Flag (64)
#       7: Authentication Signature Flag (128)
#
class ATTOpcode(IntEnum):
    ATT_ERROR_RESPONSE                   =   1 # Request Opcode in Error, Attribute Handle In Error, Error Code
    ATT_EXCH_MTU_REQUEST                 =   2 # Client Rx MTU
    ATT_EXCH_MTU_RESPONSE                =   3 # Server Rx MTU
    ATT_FIND_INFORMATION_REQUEST         =   4 # Starting Handle, Ending Handle
    ATT_FIND_INFORMATION_RESPONSE        =   5 # Format, List of Handle, UUID
    ATT_FIND_BY_TYPE_VALUE_REQUEST       =   6 # Starting Handle, Ending Handle, Attribute Type, Attribute Value
    ATT_FIND_BY_TYPE_VALUE_RESPONSE      =   7 # Handles Information List
    ATT_READ_BY_TYPE_REQUEST             =   8 # Starting Handle, Ending Handle, UUID
    ATT_READ_BY_TYPE_RESPONSE            =   9 # Length, Attribute Data List
    ATT_READ_REQUEST                     =  10 # Attribute Handle
    ATT_READ_RESPONSE                    =  11 # Attribute Value
    ATT_READ_BLOB_REQUEST                =  12 # Attribute Handle, Value Offset
    ATT_READ_BLOB_RESPONSE               =  13 # Part Attribute Value
    ATT_READ_MULTIPLE_REQUEST            =  14 # Handle Set
    ATT_READ_MULTIPLE_RESPONSE           =  15 # Value Set
    ATT_READ_BY_GROUP_TYPE_REQUEST       =  16 # Start Handle, Ending Handle, UUID
    ATT_READ_BY_GROUP_TYPE_RESPONSE      =  17 # Length, Attribute Data List
    ATT_WRITE_REQUEST                    =  18 # Attribute Handle, Attribute Value
    ATT_WRITE_RESPONSE                   =  19 # -
    ATT_PREPARE_WRITE_REQUEST            =  22 # Attribute Handle, Value Offset, Part Attribute Value
    ATT_PREPARE_WRITE_RESPONSE           =  23 # Attribute Handle, Value Offset, Part Attribute Value
    ATT_EXECUTE_WRITE_REQUEST            =  24 # Flags
    ATT_EXECUTE_WRITE_RESPONSE           =  25 # -
    ATT_HANDLE_VALUE_NOTIFICATION        =  27 # Attribute Handle, Attribute Value
    ATT_HANDLE_VALUE_INDICATION          =  29 # Attribute Handle, Attribute Value
    ATT_HANDLE_VALUE_CONFIRMATION        =  30 # -
    ATT_INVALID_REQUEST                  =  31 # -
    ATT_WRITE_COMMAND                    =  82 # Attribute Handle, Attribute Value (64+18)
    ATT_INVALID_COMMAND                  =  95 # -
    ATT_SIGNED_WRITE_COMMAND             = 210 # Attribute Handle, Attribute Value, Authentication Signature (128+64+18)

class ATTError(IntEnum):
    ATT_ERROR_INVALID_HANDLE                       = 0x01 # The attribute handle given was not valid on this server.
    ATT_ERROR_READ_NOT_PERMITTED                   = 0x02 # The attribute cannot be read.
    ATT_ERROR_WRITE_NOT_PERMITTED                  = 0x03 # The attribute cannot be written.
    ATT_ERROR_INVALID_PDU                          = 0x04 # The attribute PDU was invalid.
    ATT_ERROR_INSUFFICIENT_AUTHENTICATION          = 0x05 # The attribute requires authentication before it can be read or written.
    ATT_ERROR_REQUEST_NOT_SUPPORTED                = 0x06 # Attribute server does not support the request received from the client.
    ATT_ERROR_INVALID_OFFSET                       = 0x07 # Offset specified was past the end of the attribute.
    ATT_ERROR_INSUFFICIENT_AUTHORIZATION           = 0x08 # The attribute requires authorization before it can be read or written.
    ATT_ERROR_PREPARE_QUEUE_FULL                   = 0x09 # Too many prepare writes have been queued.
    ATT_ERROR_ATTRIBUTE_NOT_FOUND                  = 0x0A # No attribute found within the given attribute handle range.
    ATT_ERROR_ATTRIBUTE_NOT_LONG                   = 0x0B # The attribute cannot be read using the Read Blob Request.
    ATT_ERROR_INSUFFICIENT_ENCRYPTION_KEY_SIZE     = 0x0C # The Encryption Key Size used for encrypting this link is insufficient.
    ATT_ERROR_INVALID_ATTRIBUTE_VALUE_LENGTH       = 0x0D # The attribute value length is invalid for the operation.
    ATT_ERROR_UNLIKELY_ERROR                       = 0x0E # The attribute request that was requested has encountered an error that was unlikely, and therefore could not be completed as requested.
    ATT_ERROR_INSUFFICIENT_ENCRYPTION              = 0x0F # The attribute requires encryption before it can be read or written.
    ATT_ERROR_UNSUPPORTED_GROUP_TYPE               = 0x10 # The attribute type is not a supported grouping attribute as defined by a higher layer specification.
    ATT_ERROR_INSUFFICIENT_RESOURCES               = 0x11 # Insufficient Resources to complete the request.
    ATT_ERROR_APPLICATION_ERROR                    = 0x80 # Application error code defined by a higher layer specification.
    ATT_ERROR_WRITE_REQUEST_REJECTED               = 0xFC # Write Request Rejected.
    ATT_ERROR_CCC_DESCRIPTOR_IMPROPERLY_CONFIGURED = 0xFD # Client Characteristic Configuration Descriptor Improperly Configured.
    ATT_ERROR_PROCEDURE_ALREADY_IN_PROGRESS        = 0xFE # Procedure Already in Progress.
    ATT_ERROR_OUT_OF_RANGE                         = 0xFF # Attribute value is out of range as defined by a profile or service specification.

class ATTData:

    def __init__(self):
        self.data = [];

    def encode(self, opcode, *args):
      #
      # encode ATT_EXCH_MTU_REQUEST, <mtu>
      #       where <mtu> 2 octets
      #
        if   ( opcode == ATTOpcode.ATT_EXCH_MTU_REQUEST ):
            self.data = [ opcode ] + toArray( args[0], 2 );
      #
      # encode ATT_FIND_INFORMATION_REQUEST, <start_handle>, <end_handle>
      #       where <start_handle> 2 octets; <end_handle> 2 octets
      #
        elif ( opcode == ATTOpcode.ATT_FIND_INFORMATION_REQUEST ):
            self.data = [ opcode ] + toArray( args[0], 2 ) + toArray( args[1], 2 );
      #
      # encode ATT_FIND_BY_TYPE_VALUE_REQUEST, <start_handle>, <end_handle>, <attribute_type>, <attribute_values>...
      #       where <start_handle> 2 octets; <end_handle> 2 octets; <attribute_type> 2 octets UUID; <attribute_values> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_FIND_BY_TYPE_VALUE_REQUEST ):
            self.data = [ opcode ] + toArray( args[0], 2 ) + toArray( args[1], 2 ) + toArray( args[2], 2 );
            for arg in args[3:]:
                self.data += arg;
      #
      # encode ATT_READ_BY_TYPE_REQUEST, <start_handle>, <end_handle>, <attribute_group_type>
      #       where <start_handle> 2 octets; <end_handle> 2 octets; <attribute_group_type> 2 or 16 octets UUID
      #
        elif ( opcode == ATTOpcode.ATT_READ_BY_TYPE_REQUEST ):
            self.data = [ opcode ] + toArray( args[0], 2 ) + toArray( args[1], 2 ) + toArray( args[2], 2 if args[2] <= 0xFFFF else 16);
      #
      # encode ATT_READ_REQUEST, <attribute_handle>
      #       where <attribute_handle> 2 octets
      #
        elif ( opcode == ATTOpcode.ATT_READ_REQUEST ):
            self.data = [ opcode ] + toArray( args[0], 2 );
      #
      # encode ATT_READ_BLOB_REQUEST, <attribute_handle>, <value_offset>
      #       where <attribute_handle> 2 octets; <value_offset> 2 octets
      #
        elif ( opcode == ATTOpcode.ATT_READ_BLOB_REQUEST ):
            self.data = [ opcode ] + toArray( args[0], 2 ) + toArray( args[1], 2 );
      #
      # encode ATT_READ_MULTIPLE_REQUEST, <handles>...
      #       where <handles> 2 octets each
      #
        elif ( opcode == ATTOpcode.ATT_READ_MULTIPLE_REQUEST ):
            self.data = [ opcode ];
            for arg in args[0]:
                self.data += toArray( arg, 2 );
      #
      # encode ATT_READ_BY_GROUP_TYPE_REQUEST, <start_handle>, <end_handle>, <attribute_group_type>
      #       where <start_handle> 2 octets; <end_handle> 2 octets; <attribute_group_type> 2 or 16 octets UUID
      #
        elif ( opcode == ATTOpcode.ATT_READ_BY_GROUP_TYPE_REQUEST ):
            self.data = [ opcode ] + toArray( args[0], 2 ) + toArray( args[1], 2 ) + toArray( args[2], 2 if args[2] <= 0xFFFF else 16);
      #
      # encode ATT_WRITE_REQUEST, <attribute_handle>, <values>...
      #       where <attribute_handle> 2 octets; <values> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_WRITE_REQUEST ):
            self.data = [ opcode ] + toArray( args[0], 2 );
            for arg in args[1:]:
                self.data += arg;
      #
      # encode ATT_PREPARE_WRITE_REQUEST, <attribute_handle>, <value_offset>, <values>...
      #       where <attribute_handle> 2 octets; <value_offset> 2 octets; <values> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_PREPARE_WRITE_REQUEST ):
            self.data = [ opcode ] + toArray( args[0], 2 ) + toArray( args[1], 2 );
            for arg in args[2:]:
                self.data += arg;
      #
      # encode ATT_EXECUTE_WRITE_REQUEST, <flags>
      #       where <flags> 1 octet
      #
        elif ( opcode == ATTOpcode.ATT_EXECUTE_WRITE_REQUEST ):
            self.data = [ opcode, args[0] ];
      #
      # encode ATT_HANDLE_VALUE_CONFIRMATION
      #
        elif ( opcode == ATTOpcode.ATT_HANDLE_VALUE_CONFIRMATION ):
            self.data = [ opcode ];
      #
      # encode ATT_WRITE_COMMAND, <attribute_handle>, <values>...
      #       where <attribute_handle> 2 octets; <values> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_WRITE_COMMAND ):
            self.data = [ opcode ] + toArray( args[0], 2 );
            for arg in args[1:]:
                self.data += arg;
      #
      # encode ATT_SIGNED_WRITE_COMMAND, <attribute_handle>, <signature>, <values>...
      #       where <attribute_handle> 2 octets; <signature> 12 octets; <values> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_SIGNED_WRITE_COMMAND ):
            self.data = [ opcode ] + toArray( args[0], 2 ) + args[2:] + toArray( args[1], 12 );
      #
      # encode Illegal command...
      #
        else:
            self.data = [ opcode ];
            for arg in args:
                self.data += arg;
      #
      # The first two octets in the L2CAP PDU contains the length of the entire L2CAP PDU in octets, excluding the Length and CID fields.
      #
        if len(self.data) > 0:
            self.data = toArray( len(self.data), 2 ) + toArray( ATT_CID, 2 ) + self.data;
        return self.data;
            
    def decode(self, data):
        self.data = data[:];
        size = toNumber( data[:2] );
        cid = toNumber( data[2:4] );
        opcode = ATTOpcode(data[4]);

        result = { "opcode": opcode };
      #
      # decode ATT_ERROR_RESPONSE: <request_opcode>, <attribute_handle>, <error_code>
      #       where <request_opcode> 1 octet; <attribute_handle> 2 octets; <error_code> 1 octet
      #
        if   ( opcode == ATTOpcode.ATT_ERROR_RESPONSE ):
            result["request opcode"] = ATTOpcode(data[5]);
            result["handle"] = [ toNumber( data[6:8] ) ];
            result["error"] = ATTError(data[8]);
      #
      # decode ATT_EXCH_MTU_RESPONSE: <mtu>
      #       where <mtu> 2 octets
      #
        elif ( opcode == ATTOpcode.ATT_EXCH_MTU_RESPONSE ):
            result["mtu"] = toNumber( data[5:7] );
      #
      # decode ATT_FIND_INFORMATION_RESPONSE: <format>, { <handle>, <uuid> }...
      #       where <format> 1 octet; <handle> 2 octets; <uuid> 2 octets if <format> == 1 else 16 octets
      #
        elif ( opcode == ATTOpcode.ATT_FIND_INFORMATION_RESPONSE ):
            result["handle"] = [];
            result["uuid"] = [];
            length = 4 if data[5] == 1 else 18;
        
            n = 6;
            while n < size+3:
                result["handle"] += [ toNumber( data[n:n+2] ) ];
                result["uuid"] += [ toNumber( data[n+2:n+length] ) ];
                n += length;
      #
      # decode ATT_FIND_BY_TYPE_VALUE_RESPONSE: <handle>...
      #       <handle> 2 octets
      #
        elif ( opcode == ATTOpcode.ATT_FIND_BY_TYPE_VALUE_RESPONSE ):
            result["handle"] = [];

            n = 5;
            while n < size+3:
                result["handle"] += [ toNumber( data[n:n+2] ) ];
                n += 2;   
      #
      # decode ATT_READ_BY_TYPE_RESPONSE: <length>, { <handle>, <value>... }
      #       where <length> 1 octet holding the number of octets in each { <handle>, <value>... } set
      #       <handle> 2 octets; <value> 1 octet each (<length>-2) octets in total
      #
        elif ( opcode == ATTOpcode.ATT_READ_BY_TYPE_RESPONSE ):
            result["handle"] = [];
            result["value"] = [];
         
            n = 6;
            while n < size+3:
                result["handle"] += [ toNumber( data[n:n+2] ) ];
                result["value"] += [ data[n+2:n+data[5]] ];
                n += data[5];
      #
      # decode ATT_READ_RESPONSE: <value>...
      #       where <value> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_READ_RESPONSE ):
            result["value"] = data[5:];
      #
      # decode ATT_READ_BLOB_RESPONSE: <value>...
      #       where <value> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_READ_BLOB_RESPONSE ):
            result["value"] = data[5:];
      #
      # decode ATT_READ_MULTIPLE_RESPONSE: <value>...
      #       where <value> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_READ_MULTIPLE_RESPONSE ):
            result["value"] = data[5:];
      #
      # decode ATT_READ_BY_GROUP_TYPE_RESPONSE: <length>, { <attribute_handle>, <end_group_handle>, <value>... }...
      #       where <length> 1 octet; <attribute_handle> 2 octets; <end_group_handle> 2 octets; <value> 1 octet each (<length> - 4)
      #
        elif ( opcode == ATTOpcode.ATT_READ_BY_GROUP_TYPE_RESPONSE ):
            result["first_handle"] = [];
            result["last_handle"] = [];
            result["value"] = [];
         
            n = 6;
            while n < size+3:
                result["first_handle"] += [ toNumber( data[n:n+2] ) ];
                result["last_handle"] += [ toNumber( data[n+2:n+4] ) ];
                result["value"] += [ data[n+4:n+data[5]] ];
                n += data[5];
      #
      # decode ATT_WRITE_RESPONSE:
      #       where
      #
      #  elif ( opcode == ATTOpcode.ATT_WRITE_RESPONSE ):
        
      #
      # decode ATT_PREPARE_WRITE_RESPONSE: <handle>, <offset>, <value>...
      #       where <handle> 2 octets; <offset> 2 octets; <value> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_PREPARE_WRITE_RESPONSE ):
            result["handle"] = toNumber( data[5:7] );
            result["offset"] = toNumber( data[7:9] );
            result["value"] = data[9:];
      #
      # decode ATT_EXECUTE_WRITE_RESPONSE:
      #       where
      #
      #  elif ( opcode == ATTOpcode.ATT_EXECUTE_WRITE_RESPONSE ):
  
      #
      # decode ATT_HANDLE_VALUE_NOTIFICATION: <handle>, <value>...
      #       where <handle> 2 octets; <value> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_HANDLE_VALUE_NOTIFICATION ):
            result["handle"] = toNumber( data[5:7] );
            result["value"] = data[7:];
      #
      # decode ATT_HANDLE_VALUE_INDICATION: <handle>, <value>...
      #       where <handle> 2 octets; <value> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_HANDLE_VALUE_INDICATION ):
            result["handle"] = toNumber( data[5:7] );
            result["value"] = data[7:];

        return result;

    def __errorText(self, error):
        result = str(ATTError( error ));
        result = result.split('.')[1];
        result = '_'.join([_.lower().capitalize() if _ != 'ATT' else _ for _ in result.split('_')]);
        return result;

    def __opcodeName(self, opcode):
        result = str(ATTOpcode( opcode ));
        result = result.split('.')[1];
        result = '_'.join([_.lower().capitalize() if _ != 'ATT' else _ for _ in result.split('_')]);
        return result;
    
    def __hexByteArray(self, start, end):
        result = '';
        for n in range(start, min(len(self.data), end)):
            if len(result) > 0:
                result += ' ';
            result += '%02X' % self.data[n];
        return result;

    def __hexWordArray(self, start, end):
        result = '';
        for n in range(start, end, 2):
            if len(result) > 0:
                result += ' ';
            result += '%04X' % toNumber(self.data[n:n+2]);
        return result;

    def __str__(self):
        size = toNumber( self.data[:2] );
        cid = toNumber( self.data[2:4] );
        opcode = ATTOpcode( self.data[4] );

        result = self.__opcodeName( opcode );
      #
      # ATT_ERROR_RESPONSE: <request_opcode>, <attribute_handle>, <error_code>
      #       where <request_opcode> 1 octet; <attribute_handle> 2 octets; <error_code> 1 octet
      #
        if   ( opcode == ATTOpcode.ATT_ERROR_RESPONSE ):
            result += ' request=%s handle=0x%04X error=%s' % (self.__opcodeName(self.data[5]), toNumber(self.data[6:8]), self.__errorText(self.data[8]));
      #
      # ATT_EXCH_MTU_REQUEST: <mtu>
      #       where <mtu> 2 octets
      #
        elif ( opcode == ATTOpcode.ATT_EXCH_MTU_REQUEST ):
            result += ' mtu=%d' % toNumber(self.data[5:7]);
      #
      # ATT_EXCH_MTU_RESPONSE: <mtu>
      #       where <mtu> 2 octets
      #
        elif ( opcode == ATTOpcode.ATT_EXCH_MTU_RESPONSE ):
            result += ' mtu=%d' % toNumber(self.data[5:7]);
      #
      # ATT_FIND_INFORMATION_REQUEST: <start_handle>, <end_handle>
      #       where <start_handle> 2 octets; <end_handle> 2 octets
      #
        elif ( opcode == ATTOpcode.ATT_FIND_INFORMATION_REQUEST ):
            result += ' start=0x%04X end=0x%04X' % (toNumber(self.data[5:7]), toNumber(self.data[7:9]));
      #
      # ATT_FIND_INFORMATION_RESPONSE: <format>, { <handle>, <uuid> }...
      #       where <format> 1 octet; <handle> 2 octets; <uuid> 2 octets if <format> == 1 else 16 octets
      #
        elif ( opcode == ATTOpcode.ATT_FIND_INFORMATION_RESPONSE ):
            result += ' format=%d' % self.data[5];
            n, length = 6, 4 if self.data[5] == 1 else 18;
            while n < size+3:
                if length == 4:
                    result += ' { 0x%04X 0x%04X }' % (toNumber(self.data[n:n+2]), toNumber(self.data[n+2:n+length]));
                else:
                    result += ' { 0x%04X %s }' % (toNumber(self.data[n:n+2]), self.uuid(toNumber(self.data[n+2:n+length])));
                n += length;
      #
      # ATT_FIND_BY_TYPE_VALUE_REQUEST: <start_handle>, <end_handle>, <attribute_type>, <attribute_values>...
      #       where <start_handle> 2 octets; <end_handle> 2 octets; <attribute_type> 2 octets UUID; <attribute_values> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_FIND_BY_TYPE_VALUE_REQUEST ):
            result += ' start=0x%04X end=0x%04X type=0x%04X values: %s' % (toNumber(self.data[5:7]), toNumber(self.data[7:9]), toNumber(self.data[9:11]), self.__hexByteArray(11,size+4));
      #
      # ATT_FIND_BY_TYPE_VALUE_RESPONSE: <handle>...
      #       <handle> 2 octets
      #
        elif ( opcode == ATTOpcode.ATT_FIND_BY_TYPE_VALUE_RESPONSE ):
            result += ' handles: %s' % self.__hexWordArray(5, size+4);
      #
      # ATT_READ_BY_TYPE_REQUEST: <start_handle>, <end_handle>, <attribute_group_type>
      #       where <start_handle> 2 octets; <end_handle> 2 octets; <attribute_group_type> 2 or 16 octets UUID
      #
        elif ( opcode == ATTOpcode.ATT_READ_BY_TYPE_REQUEST ):
            result += ' start=0x%04X end=0x%04X' % (toNumber(self.data[5:7]), toNumber(self.data[7:9]));
            if size > 7:
                result += ' group type=%s' % self.uuid(toNumber(self.data[9:25]));
            else:
                result += ' group type=%04X' % toNumber(self.data[9:11]);
      #
      # ATT_READ_BY_TYPE_RESPONSE: <length>, { <handle>, <value>... }
      #       where <length> 1 octet holding the number of octets in each { <handle>, <value>... } set
      #       <handle> 2 octets; <value> 1 octet each (<length>-2) octets in total
      #
        elif ( opcode == ATTOpcode.ATT_READ_BY_TYPE_RESPONSE ):
            result += ' length=%d' % self.data[5];
            n = 6;
            while n < size+3:
                result += ' { handle=0x%04X values: %s }' % (toNumber(self.data[n:n+2]), self.__hexByteArray(n+2, n+self.data[5]));
                n += self.data[5];
      #
      # ATT_READ_REQUEST: <attribute_handle>
      #       where <attribute_handle> 2 octets
      #
        elif ( opcode == ATTOpcode.ATT_READ_REQUEST ):
            result += ' handle=0x%04X' % toNumber(self.data[5:7]);
      #
      # ATT_READ_RESPONSE: <value>...
      #       where <value> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_READ_RESPONSE ):
            result += ' values: %s' % self.__hexByteArray(5, size+4);
      #
      # ATT_READ_BLOB_REQUEST: <attribute_handle>, <value_offset>
      #       where <attribute_handle> 2 octets; <value_offset> 2 octets
      #
        elif ( opcode == ATTOpcode.ATT_READ_BLOB_REQUEST ):
            result += ' handle=0x%04X offset=0x%04X' % (toNumber(self.data[5:7]), toNumber(self.data[7:9]));
      #
      # ATT_READ_BLOB_RESPONSE: <value>...
      #       where <value> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_READ_BLOB_RESPONSE ):
            result += ' values: %s' % self.__hexByteArray(5, size+4);
      #
      # ATT_READ_MULTIPLE_REQUEST: <handles>...
      #       where <handles> 2 octets each
      #
        elif ( opcode == ATTOpcode.ATT_READ_MULTIPLE_REQUEST ):
            result += ' handles: %s' % self.__hexWordArray(5, size+4);
      #
      # ATT_READ_MULTIPLE_RESPONSE: <value>...
      #       where <value> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_READ_MULTIPLE_RESPONSE ):
            result += ' values: %s' % self.__hexByteArray(5, size+4);
      #
      # ATT_READ_BY_GROUP_TYPE_REQUEST: <start_handle>, <end_handle>, <attribute_group_type>
      #       where <start_handle> 2 octets; <end_handle> 2 octets; <attribute_group_type> 2 or 16 octets UUID
      #
        elif ( opcode == ATTOpcode.ATT_READ_BY_GROUP_TYPE_REQUEST ):
            result += ' start=0x%04X end=0x%04X' % (toNumber(self.data[5:7]), toNumber(self.data[7:9]));
            if size > 7:
                result += ' group type=%s' % uuid(toNumber(self.data[9:25]));
            else:
                result += ' group type=%04X' % toNumber(self.data[9:11]);
      #
      # ATT_READ_BY_GROUP_TYPE_RESPONSE: <length>, { <attribute_handle>, <end_group_handle>, <value>... }...
      #       where <length> 1 octet; <attribute_handle> 2 octets; <end_group_handle> 2 octets; <value> 1 octet each (<length> - 4)
      #
        elif ( opcode == ATTOpcode.ATT_READ_BY_GROUP_TYPE_RESPONSE ):
            result += ' length=%d' % self.data[5];
            n, indent = 6, len(result);
            while n < size+3:
                if n > 6:
                    result += '\n%*s' % (indent, ' ');
                result += ' { handle=0x%04X end group=0x%04X values: %s }' % (toNumber(self.data[n:n+2]), toNumber(self.data[n+2:n+4]), self.__hexByteArray(n+4, n+self.data[5]));
                n += self.data[5];
      #
      # ATT_WRITE_REQUEST: <attribute_handle>, <values>...
      #       where <attribute_handle> 2 octets; <values> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_WRITE_REQUEST ):
            result += ' handle=0x%04X values: %s' % (toNumber(self.data[5:7]), self.__hexByteArray(7, size+4));
      #
      # ATT_WRITE_RESPONSE:
      #       where
      #
        elif ( opcode == ATTOpcode.ATT_WRITE_RESPONSE ):
            pass;
      #
      # ATT_PREPARE_WRITE_REQUEST: <attribute_handle>, <value_offset>, <values>...
      #       where <attribute_handle> 2 octets; <value_offset> 2 octets; <values> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_PREPARE_WRITE_REQUEST ):
            result += ' handle=0x%04X offset=0x%04X values: %s' % (toNumber(self.data[5:7]), toNumber(self.data[7:9]), self.__hexByteArray(9, size+4));
      #
      # ATT_PREPARE_WRITE_RESPONSE: <handle>, <offset>, <value>...
      #       where <handle> 2 octets; <offset> 2 octets; <value> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_PREPARE_WRITE_RESPONSE ):
            result += ' handle=0x%04X offset=0x%04X values: %s' % (toNumber(self.data[5:7]), toNumber(self.data[7:9]), self.__hexByteArray(9, size+4));
      #
      # ATT_EXECUTE_WRITE_REQUEST: <flags>
      #       where <flags> 1 octet
      #
        elif ( opcode == ATTOpcode.ATT_EXECUTE_WRITE_REQUEST ):
            result += ' flags=0x%02X' % self.data[5];
      #
      # ATT_EXECUTE_WRITE_RESPONSE:
      #       where
      #
        elif ( opcode == ATTOpcode.ATT_EXECUTE_WRITE_RESPONSE ):
            pass;
      #
      # ATT_HANDLE_VALUE_NOTIFICATION: <handle>, <value>...
      #       where <handle> 2 octets; <value> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_HANDLE_VALUE_NOTIFICATION ):
            result += ' handle=0x%04X values: %s' % (toNumber(self.data[5:7]), self.__hexByteArray(7, size+4));
      #
      # ATT_HANDLE_VALUE_INDICATION: <handle>, <value>...
      #       where <handle> 2 octets; <value> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_HANDLE_VALUE_INDICATION ):
            result += ' handle=0x%04X values: %s' % (toNumber(self.data[5:7]), self.__hexByteArray(7, size+4));
      #
      # ATT_HANDLE_VALUE_CONFIRMATION:
      #
        elif ( opcode == ATTOpcode.ATT_HANDLE_VALUE_CONFIRMATION ):
            pass;
      #
      # ATT_WRITE_COMMAND: <attribute_handle>, <values>...
      #       where <attribute_handle> 2 octets; <values> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_WRITE_COMMAND ):
            result += ' handle=0x%04X values: %s' % (toNumber(self.data[5:7]), self.__hexByteArray(7, size+4));
      #
      # ATT_SIGNED_WRITE_COMMAND: <attribute_handle>, <signature>, <values>...
      #       where <attribute_handle> 2 octets; <signature> 12 octets; <values> 1 octet each
      #
        elif ( opcode == ATTOpcode.ATT_SIGNED_WRITE_COMMAND ):
            result += ' handle=0x%04X signature=0x%024X values: %s' % (toNumber(self.data[5:7]), toNumber(self.data[7:19]), self.__hexByteArray(19, size+4));
      #
      # ATT_INVALID_REQUEST:
      #
        elif ( opcode == ATTOpcode.ATT_INVALID_REQUEST ):
            result += ' ' + self.__hexByteArray(5, size+4);
      #
      # ATT_INVALID_COMMAND:
      #
        elif ( opcode == ATTOpcode.ATT_INVALID_COMMAND ):
            result += ' ' + self.__hexByteArray(5, size+4);

        return result;

    def uuid(self, data):
        if isinstance(data, str):
           uuid = 0;
           octet = '';
           for char in data:
               if char in string.hexdigits:
                   octet += char;
                   if len(octet) == 2:
                       uuid <<= 8;
                       uuid += int(octet, 16);
                       octet = '';
        else:
            if data <= 0xFFFFFFFF:
                uuid = ('%08X' % data) + '00001000800000805F9B34FB'
            else:
                uuid = ('%032X' % data)
            uuid = uuid[:8] + '-' + uuid[8:12] + '-' + uuid[12:16] + '-' + uuid[16:20] + '-' + uuid[20:];
        return uuid;

    def __formatEnumSet(self, value, texts):
        txt = '';
        for n in range(len(texts)):
            if ( value & (1<<n) ):
                if ( len(txt) ):
                    txt += '|';
                txt += texts[n];
        return txt;

    def property(self, data):
        propertyTexts = [ 'BROADCAST', 'READ', 'WRITE WITHOUT RESPONSE', 'WRITE', 'NOTIFY', 'INDICATE', 'AUTHENTICATED SIGNED WRITES', 'EXTENDED PROPERTIES' ];
        return self.__formatEnumSet(data, propertyTexts);

    def permission(self, data):
        permissionTexts = [ 'READ', 'WRITE', 'READ ENCRYPTED', 'WRITE ENCRYPTED', 'READ AUTHENTICATED', 'WRITE AUTHENTICATED', 'WRITE PREPARED', 'READ AUTHORIZED', 'WRITE AUTHORIZED' ];
        return self.__formatEnumSet(data, permissionTexts);

    def isPermissionError(self, code):
        permissionErrors = [ ATTError.ATT_ERROR_READ_NOT_PERMITTED, ATTError.ATT_ERROR_INSUFFICIENT_AUTHENTICATION, ATTError.ATT_ERROR_INSUFFICIENT_AUTHORIZATION, ATTError.ATT_ERROR_INSUFFICIENT_ENCRYPTION_KEY_SIZE, ATTError.ATT_ERROR_INSUFFICIENT_ENCRYPTION ];
        return code in permissionErrors;

    def error(self, code):
        errorTexts = {
            ATTError.ATT_ERROR_INVALID_HANDLE:
                "The attribute handle given was not valid on this server.",
            ATTError.ATT_ERROR_READ_NOT_PERMITTED:
                "The attribute cannot be read.",
            ATTError.ATT_ERROR_WRITE_NOT_PERMITTED:
                "The attribute cannot be written.",
            ATTError.ATT_ERROR_INVALID_PDU:
                "The attribute PDU was invalid.",
            ATTError.ATT_ERROR_INSUFFICIENT_AUTHENTICATION:
                "The attribute requires authentication before it can be read or written.",
            ATTError.ATT_ERROR_REQUEST_NOT_SUPPORTED:
                "Attribute server does not support the request received from the client.",
            ATTError.ATT_ERROR_INVALID_OFFSET:
                "Offset specified was past the end of the attribute.",
            ATTError.ATT_ERROR_INSUFFICIENT_AUTHORIZATION:
                "The attribute requires authorization before it can be read or written.",
            ATTError.ATT_ERROR_PREPARE_QUEUE_FULL:
                "Too many prepare writes have been queued.",
            ATTError.ATT_ERROR_ATTRIBUTE_NOT_FOUND:
                "No attribute found within the given attribute handle range.",
            ATTError.ATT_ERROR_ATTRIBUTE_NOT_LONG:
                "The attribute cannot be read using the Read Blob Request.",
            ATTError.ATT_ERROR_INSUFFICIENT_ENCRYPTION_KEY_SIZE:
                "The Encryption Key Size used for encrypting this link is insufficient.",
            ATTError.ATT_ERROR_INVALID_ATTRIBUTE_VALUE_LENGTH:
                "The attribute value length is invalid for the operation.",
            ATTError.ATT_ERROR_UNLIKELY_ERROR:
                "The attribute request that was requested has encountered an error that was unlikely, and therefore could not be completed as requested.",
            ATTError.ATT_ERROR_INSUFFICIENT_ENCRYPTION:
                "The attribute requires encryption before it can be read or written.",
            ATTError.ATT_ERROR_UNSUPPORTED_GROUP_TYPE:
                "The attribute type is not a supported grouping attribute as defined by a higher layer specification.",
            ATTError.ATT_ERROR_INSUFFICIENT_RESOURCES:
                "Insufficient Resources to complete the request.",
            ATTError.ATT_ERROR_APPLICATION_ERROR:
                "Application error code defined by a higher layer specification.",
            ATTError.ATT_ERROR_WRITE_REQUEST_REJECTED:
                "Write Request Rejected.",
            ATTError.ATT_ERROR_CCC_DESCRIPTOR_IMPROPERLY_CONFIGURED:
                "Client Characteristic Configuration Descriptor Improperly Configured.",
            ATTError.ATT_ERROR_PROCEDURE_ALREADY_IN_PROGRESS:
                "Procedure Already in Progress.",
            ATTError.ATT_ERROR_OUT_OF_RANGE:
                "Attribute value is out of range as defined by a profile or service specification."
        };
        if code in errorTexts:
            return errorTexts[code];
        else:
            return "Unknown error code (%d)" % code;
