# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

from numpy import random;
import statistics;
import os;
import numpy;
from enum import IntEnum;
from components.utils import *;
from components.basic_commands import *;
from components.address import *;
from components.events import *;
from components.resolvable import *;
from components.advertiser import *;
from components.scanner import *;
from components.initiator import *;
from components.preambles import *;
from components.addata import *;
from components.attdata import *;
from components.smpdata import *;
from components.pairing import *;
from components.gattdata import *;
from components.test_spec import TestSpec;

global lowerIRK, upperIRK, lowerRandomAddress, upperRandomAddress;

"""
    Send an ATT Profile request...
"""
def attRequest(transport, initiator, txData, trace):
    status = le_data_write(transport, initiator.initiator, initiator.handles[0], 0, 0, txData, 100);
    trace.trace(10, "LE Data Write Command returns status: 0x%02X" % status);
    success = status == 0;
    dataSent = False;

    while success and not dataSent:
        dataSent = has_event(transport, initiator.initiator, 200)[0];
        success = success and dataSent;
        if dataSent:
            event = get_event(transport, initiator.initiator, 100);
            trace.trace(7, str(event));
            dataSent = event.event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS;

    return dataSent;

"""
    Receive an ATT Profile response...
"""
def attResponse(transport, initiator, trace, timeout=100):
    success, rxData, cid = True, [], None;

    while success:
        dataReady = le_data_ready(transport, initiator.initiator, timeout);
        timeout = 99;
        success = success and dataReady;
        if dataReady:
            rxPBFlags, rxBCFlags, rxDataPart = le_data_read(transport, initiator.initiator, 100)[2:];
            trace.trace(10, "LE Data Read Command returns PB=%d BC=%d - %2d data bytes: %s" % \
                (rxPBFlags, rxBCFlags, len(rxDataPart), formatArray(rxDataPart)));
            if rxPBFlags & 0x2:
                cid = struct.unpack("<H", bytes(rxDataPart[2:4]))[0]
            if cid != 4:
                trace.trace(6, "Dropping data for non-ATT CID: %d" % cid);
                continue
            rxData += rxDataPart;

    return (len(rxData) > 0), rxData;

"""
    Exchange MTU sizes...
"""
def exchangeMTU(transport, initiator, mtuSize, trace):
    attData = ATTData();

    mtuReply = 0;
    txData = attData.encode( ATTOpcode.ATT_EXCH_MTU_REQUEST, mtuSize );
    trace.trace(7, str(attData));
    success = attRequest( transport, initiator, txData, trace );
    if success:
        success, rxData = attResponse( transport, initiator, trace );
        if success:
            reply = attData.decode( rxData );
            trace.trace(7, str(attData));
            success = reply['opcode'] == ATTOpcode.ATT_EXCH_MTU_RESPONSE;
            if success:
                mtuReply = reply['mtu'];

    return success, min(mtuSize, mtuReply);

def __nextByType(transport, initiator, uuid, firstHandle, lastHandle, trace):
    reply = { 'opcode': ATTOpcode.ATT_ERROR_RESPONSE, 'error': ATTError.ATT_ERROR_ATTRIBUTE_NOT_FOUND };
    attData = ATTData();

    txData = attData.encode( ATTOpcode.ATT_READ_BY_TYPE_REQUEST, firstHandle, lastHandle, uuid );
    trace.trace(7, str(attData));
    success = attRequest( transport, initiator, txData, trace );
    if success:
        success, rxData = attResponse( transport, initiator, trace );
        if success:
            reply = attData.decode( rxData );
            trace.trace(7, str(attData));
            success = reply['opcode'] == ATTOpcode.ATT_READ_BY_TYPE_RESPONSE;

    return success, reply

def __nextFindInformation(transport, initiator, firstHandle, lastHandle, trace):
    reply = { 'opcode': ATTOpcode.ATT_ERROR_RESPONSE, 'error': ATTError.ATT_ERROR_ATTRIBUTE_NOT_FOUND };
    attData = ATTData();

    txData = attData.encode( ATTOpcode.ATT_FIND_INFORMATION_REQUEST, firstHandle, lastHandle );
    trace.trace(7, str(attData));
    success = attRequest( transport, initiator, txData, trace );
    if success:
        success, rxData = attResponse( transport, initiator, trace );
        if success:
            reply = attData.decode( rxData );
            trace.trace(7, str(attData));
            success = reply['opcode'] == ATTOpcode.ATT_FIND_INFORMATION_RESPONSE;

    return success, reply

"""
    Discover Primary Services by using ATT_Find_By_Type_Value_Requests
"""
def discoverPrimaryService(transport, initiator, serviceUUID, trace):
    services = { 'handles': [], 'uuids': [] };
    attData = ATTData();

    success, handle = True, 1;
    while success:
        txData = attData.encode( ATTOpcode.ATT_FIND_BY_TYPE_VALUE_REQUEST, handle, 0xffff, 0x2800, toArray( serviceUUID, \
                                 2 if serviceUUID <= 0xFFFF else 16 ) );
        success = attRequest( transport, initiator, txData, trace );
        if not success:
            break;
        success, rxData = attResponse( transport, initiator, trace );
        if not success:
            break;

        reply = attData.decode( rxData );
        success = reply['opcode'] == ATTOpcode.ATT_FIND_BY_TYPE_VALUE_RESPONSE;
        if not success:
            success = (reply['opcode'] == ATTOpcode.ATT_ERROR_RESPONSE) and \
                      (reply['error'] == ATTError.ATT_ERROR_ATTRIBUTE_NOT_FOUND) and (len(services['handles']) > 0);
            break;

        for first, last in zip(reply['handle'][0::2], reply['handle'][1::2]):
            services['handles'] += [ [ first, last ] ];
            services['uuids'] += [ serviceUUID ];

        handle = reply['handle'][-1] + 1;
        if handle > 0xFFFF:
            break;

    return success, services;

"""
    Discover Services by using ATT_Read_By_Group_Type_Requests
"""
def __discoverServices(transport, initiator, first, last, uuid, trace):
    services = { 'handles': [], 'uuids': [] };
    attData = ATTData();

    success, handle = True, first;
    while success:
        txData = attData.encode( ATTOpcode.ATT_READ_BY_GROUP_TYPE_REQUEST, handle, last, uuid );
        trace.trace(7, str(attData));
        success = attRequest( transport, initiator, txData, trace );
        if not success:
            break;
        success, rxData = attResponse( transport, initiator, trace );
        if not success:
            break;

        reply = attData.decode( rxData );
        trace.trace(7, str(attData));
        success = reply['opcode'] == ATTOpcode.ATT_READ_BY_GROUP_TYPE_RESPONSE;
        if not success:
            success = (reply['opcode'] == ATTOpcode.ATT_ERROR_RESPONSE) and \
                      (reply['error'] == ATTError.ATT_ERROR_ATTRIBUTE_NOT_FOUND) and (len(services['handles']) > 0);
            break;

        for _first, _last, _uuid in zip(reply['first_handle'], reply['last_handle'], reply['value']):
            services['handles'] += [ [ _first, _last ] ];
            services['uuids'] += [ toNumber(_uuid) ];
        
        handle = reply['last_handle'][-1] + 1;
        if handle > last:
            break;

    return success, services;

"""
    Discover Primary Services by using ATT_Read_By_Group_Type_Requests
"""
def discoverPrimaryServices(transport, initiator, trace):
    return __discoverServices(transport, initiator, 0x0001, 0xffff, 0x2800, trace);

"""
    Discover Secondary Services by using ATT_Read_By_Group_Type_Requests
"""
def discoverSecondaryServices(transport, initiator, trace):
    return __discoverServices(transport, initiator, 0x0001, 0xffff, 0x2801, trace);

"""
    Discover Secondary Services by using ATT_Read_By_Type_Requests
"""
def secondaryServicesByType(transport, initiator, trace):
    services = { 'handle': [], 'uuid': [] };
    uuid, attData = 0x2801, ATTData();

    success, handle = True, 1;
    while success:
        success, reply = __nextByType(transport, initiator, uuid, handle, 0xffff, trace);
        if not success:
            success = (reply['opcode'] == ATTOpcode.ATT_ERROR_RESPONSE) and \
                      (reply['error'] == ATTError.ATT_ERROR_ATTRIBUTE_NOT_FOUND) and (len(services['handle']) > 0);
            break;

        for _handle, _value in zip(reply['handle'], reply['value']):
            services['handle'] += [ _handle ];
            if len(_value) > 0:
                services['uuid'] += [ toNumber(_value) ];
            else:
                """
                    NOTE: Test Specification suggest to issue a ATT_READ_REQUEST to get the 128-bit UUID,
                          but the ATT_READ_RESPONSE will only contain the handle range.
                """
                success, _service = __discoverServices(transport, initiator, _handle, _handle, uuid, trace);
                if success:
                    services['uuid'] += _service['uuids'];
        
        handle = reply['handle'][-1] + 1;
        if handle > 0xFFFF:
            break;

    return success, services;

"""
    Discover Included Services by using ATT_Read_By_Type_Requests
"""
def includedServicesByType(transport, initiator, trace):
    services = { 'handles': [], 'uuids': [] };
    uuid, attData = 0x2802, ATTData();

    success, handle = True, 1;
    while success:
        success, reply = __nextByType(transport, initiator, uuid, handle, 0xffff, trace);
        if not success:
            success = (reply['opcode'] == ATTOpcode.ATT_ERROR_RESPONSE) and \
                      (reply['error'] == ATTError.ATT_ERROR_ATTRIBUTE_NOT_FOUND) and (len(services['handles']) > 0);
            break;

        for _handle, _value in zip(reply['handle'], reply['value']):
            services['handles'] += [ [ toNumber(_value[:2]), toNumber(_value[2:4]) ] ];
            if len(_value) > 4:
                services['uuids'] += [ toNumber(_value[4:]) ];
            else:
                """

                    NOTE: Test Specification suggest to issue a ATT_READ_REQUEST to get the 128-bit UUID,
                          but the ATT_READ_RESPONSE will only contain the handle range.
                """
                success, _service = __discoverServices(transport, initiator, toNumber(_value[:2]), toNumber(_value[2:4]), 0x2800, trace);
                if success:
                    services['uuids'] += _service['uuids'];
        
        handle = reply['handle'][-1] + 1;
        if handle > 0xFFFF:
            break;

    return success, services;

"""
    Discover Characteristic by using ATT_Read_By_Type_Requests
"""
def characteristicByType(transport, initiator, handles, characteristicUUID, ignoreErrors, trace):
    characteristics = { 'handle': [], 'value': [] };
    reply = {};
    attData = ATTData();

    success, handle = True, handles[0];
    while success:
        success, reply = __nextByType(transport, initiator, characteristicUUID, handle, handles[1], trace);
        if success:
            for _handle, _value in zip(reply['handle'], reply['value']):
                characteristics['handle'] += [ _handle ];
                characteristics['value'] += [ _value ];

        elif reply['opcode'] == ATTOpcode.ATT_ERROR_RESPONSE:
            if reply['error'] == ATTError.ATT_ERROR_ATTRIBUTE_NOT_FOUND:
                success = len(characteristics['handle']) > 0;
                break;
            elif attData.isPermissionError(reply['error']):
                success = ignoreErrors;

        handle = reply['handle'][-1] + 1;
        if handle > handles[1]:
            break;

    return success, characteristics if success else reply;

"""
    Discover Characteristics by using ATT_Read_By_Type_Requests
"""
def characteristicsByType(transport, initiator, handles, trace):
    characteristics = { 'handle': [], 'property': [], 'value_handle': [], 'uuid': [] };
    attData = ATTData();

    success, handle, uuid = True, handles[0], 0x2803;
    while success:
        success, reply = __nextByType(transport, initiator, uuid, handle, handles[1], trace);
        if success:
            for _handle, _value in zip(reply['handle'], reply['value']):
                characteristics['handle'] += [ _handle ];
                characteristics['property'] += [ _value[0] ];
                characteristics['value_handle'] += [ toNumber(_value[1:3]) ];
                characteristics['uuid'] += [ toNumber(_value[3:]) ];

        elif reply['opcode'] == ATTOpcode.ATT_ERROR_RESPONSE:
            if reply['error'] == ATTError.ATT_ERROR_ATTRIBUTE_NOT_FOUND:
                success = len(characteristics['handle']) > 0;
                break;
            elif reply['error'] == ATTError.ATT_ERROR_READ_NOT_PERMITTED:
                success = True;

        handle = reply['handle'][-1] + 1;
        if handle > handles[1]:
            break;

    return success, characteristics;

"""
    Discover Descriptors by using ATT_Find_Information_Requests
"""
def discoverDescriptors(transport, initiator, handles, trace):
    characteristics = { 'handle': [], 'uuid': [] };
    attData = ATTData();

    success, handle, bCharacteristic, bValue, bDescriptor = True, handles[0], False, False, False;
    while success:
        success, reply = __nextFindInformation(transport, initiator, handle, handles[1], trace);
        if not success:
            success = (reply['opcode'] == ATTOpcode.ATT_ERROR_RESPONSE) and \
                      (reply['error'] == ATTError.ATT_ERROR_ATTRIBUTE_NOT_FOUND) and (len(characteristics['handle']) > 0);
            break;
        """
            The hirachy is:
                CHARACTERIISTIC
                    VALUE
                    DESCRIPTOR...
        """
        for _handle, _uuid in zip(reply['handle'], reply['uuid']):
            bCharacteristic = _uuid == 0x2803;
            bDescriptor = bDescriptor and not bCharacteristic;
            if bDescriptor:
                characteristics['handle'] += [ _handle ];
                characteristics['uuid'] += [ _uuid ];
            bDescriptor = bDescriptor or bValue;
            bValue = bCharacteristic;

        handle = reply['handle'][-1] + 1;
        if handle > handles[1]:
            break;

    return success, characteristics;

