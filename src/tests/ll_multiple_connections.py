# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

import statistics;
from enum import IntEnum;
from components.utils import *;
from components.basic_commands import *;
from .ll_verification import *;
from components.test_spec import TestSpec;

"""
    ll_multiple_connections
"""
def ll_multiple_connections(transport, trace):
    trace.trace(3, "ll_multiple_connections");

    try:
        """
            Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
        """
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        rawPeerAddress = 0x456789ABCDEF    
        peerAddress = Address( SimpleAddressType.PUBLIC, rawPeerAddress );
        advertiser = Advertiser(transport, 0, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

        ownAddress = Address( ExtendedAddressType.PUBLIC );
        scanner1 = Scanner(transport, 1, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1);
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        scanner2 = Scanner(transport, 2, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1);
    
        trace.trace(1, '-'*80);
    
        success = advertiser.enable();
        
        trace.trace(1, "\nUsing initiator address: %s\n" % formatAddress( toArray(rawPeerAddress, 6), SimpleAddressType.PUBLIC));
        success = success and preamble_set_public_address( transport, 1, rawPeerAddress, trace );
        success = success and preamble_set_public_address( transport, 2, rawPeerAddress, trace );
    
        success = success and scanner1.enable();
        scanner1.monitor();
        success = success and scanner1.disable();
        success = success and scanner1.qualifyReports( 1 );
    
        initiatorAddress = Address( ExtendedAddressType.PUBLIC );
        initiator1 = Initiator(transport, 1, 0, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABC ));
        connected = initiator1.connect();
        success = success and connected;

        initiatorAddress = Address( ExtendedAddressType.PUBLIC );    
        initiator2 = Initiator(transport, 2, 0, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABC ));
        
        if connected:      
            print("\nStarting peripheral advertising...");
            success = advertiser.enable();

            print("\nStarting central 2 scanning...");
            success = success and scanner2.enable();
            scanner2.monitor();
            success = success and scanner2.disable();
            success = success and scanner2.qualifyReports( 1 );

            print("\nStarting central 2 connection...");
            connected = initiator2.connect();
            success = success and connected;
        
            print("\nDisconnecting...");
            disconnected = initiator1.disconnect(0x3E);
            success = success and disconnected;
            disconnected = initiator2.disconnect(0x3E);
            success = success and disconnected;

    except Exception as e:
        trace.trace(1, "Connection Request test failed: %s" % str(e));
        success = False;

    trace.trace(3, "Connection Request test " + ("PASSED" if success else "FAILED"));
    return success


_spec = {};
_spec["Echo_test"] = \
    TestSpec(name = "Multiple Connections Test Suite",
             number_devices = 3,
             description = "Verify ability to have multiple BLE connections.");

"""
    Return the test spec which contains info about all the tests
    this test module provides
"""
def get_tests_specs():
    return _spec;

"""
    Run the command...
"""
def main(transport, trace):
    success = True
    print(("preamble Standby Peripheral "    + ("PASS" if preamble_standby(transport, 0, trace) else "FAIL")));
    print(("preamble Standby Central 1 " + ("PASS" if preamble_standby(transport, 1, trace) else "FAIL")));
    print(("preamble Standby Central 2 " + ("PASS" if preamble_standby(transport, 2, trace) else "FAIL")));
    print(("preamble Device Address Set Peripheral "    + ("PASS" if preamble_device_address_set(transport, 0, trace) else "FAIL")));
    print(("preamble Device Address Set Central 1 " + ("PASS" if preamble_device_address_set(transport, 1, trace) else "FAIL")));
    print(("preamble Device Address Set Central 2 " + ("PASS" if preamble_device_address_set(transport, 2, trace) else "FAIL")));
    print();
    success = ll_multiple_connections(transport, trace);
    return (0 if success else 1)

"""
    Run a test given its test_spec
"""
def run_a_test(args, transport, trace, test_spec):
    return main(transport, trace);