"""
    Discover Descriptors by using ATT_Find_Information_Requests
"""
def specificDescriptors(transport, initiator, handles, uuid, trace):
    characteristics = { 'handle': [], 'uuid': [] };
    attData = ATTData();

    success, handle, bCharacteristic, bValue, bDescriptor = True, handles[0], False, False, False;
    while success:
        success, reply = __nextFindInformation(transport, initiator, handle, handles[1], trace);
        if not success:
            success = (reply['opcode'] == ATTOpcode.ATT_ERROR_RESPONSE) and \
                      (reply['error'] == ATTError.ATT_ERROR_ATTRIBUTE_NOT_FOUND) and (len(characteristics['handle']) > 0);
            break;

        for _handle, _uuid in zip(reply['handle'], reply['uuid']):
            bDescriptor = _uuid == uuid;
            if bDescriptor:
                characteristics['handle'] += [ _handle ];
                characteristics['uuid'] += [ _uuid ];

        handle = reply['handle'][-1] + 1;
        if handle > handles[1]:
            break;

    return success, characteristics;

"""
    Partial Read Blob passing handle and offset
"""
def __readBlob(transport, initiator, handle, offset, trace):
    attData = ATTData();
    reply = { 'error': -1 };

    txData = attData.encode( ATTOpcode.ATT_READ_BLOB_REQUEST, handle, offset );
    trace.trace(7, str(attData));
    success = attRequest( transport, initiator, txData, trace );
    if success:
        success, rxData = attResponse( transport, initiator, trace );
        if success:
            reply = attData.decode( rxData );
            trace.trace(7, str(attData));
            success = reply['opcode'] == ATTOpcode.ATT_READ_BLOB_RESPONSE;

    return success, reply;

"""
    Read Blob passing handle and MTU size
"""
def readBlob(transport, initiator, handle, mtuSize, trace):
    attData = ATTData();

    value, offset, success = [], 0, True;
    while success:
        success, reply = __readBlob(transport, initiator, handle, offset, trace);
        if success and len(reply['value']) > 0:
            value += reply['value'];
            offset += len(reply['value']);
            if len(reply['value']) < mtuSize-1:
                break;
        else:
            break;
     
    return success, value if success else reply['error'];

"""
    Read Characteristic passing handle
"""
def readCharacteristic(transport, initiator, handle, trace):
    attData = ATTData();

    txData = attData.encode( ATTOpcode.ATT_READ_REQUEST, handle );
    trace.trace(7, str(attData));
    success = attRequest( transport, initiator, txData, trace );
    if success:
        success, rxData = attResponse( transport, initiator, trace );
        if success:
            reply = attData.decode( rxData );
            trace.trace(7, str(attData));
            success = reply['opcode'] == ATTOpcode.ATT_READ_RESPONSE;

    return success, reply['value'] if success else reply['error'];

"""
    Read Multiple Characteristics passing handles
"""
def readMultipleCharacteristics(transport, initiator, handles, trace):
    attData = ATTData();

    txData = attData.encode( ATTOpcode.ATT_READ_MULTIPLE_REQUEST, handles );
    trace.trace(7, str(attData));
    success = attRequest( transport, initiator, txData, trace );
    if success:
        success, rxData = attResponse( transport, initiator, trace );
        if success:
            reply = attData.decode( rxData );
            trace.trace(7, str(attData));
            success = reply['opcode'] == ATTOpcode.ATT_READ_MULTIPLE_RESPONSE;

    return success, reply['value'] if success else reply['error'];

"""
    Read Characteristics as a String passing handles
"""
def readStringCharacteristic(transport, initiator, handle, trace):
    success, data = readCharacteristic(transport, initiator, handle, trace);

    return success, bytes(data).decode('utf-8') if success else '';

"""
    Writing Characteristic passing handle
"""
def writeCharacteristic(transport, initiator, handle, data, trace):
    attData = ATTData();
    reply = { 'opcode': ATTOpcode.ATT_WRITE_RESPONSE };

    txData = attData.encode( ATTOpcode.ATT_WRITE_REQUEST, handle, data );
    trace.trace(7, str(attData));
    success = attRequest( transport, initiator, txData, trace );
    """
        Receive the response ATT_WRITE_RESPONSE or ATT_ERROR_RESPONSE...
    """
    if success:
        success, rxData = attResponse( transport, initiator, trace );
        if success:
            reply = attData.decode( rxData );
            trace.trace(7, str(attData));
            success = reply['opcode'] == ATTOpcode.ATT_WRITE_RESPONSE;

    return success, reply;

"""
    Writing Characteristic with No Response
"""
def writeNoResponse(transport, initiator, handle, data, trace):
    attData = ATTData();
    reply = { 'opcode': ATTOpcode.ATT_ERROR_RESPONSE, 'error': 0 };

    txData = attData.encode( ATTOpcode.ATT_WRITE_COMMAND, handle, data );
    success = attRequest( transport, initiator, txData, trace );
    """
        Check for a response, could be an ATT_ERROR_RESPONSE...
    """
    if success:
        success, rxData = attResponse( transport, initiator, trace );
        if success:
            reply = attData.decode( rxData );
            success = False;
        else:
            success = True;

    return success, reply;

"""
    Partial Writing Long Characteristic passing handle, offset and data (ATT_Prepare_Write_Request)
"""
def __writeLong(transport, initiator, handle, data, offset, trace):
    attData = ATTData();
    reply = { 'opcode': ATTOpcode.ATT_ERROR_RESPONSE, 'error': -1 };

    txData = attData.encode( ATTOpcode.ATT_PREPARE_WRITE_REQUEST, handle, offset, data );
    success = attRequest( transport, initiator, txData, trace );
    """
        Check for a response, could be an ATT_ERROR_RESPONSE...
    """
    if success:
        success, rxData = attResponse( transport, initiator, trace );
        if success:
            reply = attData.decode( rxData );
            success = reply['opcode'] == ATTOpcode.ATT_PREPARE_WRITE_RESPONSE;

    return success, reply;

"""
    Partial Writing Long Characteristic (ATT_Execute_Write_Request)
"""
def __writeExecute(transport, initiator, trace):
    attData = ATTData();
    reply = { 'opcode': ATTOpcode.ATT_ERROR_RESPONSE, 'error': -1 };

    txData = attData.encode( ATTOpcode.ATT_EXECUTE_WRITE_REQUEST, 1 );
    success = attRequest( transport, initiator, txData, trace );
    if success:
        success, rxData = attResponse( transport, initiator, trace );
        if success:
            reply = attData.decode( rxData );
            success = reply['opcode'] == ATTOpcode.ATT_EXECUTE_WRITE_RESPONSE;

    return success, reply;

"""
    Writing Long Characteristic passing handle, data and MTU size
"""
def writeLong(transport, initiator, handle, data, mtuSize, trace):
    offset, success, attData = 0, True, ATTData();
    reply = { 'opcode': ATTOpcode.ATT_ERROR_RESPONSE, 'error': 0 };

    while success:
        success, reply = __writeLong(transport, initiator, handle, \
                                     data[offset:offset+mtuSize-5 if offset+mtuSize-5 < len(data) else len(data)], offset, trace);
        if not success:
            break;
        offset += len(reply['value']);
        if offset >= len(data):
            break;

    if success:
        success, reply = __writeExecute(transport, initiator, trace);

    return success, reply;

"""
    Receive Notification...
"""
def notification(transport, initiator, trace):
    attData = ATTData();
    reply = { 'opcode': ATTOpcode.ATT_HANDLE_VALUE_NOTIFICATION, 'value': [] };

    success, rxData = attResponse( transport, initiator, trace );
    if success:
        reply = attData.decode( rxData );
        trace.trace(7, str(attData));
        success = reply['opcode'] == ATTOpcode.ATT_HANDLE_VALUE_NOTIFICATION;

    return success, reply;

"""
    Receive Indication and issue Indication Confirmation...
"""
def indication(transport, initiator, trace):
    attData = ATTData();
    reply = { 'opcode': ATTOpcode.ATT_HANDLE_VALUE_INDICATION, 'value': [] };

    success, rxData = attResponse( transport, initiator, trace, 200 );
    if success:
        reply = attData.decode( rxData );
        trace.trace(7, str(attData));
        success = reply['opcode'] == ATTOpcode.ATT_HANDLE_VALUE_INDICATION;
        if success:
            txData = attData.encode( ATTOpcode.ATT_HANDLE_VALUE_CONFIRMATION );
            trace.trace(7, str(attData));
            success = attRequest( transport, initiator, txData, trace );

    return success, reply;

"""
    Obtain the value handle for a Characteristic given its UUID
"""
def valueHandle(characteristics, uuid):
    handle = -1;
    for value_handle, char_uuid in zip(characteristics['value_handle'], characteristics['uuid']):
        if char_uuid == uuid:
            handle = value_handle;
            break;
    return handle;

def filterCharacteristics(characteristics, uuid):
    _characteristics = { 'uuid': [], 'handle': [] };
    for _uuid, _handle in zip(characteristics['uuid'], characteristics['handle']):
        if _uuid == uuid:
            _characteristics['uuid'] += [ _uuid ];
            _characteristics['handle'] += [ _handle ];
    return _characteristics;

"""
    Obtain the peer Bluetooth address by starting a scanner...
"""
def peerAddress(transport, upperTester, trace):
    success, address = False, Address( None, None );

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        scanner = Scanner(transport, upperTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1);
        """
            Start Scanner to obtain address of peer
        """
        success = scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
        """
            Obtain address of Advertiser
        """
        if success:
            address = scanner.reportAddress;

    except Exception as e:
        trace.trace(3, "Failed to obtain peer Address: %s" % str(e));
        success = False;

    return success, address;

"""
    Obtain address of peer, connect to peer and exchange MTU sizes
"""
def preambleConnected(transport, idx, mtuSizeRequested, trace):
    mtuSize = -1;
    """
        Obtain address of Advertiser
    """
    success, address = peerAddress(transport, idx, trace);
    if not success:
        raise UnboundLocalError('Failed to obtain peer Address');

    trace.trace(6, "Advertiser address: %s" % str(address));
    """
        Initiate connection with Advertiser
    """
    initiator = Initiator(transport, idx, None, trace, Address( ExtendedAddressType.PUBLIC, 0x123456789ABC ), address );
    connected = initiator.connect();
    success = success and connected;
    if connected:
        """
            Exchange MTU Size
        """
        success, mtuSize = exchangeMTU(transport, initiator, mtuSizeRequested, trace);
        trace.trace(6,"MTU Size: %d" % mtuSize);

    return success, mtuSize, initiator;

"""
    Trial Pairing and Pairing pause
"""
def pairing_bv_01_c(transport, upperTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        pairing = Pairing(transport, trace, initiator, toNumber(upperIRK));
        paired = pairing.pair();
        if paired:
            trace.trace(6,"Link Encrypted!");
            success = pairing.pause();
            if success:
                trace.trace(6, "Link re-encrypted!");
            else:
                trace.trace(6, "Failed to re-encrypt link!");

        success = success and paired;

        connected = not initiator.disconnect(0x13)
        success = success and not connected;

    return success;

"""
    GAP/GAT/BV-01-C [Mandatory Characteristics]
"""
def gap_gat_bv_01_c(transport, upperTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        """
            Lookup the Generic Access Service (0x1800)
        """
        success, service = discoverPrimaryService(transport, initiator, 0x1800, trace);
        if success:
            """
                Fetch the Characteristics
            """
            sset, attData, gattData = 1, ATTData(), GATTData.instance();
            success, characteristics = characteristicsByType(transport, initiator, service["handles"][0], trace);
            if success:
                for c_uuid, c_handle, c_property, c_vhandle in zip(characteristics["uuid"], characteristics["handle"], \
                                                                   characteristics["property"], characteristics["value_handle"]):
                    trace.trace(6, "Characteristic %s handle %02X value-handle %02X properties %s" % \
                                   (attData.uuid(c_uuid), c_handle, c_vhandle, attData.property(c_property)));

                _characteristics = gattData.characteristics(sset, service["handles"][0][0]);
                _characteristics.pop("permission");
                """
                    Verify Characteristics outline...
                """
                success = characteristics == _characteristics
                trace.trace(6, "GAP Characteristics structure verified %s" % success);
                if success:
                    """
                        Verify Characteristic values...
                    """
                    for c_uuid, c_handle, c_vhandle in zip(characteristics["uuid"], characteristics["handle"], characteristics["value_handle"]):
                        if c_uuid == 0x2A00:
                            _value = gattData.characteristicString(sset, c_handle);
                            ok, reply = readStringCharacteristic(transport, initiator, c_vhandle, trace);
                            trace.trace(6, "Read Characteristic with handle #%d - %s" % (c_vhandle, reply));
                        else:
                            _value = gattData.characteristicValue(sset, c_handle);
                            ok, reply = readCharacteristic(transport, initiator, c_vhandle, trace);
                            trace.trace(6, "Read Characteristic with handle #%d - %s" % (c_vhandle, formatArray(reply)));
                        success = success and ok and reply == _value;
                else:
                    trace.trace(6, "Failed to verify GAP Characteristics structure!");
            else:
                trace.trace(6, "Failed to read GAP Service Characteristics!");
        else:
            trace.trace(6, "Failed to locate GAP Service!");

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GAP/GAT/BV-02-C [Peripheral Privacy Flag Characteristic]
"""
def gap_gat_bv_02_c(transport, upperTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        """
            Lookup the Generic Access Service (0x1800)
        """
        success, service = discoverPrimaryService(transport, initiator, 0x1800, trace);
        """
            Fetch the Peripheral Privacy Flag Characteristic
        """
        success, characteristic = characteristicByType(transport, initiator, service["handles"][0], 0x2A02, False, trace);
        if success:
            flag = characteristic["value"][0]        
            trace.trace(6,"Peripheral Privacy Flag: %d" % flag);
        else:
            trace.trace(6,"Peripheral Privacy Flag: Not present!");

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GAP/GAT/BV-03-C [Reconnection Address Characteristic]
"""
def gap_gat_bv_03_c(transport, upperTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        """
            Lookup the Generic Access Service (0x1800)
        """
        success, service = discoverPrimaryService(transport, initiator, 0x1800, trace);
        """
            Fetch the Reconnection Address Characteristic
        """
        success, characteristic = characteristicByType(transport, initiator, service["handles"][0], 0x2A03, False, trace);
        if success:
            data = characteristic["value"][0];
            trace.trace(6,"Reconnection Address: %s" % formatAddress( data ));
        else:
            trace.trace(6,"Reconnection Address: Not present!");

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GAP/GAT/BV-04-C [Peripheral Preferred Connection Parameters Characteristic]
"""
def gap_gat_bv_04_c(transport, upperTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 512, trace);
    if success:
        """
            Lookup the Generic Access Service (0x1800)
        """
        success, service = discoverPrimaryService(transport, initiator, 0x1800, trace);
        """
            Fetch the Peripheral Preferred Connection Parameters Characteristic
        """
        success, characteristic = characteristicByType(transport, initiator, service["handles"][0], 0x2A04, False, trace);
        if success:
            data = characteristic["value"][0];
            trace.trace(6,"Peripheral Preferred Connection Parameters:");
            trace.trace(6,"Minimum Connection Interval: %d" % toNumber( data[0:2] ));
            trace.trace(6,"Maximum Connection Interval: %d" % toNumber( data[2:4] ));
            trace.trace(6,"              Peripheral Latency: %d" % toNumber( data[4:6] ));
            trace.trace(6,"Connection Supervision Timeout Multiplier: %d" % toNumber( data[6:8] ));
        else:
            trace.trace(6,"Peripheral Preferred Connection Parameters: Not present!");

        connected = not initiator.disconnect(0x13)
        success = success and not connected;
        if not connected:
            """
                Attempt to reconnect with proposed connection parameters
            """
            initiator.intervalMin = toNumber( data[0:2] );
            initiator.intervalMax = toNumber( data[2:4] );
            initiator.latency     = toNumber( data[4:6] );
            initiator.supervisionTimeout = toNumber( data[6:8] );

            connected = initiator.connect();
            success = success and connected;
            if connected:
                transport.wait(200);
                success = initiator.disconnect(0x13) and success;

    return success;

"""
    GAP/GAT/BV-05-C [Changing Device Name]
"""
def gap_gat_bv_05_c(transport, upperTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 512, trace);
    if success:
        """
            Lookup the Generic Access Service (0x1800)
        """
        success, service = discoverPrimaryService(transport, initiator, 0x1800, trace);
        """
            Fetch the Device Name Characteristic
        """
        success, characteristic = characteristicByType(transport, initiator, service["handles"][0], 0x2A00, False, trace);
        if success:
            handle = characteristic["handle"][0];
            data = characteristic["value"][0];
            name = ''.join([chr(_) for _ in data]).decode('utf-8');
            trace.trace(6,"Device Name: %s" % name);

            setName = 'Rødgrød & Blåbær med fløde'.encode('UTF-8');
            data = [ ord(_) for _ in setName ];
            success, reply = writeCharacteristic(transport, initiator, handle, data, trace);
        
            if success:
                success, gotName = readStringCharacteristic(transport, initiator, handle, trace);
                trace.trace(6,"Device Name: %s" % gotName);
                success = success and (gotName == setName);
            else:
                if reply["opcode"] == ATTOpcode.ATT_ERROR_RESPONSE:
                    trace.trace(6,"Failed to write Device Name - error code: %d - %s" % (reply["error"], ATTData().error(reply["error"])) );
                else:
                    trace.trace(6,"Failed to write Device Name - unknown reply: %d" % reply["opcode"]);
        else:
            trace.trace(6,"Device Name: Not present!");

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GAP/GAT/BX-01-C [Discover All Services]
"""
def gap_gat_bx_01_c(transport, upperTester, trace):
    try:
        success, mtuSize, initiator = preambleConnected(transport, upperTester, 512, trace);
        if success:
            """
                Discover all Services
            """
            attData = ATTData();
            success, services = discoverPrimaryServices(transport, initiator, trace);
            for uuid, handles in zip(services["uuids"], services["handles"]):
                trace.trace(6, "Service %s covers [%02X, %02X]" % (attData.uuid(uuid), handles[0], handles[1]));

                success, characteristics = characteristicsByType(transport, initiator, handles, trace);
                for c_uuid, c_handle, c_property, c_vhandle in zip(characteristics["uuid"], characteristics["handle"], \
                                                                   characteristics["property"], characteristics["value_handle"]):
                    trace.trace(6, "    Characteristic %s handle %02X value-handle %02X properties %s" % \
                                   (attData.uuid(c_uuid), c_handle, c_vhandle, attData.property(c_property)));

            success = initiator.disconnect(0x13) and success;

    except Exception as e:
        trace.trace(3, "Discover All Services test failed: %s" % str(e));
        success = False;

    return success;

"""
    GAP/IDLE/NAMP/BV-01-C [Name Discovery Procedure GATT Client]
"""
def gap_idle_namp_bv_01_c(transport, upperTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 512, trace);
    if success:
        """
            Lookup the Generic Access Service (0x1800)
        """
        success, service = discoverPrimaryService(transport, initiator, 0x1800, trace);
        """
            Fetch the Device Name Characteristic
        """
        success, characteristic = characteristicByType(transport, initiator, service["handles"][0], 0x2A00, False, trace);
        if success:
            data = characteristic["value"][0];
            name = bytes(data).decode('utf-8');
            trace.trace(6,"Device Name: %s" % name);
        else:
            trace.trace(6,"Device Name: Not present!");

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAC/BV-01-C [Server accepts Server Configuration]
"""
def gatt_sr_gac_bv_01_c(transport, upperTester, lowerTester, trace):
    for mtuSize in [ 23, 512 ]:
        success, mtuSize, initiator = preambleConnected(transport, upperTester, mtuSize, trace);
        if success:
            """
                Switch to Service Set #1
            """
            sset, attData, gattData = 1, ATTData(), GATTData.instance();
            switch_gatt_service_set(transport, lowerTester, sset, 200);
            """
                Collect all Characteristics that have READ permission
            """
            characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_READ);
            """
                Find the ones that is longer than (MTU-1) if MTU < 512 else the ones that is 512 if MTU = 512
            """
            for _uuid, _handle, _value_handle in zip(characteristics['uuid'], characteristics['handle'], characteristics['value_handle']):
                _value = gattData.characteristicValue(sset, _handle);
                if len(_value) > mtuSize-1:             
                    trace.trace(6, "Read Characteristic %s handle #%d length %d" % (attData.uuid(_uuid), _value_handle, len(_value)));
                    ok, reply = readCharacteristic(transport, initiator, _value_handle, trace);
                    success = success and ok and reply == _value[:mtuSize-1];
    
            success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAD/BV-01-C [Server Discovers All Primary Services]
"""
def gatt_sr_gad_bv_01_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        attData, gattData = ATTData(), GATTData.instance();

        for sset in range(4):
            """
                Switching Service Set
            """
            trace.trace(6, "Switching to Service Set #%d" % sset);
            switch_gatt_service_set(transport, lowerTester, sset, 200);
            """
                Discover all Primary Services
            """
            success, services = discoverPrimaryServices(transport, initiator, trace);
            if success:
                for _uuid, _handles in zip(services["uuids"], services["handles"]):
                    trace.trace(6, "Service %s covers handles [0x%02X, 0x%02X]" % (attData.uuid(_uuid), _handles[0], _handles[1]));
                success = services == gattData.primaryServices(sset)
                trace.trace(6, "Verified Service Set: %s" % success);
            else:
                trace.trace(6, "Unable to discover Primary Services!");
    
        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAD/BV-02-C [Server Discovers Primary Services by Service UUID]
"""
def gatt_sr_gad_bv_02_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        attData, gattData = ATTData(), GATTData.instance();

        for sset in range(4):
            """
                Switching Service Set
            """
            trace.trace(6, "Switching to Service Set #%d" % sset);
            switch_gatt_service_set(transport, lowerTester, sset, 200);
            """
                Iterate over the unique Service UUIDs in the Service Set...
            """
            trace.trace(6, "Service Set #%d:" % sset);
            for uuid in sorted(list(set(gattData.primaryServices(sset)['uuids']))):
                found, services = discoverPrimaryService(transport, initiator, uuid, trace);
                if found:
                    for _uuid, _handles in zip(services["uuids"], services["handles"]):
                        trace.trace(6, "Service %s covers handles [0x%02X, 0x%02X]" % (attData.uuid(_uuid), _handles[0], _handles[1]));
                else:
                    trace.trace(6, "Couldn't find Service %s" % attData.uuid(uuid));

                success = success and found;
                success = success and (services == gattData.primaryServices(sset, uuid));
                trace.trace(6, "Verified Services: %s" % success);
    
        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAD/BV-03-C [Server Finds Included Services]
"""
def gatt_sr_gad_bv_03_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        attData, gattData = ATTData(), GATTData.instance();

        for sset in range(4):
            """
                Switching Service Set
            """
            trace.trace(6, "Switching to Service Set #%d" % sset);
            switch_gatt_service_set(transport, lowerTester, sset, 200);
            """
                Discover Included Services in the selected Service Set...
            """
            found, services = includedServicesByType(transport, initiator, trace);
            if found:
                for uuid, handles in zip(services["uuids"], services["handles"]):
                    trace.trace(6, "Service %s covers handles [0x%02X, 0x%02X]" % (attData.uuid(uuid), handles[0], handles[1]));

            if sset == 0:
                success = success and not found;
            else:
                success = success and found;
                success = success and (services == gattData.includedServices(sset))
            trace.trace(6, "Verified Included Services: %s" % success);

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAD/BV-04-C [Server Discovers All Characteristics of a Service]
"""
def gatt_sr_gad_bv_04_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        attData, gattData = ATTData(), GATTData.instance();

        for sset in range(4):
            """
                Switching Service Set
            """
            trace.trace(6, "Switching to Service Set #%d" % sset);
            switch_gatt_service_set(transport, lowerTester, sset, 200);
            """
                Discover all Primary Services...
            """
            found, services = discoverPrimaryServices(transport, initiator, trace);
            success = success and found;
            for uuid, handles in zip(services["uuids"], services["handles"]):
                trace.trace(6, "Service %s covers handles [0x%02X, 0x%02X]" % (attData.uuid(uuid), handles[0], handles[1]));

                _characteristics = gattData.characteristics(sset, handles[0]);
                _characteristics.pop("permission");

                found, characteristics = characteristicsByType(transport, initiator, handles, trace);
                if found:
                    for c_uuid, c_handle, c_property, c_vhandle in zip(characteristics["uuid"], characteristics["handle"], \
                                                                       characteristics["property"], characteristics["value_handle"]):
                        trace.trace(6, "    Characteristic %s handle 0x%02X value-handle 0x%02X properties %s" % \
                                       (attData.uuid(c_uuid), c_handle, c_vhandle, attData.property(c_property)));
                    success = success and (characteristics == _characteristics)
                else:
                    success = success and len(_characteristics["uuid"]) == 0;
                trace.trace(6, "Characteristics for Service %s Verified: %s" % (attData.uuid(uuid), success));

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAD/BV-05-C [Server Discovers Characteristics by UUID]
"""
def gatt_sr_gad_bv_05_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        attData, gattData = ATTData(), GATTData.instance();

        for sset in range(4):
            """
                Switching Service Set
            """
            trace.trace(6, "Switching to Service Set #%d" % sset);
            switch_gatt_service_set(transport, lowerTester, sset, 200);
            """
                Discover all Primary Services
            """
            found, services = discoverPrimaryServices(transport, initiator, trace);
            success = success and found;
            for uuid, handles in zip(services["uuids"], services["handles"]):
                trace.trace(6, "Service %s covers handles [0x%02X, 0x%02X]" % (attData.uuid(uuid), handles[0], handles[1]));

                _characteristics = gattData.characteristics(sset, handles[0]);
                _characteristics.pop("permission");

                found, characteristics = characteristicsByType(transport, initiator, handles, trace);
                if found:
                    for c_uuid, c_handle, c_property, c_vhandle in zip(characteristics["uuid"], characteristics["handle"], \
                                                                       characteristics["property"], characteristics["value_handle"]):
                        trace.trace(6, "    Characteristic %s handle 0x%02X value-handle 0x%02X properties %s" % \
                                       (attData.uuid(c_uuid), c_handle, c_vhandle, attData.property(c_property)));
                    success = success and (characteristics == _characteristics)
                else:
                    success = success and len(_characteristics["uuid"]) == 0;
                trace.trace(6, "Characteristics for Service %s Verified: %s" % (attData.uuid(uuid), success));

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAD/BV-06-C [Server Discovers All Characteristic Descriptors]
"""
def gatt_sr_gad_bv_06_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        attData, gattData = ATTData(), GATTData.instance();

        for sset in range(4):
            """
                Switching Service Set
            """
            trace.trace(6, "Switching to Service Set #%d" % sset);
            switch_gatt_service_set(transport, lowerTester, sset, 200);
            """
                Discover all Primary Services
            """
            found, services = discoverPrimaryServices(transport, initiator, trace);
            success = success and found;
            for uuid, handles in zip(services["uuids"], services["handles"]):
                trace.trace(6, "Service %s covers handles [0x%02X, 0x%02X]" % (attData.uuid(uuid), handles[0], handles[1]));

                _descriptors = gattData.descriptors(sset, handles[0]);

                found, descriptors = discoverDescriptors(transport, initiator, handles, trace);
                if found:
                    for c_uuid, c_handle in zip(descriptors["uuid"], descriptors["handle"]):
                        trace.trace(6, "    Descriptor %s handle 0x%02X" % (attData.uuid(c_uuid), c_handle));
                    success = success and (descriptors == _descriptors)
                else:
                    success = success and len(_descriptors["uuid"]) == 0;
                trace.trace(6, "Descriptors for Service %s Verified: %s" % (attData.uuid(uuid), success));

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BV-01-C [Server Reads Characteristic Value]
"""
def gatt_sr_gar_bv_01_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 2, ATTData(), GATTData.instance();
        """
            Switch to Service Set #2
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Get all Characteristics that have READ permission
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_READ);
        for c_uuid, c_handle, c_property, c_vhandle in zip(characteristics["uuid"], characteristics["handle"], \
                                                           characteristics["property"], characteristics["value_handle"]):
            trace.trace(6, "Characteristic %s handle 0x%02X value-handle 0x%02X properties %s" % \
                           (attData.uuid(c_uuid), c_handle, c_vhandle, attData.property(c_property)));
            success, data = readCharacteristic(transport, initiator, c_vhandle, trace);
            trace.trace(6, "   Characteristic Value: %s" % formatArray(data));
            match = data == gattData.characteristicValue(sset, c_handle);
            success = success and match;                    
            trace.trace(6, "   Characteristic Value Verified: %s" % success);

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-01-C [Read Not Permitted error - Reading Characteristic Value]
"""
def gatt_sr_gar_bi_01_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, prevLast, attData, gattData = 2, 0, ATTData(), GATTData.instance();
        """
            Switch to Service Set #2
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Services
        """
        services = gattData.allServices(sset);
        for uuid, handles in zip(services["uuids"], services["handles"]):
            trace.trace(6, "Service %s covers handles [%02d, %02d]" % (attData.uuid(uuid), handles[0], handles[1]));
        
            if handles[0] > (prevLast+1):
                ok, data = readCharacteristic(transport, initiator, (handles[0] + prevLast)//2, trace);
                success = success and not ok and data == ATTError.ATT_ERROR_INVALID_HANDLE;
                trace.trace(6, "Attempted to read Characteristic @ handle %02d - %s" % ((handles[0] + prevLast)//2, attData.error(data)));
            prevLast = handles[1];

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-02-C [Invalid Handle error - Reading Characteristic Value]
"""
def gatt_sr_gar_bi_02_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 2, ATTData(), GATTData.instance();
        """
            Switch to Service Set #2
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Get all Characteristics that doesn't have READ permission
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_ANY_READ, True);
        for c_uuid, c_handle, c_property, c_vhandle in zip(characteristics["uuid"], characteristics["handle"], \
                                                           characteristics["property"], characteristics["value_handle"]):
            trace.trace(6, "Characteristic %s handle 0x%02X value-handle 0x%02X properties %s" % \
                           (attData.uuid(c_uuid), c_handle, c_vhandle, attData.property(c_property)));
            ok, data = readCharacteristic(transport, initiator, c_vhandle, trace);
            success = success and not ok and data == ATTError.ATT_ERROR_READ_NOT_PERMITTED;
            trace.trace(6, "Attempted to read Characteristic @ handle %02d - %s" % (c_vhandle, attData.error(data)));

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-03-C [Insufficient Authorization error - Reading Characteristic Value]
"""
def gatt_sr_gar_bi_03_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that have Authorized READ permission
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_READ_AUTHOR);
        for c_uuid, c_handle, c_property, c_permission, c_vhandle in zip(characteristics["uuid"], characteristics["handle"], \
                                                                         characteristics["property"], characteristics["permission"], \
                                                                         characteristics["value_handle"]):
            trace.trace(6, "Characteristic %s handle 0x%02X value-handle 0x%02X properties %s permissions %s" % \
                           (attData.uuid(c_uuid), c_handle, c_vhandle, attData.property(c_property), attData.permission(c_permission)));
            ok, data = readCharacteristic(transport, initiator, c_vhandle, trace);
            success = success and not ok and data == ATTError.ATT_ERROR_INSUFFICIENT_AUTHORIZATION;
            trace.trace(6, "Attempted to read Characteristic @ handle 0x%02X - %s" % (c_vhandle, attData.error(data)));

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-04-C [Insufficient Authentication error - Reading Characteristic Value]
"""
def gatt_sr_gar_bi_04_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 512, trace);
    if success:
        sset, found, attData, gattData = 1, False, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that have Authenticated READ permission
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_READ_AUTHEN);
        for c_uuid, c_handle, c_property, c_permission, c_vhandle in zip(characteristics["uuid"], characteristics["handle"], \
                                                                         characteristics["property"], characteristics["permission"], \
                                                                         characteristics["value_handle"]):
            trace.trace(6, "Characteristic %s handle 0x%02X value-handle 0x%02X properties %s permissions %s" % \
                           (attData.uuid(c_uuid), c_handle, c_vhandle, attData.property(c_property), attData.permission(c_permission)));
            ok, data = readCharacteristic(transport, initiator, c_vhandle, trace);
            success = success and not ok and data == ATTError.ATT_ERROR_INSUFFICIENT_AUTHENTICATION;
            trace.trace(6, "Attempted to read Characteristic @ handle 0x%02X - %s" % (c_vhandle, attData.error(data)));
            found = True;
    
        if not found:
            trace.trace(6, "Didn't find any characteristics that require Authentication for reading...");
        success = success and found;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BV-03-C [Server Reads using Characteristic UUID]
"""
def gatt_sr_gar_bv_03_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect a set of unique Characteristics UUIDs
        """
        uuids = set(gattData.characteristics(sset)['uuid']);
        for uuid in list(uuids):
            s_uuid = attData.uuid(uuid);
            """
                Select one 16-bit UUID and one 128-bit UUID
            """
            if s_uuid == '0000B006-0000-1000-8000-00805F9B34FB' or s_uuid == '0000B009-0000-0000-0123-456789ABCDEF':
                trace.trace(6, "Read Characteristics matching %s" % attData.uuid(uuid));
                found, characteristics = characteristicByType(transport, initiator, [ 0x0001, 0xFFFF ], uuid, True, trace);
                success = success and found;
                for c_handle, c_value in zip(characteristics["handle"], characteristics["value"]):
                    trace.trace(6, "    Characteristic %s handle 0x%02X value %s" % (attData.uuid(uuid), c_handle, formatArray(c_value)));
                    e_value = gattData.characteristicValue(sset, c_handle-1);
                    match = (c_value == e_value) if len(e_value) < mtuSize-3 else (c_value == e_value[:mtuSize-4]);
                    success = success and match;                    
                    trace.trace(6, "    Characteristic Value Verified: %s" % success);
   
        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-06-C [Read Not Permitted error - Reading Characteristic by UUID]
"""
def gatt_sr_gar_bi_06_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Filter out all Characteristics which doesn't have READ permission
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_ANY_READ, True);
        for _uuid, _handle, in zip(characteristics['uuid'], characteristics['handle']):
            _service = gattData.serviceCovering(sset, _handle);
            trace.trace(6, "Read Characteristics matching %s [%d, %d]" % (attData.uuid(_uuid), _service['handles'][0], _service['handles'][1]));
            found, reply = characteristicByType(transport, initiator, _service['handles'], _uuid, False, trace);
            if found and reply['handle'] != _handle+1:
                continue;
            success = success and not found and reply['error'] == ATTError.ATT_ERROR_READ_NOT_PERMITTED;
            trace.trace(6, "Reply: %s" % attData.error(reply['error']));
   
        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-07-C [Attribute Not Found error - Reading Characteristic by UUID]
"""
def gatt_sr_gar_bi_07_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 512, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);

        for _uuid in [ 0xB018, 0xB019 ]:
            trace.trace(6, "Read Characteristics matching %s [%d, %d]" % (attData.uuid(_uuid), 1, 0xFFFF));
            found, reply = characteristicByType(transport, initiator, [ 0x0001, 0xFFFF ], _uuid, False, trace);
            success = success and not found and reply['error'] == ATTError.ATT_ERROR_ATTRIBUTE_NOT_FOUND;
            trace.trace(6, "Reply: %s" % attData.error(reply['error']));
   
        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-09-C [Insufficient Authorization error - Reading Using Characteristic UUID]
"""
def gatt_sr_gar_bi_09_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 512, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Filter out all Characteristics which have READ AUTHORIZED permission
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_READ_AUTHOR);
        for _uuid, _handle, in zip(characteristics['uuid'], characteristics['handle']):
            trace.trace(6, "Read Characteristics matching %s [%d, %d]" % (attData.uuid(_uuid), _handle, 0xFFFF));
            found, reply = characteristicByType(transport, initiator, [_handle, 0xFFFF], _uuid, False, trace);
            success = success and not found and reply['error'] == ATTError.ATT_ERROR_INSUFFICIENT_AUTHORIZATION;
            trace.trace(6, "Reply: %s" % attData.error(reply['error']));
   
        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-10-C [Insufficient Authentication error - Reading Using Characteristic UUID]
"""
def gatt_sr_gar_bi_10_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 512, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Filter out all Characteristics which have READ AUTHENTICATION permission
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_READ_AUTHEN);
        for _uuid, _handle, in zip(characteristics['uuid'], characteristics['handle']):
            trace.trace(6, "Read Characteristics matching %s [%d, %d]" % (attData.uuid(_uuid), _handle, 0xFFFF));
            found, reply = characteristicByType(transport, initiator, [_handle, 0xFFFF], _uuid, False, trace);
            success = success and not found and reply['error'] == ATTError.ATT_ERROR_INSUFFICIENT_AUTHENTICATION;
            trace.trace(6, "Reply: %s" % attData.error(reply['error']));
   
        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-11-C [Insufficient Encryption Key Size error - Reading Using Characteristic UUID]
"""
def gatt_sr_gar_bi_11_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 512, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Filter out all Characteristics which have READ ENCRYPTED permission
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_READ_ENCRYPT);
        for _uuid, _handle, in zip(characteristics['uuid'], characteristics['handle']):
            trace.trace(6, "Read Characteristics matching %s [%d, %d]" % (attData.uuid(_uuid), _handle, 0xFFFF));
            found, reply = characteristicByType(transport, initiator, [_handle, 0xFFFF], _uuid, False, trace);
            success = success and not found and reply['error'] == ATTError.ATT_ERROR_INSUFFICIENT_ENCRYPTION;
            trace.trace(6, "Reply: %s" % attData.error(reply['error']));
   
        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BV-04-C [Server Reads Long Characteristic Value]
"""
def gatt_sr_gar_bv_04_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 23, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Filter out all Characteristics which have READ permission
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_READ);

        prevSize = 513;
        for m,n in zip([2,2,1,0], [mtuSize//2,0,0,mtuSize//2]):
            _characteristics = { 'uuid': [], 'handle': [], 'value_handle': [] };
            for _uuid, _handle, _value_handle in zip(characteristics['uuid'], characteristics['handle'], characteristics['value_handle']):
                _size = len(gattData.characteristicValue(sset, _handle));
                if m*mtuSize-1+n <= _size and _size < prevSize:
                    _characteristics['uuid']         += [ _uuid ];
                    _characteristics['handle']       += [ _handle ];
                    _characteristics['value_handle'] += [ _value_handle ];
                    prevSize = _size;

            for _uuid, _handle, _value_handle in zip(_characteristics['uuid'], _characteristics['handle'], _characteristics['value_handle']):
                trace.trace(6, "Read Characteristic %s [#%d]" % (attData.uuid(_uuid), _handle));
                found, reply = readCharacteristic(transport, initiator, _value_handle, trace);
                success = success and found and reply == gattData.characteristicValue(sset, _handle)[:mtuSize-1];
                if found:            
                    trace.trace(6, "Data: %s" % formatArray(reply));
                found, reply = readBlob(transport, initiator, _value_handle, mtuSize, trace);
                success = success and found and reply == gattData.characteristicValue(sset, _handle);
                if found:
                    trace.trace(6, "Data: %s" % formatArray(reply));
   
        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-12-C [Read Not Permitted error - Reading Long Characteristic Value]
"""
def gatt_sr_gar_bi_12_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Filter out all Characteristics which doesn't have READ permission
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_ANY_READ, True);
        for _uuid, _handle, _value_handle in zip(characteristics['uuid'], characteristics['handle'], characteristics['value_handle']):
            trace.trace(6, "Read Characteristic %s [#%d]" % (attData.uuid(_uuid), _handle));
            found, reply = readBlob(transport, initiator, _value_handle, mtuSize, trace);
            success = success and not found and reply == ATTError.ATT_ERROR_READ_NOT_PERMITTED;
            if not found:
                trace.trace(6, "Reply: %s" % attData.error(reply));
   
        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-13-C [Invalid Offset error - Reading Long Characteristic Value]
"""
def gatt_sr_gar_bi_13_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Filter out all Characteristics which have READ permission
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_READ);
        for _uuid, _handle, _value_handle in zip(characteristics['uuid'], characteristics['handle'], characteristics['value_handle']):
            trace.trace(6, "Read Characteristic %s [#%d]" % (attData.uuid(_uuid), _handle));
            found, reply = __readBlob(transport, initiator, _value_handle, len(gattData.characteristicValue(sset, _handle))+1, trace);
            success = success and not found and reply['error'] == ATTError.ATT_ERROR_INVALID_OFFSET;
            if not found:
                trace.trace(6, "Reply: %s" % attData.error(reply['error']));
   
        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-14-C [Invalid Handle error - Reading Long Characteristic Value]
"""
def gatt_sr_gar_bi_14_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, prevLast, attData, gattData = 1, 0, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Services
        """
        services = gattData.allServices(sset);
        for uuid, handles in zip(services["uuids"], services["handles"]):
            trace.trace(6, "Service %s covers [%02d, %02d]" % (attData.uuid(uuid), handles[0], handles[1]));
        
            if handles[0] > (prevLast+1):
                trace.trace(6, "Read Blob @[#%d]" % ((handles[0] + prevLast)//2));
                found, reply = __readBlob(transport, initiator, (handles[0] + prevLast)//2, 0, trace);
                success = success and not found and reply['error'] == ATTError.ATT_ERROR_INVALID_HANDLE;
                if not found:
                    trace.trace(6, "Reply: %s" % attData.error(reply['error']));
            prevLast = handles[1];
  
        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-15-C [Insufficient Authorization error - Reading Long Characteristic Value]
"""
def gatt_sr_gar_bi_15_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that require READ AUTHORIZATION
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_READ_AUTHOR);
        for _uuid, _handle, _value_handle in zip(characteristics['uuid'], characteristics['handle'], characteristics['value_handle']):
            trace.trace(6, "Read Blob @[#%d]" % _value_handle);
            found, reply = readBlob(transport, initiator, _value_handle, mtuSize, trace);
            success = success and not found and (reply == ATTError.ATT_ERROR_INSUFFICIENT_AUTHORIZATION);
            trace.trace(6, "Reply: %s" % attData.error(reply));
  
        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-16-C [Insufficient Authentication error - Reading Long Characteristic Value]
"""
def gatt_sr_gar_bi_16_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that require READ AUTHENTICATION
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_READ_AUTHEN);
        for _uuid, _handle, _value_handle in zip(characteristics['uuid'], characteristics['handle'], characteristics['value_handle']):
            trace.trace(6, "Read Blob @[#%d]" % _value_handle);
            found, reply = readBlob(transport, initiator, _value_handle, mtuSize, trace);
            success = success and not found and (reply == ATTError.ATT_ERROR_INSUFFICIENT_AUTHENTICATION);
            trace.trace(6, "Reply: %s" % attData.error(reply));
  
        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-17-C [Insufficient Encryption Key Size error - Reading Long Characteristic Value]
"""
def gatt_sr_gar_bi_17_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that require READ ENCRYPTED
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_READ_ENCRYPT);
        for _uuid, _handle, _value_handle in zip(characteristics['uuid'], characteristics['handle'], characteristics['value_handle']):
            trace.trace(6, "Read Blob @[#%d]" % _value_handle);
            found, reply = readBlob(transport, initiator, _value_handle, mtuSize, trace);
            success = success and not found and (reply == ATTError.ATT_ERROR_INSUFFICIENT_ENCRYPTION);
            trace.trace(6, "Reply: %s" % attData.error(reply));
  
        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BV-05-C [Server Reads Multiple Characteristic Values]

    NOTE: If the Request is fragmented - no reponse is received.
"""
def gatt_sr_gar_bv_05_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        sset, gattData = 2, GATTData.instance();
        """
            Switch to Service Set #2
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that can be READ
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_READ);
        _size = 0; _handles = []; _values = [];
        for _handle, _value_handle in zip(characteristics['handle'], characteristics['value_handle']):
            _value = gattData.characteristicValue(sset, _handle);
            if (_size + len(_value)) < (mtuSize-1):
                _size += len(_value);
                _handles += [ _value_handle ];
                _values += _value;
    
        trace.trace(6, "Read Multiple Characteristics @[%s]" % formatArray(_handles));
        found, values = readMultipleCharacteristics(transport, initiator, _handles, trace);
        success = success and found and values == _values;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-18-C [Read Not Permitted error - Reading Multiple Characteristic Values]
"""
def gatt_sr_gar_bi_18_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 2, ATTData(), GATTData.instance();
        """
            Switch to Service Set #2
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that can be READ
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_ANY_READ, True);
        _size = 0; _handles = []; _values = [];
        for _handle, _value_handle in zip(characteristics['handle'], characteristics['value_handle']):
            _value = gattData.characteristicValue(sset, _handle);
            if (_size + len(_value)) < (mtuSize-1):
                _size += len(_value);
                _handles += [ _value_handle ];
                _values += _value;
    
        trace.trace(6, "Read Multiple Characteristics @[%s]" % formatArray(_handles));
        found, values = readMultipleCharacteristics(transport, initiator, _handles, trace);
        success = success and not found and values == ATTError.ATT_ERROR_READ_NOT_PERMITTED;
        if not found:
            trace.trace(6, "Reply: %s" % attData.error(values));

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-19-C [Invalid Handle error - Reading Multiple Characteristic Values]
"""
def gatt_sr_gar_bi_19_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, prevLast, attData, gattData = 2, 0, ATTData(), GATTData.instance();
        """
            Switch to Service Set #2
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Services
        """
        services = gattData.allServices(sset);
        _handles = [];
        for handles in services["handles"]:
            if handles[0] > (prevLast+1):
                _handles += [ (handles[0] + prevLast)//2 ];
            prevLast = handles[1];

        trace.trace(6, "Read Multiple Characteristics @[%s]" % formatArray(_handles));
        found, values = readMultipleCharacteristics(transport, initiator, _handles, trace);
        success = success and not found and values == ATTError.ATT_ERROR_INVALID_HANDLE;
        if not found:
            trace.trace(6, "Reply: %s" % attData.error(values));

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-20-C [Insufficient Authorization error - Reading Multiple Characteristic Values]
"""
def gatt_sr_gar_bi_20_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that require READ AUTHORIZATION
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_READ_AUTHOR);
        _handles = [];
        for _handle, _value_handle in zip(characteristics['handle'], characteristics['value_handle']):
            _handles += [ _value_handle ];
    
        trace.trace(6, "Read Multiple Characteristics @[%s]" % formatArray(_handles));
        found, values = readMultipleCharacteristics(transport, initiator, _handles, trace);
        success = success and not found and values == ATTError.ATT_ERROR_INSUFFICIENT_AUTHORIZATION;
        if not found:
            trace.trace(6, "Reply: %s" % attData.error(values));

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-21-C [Insufficient Authentication error - Reading Multiple Characteristic Values]
"""
def gatt_sr_gar_bi_21_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that require READ AUTHENTICATION
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_READ_AUTHEN);
        _handles = [];
        for _handle, _value_handle in zip(characteristics['handle'], characteristics['value_handle']):
            _handles += [ _value_handle ];
    
        trace.trace(6, "Read Multiple Characteristics @[%s]" % formatArray(_handles));
        found, values = readMultipleCharacteristics(transport, initiator, _handles, trace);
        success = success and not found and values == ATTError.ATT_ERROR_INSUFFICIENT_AUTHENTICATION;
        if not found:
            trace.trace(6, "Reply: %s" % attData.error(values));

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BI-22-C [Insufficient Encryption Key Size error - Reading Multiple Characteristic Values]
"""
def gatt_sr_gar_bi_22_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that require READ ENCRYPTED
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_READ_ENCRYPT);
        _handles = [];
        for _handle, _value_handle in zip(characteristics['handle'], characteristics['value_handle']):
            _handles += [ _value_handle ];
    
        trace.trace(6, "Read Multiple Characteristics @[%s]" % formatArray(_handles));
        found, values = readMultipleCharacteristics(transport, initiator, _handles, trace);
        success = success and not found and values == ATTError.ATT_ERROR_INSUFFICIENT_ENCRYPTION;
        if not found:
            trace.trace(6, "Reply: %s" % attData.error(values));

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BV-06-C [Server Reads Characteristic Descriptors]
"""
def gatt_sr_gar_bv_06_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, gattData = 1, GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Descriptors that have READ access
        """
        descriptors = gattData.descriptors(sset, None, ATTPermission.ATT_PERM_READ);
        for _handle in descriptors['handle']:
            trace.trace(6, "Read Descriptor @[#%d]" % _handle);
            success, data = readCharacteristic(transport, initiator, _handle, trace);
            trace.trace(6, "Descriptor Value: %s" % formatArray(data));
            match = data == gattData.descriptorValue(sset, _handle);
            if not match:
                trace.trace(6, "    GATT Database  Value: %s" % formatArray(gattData.descriptorValue(sset, _handle)));
            success = success and match;                    

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAR/BV-07-C [Server Reads Long Characteristic Descriptor]
"""
def gatt_sr_gar_bv_07_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 23, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Descriptors that have READ access
        """
        descriptors = gattData.descriptors(sset, None, ATTPermission.ATT_PERM_READ);
        prevSize = 513;
        for m,n in zip([2,2,1,0], [mtuSize/2,0,0,mtuSize/2]):
            _descriptors = { 'uuid': [], 'handle': [] };
            for _uuid, _handle in zip(descriptors['uuid'], descriptors['handle']):
                _size = len(gattData.descriptorValue(sset, _handle));
                if m*mtuSize-1+n <= _size and _size < prevSize:
                    _descriptors['uuid']         += [ _uuid ];
                    _descriptors['handle']       += [ _handle ];
                    prevSize = _size;

            for _uuid, _handle in zip(_descriptors['uuid'], _descriptors['handle']):
                trace.trace(6, "Read Descriptor %s [#%d]" % (attData.uuid(_uuid), _handle));
                found, reply = readCharacteristic(transport, initiator, _handle, trace);
                success = success and found and reply == gattData.descriptorValue(sset, _handle)[:mtuSize-1];
                if found:            
                    trace.trace(6, "Data: %s" % formatArray(reply));
                found, reply = readBlob(transport, initiator, _handle, mtuSize, trace);
                success = success and found and reply == gattData.descriptorValue(sset, _handle);
                if found:
                    trace.trace(6, "Data: %s" % formatArray(reply));

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BV-01-C [Server Writes Without Response]
"""
def gatt_sr_gaw_bv_01_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        sset, attData, gattData = 2, ATTData(), GATTData.instance();
        """
            Switch to Service Set #2
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that have WRITE access
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_WRITE);
        for _uuid, _handle, _value_handle, _permission in zip(characteristics['uuid'], characteristics['handle'], \
                                                              characteristics['value_handle'], characteristics['permission']):
            _value = gattData.characteristicValue(sset, _handle);
            if 1 < len(_value) and len(_value) < mtuSize-4:
                trace.trace(6, "Write Characteristic %s [#%d]" % (attData.uuid(_uuid), _value_handle));
                ok, reply = writeNoResponse(transport, initiator, _value_handle, _value[::-1], trace);
                success = success and ok;
                if not ok:
                    trace.trace(6, "Write failed: %s" % attData.error(reply['error']));
                else:
                    if (_permission & ATTPermission.ATT_PERM_READ) == ATTPermission.ATT_PERM_READ:
                        ok, value = readCharacteristic(transport, initiator, _value_handle, trace);
                        success = success and ok and value == _value[::-1];
                        trace.trace(6, "Write Verified: %s" % success);
                    if _value != _value[::-1]:
                        ok, reply = writeNoResponse(transport, initiator, _value_handle, _value, trace);
                        success = success and ok;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BV-03-C [Server Writes Characteristic Value]
"""
def gatt_sr_gaw_bv_03_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 2, ATTData(), GATTData.instance();
        """
            Switch to Service Set #2
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that have WRITE access
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_WRITE);
        for _uuid, _handle, _value_handle, _permission in zip(characteristics['uuid'], characteristics['handle'], \
                                                              characteristics['value_handle'], characteristics['permission']):
            _value = gattData.characteristicValue(sset, _handle);
            if 2 < len(_value) and len(_value) < mtuSize-4:
                trace.trace(6, "Write Characteristic %s [#%d]" % (attData.uuid(_uuid), _value_handle));
                ok, reply = writeCharacteristic(transport, initiator, _value_handle, _value[::-1], trace);
                success = success and ok;
                if not ok:
                    trace.trace(6, "Write failed: %s" % attData.error(reply['error']));
                else:
                    if (_permission & ATTPermission.ATT_PERM_READ) == ATTPermission.ATT_PERM_READ:
                        ok, value = readCharacteristic(transport, initiator, _value_handle, trace);
                        success = success and ok and value == _value[::-1];
                        trace.trace(6, "Write Verified: %s" % success);
                    if _value != _value[::-1]:
                        ok, reply = writeCharacteristic(transport, initiator, _value_handle, _value, trace);
                        success = success and ok;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BI-02-C [Invalid Handle error - Writing Characteristic Value]
"""
def gatt_sr_gaw_bi_02_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, prevLast, attData, gattData = 2, 0, ATTData(), GATTData.instance();
        """
            Switch to Service Set #2
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Services
        """
        services = gattData.allServices(sset);
        for uuid, handles in zip(services["uuids"], services["handles"]):
            trace.trace(6, "Service %s covers [%02d, %02d]" % (attData.uuid(uuid), handles[0], handles[1]));
        
            if handles[0] > (prevLast+1):
                trace.trace(6, "Write Characteristic @[#%d]" % ((handles[0] + prevLast)//2));
                ok, reply = writeCharacteristic(transport, initiator, (handles[0] + prevLast)//2, [ 0x00 ], trace);
                success = success and not ok and reply['error'] == ATTError.ATT_ERROR_INVALID_HANDLE;
                if not ok:
                    trace.trace(6, "Write failed: %s" % attData.error(reply['error']));
            prevLast = handles[1];

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BI-03-C [Write Not Permitted error - Writing Characteristic Value]
"""
def gatt_sr_gaw_bi_03_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that doesn't allow WRITE access
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_ANY_WRITE, True);
        for _uuid, _handle, _value_handle in zip(characteristics['uuid'], characteristics['handle'], characteristics['value_handle']):
            _value = gattData.characteristicValue(sset, _handle);
            if len(_value) < mtuSize-4:
                trace.trace(6, "Write Characteristic %s [#%d]" % (attData.uuid(_uuid), _value_handle));
                ok, reply = writeCharacteristic(transport, initiator, _value_handle, _value[::-1], trace);
                success = success and not ok and reply['error'] == ATTError.ATT_ERROR_WRITE_NOT_PERMITTED;
                if not ok:
                    trace.trace(6, "Write failed: %s" % attData.error(reply['error']));

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BI-04-C [Insufficient Authorization error - Writing Characteristic Value]
"""
def gatt_sr_gaw_bi_04_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that require WRITE Authorization
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_WRITE_AUTHOR);
        for _uuid, _handle, _value_handle in zip(characteristics['uuid'], characteristics['handle'], characteristics['value_handle']):
            _value = gattData.characteristicValue(sset, _handle);
            if len(_value) < mtuSize-4:
                trace.trace(6, "Write Characteristic %s [#%d]" % (attData.uuid(_uuid), _value_handle));
                ok, reply = writeCharacteristic(transport, initiator, _value_handle, _value[::-1], trace);
                success = success and not ok and reply['error'] == ATTError.ATT_ERROR_INSUFFICIENT_AUTHORIZATION;
                if not ok:
                    trace.trace(6, "Write failed: %s" % attData.error(reply['error']));
                else:
                    ok, reply = writeCharacteristic(transport, initiator, _value_handle, _value, trace);

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BI-05-C [Insufficient Authentication error - Writing Characteristic Value]
"""
def gatt_sr_gaw_bi_05_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that require WRITE Authentication
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_WRITE_AUTHEN);
        for _uuid, _handle, _value_handle in zip(characteristics['uuid'], characteristics['handle'], characteristics['value_handle']):
            _value = gattData.characteristicValue(sset, _handle);
            if len(_value) < mtuSize-4:
                trace.trace(6, "Write Characteristic %s [#%d]" % (attData.uuid(_uuid), _value_handle));
                ok, reply = writeCharacteristic(transport, initiator, _value_handle, _value[::-1], trace);
                success = success and not ok and reply['error'] == ATTError.ATT_ERROR_INSUFFICIENT_AUTHENTICATION;
                if not ok:
                    trace.trace(6, "Write failed: %s" % attData.error(reply['error']));
                else:
                    ok, reply = writeCharacteristic(transport, initiator, _value_handle, _value, trace);

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BI-06-C [Insufficient Encryption Key Size error - Writing Characteristic Value]
"""
def gatt_sr_gaw_bi_06_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that require WRITE Authentication
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_WRITE_ENCRYPT);
        for _uuid, _handle, _value_handle in zip(characteristics['uuid'], characteristics['handle'], characteristics['value_handle']):
            _value = gattData.characteristicValue(sset, _handle);
            if len(_value) < mtuSize-4:
                trace.trace(6, "Write Characteristic %s [#%d]" % (attData.uuid(_uuid), _value_handle));
                ok, reply = writeCharacteristic(transport, initiator, _value_handle, _value[::-1], trace);
                success = success and not ok and reply['error'] == ATTError.ATT_ERROR_INSUFFICIENT_ENCRYPTION;
                if not ok:
                    trace.trace(6, "Write failed: %s" % attData.error(reply['error']));
                else:
                    ok, reply = writeCharacteristic(transport, initiator, _value_handle, _value, trace);

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BV-05-C [Server Writes Long Characteristic Value]

    NOTE: Attempting to execute this test with an MTU size of 23 bytes will fail with an error ATT_ERROR_PREPARE_QUEUE_FULL.
"""
def gatt_sr_gaw_bv_05_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        sset, attData, gattData = 2, ATTData(), GATTData.instance();
        """
            Switch to Service Set #2
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that have WRITE access
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_WRITE);
        for _uuid, _handle, _value_handle, _permission in zip(characteristics['uuid'], characteristics['handle'], \
                                                              characteristics['value_handle'], characteristics['permission']):
            _value = gattData.characteristicValue(sset, _handle);
            if len(_value) > mtuSize-5:
                trace.trace(6, "Write Characteristic %s [#%d]" % (attData.uuid(_uuid), _value_handle));
                ok, reply = writeLong(transport, initiator, _value_handle, _value[::-1], mtuSize, trace);
                success = success and ok;
                if not ok:
                    trace.trace(6, "Write Long failed: %s" % attData.error(reply['error']));
                else:
                    if (_permission & ATTPermission.ATT_PERM_READ) == ATTPermission.ATT_PERM_READ:
                        ok, value = readBlob(transport, initiator, _value_handle, mtuSize, trace);
                        success = success and ok and value == _value[::-1];
                        trace.trace(6, "Write Verified: %s" % success);
                    if _value != _value[::-1]:
                        ok, reply = writeLong(transport, initiator, _value_handle, _value, mtuSize, trace);
                        success = success and ok;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BI-07-C [Invalid Handle error - Writing Long Characteristic Value]
"""
def gatt_sr_gaw_bi_07_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, prevLast, attData, gattData = 2, 0, ATTData(), GATTData.instance();
        """
            Switch to Service Set #2
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Services
        """
        services = gattData.allServices(sset);
        for uuid, handles in zip(services["uuids"], services["handles"]):
            trace.trace(6, "Service %s covers [%02d, %02d]" % (attData.uuid(uuid), handles[0], handles[1]));
        
            if handles[0] > (prevLast+1):
                trace.trace(6, "Write Long Characteristic @[#%d]" % ((handles[0] + prevLast)//2));
                ok, reply = writeLong(transport, initiator, (handles[0] + prevLast)//2, [ 0x00 ], mtuSize, trace);
                success = success and not ok and reply['error'] == ATTError.ATT_ERROR_INVALID_HANDLE;
                if not ok:
                    trace.trace(6, "Write failed: %s" % attData.error(reply['error']));
            prevLast = handles[1];

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BI-08-C [Write Not Permitted error - Writing Long Characteristic Value]
"""
def gatt_sr_gaw_bi_08_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that doesn't allow WRITE access
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_ANY_WRITE, True);
        for _uuid, _handle, _value_handle in zip(characteristics['uuid'], characteristics['handle'], characteristics['value_handle']):
            _value = gattData.characteristicValue(sset, _handle);
            if len(_value) > mtuSize-5:
                trace.trace(6, "Write Long Characteristic %s [#%d]" % (attData.uuid(_uuid), _value_handle));
                ok, reply = writeLong(transport, initiator, _value_handle, _value[::-1], mtuSize, trace);
                success = success and not ok and reply['error'] == ATTError.ATT_ERROR_WRITE_NOT_PERMITTED;
                if not ok:
                    trace.trace(6, "Write failed: %s" % attData.error(reply['error']));
                else:
                    ok, reply = writeLong(transport, initiator, _value_handle, _value, mtuSize, trace);

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BI-09-C [Invalid Offset error - Writing Long Characteristic Value]
"""
def gatt_sr_gaw_bi_09_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 43, trace);
    if success:
        sset, attData, gattData = 2, ATTData(), GATTData.instance();
        """
            Switch to Service Set #2
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Filter out all Characteristics which have WRITE permission
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_WRITE);
        for _uuid, _handle, _value_handle in zip(characteristics['uuid'], characteristics['handle'], characteristics['value_handle']):
            _value = gattData.characteristicValue(sset, _handle);
            if len(_value) > mtuSize-5:
                trace.trace(6, "Write Long Characteristic %s [#%d]" % (attData.uuid(_uuid), _handle));
                ok, reply = __writeLong(transport, initiator, _value_handle, [ 0x00 ], len(_value)+1, trace);
                success = success and ok;
                if not ok:
                    trace.trace(6, "Reply: %s" % attData.error(reply['error']));
                else:
                    ok, reply = __writeExecute(transport, initiator, trace);
                    success = success and not ok and reply['error'] == ATTError.ATT_ERROR_INVALID_OFFSET;
                    if not ok:
                        trace.trace(6, "Reply: %s" % attData.error(reply['error']));
   
        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BI-11-C [Insufficient Authorization error - Writing Long Characteristic Value]
"""
def gatt_sr_gaw_bi_11_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 43, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that require WRITE Authorization
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_WRITE_AUTHOR);
        for _uuid, _handle, _value_handle in zip(characteristics['uuid'], characteristics['handle'], characteristics['value_handle']):
            _value = gattData.characteristicValue(sset, _handle);
            trace.trace(6, "Write Characteristic %s [#%d]" % (attData.uuid(_uuid), _value_handle));
            ok, reply = writeLong(transport, initiator, _value_handle, _value[::-1], mtuSize, trace);
            success = success and not ok and reply['error'] == ATTError.ATT_ERROR_INSUFFICIENT_AUTHORIZATION;
            if not ok:
                trace.trace(6, "Write failed: %s" % attData.error(reply['error']));
            else:
                ok, reply = writeLong(transport, initiator, _value_handle, _value, mtuSize, trace);

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BI-12-C [Insufficient Authentication error - Writing Long Characteristic Value]
"""
def gatt_sr_gaw_bi_12_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 43, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that require WRITE Authentication
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_WRITE_AUTHEN);
        for _uuid, _handle, _value_handle in zip(characteristics['uuid'], characteristics['handle'], characteristics['value_handle']):
            _value = gattData.characteristicValue(sset, _handle);
            trace.trace(6, "Write Characteristic %s [#%d]" % (attData.uuid(_uuid), _value_handle));
            ok, reply = writeLong(transport, initiator, _value_handle, _value[::-1], mtuSize, trace);
            success = success and not ok and reply['error'] == ATTError.ATT_ERROR_INSUFFICIENT_AUTHENTICATION;
            if not ok:
                trace.trace(6, "Write failed: %s" % attData.error(reply['error']));
            else:
                ok, reply = writeLong(transport, initiator, _value_handle, _value, mtuSize, trace);

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BI-13-C [Insufficient Encryption Key Size error - Writing Long Characteristic Value]
"""
def gatt_sr_gaw_bi_13_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 43, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that require WRITE Authentication
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_WRITE_ENCRYPT);
        for _uuid, _handle, _value_handle in zip(characteristics['uuid'], characteristics['handle'], characteristics['value_handle']):
            _value = gattData.characteristicValue(sset, _handle);
            trace.trace(6, "Write Characteristic %s [#%d]" % (attData.uuid(_uuid), _value_handle));
            ok, reply = writeLong(transport, initiator, _value_handle, _value[::-1], mtuSize, trace);
            success = success and not ok and reply['error'] == ATTError.ATT_ERROR_INSUFFICIENT_ENCRYPTION;
            if not ok:
                trace.trace(6, "Write failed: %s" % attData.error(reply['error']));
            else:
                ok, reply = writeLong(transport, initiator, _value_handle, _value, mtuSize, trace);

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BV-08-C [Server Writes Characteristic Descriptors]
"""
def gatt_sr_gaw_bv_08_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Descriptors that have WRITE access
        """
        descriptors = gattData.descriptors(sset, None, ATTPermission.ATT_PERM_WRITE);
        for _handle in descriptors['handle']:
            _value = gattData.descriptorValue(sset, _handle);
            if len(_value) < mtuSize-3:
                trace.trace(6, "Write Descriptor @[#%d]" % _handle);
                ok, reply = writeCharacteristic(transport, initiator, _handle, _value[::-1], trace);
                success = success and ok;                    
                if not ok:
                    trace.trace(6, "Write failed: %s" % attData.error(reply['error']));
                else:
                    ok, reply = writeCharacteristic(transport, initiator, _handle, _value, trace);
                    success = success and ok;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BV-09-C [Server Writes Long Characteristic Descriptors]
"""
def gatt_sr_gaw_bv_09_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Descriptors that have WRITE access
        """
        descriptors = gattData.descriptors(sset, None, ATTPermission.ATT_PERM_WRITE);
        for _handle in descriptors['handle']:
            _value = gattData.descriptorValue(sset, _handle);
            if len(_value) > mtuSize-5:
                trace.trace(6, "Write Descriptor @[#%d]" % _handle);
                ok, reply = writeLong(transport, initiator, _handle, _value[::-1], mtuSize, trace);
                success = success and ok;                    
                if not ok:
                    trace.trace(6, "Write failed: %s" % attData.error(reply['error']));
                else:
                    ok, reply = writeLong(transport, initiator, _handle, _value, mtuSize, trace);
                    success = success and ok;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BV-11-C [No Pending Prepared Write Requests error - Characteristic Value Reliable Writes]
"""
def gatt_sr_gaw_bv_11_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset = 1;
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Issue a WRITE EXECUTE command without any pending PREPARED WRITES
        """
        ok, reply = __writeExecute(transport, initiator, trace);
        success = success and ok;        

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BI-32-C [Invalid Attribute Value Length error - Writing Characteristic Value]
"""
def gatt_sr_gaw_bi_32_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 92, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that have WRITE access
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_WRITE);
        for _uuid, _handle, _value_handle, _permission in zip(characteristics['uuid'], characteristics['handle'], \
                                                              characteristics['value_handle'], characteristics['permission']):
            _value = gattData.characteristicValue(sset, _handle);
            if 4 < len(_value) and len(_value) < mtuSize-6:
                trace.trace(6, "Write Characteristic %s [#%d]" % (attData.uuid(_uuid), _value_handle));
                ok, reply = writeCharacteristic(transport, initiator, _value_handle, _value + [ 0x00, 0x00 ], trace);
                success = success and not ok and reply['error'] == ATTError.ATT_ERROR_INVALID_ATTRIBUTE_VALUE_LENGTH;
                if not ok:
                    trace.trace(6, "Write failed: %s" % attData.error(reply['error']));

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAW/BI-33-C [Invalid Attribute Value Length error - Writing Long Characteristic Value]
"""
def gatt_sr_gaw_bi_33_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        sset, attData, gattData = 2, ATTData(), GATTData.instance();
        """
            Switch to Service Set #2
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Characteristics that have WRITE access
        """
        characteristics = gattData.characteristics(sset, None, ATTPermission.ATT_PERM_WRITE);
        for _uuid, _handle, _value_handle, _permission in zip(characteristics['uuid'], characteristics['handle'], \
                                                              characteristics['value_handle'], characteristics['permission']):
            _value = gattData.characteristicValue(sset, _handle);
            if len(_value) > mtuSize-5:
                trace.trace(6, "Write Characteristic %s [#%d]" % (attData.uuid(_uuid), _value_handle));
                ok, reply = writeLong(transport, initiator, _value_handle, _value + [ 0x00, 0x00 ], mtuSize, trace);
                success = success and not ok and reply['error'] == ATTError.ATT_ERROR_INVALID_ATTRIBUTE_VALUE_LENGTH;
                if not ok:
                    trace.trace(6, "Write failed: %s" % attData.error(reply['error']));

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAN/BV-01-C [Server generates Characteristic Value Notification]
"""
def gatt_sr_gan_bv_01_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
            Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Descriptors that have WRITE access
        """
        descriptors = gattData.descriptors(sset, None, ATTPermission.ATT_PERM_WRITE);
        for _uuid, _handle in zip(descriptors['uuid'], descriptors['handle']):
            if _uuid == 0x2902 and _handle >= 16:
                trace.trace(7, "Descriptor %s @[#%d]" %(attData.uuid(_uuid), _handle));
                ok, reply = writeCharacteristic(transport, initiator, _handle, [ 0x01, 0x00 ], trace);
                success = success and ok;
                if success:
                    gatt_service_notify(transport, lowerTester, 100);
                    ok, reply = notification(transport, initiator, trace);
                    success = success and ok;
                    if ok:
                        trace.trace(7, "Notification @[#%d] %s" %(reply['handle'], formatArray(reply['value'])));
                    ok, reply = writeCharacteristic(transport, initiator, _handle, [ 0x00, 0x00 ], trace);
                    success = success and ok;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAI/BV-01-C [Server generates Characteristic Value Indication]
"""
def gatt_sr_gai_bv_01_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        sset, attData, gattData = 2, ATTData(), GATTData.instance();
        """
            Switch to Service Set #2
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
            Collect all Descriptors that have WRITE access
        """
        descriptors = gattData.descriptors(sset, None, ATTPermission.ATT_PERM_WRITE);
        for _uuid, _handle in zip(descriptors['uuid'], descriptors['handle']):
            if _uuid == 0x2902 and _handle >= 16:
                trace.trace(7, "Descriptor %s @[#%d]" %(attData.uuid(_uuid), _handle));
                ok, reply = writeCharacteristic(transport, initiator, _handle, [ 0x02, 0x00 ], trace);
                success = success and ok;
                if success:
                    gatt_service_indicate(transport, lowerTester, 100);
                    ok, reply = indication(transport, initiator, trace);
                    success = success and ok;
                    if ok:
                        trace.trace(7, "Indication @[#%d] %s" %(reply['handle'], formatArray(reply['value'])));
                    ok, reply = writeCharacteristic(transport, initiator, _handle, [ 0x00, 0x00 ], trace);
                    success = success and ok;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GAS/BV-01-C [Server accepts Service Changed Characteristic Indication]
"""
def gatt_sr_gas_bv_01_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        sset, attData, gattData = 1, ATTData(), GATTData.instance();
        """
        Switch to Service Set #1
        """
        trace.trace(6, "Switching to Service Set #%d" % sset);
        switch_gatt_service_set(transport, lowerTester, sset, 200);
        """
        Collect all Descriptors that have WRITE access
        """
        descriptors = gattData.descriptors(sset, None, ATTPermission.ATT_PERM_WRITE);
        for _uuid, _handle in zip(descriptors['uuid'], descriptors['handle']):
            if _uuid == 0x2902 and _handle < 16:
	            trace.trace(7, "Descriptor %s @[#%d]" %(attData.uuid(_uuid), _handle));
	            ok, reply = writeCharacteristic(transport, initiator, _handle, [ 0x02, 0x00 ], trace);
	            success = success and ok;
	            if success:
	                sset = 2;
	                """
	                    Switch to Service Set #2
	                """
	                trace.trace(6, "Switching to Service Set #%d" % sset);
	                switch_gatt_service_set(transport, lowerTester, sset, 200);
	                ok, reply = indication(transport, initiator, trace);
	                success = success and ok;
	                if ok:
	                    trace.trace(7, "Indication @[#%d] %s" %(reply['handle'], formatArray(reply['value'])));
	                ok, reply = writeCharacteristic(transport, initiator, _handle, [ 0x00, 0x00 ], trace);
	                success = success and ok;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/UNS/BI-01-C [Server sends Unsupported ATT Requests]
"""
def gatt_sr_uns_bi_01_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        attData = ATTData();
        """
        Generate an Invalid ATT Request
        """
        txData = attData.encode( ATTOpcode.ATT_INVALID_REQUEST, [ random.randint(0,255) for _ in range(mtuSize-4) ] );
        trace.trace(7, str(attData));
        success = attRequest( transport, initiator, txData, trace );
        if success:
            success, rxData = attResponse( transport, initiator, trace );
            if success:
                reply = attData.decode( rxData );
                trace.trace(7, str(attData));
                success = reply['opcode'] == ATTOpcode.ATT_ERROR_RESPONSE;
                if success:
                    success = reply['error'] == ATTError.ATT_ERROR_REQUEST_NOT_SUPPORTED;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/UNS/BI-02-C [Server sends Unsupported ATT Commands]
"""
def gatt_sr_uns_bi_02_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        attData = ATTData();
        """
        Generate an Invalid ATT Command
        """
        txData = attData.encode( ATTOpcode.ATT_INVALID_COMMAND, [ random.randint(0,255) for _ in range(mtuSize-4) ] );
        trace.trace(7, str(attData));
        success = attRequest( transport, initiator, txData, trace );
        if success:
            success, rxData = attResponse( transport, initiator, trace );
            if success:
                reply = attData.decode( rxData );
                trace.trace(7, str(attData));
            success = not success;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GPA/BV-01-C [Server Reads Primary Service Declaration]
"""
def gatt_sr_gpa_bv_01_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        attData, gattData = ATTData(), GATTData.instance();

        for sset in range(4):
            """
                Switching Service Set
            """
            trace.trace(6, "Switching to Service Set #%d" % sset);
            switch_gatt_service_set(transport, lowerTester, sset, 200);
            """
                Discover all Primary Services
            """
            ok, services = discoverPrimaryServices(transport, initiator, trace);
            if ok:
                for _uuid, _handles in zip(services["uuids"], services["handles"]):
                    trace.trace(6, "Service %s covers handles [0x%02X, 0x%02X]" % (attData.uuid(_uuid), _handles[0], _handles[1]));
                ok = services == gattData.primaryServices(sset)
                trace.trace(6, "Verified Service Set: %s" % ok);
            else:
                trace.trace(6, "Unable to discover Primary Services!");
            success = success and ok;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GPA/BV-02-C [Server Reads Secondary Service Declaration]
"""
def gatt_sr_gpa_bv_02_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        attData, gattData = ATTData(), GATTData.instance();

        for sset in range(4):
            """
                Switching Service Set
            """
            trace.trace(6, "Switching to Service Set #%d" % sset);
            switch_gatt_service_set(transport, lowerTester, sset, 200);
            """
                Discover all Secondary Services
            """
            ok, services = secondaryServicesByType(transport, initiator, trace);
            if ok:
                for _uuid, _handle in zip(services["uuid"], services["handle"]):
                    trace.trace(6, "Service %s at handle 0x%02X" % (attData.uuid(_uuid), _handle));
                ok = services == gattData.secondaryServices(sset)
                trace.trace(6, "Verified Service Set: %s" % ok);
            elif sset == 0:
                ok = services == gattData.secondaryServices(sset)
                trace.trace(6, "Verified Service Set: %s" % ok);
            else:
                trace.trace(6, "Unable to discover Secondary Services!");
            success = success and ok;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GPA/BV-03-C [Server Reads Include Declaration]
"""
def gatt_sr_gpa_bv_03_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        attData, gattData = ATTData(), GATTData.instance();

        for sset in range(4):
            """
                Switching Service Set
            """
            trace.trace(6, "Switching to Service Set #%d" % sset);
            switch_gatt_service_set(transport, lowerTester, sset, 200);
            """
                Discover all Included Services
            """
            ok, services = includedServicesByType(transport, initiator, trace);
            if ok:
                for _uuid, _handles in zip(services["uuids"], services["handles"]):
                    trace.trace(6, "Service %s covers handles [0x%02X, 0x%02X]" % (attData.uuid(_uuid), _handles[0], _handles[1]));
                ok = services == gattData.includedServices(sset)
                trace.trace(6, "Verified Service Set: %s" % ok);
            elif sset == 0:
                ok = services == gattData.includedServices(sset)
                trace.trace(6, "Verified Service Set: %s" % ok);
            else:
                trace.trace(6, "Unable to discover Included Services!");
            success = success and ok;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GPA/BV-04-C [Server Reads Characteristic Declaration]
"""
def gatt_sr_gpa_bv_04_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        attData, gattData = ATTData(), GATTData.instance();

        for sset in range(4):
            """
                Switching Service Set

            """
            trace.trace(6, "Switching to Service Set #%d" % sset);
            switch_gatt_service_set(transport, lowerTester, sset, 200);
            """
                Discover all Characteristic Declarations
            """
            ok, characteristics = characteristicsByType(transport, initiator, [0x0001, 0xffff], trace);
            if ok:
                for _uuid, _handle, _value_handle, _property in zip(characteristics['uuid'], characteristics['handle'], \
                                                                    characteristics['value_handle'], characteristics['property']):
                    trace.trace(6, "Characteristic %s handle 0x%02X value handle 0x%02X properties %s" % \
                                   (attData.uuid(_uuid), _handle, _value_handle, attData.property(_property)));
            
                _characteristics = gattData.characteristics(sset);
                _characteristics.pop("permission");

                ok = characteristics == _characteristics
                trace.trace(6, "Verified Characteristics: %s" % ok);
            else:
                trace.trace(6, "Unable to discover Characteristic Declarations!");
            success = success and ok;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GPA/BV-05-C [Server Reads Characteristic Extended Properties Declaration]
"""
def gatt_sr_gpa_bv_05_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        attData, gattData = ATTData(), GATTData.instance();

        for sset in range(4):
            """
                Switching Service Set

            """
            trace.trace(6, "Switching to Service Set #%d" % sset);
            switch_gatt_service_set(transport, lowerTester, sset, 200);

            _descriptors = filterCharacteristics(gattData.descriptors(sset), 0x2900);

            """
                Discover all Characteristic Declarations for Extended Properties
            """
            ok, descriptors = specificDescriptors(transport, initiator, [0x0001, 0xffff], 0x2900, trace);
            if ok:
                for _uuid, _handle in zip(descriptors['uuid'], descriptors['handle']):
                    _success, value = readCharacteristic(transport, initiator, _handle, trace);
                    _value = gattData.descriptorValue(sset, _handle);
                    if _success:
                        _success = value == _value;
                        trace.trace(6, "Descriptor %s handle 0x%02X value %s - %s" % (attData.uuid(_uuid), _handle, formatArray(value), _success));
                    else:
                        trace.trace(6, "Descriptor %s handle 0x%02X value %s" % (attData.uuid(_uuid), _handle, attData.error(value)));
                    success = success and _success;

                ok = descriptors == _descriptors
                trace.trace(6, "Verified Descriptors: %s" % ok);
            elif sset == 0:
                ok = descriptors == _descriptors
                trace.trace(6, "Verified Descriptors: %s" % ok);
            else:
                trace.trace(6, "Unable to discover Extended Properties Descriptors!");
            success = success and ok;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GPA/BV-06-C [Server Reads Characteristic User Description Descriptor]
"""
def gatt_sr_gpa_bv_06_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        attData, gattData = ATTData(), GATTData.instance();

        for sset in range(4):
            """
                Switching Service Set

            """
            trace.trace(6, "Switching to Service Set #%d" % sset);
            switch_gatt_service_set(transport, lowerTester, sset, 200);

            _descriptors = filterCharacteristics(gattData.descriptors(sset), 0x2901);

            """
                Discover all Characteristic Declarations for Extended Properties
            """
            ok, descriptors = specificDescriptors(transport, initiator, [0x0001, 0xffff], 0x2901, trace);
            if ok:
                for _uuid, _handle in zip(descriptors['uuid'], descriptors['handle']):
                    _success, value = readStringCharacteristic(transport, initiator, _handle, trace);
                    _value = gattData.descriptorString(sset, _handle);
                    if _success:
                        _success = value == _value;
                        trace.trace(6, "Descriptor %s handle 0x%02X value %s - %s" % (attData.uuid(_uuid), _handle, value, _success));
                    else:
                        trace.trace(6, "Descriptor %s handle 0x%02X value %s" % (attData.uuid(_uuid), _handle, attData.error(value)));
                    success = success and _success;

                ok = descriptors == _descriptors
                trace.trace(6, "Verified Descriptors: %s" % ok);
            elif sset == 0:
                ok = descriptors == _descriptors
                trace.trace(6, "Verified Descriptors: %s" % ok);
            else:
                trace.trace(6, "Unable to discover User Description Descriptors!");
            success = success and ok;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GPA/BV-07-C [Server Reads Client Characteristic Configuration Descriptor]
"""
def gatt_sr_gpa_bv_07_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        attData, gattData = ATTData(), GATTData.instance();

        for sset in range(4):
            """
                Switching Service Set

            """
            trace.trace(6, "Switching to Service Set #%d" % sset);
            switch_gatt_service_set(transport, lowerTester, sset, 200);

            _descriptors = filterCharacteristics(gattData.descriptors(sset), 0x2902);

            """
                Discover all Client Characteristic Configuration Descriptors
            """
            ok, descriptors = specificDescriptors(transport, initiator, [0x0001, 0xffff], 0x2902, trace);
            if ok:
                for _uuid, _handle in zip(descriptors['uuid'], descriptors['handle']):
                    _success, value = readCharacteristic(transport, initiator, _handle, trace);
                    _value = gattData.descriptorValue(sset, _handle);
                    if _success:
                        _success = value == _value;
                        trace.trace(6, "Descriptor %s handle 0x%02X value %s - %s" % (attData.uuid(_uuid), _handle, formatArray(value), _success));
                    else:
                        trace.trace(6, "Descriptor %s handle 0x%02X value %s" % (attData.uuid(_uuid), _handle, attData.error(value)));
                    success = success and _success;

                ok = descriptors == _descriptors
                trace.trace(6, "Verified Descriptors: %s" % ok);
            elif sset == 0:
                ok = descriptors == _descriptors
                trace.trace(6, "Verified Descriptors: %s" % ok);
            else:
                trace.trace(6, "Unable to discover Client Characteristic Configuration Descriptors!");
            success = success and ok;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GPA/BV-08-C [Server Reads Server Characteristic Configuration Descriptor]
"""
def gatt_sr_gpa_bv_08_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        attData, gattData = ATTData(), GATTData.instance();

        for sset in range(4):
            """
                Switching Service Set

            """
            trace.trace(6, "Switching to Service Set #%d" % sset);
            switch_gatt_service_set(transport, lowerTester, sset, 200);

            _descriptors = filterCharacteristics(gattData.descriptors(sset), 0x2903);

            """
                Discover all Server Characteristic Configuration Descriptors
            """
            ok, descriptors = specificDescriptors(transport, initiator, [0x0001, 0xffff], 0x2903, trace);
            if ok:
                for _uuid, _handle in zip(descriptors['uuid'], descriptors['handle']):
                    _success, value = readCharacteristic(transport, initiator, _handle, trace);
                    _value = gattData.descriptorValue(sset, _handle);
                    if _success:
                        _success = value == _value;
                        trace.trace(6, "Descriptor %s handle 0x%02X value %s - %s" % (attData.uuid(_uuid), _handle, formatArray(value), _success));
                    else:
                        trace.trace(6, "Descriptor %s handle 0x%02X value %s" % (attData.uuid(_uuid), _handle, attData.error(value)));
                    success = success and _success;

                ok = descriptors == _descriptors
                trace.trace(6, "Verified Descriptors: %s" % ok);
            elif sset == 0:
                ok = descriptors == _descriptors
                trace.trace(6, "Verified Descriptors: %s" % ok);
            else:
                trace.trace(6, "Unable to discover Server Characteristic Configuration Descriptors!");
            success = success and ok;

        success = initiator.disconnect(0x13) and success;

    return success;

"""
    GATT/SR/GPA/BV-12-C [Server handles Characteristic Presentation Format Descriptors]
"""
def gatt_sr_gpa_bv_12_c(transport, upperTester, lowerTester, trace):
    success, mtuSize, initiator = preambleConnected(transport, upperTester, 46, trace);
    if success:
        attData, gattData = ATTData(), GATTData.instance();

        for sset in range(4):
            """
                Switching Service Set

            """
            trace.trace(6, "Switching to Service Set #%d" % sset);
            switch_gatt_service_set(transport, lowerTester, sset, 200);

            _descriptors = filterCharacteristics(gattData.descriptors(sset), 0x2904);

            """
                Discover all Characteristic Presentation Format Descriptors
            """
            ok, descriptors = specificDescriptors(transport, initiator, [0x0001, 0xffff], 0x2904, trace);
            if ok:
                for _uuid, _handle in zip(descriptors['uuid'], descriptors['handle']):
                    _success, value = readCharacteristic(transport, initiator, _handle, trace);
                    _value = gattData.descriptorValue(sset, _handle);
                    if _success:
                        _success = value == _value;
                        trace.trace(6, "Descriptor %s handle 0x%02X value %s - %s" % (attData.uuid(_uuid), _handle, formatArray(value), _success));
                    else:
                        trace.trace(6, "Descriptor %s handle 0x%02X value %s" % (attData.uuid(_uuid), _handle, attData.error(value)));
                    success = success and _success;

                    characteristic = gattData.characteristicWithDescriptor(sset, _handle);
                    _success, value = readCharacteristic(transport, initiator, characteristic['value_handle'], trace);
                    trace.trace(6, "Characteristic %s handle 0x%02X value %s" % \
                                   (attData.uuid(characteristic['uuid']), characteristic['handle'], formatArray(value)));

                ok = descriptors == _descriptors
                trace.trace(6, "Verified Descriptors: %s" % ok);
            elif sset == 0:
                ok = descriptors == _descriptors
                trace.trace(6, "Verified Descriptors: %s" % ok);
            else:
                trace.trace(6, "Unable to discover Characteristic Presentation Format Descriptors!");
            success = success and ok;

        success = initiator.disconnect(0x13) and success;

    return success;

__tests__ = {
    "GAP/GAT/BV-01-C":       [ gap_gat_bv_01_c,       'Mandatory Characteristics' ],
#   "GAP/GAT/BV-02-C":       [ gap_gat_bv_02_c,       'Peripheral Privacy Flag Characteristic' ],
#   "GAP/GAT/BV-03-C":       [ gap_gat_bv_03_c,       'Reconnection Address Characteristic' ],
    "GAP/GAT/BV-04-C":       [ gap_gat_bv_04_c,       'Peripheral Preferred Connection Parameters Characteristic' ],
#   "GAP/GAT/BV-05-C":       [ gap_gat_bv_05_c,       'Changing Device Name' ],
    "GAP/IDLE/NAMP/BV-01-C": [ gap_idle_namp_bv_01_c, 'Name Discovery Procedure GATT Client' ],
#   "GAP/GAT/BX-01-C":       [ gap_gat_bx_01_c,       'Discover All Services' ],

    "GATT/SR/GAC/BV-01-C":   [ gatt_sr_gac_bv_01_c,   'Server accepts Server Configuration' ],
    "GATT/SR/GAD/BV-01-C":   [ gatt_sr_gad_bv_01_c,   'Server Discovers All Primary Services' ],
    "GATT/SR/GAD/BV-02-C":   [ gatt_sr_gad_bv_02_c,   'Server Discovers Primary Services by Service UUID' ],
    "GATT/SR/GAD/BV-03-C":   [ gatt_sr_gad_bv_03_c,   'Server Finds Included Services' ],
    "GATT/SR/GAD/BV-04-C":   [ gatt_sr_gad_bv_04_c,   'Server Discovers All Characteristics of a Service' ],
    "GATT/SR/GAD/BV-05-C":   [ gatt_sr_gad_bv_05_c,   'Server Discovers Characteristics by UUID' ],
    "GATT/SR/GAD/BV-06-C":   [ gatt_sr_gad_bv_06_c,   'Server Discovers All Characteristic Descriptors' ],
    "GATT/SR/GAR/BV-01-C":   [ gatt_sr_gar_bv_01_c,   'Server Reads Characteristic Value' ],
    "GATT/SR/GAR/BI-01-C":   [ gatt_sr_gar_bi_01_c,   'Read Not Permitted error - Reading Characteristic Value' ],
    "GATT/SR/GAR/BI-02-C":   [ gatt_sr_gar_bi_02_c,   'Invalid Handle error - Reading Characteristic Value' ],
    "GATT/SR/GAR/BI-03-C":   [ gatt_sr_gar_bi_03_c,   'Insufficient Authorization error - Reading Characteristic Value' ],
    "GATT/SR/GAR/BI-04-C":   [ gatt_sr_gar_bi_04_c,   'Insufficient Authentication error - Reading Characteristic Value' ],
    "GATT/SR/GAR/BV-03-C":   [ gatt_sr_gar_bv_03_c,   'Server Reads using Characteristic UUID' ],
    "GATT/SR/GAR/BI-06-C":   [ gatt_sr_gar_bi_06_c,   'Read Not Permitted error - Reading Characteristic by UUID' ],
    "GATT/SR/GAR/BI-07-C":   [ gatt_sr_gar_bi_07_c,   'Attribute Not Found error - Reading Characteristic by UUID' ],
    "GATT/SR/GAR/BI-09-C":   [ gatt_sr_gar_bi_09_c,   'Insufficient Authorization error - Reading Using Characteristic UUID' ],
    "GATT/SR/GAR/BI-10-C":   [ gatt_sr_gar_bi_10_c,   'Insufficient Authentication error - Reading Using Characteristic UUID' ],
    "GATT/SR/GAR/BI-11-C":   [ gatt_sr_gar_bi_11_c,   'Insufficient Encryption Key Size error - Reading Using Characteristic UUID' ],
    "GATT/SR/GAR/BV-04-C":   [ gatt_sr_gar_bv_04_c,   'Server Reads Long Characteristic Value' ],
    "GATT/SR/GAR/BI-12-C":   [ gatt_sr_gar_bi_12_c,   'Read Not Permitted error - Reading Long Characteristic Value' ],
    "GATT/SR/GAR/BI-13-C":   [ gatt_sr_gar_bi_13_c,   'Invalid Offset error - Reading Long Characteristic Value' ],
    "GATT/SR/GAR/BI-14-C":   [ gatt_sr_gar_bi_14_c,   'Invalid Handle error - Reading Long Characteristic Value' ],
    "GATT/SR/GAR/BI-15-C":   [ gatt_sr_gar_bi_15_c,   'Insufficient Authorization error - Reading Long Characteristic Value' ],
    "GATT/SR/GAR/BI-16-C":   [ gatt_sr_gar_bi_16_c,   'Insufficient Authentication error - Reading Long Characteristic Value' ],
    "GATT/SR/GAR/BI-17-C":   [ gatt_sr_gar_bi_17_c,   'Insufficient Encryption Key Size error - Reading Long Characteristic Value' ],
    "GATT/SR/GAR/BV-05-C":   [ gatt_sr_gar_bv_05_c,   'Server Reads Multiple Characteristic Values' ],
    "GATT/SR/GAR/BI-18-C":   [ gatt_sr_gar_bi_18_c,   'Read Not Permitted error - Reading Multiple Characteristic Values' ],
    "GATT/SR/GAR/BI-19-C":   [ gatt_sr_gar_bi_19_c,   'Invalid Handle error - Reading Multiple Characteristic Values' ],
    "GATT/SR/GAR/BI-20-C":   [ gatt_sr_gar_bi_20_c,   'Insufficient Authorization error - Reading Multiple Characteristic Values' ],
    "GATT/SR/GAR/BI-21-C":   [ gatt_sr_gar_bi_21_c,   'Insufficient Authentication error - Reading Multiple Characteristic Values' ],
    "GATT/SR/GAR/BI-22-C":   [ gatt_sr_gar_bi_22_c,   'Insufficient Encryption Key Size error - Reading Multiple Characteristic Values' ],
    "GATT/SR/GAR/BV-06-C":   [ gatt_sr_gar_bv_06_c,   'Server Reads Characteristic Descriptors' ],
    "GATT/SR/GAR/BV-07-C":   [ gatt_sr_gar_bv_07_c,   'Server Reads Long Characteristic Descriptor' ],
    "GATT/SR/GAW/BV-01-C":   [ gatt_sr_gaw_bv_01_c,   'Server Writes Without Response' ],
    "GATT/SR/GAW/BV-03-C":   [ gatt_sr_gaw_bv_03_c,   'Server Writes Characteristic Value' ],
    "GATT/SR/GAW/BI-02-C":   [ gatt_sr_gaw_bi_02_c,   'Invalid Handle error - Writing Characteristic Value' ],
    "GATT/SR/GAW/BI-03-C":   [ gatt_sr_gaw_bi_03_c,   'Write Not Permitted error - Writing Characteristic Value' ],
    "GATT/SR/GAW/BI-04-C":   [ gatt_sr_gaw_bi_04_c,   'Insufficient Authorization error - Writing Characteristic Value' ],
    "GATT/SR/GAW/BI-05-C":   [ gatt_sr_gaw_bi_05_c,   'Insufficient Authentication error - Writing Characteristic Value' ],
    "GATT/SR/GAW/BI-06-C":   [ gatt_sr_gaw_bi_06_c,   'Insufficient Encryption Key Size error - Writing Characteristic Value' ],
    "GATT/SR/GAW/BV-05-C":   [ gatt_sr_gaw_bv_05_c,   'Server Writes Long Characteristic Value' ],
    "GATT/SR/GAW/BI-07-C":   [ gatt_sr_gaw_bi_07_c,   'Invalid Handle error - Writing Long Characteristic Value' ],
    "GATT/SR/GAW/BI-08-C":   [ gatt_sr_gaw_bi_08_c,   'Write Not Permitted error - Writing Long Characteristic Value' ],
    "GATT/SR/GAW/BI-09-C":   [ gatt_sr_gaw_bi_09_c,   'Invalid Offset error - Writing Long Characteristic Value' ],
    "GATT/SR/GAW/BI-11-C":   [ gatt_sr_gaw_bi_11_c,   'Insufficient Authorization error - Writing Long Characteristic Value' ],
    "GATT/SR/GAW/BI-12-C":   [ gatt_sr_gaw_bi_12_c,   'Insufficient Authentication error - Writing Long Characteristic Value' ],
    "GATT/SR/GAW/BI-13-C":   [ gatt_sr_gaw_bi_13_c,   'Insufficient Encryption Key Size error - Writing Long Characteristic Value' ],
    "GATT/SR/GAW/BV-08-C":   [ gatt_sr_gaw_bv_08_c,   'Server Writes Characteristic Descriptors' ],
    "GATT/SR/GAW/BV-09-C":   [ gatt_sr_gaw_bv_09_c,   'Server Writes Long Characteristic Descriptors' ],
    "GATT/SR/GAW/BV-11-C":   [ gatt_sr_gaw_bv_11_c,   'No Pending Prepared Write Requests error - Characteristic Value Reliable Writes' ],
    "GATT/SR/GAW/BI-32-C":   [ gatt_sr_gaw_bi_32_c,   'Invalid Attribute Value Length error - Writing Characteristic Value' ],
    "GATT/SR/GAW/BI-33-C":   [ gatt_sr_gaw_bi_33_c,   'Invalid Attribute Value Length error - Writing Long Characteristic Value' ],
    "GATT/SR/GAN/BV-01-C":   [ gatt_sr_gan_bv_01_c,   'Server generates Characteristic Value Notification' ],
    "GATT/SR/GAI/BV-01-C":   [ gatt_sr_gai_bv_01_c,   'Server generates Characteristic Value Indication' ],
    "GATT/SR/GAS/BV-01-C":   [ gatt_sr_gas_bv_01_c,   'Server accepts Service Changed Characteristic Indication' ],
    "GATT/SR/UNS/BI-01-C":   [ gatt_sr_uns_bi_01_c,   'Server sends Unsupported ATT Requests' ],
    "GATT/SR/UNS/BI-02-C":   [ gatt_sr_uns_bi_02_c,   'Server sends Unsupported ATT Commands' ],
    "GATT/SR/GPA/BV-01-C":   [ gatt_sr_gpa_bv_01_c,   'Server Reads Primary Service Declaration' ],
    "GATT/SR/GPA/BV-02-C":   [ gatt_sr_gpa_bv_02_c,   'Server Reads Secondary Service Declaration' ],
    "GATT/SR/GPA/BV-03-C":   [ gatt_sr_gpa_bv_03_c,   'Server Reads Include Declaration' ],
    "GATT/SR/GPA/BV-04-C":   [ gatt_sr_gpa_bv_04_c,   'Server Reads Characteristic Declaration' ],
    "GATT/SR/GPA/BV-05-C":   [ gatt_sr_gpa_bv_05_c,   'Server Reads Characteristic Extended Properties Declaration' ],
    "GATT/SR/GPA/BV-06-C":   [ gatt_sr_gpa_bv_06_c,   'Server Reads Characteristic User Description Descriptor' ],
    "GATT/SR/GPA/BV-07-C":   [ gatt_sr_gpa_bv_07_c,   'Server Reads Client Characteristic Configuration Descriptor' ],
    "GATT/SR/GPA/BV-08-C":   [ gatt_sr_gpa_bv_08_c,   'Server Reads Server Characteristic Configuration Descriptor' ],
    "GATT/SR/GPA/BV-12-C":   [ gatt_sr_gpa_bv_12_c,   'Server handles Characteristic Presentation Format Descriptors' ]
};

_maxNameLength = max([ len(key) for key in __tests__ ]);

_spec = { key: TestSpec(name = key, number_devices = 1, description = "#[" + __tests__[key][1] + "]", test_private = __tests__[key][0]) for key in __tests__ };

"""
    Return the test spec which contains info about all the tests
    this test module provides
"""
def get_tests_specs():
    return _spec;

def preamble(transport, trace):
    global lowerIRK, upperIRK, lowerRandomAddress, upperRandomAddress;

    ok = success = preamble_standby(transport, 0, trace);
    trace.trace(4, "preamble Standby " + ("PASS" if success else "FAIL"));
    success, upperIRK, upperRandomAddress = preamble_device_address_set(transport, 0, trace);
    trace.trace(4, "preamble Device Address Set " + ("PASS" if success else "FAIL"));
    ok = ok and success;        
    return ok;      

"""
    Run a test given its test_spec
"""
def run_a_test(args, transport, trace, test_spec, device_dumps):
    try:
        success = preamble(transport, trace);
    except Exception as e:
        trace.trace(3, "Preamble generated exception: %s" % str(e));
        success = False;

    trace.trace(2, "%-*s %s test started..." % (_maxNameLength, test_spec.name, test_spec.description[1:]));
    test_f = test_spec.test_private;
    try:
        if test_f.__code__.co_argcount > 4:
            success = success and test_f(transport, 0, 1, trace, device_dumps);
        elif test_f.__code__.co_argcount > 3:
            success = success and test_f(transport, 0, 1, trace);
        else:
            success = success and test_f(transport, 0, trace);
    except Exception as e:
        import traceback
        traceback.print_exc()
        trace.trace(3, "Test generated exception: %s" % str(e));
        success = False;

    return not success
