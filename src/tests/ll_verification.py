# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

from numpy import random;
import copy
import statistics;
import os;
import numpy;
import csv;
import tests.test_utils;
from collections import defaultdict, namedtuple
from enum import IntEnum;
from components.utils import *;
from components.basic_commands import *;
from components.address import *;
from components.events import *;
from components.resolvable import *;
from components.advertiser import *;
from components.scanner import *;
from components.initiator import *;
from components.addata import *;
from components.preambles import *;
from components.test_spec import TestSpec;
from tests.test_utils import *

global lowerIRK, upperIRK, ENC_KEYS

class FragmentOperation(IntEnum):
    INTERMEDIATE_FRAGMENT = 0      # Intermediate fragment of fragmented extended advertising data
    FIRST_FRAGMENT        = 1      # First fragment of fragmented extended advertising data
    LAST_FRAGMENT         = 2      # Last fragment of fragmented extended advertising data
    COMPLETE_FRAGMENT     = 3      # Complete extended advertising data
    UNCHANGED_FRAGMENT    = 4      # Unchanged data (just update the Advertising DID)

class FragmentPreference(IntEnum):
    FRAGMENT_ALL_DATA = 0          # The Controller may fragment all Host advertising data
    FRAGMENT_MIN_DATA = 1          # The Controller should not fragment or should minimize fragmentation of Host advertising data

class PhysicalChannel(IntEnum):
    LE_1M    = 1
    LE_2M    = 2
    LE_CODED = 3

class PreferredPhysicalChannel(IntEnum):
    LE_1M    = 0                   # 0 ~ The Host prefers to use the LE 1M transmitter PHY (possibly among others)
    LE_2M    = 1                   # 1 ~ The Host prefers to use the LE 2M transmitter PHY (possibly among others)
    LE_CODED = 2                   # 2 ~ The Host prefers to use the LE Coded transmitter PHY (possibly among others)

"""
    LL/DDI/ADV/BV-01-C [Non-Connectable Advertising Packets on one channel]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_01_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 100, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);

    success = advertiser.enable();
    if success:
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = success and scanner.qualifyReports( 100, None, advertiser.advertiseData );

        success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-02-C [Undirected Advertising Packets on one channel]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_02_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 100, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);

    success = advertiser.enable();
    if success:
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = success and scanner.qualifyReports( 100, None, advertiser.advertiseData );

        success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-03-C [Non-Connectable Advertising Packets on all channels]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_03_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 50, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    success = True;
    adData = ADData();
    adData.encode( ADType.COMPLETE_LOCAL_NAME, 'THIS IS JUST A RANDOM NAME...' );

    for dataLength in [ 1, 0, 31, 0 ]:
        trace.trace(7, '-'*80);

        advertiser.advertiseData = [ ] if dataLength == 0 else [ 0x01 ] if dataLength == 1 else adData.asBytes();

        advertising = advertiser.enable();
        success = success and advertising;
        if advertising:
            success = scanner.enable() and success;
            scanner.monitor();
            success = scanner.disable() and success;
            success = scanner.qualifyReports( 50, None, list(advertiser.advertiseData) ) and success;
            success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-04-C [Undirected Advertising with Data on all channels ]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_04_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 50, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    success = True;
    adData = ADData();

    for dataLength in [ 1, 0, 31, 0 ]:
        trace.trace(7, '-'*80);

        advertiser.advertiseData = [ ] if dataLength == 0 else [ 0x01 ] if dataLength == 1 else \
                                   adData.encode( ADType.COMPLETE_LOCAL_NAME, 'THIS IS JUST A RANDOM NAME...' );

        advertising = advertiser.enable();
        success = success and advertising;
        if advertising:
            success = scanner.enable() and success;
            scanner.monitor();
            success = scanner.disable() and success;
            success = success and scanner.qualifyReports( 50, None, advertiser.advertiseData );

            success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-05-C [Undirected Connectable Advertising with Scan Request/Response ]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_05_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 30, 1);

    success = True;
    adData = ADData();

    for address in [ 0x456789ABCDEF, address_scramble_OUI( 0x456789ABCDEF ), address_exchange_OUI_LAP( 0x456789ABCDEF ) ]:
        for nameLength in [ 2, 31 ]:
            trace.trace(7, '-'*80);

            advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, '' ) if nameLength < 31 else \
                                      adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IUT IUT IUT IUT IUT IUT IUT IUT' );

            advertising = advertiser.enable();
            success = success and advertising;

            trace.trace(6, "\nUsing scanner address: %s SCAN_RSP data length: %d\n" % (formatAddress( toArray(address, 6), SimpleAddressType.PUBLIC), nameLength) );
            success = success and preamble_set_public_address( transport, lowerTester, address, trace );

            if advertising:
                success = scanner.enable() and success;
                scanner.monitor();
                success = scanner.disable() and success;
                success = success and scanner.qualifyReports( 1 );
                success = success and scanner.qualifyResponses( 1, advertiser.responseData );

                success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-06-C [Stop Advertising on Connection Request]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_06_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 0);

    success = True;
    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IUT' );

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, publicIdentityAddress(upperTester));

    for address in [ 0x456789ABCDEF, address_scramble_OUI( 0x456789ABCDEF ), address_scramble_LAP( 0x456789ABCDEF ), address_exchange_OUI_LAP( 0x456789ABCDEF ) ]:
        trace.trace(7, '-'*80);

        trace.trace(6, "\nUsing initiator address: %s\n" % formatAddress( toArray(address, 6), SimpleAddressType.PUBLIC));
        success = success and preamble_set_public_address( transport, lowerTester, address, trace );

        success = advertiser.enable() and success;
        connected = initiator.connect();
        success = success and connected;

        if connected:
            """
                If a connection was established Advertising should have seized...
            """
            scanner.expectedResponses = None;
            success = scanner.enable() and success;
            scanner.monitor();
            success = scanner.disable() and success;
            success = success and not scanner.qualifyReports( 1 );

            success = initiator.disconnect(0x13) and success;
        else:
            success = advertiser.disable() and success;

        if not success:
            break;

    return success;

"""
    LL/DDI/ADV/BV-07-C [Scan Request/Response followed by Connection Request]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_07_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 1, 1);

    success = True;
    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IUT' );

    success = advertiser.enable();
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, publicIdentityAddress(upperTester));
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            If a connection was established Advertising should have seized...
        """
        scanner.expectedResponses = None;
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = success and not scanner.qualifyReports( 1 );

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-08-C [Advertiser Filtering Scan requests]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_08_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Place Public and static Random addresses of lowerTester in the White List for the Advertiser
    """
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddresses = [ Address( IdentityAddressType.PUBLIC, 0x456789ABCDEF ), Address( IdentityAddressType.RANDOM, 0x456789ABCDEF | 0xC00000000000 ) ];
    success = addAddressesToWhiteList(transport, upperTester, peerAddresses, trace);

    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IUT' );

    for filterPolicy in [ AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS, AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS ]:
        trace.trace(7, "\nTesting Advertising Filter Policy: %s" % filterPolicy.name);
        advertiser.filterPolicy = filterPolicy;

        for addressType, peerAddress in zip([ ExtendedAddressType.PUBLIC, ExtendedAddressType.RANDOM ], peerAddresses):

            advertiser.peerAddress = peerAddress;
            success = advertiser.enable() and success;

            for i in range(3):
                useAddressType = addressType;
                trace.trace(7, '-'*80);
                if   i == 0:
                    """
                        Correct Address Type - scrambled Address
                    """
                    if useAddressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using scrambled PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, address_scramble_LAP( 0x456789ABCDEF ), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using scrambled RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, address_scramble_LAP( 0x456789ABCDEF ) | 0xC00000000000, trace );
                elif i == 1:
                    """
                        Incorrect Address Type - correct Address
                    """
                    useAddressType = ExtendedAddressType.RANDOM if addressType == ExtendedAddressType.PUBLIC else ExtendedAddressType.PUBLIC;
                    if useAddressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using incorrect PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, toNumber(peerAddresses[1].address), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using incorrect RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, toNumber(peerAddresses[0].address), trace );
                else:
                    """
                        Correct Address Type - correct Address
                    """
                    if useAddressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, toNumber(peerAddresses[0].address), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, toNumber(peerAddresses[1].address), trace );

                scanner.ownAddress.type = useAddressType;
                scanner.expectedReports = 30;
                scanner.expectedResponses = 1 if (i == 2) else None;

                success = scanner.enable() and success;
                scanner.monitor();
                success = scanner.disable() and success;
                success = success and scanner.qualifyReports( scanner.expectedReports );
                if not scanner.expectedResponses is None:
                    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                else:
                    success = success and not scanner.qualifyResponses( 1 );

            success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-09-C [Advertiser Filtering Connection requests]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_09_c(transport, upperTester, lowerTester, trace):

    """
        Place Public address and Random static address of lowerTester in the White List for the Advertiser
    """
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddresses = [ Address( IdentityAddressType.PUBLIC, 0x456789ABCDEF ), Address( IdentityAddressType.RANDOM, 0x456789ABCDEF | 0xC00000000000 ) ];
    success = addAddressesToWhiteList(transport, upperTester, peerAddresses, trace);
    """
        Initialize Advertiser with Connectable Undirected advertising using a Public Address
    """
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddresses[0], AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);

    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IUT' );

    for filterPolicy in [ AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS, AdvertisingFilterPolicy.FILTER_CONNECTION_REQUESTS, AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS ]:
        trace.trace(7, "\nTesting Advertising Filter Policy: %s" % filterPolicy.name);
        advertiser.filterPolicy = filterPolicy;

        for addressType, peerAddress in zip([ ExtendedAddressType.PUBLIC, ExtendedAddressType.RANDOM ], peerAddresses):

            advertiser.peerAddress = peerAddress;

            for i in range(3):
                useAddressType = addressType;
                success = advertiser.enable() and success;
                trace.trace(7, '-'*80);
                if   i == 0:
                    """
                        Correct Address Type - scrambled Address
                    """
                    if useAddressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using scrambled PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, address_scramble_OUI( 0x456789ABCDEF ), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using scrambled RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, address_scramble_OUI( 0x456789ABCDEF ) | 0xC00000000000, trace );
                elif i == 1:
                    """
                        Incorrect Address Type - correct Address
                    """
                    useAddressType = ExtendedAddressType.RANDOM if addressType == ExtendedAddressType.PUBLIC else ExtendedAddressType.PUBLIC;
                    if useAddressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using incorrect PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, toNumber(peerAddresses[1].address), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using incorrect RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, toNumber(peerAddresses[0].address), trace );
                else:
                    """
                        Correct Address Type - correct Address
                    """
                    if useAddressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using correct PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, toNumber(peerAddresses[0].address), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using correct RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, toNumber(peerAddresses[1].address), trace );

                initiatorAddress = Address( useAddressType );
                initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, publicIdentityAddress(upperTester));

                for j in range(30):
                    connected = initiator.connect();
                    success = success and (connected if (i == 2 or filterPolicy == AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS) else not connected);

                    if connected:
                        """
                            If a connection was established - disconnect...
                        """
                        success = initiator.disconnect(0x13) and success;
                        break;

                if not connected:
                    success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-11-C [High Duty Cycle Connectable Directed Advertising on all channels]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_11_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_HDC_DIRECTED, 30, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Place Public address of lowerTester in the White List
    """
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = publicIdentityAddress(lowerTester);
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    success = scanner.enable() and success;
    success = advertiser.enable() and success;
    scanner.monitor(True);
    success = advertiser.timeout() and success;
    success = scanner.disable() and success;

    success = success and scanner.qualifyReportTime( 30, 1300 );

    success = advertiser.enable() and success;

    initiator = Initiator(transport, lowerTester, upperTester, trace, ownAddress, publicIdentityAddress(upperTester));
    connected = initiator.connect();
    success = success and connected;
    if connected:
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-15-C [Discoverable Undirected Advertising on all channels]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_15_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 100, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Place Public address of lowerTester in the White List
    """
    peerAddress = publicIdentityAddress(lowerTester);
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    success = scanner.enable() and success;
    success = advertiser.enable() and success;
    scanner.monitor();
    success = advertiser.disable() and success;
    success = scanner.disable() and success;
    success = success and scanner.qualifyReports( 100, None, advertiser.advertiseData );

    return success;

"""
    LL/DDI/ADV/BV-16-C [Discoverable Undirected Advertising with Data on all channels]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_16_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 50);

    success = True;

    for i in range(4):
        advertiser.advertiseData = [ 0x01 ] if i == 0 else [ ] if i == 1 or i == 3 else [ 0x1E if _ == 0 else 0x00 for _ in range(31) ];

        success = scanner.enable() and success;
        success = advertiser.enable() and success;
        scanner.monitor();
        success = advertiser.disable()and success;
        success = scanner.disable() and success;
        success = success and scanner.qualifyReports( 50, None, advertiser.advertiseData );

    return success;

"""
    LL/DDI/ADV/BV-17-C [Discoverable Undirected Advertising with Scan Request/Response]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_17_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 30, 5);

    success = True;
    adData = ADData();

    for i in range(3):
        for j in range(2):
            advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, '' ) if j == 0 else \
                                      adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IUT IUT IUT IUT IUT IUT IUT I' );
            if   i == 1:
                success = success and preamble_set_public_address( transport, lowerTester, address_scramble_OUI( 0x456789ABCDEF ), trace );
            elif i == 2:
                success = success and preamble_set_public_address( transport, lowerTester, address_exchange_OUI_LAP( 0x456789ABCDEF ), trace );

            success = scanner.enable() and success;
            success = advertiser.enable() and success;
            scanner.monitor();
            success = advertiser.disable() and success;
            success = scanner.disable() and success;
            success = success and scanner.qualifyReports( 5 );
            success = success and scanner.qualifyResponses( 5, advertiser.responseData );

    return success;

"""
    LL/DDI/ADV/BV-18-C [Discoverable Undirected Advertiser Filtering Scan requests ]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen
"""
def ll_ddi_adv_bv_18_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 30, None, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Place Public address of lowerTester in the White List
    """
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = publicIdentityAddress(lowerTester);
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IUT' );

    success = advertiser.enable() and success;

    for i, addressType in enumerate([ ExtendedAddressType.PUBLIC, ExtendedAddressType.RANDOM, ExtendedAddressType.PUBLIC ]):
        if   i == 0:
            success = success and preamble_set_public_address( transport, lowerTester, address_scramble_LAP( 0x456789ABCDEF ), trace);
        elif i == 1:
            success = success and preamble_set_random_address( transport, lowerTester, 0x456789ABCDEF, trace );
        else:
            success = success and preamble_set_public_address( transport, lowerTester, 0x456789ABCDEF, trace );
            scanner.expectedResponses = 1;

        scanner.ownAddress = Address( addressType );

        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = success and scanner.qualifyReports( 1 if i > 1 else 30 );
        success = success and scanner.qualifyResponses( 1 if i > 1 else 0, advertiser.responseData if i > 1 else None );

    success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-19-C [Low Duty Cycle Directed Advertising on all channels]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen (NOTE: The automatic disconnect due to supervision timeout cannot be achieved)
"""
def ll_ddi_adv_bv_19_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED, 100, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Place Public address of lowerTester in the White List
    """
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = publicIdentityAddress(lowerTester);
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    success = advertiser.enable() and success;

    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = success and scanner.qualifyReports( 100 );

    initiator = Initiator(transport, lowerTester, upperTester, trace, ownAddress, publicIdentityAddress(upperTester));
    connected = initiator.connect();
    success = success and connected;

    if connected:
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/DDI/ADV/BV-20-C [Advertising on the LE 1M PHY on all channels]

    Last modified: 30-07-2019
    Reviewed and verified: 30-07-2019 Henrik Eriksen (NOTE: The PHY channel used in advertising can only be verified by looking at the Air trace)
"""
def ll_ddi_adv_bv_20_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 100, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Place Public address of lowerTester in the White List
    """
    peerAddress = publicIdentityAddress(lowerTester);
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    AllPhys, TxPhys, RxPhys = 0, PreferredPhysicalChannel.LE_2M, PreferredPhysicalChannel.LE_2M;

    success = success and preamble_default_physical_channel(transport, upperTester, AllPhys, TxPhys, RxPhys, trace);

    success = scanner.enable() and success;
    success = advertiser.enable() and success;
    scanner.monitor();
    success = advertiser.disable() and success;
    success = scanner.disable() and success;
    success = success and scanner.qualifyReports( 100 );

    return success;

"""
    LL/DDI/ADV/BV-21-C [Non-Connectable Extended Legacy Advertising with Data on all channels]
"""
def ll_ddi_adv_bv_21_c(transport, upperTester, lowerTester, trace):

    Handle          = 0;
    Properties      = ExtAdvertiseType.LEGACY;
    PrimMinInterval = toArray(0x0020, 3); # Minimum Advertise Interval = 32 x 0.625 ms = 20.00 ms
    PrimMaxInterval = toArray(0x0022, 3); # Maximum Advertise Interval = 34 x 0.625 ms = 21.25 ms
    PrimChannelMap  = 0x07;  # Advertise on all three channels (#37, #38 and #39)
    OwnAddrType     = SimpleAddressType.PUBLIC;
    PeerAddrType, PeerAddress = random_address( 0x456789ABCDEF );
    FilterPolicy    = AdvertisingFilterPolicy.FILTER_NONE;
    TxPower         = 0;
    PrimAdvPhy      = PhysicalChannel.LE_1M; # Primary advertisement PHY is LE 1M
    SecAdvMaxSkip   = 0;     # AUX_ADV_IND shall be sent prior to the next advertising event
    SecAdvPhy       = PhysicalChannel.LE_2M;
    Sid             = 0;
    ScanReqNotifyEnable = 0; # Scan request notifications disabled

    success = preamble_ext_advertising_parameters_set(transport, upperTester, Handle, Properties, PrimMinInterval, PrimMaxInterval, \
                                                      PrimChannelMap, OwnAddrType, PeerAddrType, PeerAddress, FilterPolicy, TxPower, \
                                                      PrimAdvPhy, SecAdvMaxSkip, SecAdvPhy, Sid, ScanReqNotifyEnable, trace);

    for i in range(3):
        if i == 0:
            AdvData = [ 0x01 ];
        elif i == 1:
            AdvData = [ ];
        else:
            AdvData = [ 0x1F ] + [ 0 for _ in range(30) ];

        Operation      = FragmentOperation.COMPLETE_FRAGMENT;
        FragPreference = FragmentPreference.FRAGMENT_ALL_DATA;

        success = success and preamble_ext_advertising_data_set(transport, upperTester, Handle, Operation, FragPreference, advData, trace);

        scanInterval = 32; # Scan Interval = 32 x 0.625 ms = 20.0 ms
        scanWindow   = 32; # Scan Window   = 32 x 0.625 ms = 20.0 ms
        addrType     = SimpleAddressType.RANDOM;
        filterPolicy = ScanningFilterPolicy.FILTER_NONE;

        success = success and preamble_passive_scanning(transport, lowerTester, scanInterval, scanWindow, addrType, filterPolicy, trace);

        SHandle        = [ Handle ];
        SDuration      = [ 0 ];
        SMaxExtAdvEvts = [ 0 ];

        success = success and preamble_ext_advertise_enable(transport, upperTester, Advertise.ENABLE, SHandle, SDuration, SMaxExtAdvEvts, trace);

        deltas = [];
        reports = 0;
        while reports < 50:
            if has_event(transport, lowerTester, 100)[0]:
                event = get_event(transport, lowerTester, 100);
                # showEvent(event, eventData, trace);
                isReport = event.subEvent == MetaEvents.BT_HCI_EVT_LE_ADVERTISING_REPORT;
                if isReport:
                    eventType, data = event.decode()[0:3:2];
                    if eventType == AdvertisingReport.ADV_NONCONN_IND:
                        reports += 1;
                        reportData = data;
                        if reports > 1:
                            deltas += [event.time - prevTime];
                        prevTime = event.time;

        success = success and preamble_scan_enable(transport, lowerTester, Scan.DISABLE, ScanFilterDuplicate.DISABLE, trace);
        success = success and preamble_ext_advertise_enable(transport, upperTester, Advertise.DISABLE, SHandle, SDuration, SMaxExtAdvEvts, trace);
        success = success and (reportData == AdvData);

        trace.trace(7, "Mean distance between Advertise Events %d ms std. deviation %.1f ms" % (statistics.mean(deltas), statistics.pstdev(deltas)));

    return success;

"""
    LL/DDI/SCN/BV-01-C [Passive Scanning of Non-Connectable Advertising Packets]

    Last modified: 31-07-2019
    Reviewed and verified: 31-07-2019 Henrik Eriksen (NOTE: Advertise data not modified for each advertise event)
"""
def ll_ddi_scn_bv_01_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, upperTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 20);

    success = scanner.enable();

    for i, channel in enumerate([ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ]):
        if   i == 0:
            advertiser.ownAddress = publicIdentityAddress(lowerTester);
        elif i == 1:
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_LAP(0x456789ABCDEF) );
        elif i == 2:
            advertiser.ownAddress = Address( ExtendedAddressType.RANDOM, address_scramble_OUI(0x456789ABCDEF) | 0xC00000000000);

        if advertiser.ownAddress.type == ExtendedAddressType.PUBLIC:
            success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
        else:
            success = success and preamble_set_random_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);

        advertiser.channels = channel;
        advertiser.advertiseData = [ i + 1 ];

        success = advertiser.enable() and success;
        scanner.monitor();
        success = advertiser.disable() and success;
        success = success and scanner.qualifyReports( 20, advertiser.ownAddress, advertiser.advertiseData );

    success = scanner.disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-02-C [Filtered Passive Scanning of Non-Connectable Advertising Packets]

    Last modified: 31-07-2019
    Reviewed and verified: 31-07-2019 Henrik Eriksen (NOTE: Advertise data not modified for each advertise event)
"""
def ll_ddi_scn_bv_02_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, upperTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 20, \
                                             AdvertisingFilterPolicy.FILTER_NONE, AdvertiseChannel.CHANNEL_37, ScanningFilterPolicy.FILTER_WHITE_LIST);
    """
        Place Public address of lowerTester in the White List
    """
    peerAddress = publicIdentityAddress(lowerTester);
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    success = scanner.enable() and success;

    for i in range(4):
        if   i == 0:
            advertiser.ownAddress = publicIdentityAddress(lowerTester);
        elif i == 1:
            advertiser.ownAddress = Address( ExtendedAddressType.RANDOM, 0x456789ABCDEF | 0xC00000000000);
        elif i == 2:
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_LAP(0x456789ABCDEF) );
        elif i == 3:
            advertiser.ownAddress = Address( ExtendedAddressType.RANDOM, address_exchange_OUI_LAP(0x456789ABCDEF) | 0xC00000000000);

        if advertiser.ownAddress.type == ExtendedAddressType.PUBLIC:
            success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
        else:
            success = success and preamble_set_random_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);

        advertiser.advertiseData = [ i + 1 ];

        success = advertiser.enable() and success;
        scanner.monitor();
        success = advertiser.disable() and success;
        if i == 0:
            success = success and scanner.qualifyReports( 20, advertiser.ownAddress, advertiser.advertiseData );
        else:
            success = success and scanner.qualifyReports( 0 );

    success = scanner.disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-03-C [Active Scanning of Connectable Undirected Advertising Packets]

    Last modified: 31-07-2019
    Reviewed and verified: 31-07-2019 Henrik Eriksen (NOTE: Advertise data not modified for each advertise event)
"""
def ll_ddi_scn_bv_03_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 20, 1);

    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IX' );
    success = scanner.enable();

    for channel in [ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ]:
        for i in range(4):
            if   i == 0:
                advertiser.ownAddress = publicIdentityAddress(lowerTester);
            elif i == 1:
                advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_OUI(0x456789ABCDEF) );
            elif i == 2:
                advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_LAP(0x456789ABCDEF) );
            else:
                advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_exchange_OUI_LAP(0x456789ABCDEF) );

            success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
            advertiser.channels = channel;
            advertiser.advertiseData = [ i + 1 ];

            success = advertiser.enable() and success;
            scanner.monitor();
            success = advertiser.disable() and success;
            success = success and scanner.qualifyReports( 20, advertiser.ownAddress, advertiser.advertiseData );
            success = success and scanner.qualifyResponses( 1, advertiser.responseData );

    success = scanner.disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-04-C [Filtered Active Scanning of Connectable Undirected Advertising Packets]

    Last modified: 31-07-2019
    Reviewed and verified: 31-07-2019 Henrik Eriksen (NOTE: Advertise data not modified for each advertise event)
"""
def ll_ddi_scn_bv_04_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 20, 1, \
                                            AdvertisingFilterPolicy.FILTER_NONE, AdvertiseChannel.ALL_CHANNELS, ScanningFilterPolicy.FILTER_WHITE_LIST);
    """
        Place Public address of lowerTester in the White List
    """
    peerAddress = publicIdentityAddress(lowerTester);
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IX' );
    success = scanner.enable();

    for channel in [ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ]:
        for i in range(3):
            if   i == 0:
                advertiser.ownAddress = publicIdentityAddress(lowerTester);
            elif i == 1:
                advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_LAP(0x456789ABCDEF) );
            else:
                advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_exchange_OUI_LAP(0x456789ABCDEF) );

            success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
            advertiser.channels = channel;
            advertiser.advertiseData = [ i + 1 ];

            success = advertiser.enable() and success;
            scanner.monitor();
            success = advertiser.disable() and success;
            if i == 0:
                success = success and scanner.qualifyReports( 20, advertiser.ownAddress, advertiser.advertiseData );
                success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            else:
                success = success and scanner.qualifyReports( 0 );
                success = success and scanner.qualifyResponses( 0 );

    success = scanner.disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-05-C [Scanning for different Advertiser types with and without Data]

    Last modified: 31-07-2019
    Reviewed and verified: 31-07-2019 Henrik Eriksen (NOTE: Advertise data not modified for each advertise event)
"""
def ll_ddi_scn_bv_05_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, upperTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 20, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.FLAGS, ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IX' );
    success = scanner.enable();

    for i, (channel, advertiseType, reports) in enumerate(zip( \
                             [ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ], \
                             [ Advertising.NON_CONNECTABLE_UNDIRECTED, Advertising.SCANNABLE_UNDIRECTED, Advertising.CONNECTABLE_HDC_DIRECTED ], \
                             [ 20, 30, 15 ] )):
        if   i == 0:
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_OUI(0x456789ABCDEF) );
        elif i == 1:
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_LAP(0x456789ABCDEF) );
        else:
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_exchange_OUI_LAP(0x456789ABCDEF) );

        success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
        advertiser.channels = channel;
        advertiser.advertiseType = advertiseType;
        advertiser.advertiseData = [ i + 1 ] if i < 2 else [ ];

        scanner.expectedReports = reports;
        scanner.reportType = matchingReportType(advertiseType);

        success = advertiser.enable() and success;
        scanner.monitor();
        success = advertiser.disable() and success;
        success = success and scanner.qualifyReports( reports, advertiser.ownAddress, advertiser.advertiseData );
        if i == 1:
            success = success and scanner.qualifyResponses( 1, advertiser.responseData );
        else:
            success = success and scanner.qualifyResponses( 0 );

    success = scanner.disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-10-C [Passive Scanning for Undirected Advertising Packets with Data]

    Last modified: 31-07-2019
    Reviewed and verified: 31-07-2019 Henrik Eriksen (NOTE: Advertise data not modified for each advertise event)
"""
def ll_ddi_scn_bv_10_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 20);

    success = True;

    for i, channel in enumerate([ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ]):
        if   i == 0:
            advertiser.ownAddress = publicIdentityAddress(lowerTester);
        elif i == 1:
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_LAP(0x456789ABCDEF) );
        elif i == 2:
            advertiser.ownAddress = Address( ExtendedAddressType.RANDOM, address_scramble_OUI(0x456789ABCDEF) | 0xC00000000000);

        if (advertiser.ownAddress.type == ExtendedAddressType.PUBLIC):
            success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
        else:
            success = success and preamble_set_random_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);

        advertiser.channels = channel;
        advertiser.advertiseData = [ i + 1 ];

        success = advertiser.enable() and success;
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = advertiser.disable() and success;
        success = success and scanner.qualifyReports( 20, advertiser.ownAddress, advertiser.advertiseData );

    return success;

"""
    LL/DDI/SCN/BV-11-C [Passive Scanning for Directed Advertising Packets]

    Last modified: 31-07-2019
    Reviewed and verified: 31-07-2019 Henrik Eriksen (NOTE: Advertise data not modified for each advertise event)
"""
def ll_ddi_scn_bv_11_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED, 20, \
                                             AdvertisingFilterPolicy.FILTER_NONE, AdvertiseChannel.ALL_CHANNELS, ScanningFilterPolicy.FILTER_WHITE_LIST);
    """
        Place Public address of lowerTester in the White List
    """
    peerAddress = publicIdentityAddress(lowerTester);
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    for i, channel in enumerate([ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ]):
        if   i == 0:
            advertiser.ownAddress = publicIdentityAddress(lowerTester);
        elif i == 1:
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_LAP(0x456789ABCDEF) );
        elif i == 2:
            advertiser.ownAddress = Address( ExtendedAddressType.RANDOM, 0x456789ABCDEF | 0xC00000000000 );

        if (advertiser.ownAddress.type == ExtendedAddressType.PUBLIC):
            success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
        else:
            success = success and preamble_set_random_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);

        advertiser.channels = channel;

        success = advertiser.enable() and success;
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = advertiser.disable() and success;
        if i == 0:
            success = success and scanner.qualifyReports( 20, advertiser.ownAddress, advertiser.advertiseData );
        else:
            success = success and scanner.qualifyReports( 0 );

    return success;

"""
    LL/DDI/SCN/BV-12-C [Passive Scanning for Discoverable Undirected Advertising Packets]

    Last modified: 31-07-2019
    Reviewed and verified: 31-07-2019 Henrik Eriksen (NOTE: Advertise data not modified for each advertise event)
"""
def ll_ddi_scn_bv_12_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, upperTester, trace, Advertising.SCANNABLE_UNDIRECTED, 20, \
                                             AdvertisingFilterPolicy.FILTER_NONE, AdvertiseChannel.ALL_CHANNELS, ScanningFilterPolicy.FILTER_WHITE_LIST);
    """
        Place Public address of lowerTester in the White List
    """
    peerAddress = publicIdentityAddress(lowerTester);
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    for i, channel in enumerate([ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ]):
        if   i == 0:
            advertiser.ownAddress = publicIdentityAddress(lowerTester);
        elif i == 1:
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_LAP(0x456789ABCDEF) );
        elif i == 2:
            advertiser.ownAddress = Address( ExtendedAddressType.RANDOM, address_scramble_OUI(0x456789ABCDEF) | 0xC00000000000);

        if (advertiser.ownAddress.type == ExtendedAddressType.PUBLIC):
            success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
        else:
            success = success and preamble_set_random_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);

        advertiser.channels = channel;
        advertiser.advertiseData = [ i + 1 ];

        success = advertiser.enable() and success;
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = advertiser.disable() and success;
        if i == 0:
            success = success and scanner.qualifyReports( 20, advertiser.ownAddress, advertiser.advertiseData );
        else:
            success = success and scanner.qualifyReports( 0 );

    return success;

"""
    LL/DDI/SCN/BV-13-C [Passive Scanning for Non-Connectable Advertising Packets using Network Privacy]

    Last modified: 31-07-2019
    Reviewed and verified: 31-07-2019 Henrik Eriksen
"""
def ll_ddi_scn_bv_13_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivatePassiveScanning(transport, upperTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 20);
    advertiser.channels = AdvertiseChannel.CHANNEL_37;
    """
        Add Public address of lowerTester to upperTesters Resolving List
        Add Public address of upperTester to lowerTesters Resolving List (to allow the Controller to generate a Private Resolvable Address)
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester) ) and success;
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    """
        Set Resolvable Private Address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = advertiser.disable() and success;
    """
        Verify that the Advertise address of the lowerTester has been correctly resolved
    """
    success = success and scanner.qualifyReports( 20, Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEF ) );

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-14-C [Passive Scanning for Connectable Directed Advertising Packets using Network Privacy]

    Last modified: 01-08-2019
    Reviewed and verified: 01-08-2019 Henrik Eriksen
"""
def ll_ddi_scn_bv_14_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivatePassiveScanning(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED, 20, \
                                                    ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                                                    AdvertisingFilterPolicy.FILTER_NONE, AdvertiseChannel.CHANNEL_37, ScanningFilterPolicy.FILTER_ID_DIRECTED);
    """
        Add Public address of lowerTester to upperTesters Resolving List
        Add Public address of upperTester to lowerTesters Resolving List (to allow the Controller to generate a Private Resolvable Address)
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester) ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = advertiser.disable() and success;
    success = success and scanner.qualifyDirectedReports( 20 );

    ok, address = readLocalResolvableAddress(transport, upperTester, publicIdentityAddress(upperTester), trace);
    trace.trace(8, "Address used by Scanner: %s" % str(Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, address )));

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-15-C [Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with no Local or Peer IRK]

    Last modified: 01-08-2019
    Reviewed and verified: 01-08-2019 Henrik Eriksen
"""
def ll_ddi_scn_bv_15_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivateActiveScanning(transport, upperTester, trace, Advertising.SCANNABLE_UNDIRECTED, 20, 1, \
                                                   ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_RANDOM);

    adData = ADData();
    advertiser.channels = AdvertiseChannel.CHANNEL_37;
    advertiser.advertiseData = [ 0x00 ];
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IX' );
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester) ) and success;
    success = RPAs[upperTester].add( Address( SimpleAddressType.RANDOM, tests.test_utils.lowerRandomAddress ) ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = advertiser.disable() and success;
    success = success and scanner.qualifyReports( 5, None, advertiser.advertiseData );
    success = success and scanner.qualifyResponses( 5, advertiser.responseData );

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-16-C [Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with Local and no Peer IRK]

    Last modified: 01-08-2019
    Reviewed and verified: 01-08-2019 Henrik Eriksen (Peer address type not set to 0x01 in entry added to RPA List)
"""
def ll_ddi_scn_bv_16_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivateActiveScanning(transport, upperTester, trace, Advertising.SCANNABLE_UNDIRECTED, 20, 1);

    adData = ADData();
    advertiser.channels = AdvertiseChannel.CHANNEL_37;
    advertiser.advertiseData = [ 0x00 ];
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IX' );

    lowerIdentityAddress = publicIdentityAddress(lowerTester);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPA = ResolvableAddresses( transport, upperTester, trace, upperIRK );
    success = RPA.clear();
    success = RPA.add( lowerIdentityAddress ) and success;
    """
        Set resolvable private address timeout in seconds ( two seconds )
    """
    success = RPA.timeout( 2 ) and success;
    success = RPA.enable() and success;

    success = advertiser.enable() and success;

    resolvableAddresses = [ 0, 0 ];

    for i in range(2):
        if i == 1:
            """
                Wait for Resolvable Private Address timeout to expire...
            """
            transport.wait(2000);
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = success and scanner.qualifyReports( 5, lowerIdentityAddress, advertiser.advertiseData );
        success = success and scanner.qualifyResponses( 5, advertiser.responseData );

        addressRead, resolvableAddresses[i] = readLocalResolvableAddress(transport, upperTester, lowerIdentityAddress, trace);
        trace.trace(6, "Local Resolvable Address: %s" % formatAddress(resolvableAddresses[i]));

    success = advertiser.disable() and success;
    success = success and toNumber(resolvableAddresses[0]) != toNumber(resolvableAddresses[1]);
    success = RPA.disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-17-C [Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with no Local and a Peer IRK]

    Last modified: 01-08-2019
    Reviewed and verified: 01-08-2019 Henrik Eriksen
"""
def ll_ddi_scn_bv_17_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivateActiveScanning(transport, upperTester, trace, Advertising.SCANNABLE_UNDIRECTED, 20, 1, \
                                                   ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_RANDOM);
    adData = ADData();
    advertiser.channels = AdvertiseChannel.CHANNEL_37;
    advertiser.advertiseData = [ 0x00 ];
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IX' );
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester) ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = advertiser.disable() and success;
    success = success and scanner.qualifyReports( 5, None, advertiser.advertiseData );
    success = success and scanner.qualifyResponses( 5, advertiser.responseData );

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-18-C [Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with both Local and Peer IRKs]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_ddi_scn_bv_18_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivateActiveScanning(transport, upperTester, trace, Advertising.SCANNABLE_UNDIRECTED, 20);

    adData = ADData();
    advertiser.channels = AdvertiseChannel.CHANNEL_37;
    advertiser.advertiseData = [ 0x00 ];
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IX' );
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[upperTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = advertiser.disable() and success;
    success = success and scanner.qualifyReports( 5, None, advertiser.advertiseData );
    success = success and scanner.qualifyResponses( 5, advertiser.responseData );

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-26-C [Passive Scanning for Non-Connectable Advertising Packets using Network Privacy]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_ddi_scn_bv_26_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivatePassiveScanning(transport, upperTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 20);
    advertiser.channels = AdvertiseChannel.CHANNEL_37;
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPA = ResolvableAddresses( transport, upperTester, trace );
    success = RPA.clear();
    success = RPA.add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPA.timeout( 60 ) and success;
    success = RPA.enable() and success;

    success = advertiser.enable() and success;
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = advertiser.disable() and success;
    success = success and scanner.qualifyReports( 0 );

    success = RPA.disable() and success;

    return success;

"""
    LL/DDI/SCN/BV-28-C [Passive Scanning for Non-Connectable Advertising Packets using Device Privacy]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_ddi_scn_bv_28_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivatePassiveScanning(transport, upperTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 20);
    advertiser.channels = AdvertiseChannel.CHANNEL_37;

    """
        Add Public address of lowerTester to the Resolving List
    """
    lowerIdentityAddress = publicIdentityAddress(lowerTester);
    RPA = ResolvableAddresses( transport, upperTester, trace );
    success = RPA.clear();
    success = RPA.add( lowerIdentityAddress, lowerIRK ) and success;
    """
        Set Device Privacy Mode
    """
    success = setPrivacyMode(transport, upperTester, lowerIdentityAddress, PrivacyMode.DEVICE_PRIVACY, trace) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPA.timeout( 60 ) and success;
    success = RPA.enable() and success;

    success = advertiser.enable() and success;
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = advertiser.disable() and success;
    success = success and scanner.qualifyReports( 20, lowerIdentityAddress );

    success = RPA.disable() and success;

    return success;

"""
    LL/CON/ADV/BV-01-C [Accepting Connection Request]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_con_adv_bv_01_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 5);
    advertiser.channels = AdvertiseChannel.CHANNEL_37;

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, publicIdentityAddress(upperTester));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
    """
        If a connection was established Advertising should have seized...
    """
    if connected:
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = success and not scanner.qualifyReports( 1 );

        transport.wait(24820);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/ADV/BV-04-C [Accepting Connection Request after Directed Advertising]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_con_adv_bv_04_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_HDC_DIRECTED);

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, address_scramble_OUI(0x123456789ABC) ));
    """
        Verify that connection is not established to wrong Init Address
    """
    success = advertiser.enable();
    connected = initiator.connect();
    success = success and not connected;
    if connected:
        success = initiator.disconnect(0x13) and success;
    else:
        """
            Need to stop connection attempt - otherwise following commands will fail with not allowed...
        """
        success = advertiser.disable() and success;
        success = initiator.cancelConnect() and success;
    """
        Verify that the upper Tester continues to Advertise for 1280 ms.
    """
    transport.wait(200);
    success = scanner.enable() and success;
    success = advertiser.enable() and success;
    scanner.monitor(True);
    success = advertiser.timeout() and success;
    success = scanner.disable() and success;
    success = success and not scanner.qualifyReportTime( 100, 1200 );

    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, publicIdentityAddress(upperTester));
    """
        Verify that connection is established to correct Init Address
    """
    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(2660);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/ADV/BV-09-C [Accepting Connection Request using Channel Selection Algorithm #2]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_con_adv_bv_09_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
       Enable the LE Channel Selection Algorithm Event
    """
    events = [0xFF, 0xFF, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];

    success = setLEEventMask(transport, upperTester, events, trace);

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Check for LE Channel Selection Algorithm Event in upper Tester...
        """
        success, handle, chSelAlgorithm = hasChannelSelectionAlgorithmEvent(transport, upperTester, trace);
        success = success and (chSelAlgorithm == 1);

        transport.wait(2600);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/ADV/BV-10-C [Accepting Connection Request after Directed Advertising using Channel Selection Algorithm #2]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_con_adv_bv_10_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED);
    """
        Enable the LE Channel Selection Algorithm Event
    """
    events = [0xFF, 0xFF, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];

    success = setLEEventMask(transport, upperTester, events, trace);

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Check for LE Channel Selection Algorithm Event in upper Tester...
        """
        success, handle, chSelAlgorithm = hasChannelSelectionAlgorithmEvent(transport, upperTester, trace);
        success = success and (chSelAlgorithm == 1);

        transport.wait(2600);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/INI/BV-01-C [Connection Initiation rejects Address change]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen (NOTE: Timing for connection events not verified - see Air Trace)
"""
def ll_con_ini_bv_01_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = True;
    for channel in [ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ]:

        advertiser.channels = channel;

        for address in [ 0x456789ABCDEF, address_scramble_OUI(0x456789ABCDEF), address_scramble_LAP(0x456789ABCDEF), address_exchange_OUI_LAP(0x456789ABCDEF) ]:

            trace.trace(7, "\nUsing channel %s and Lower Tester address %s\n" % (str(channel), formatAddress(toArray(address, 6))));

            success = preamble_set_public_address(transport, lowerTester, address, trace) and success;
            initiator.peerAddress = Address( ExtendedAddressType.PUBLIC, address );

            success = initiator.preConnect() and success;

            randAddress = [ random.randint(0,255) for _ in range(6) ];
            randAddress[5] |= 0xC0;
            status = le_set_random_address(transport, upperTester, randAddress, 100);
            trace.trace(6, "LE Set Random Address Command returns status: 0x%02X" % status);
            success = success and (status == 0x0C);
            getCommandCompleteEvent(transport, upperTester, trace);

            success = advertiser.enable() and success;
            connected = initiator.postConnect();
            success = success and connected;

            if connected:
                transport.wait(2660);
                success = initiator.disconnect(0x13) and success;
            else:
                success = advertiser.disable() and success;

            if not success:
                break;

    return success;

"""
    LL/CON/INI/BV-02-C [Connecting to Advertiser using Directed Advertising Packets]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen (NOTE: Timing for connection events not verified - see Air Trace)
"""
def ll_con_ini_bv_02_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(2660);
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/INI/BV-06-C [Filtered Connection to Advertiser using Undirected Advertising Packets]

    Last modified: 09-12-2019
    Reviewed and verified: 09-12-2019 Henrik Eriksen
"""
def ll_con_ini_bv_06_c(transport, upperTester, lowerTester, trace):

    success = True;
    for j in range(2):
        if j == 0:
            advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                       AdvertisingFilterPolicy.FILTER_NONE, AdvertiseChannel.CHANNEL_38, InitiatorFilterPolicy.FILTER_WHITE_LIST_ONLY);
        else:
            advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                        ExtendedAddressType.RANDOM, ExtendedAddressType.RANDOM, AdvertisingFilterPolicy.FILTER_NONE, \
                                                        AdvertiseChannel.CHANNEL_38, InitiatorFilterPolicy.FILTER_WHITE_LIST_ONLY);
        """
            Place Public|Random address of lowerTester in the White List
        """
        whiteListAddress = publicIdentityAddress(lowerTester) if j == 0 else randomIdentityAddress(lowerTester);

        success = addAddressesToWhiteList(transport, upperTester, [ whiteListAddress ], trace) and success;
        addresses = [ Address( ExtendedAddressType.RANDOM if whiteListAddress.type == SimpleAddressType.PUBLIC \
                                                          else ExtendedAddressType.PUBLIC, whiteListAddress.address ),
                      Address( ExtendedAddressType.PUBLIC if whiteListAddress.type == SimpleAddressType.PUBLIC \
                                                          else ExtendedAddressType.RANDOM, address_scramble_LAP(toNumber(whiteListAddress.address)) ),
                      whiteListAddress ];

        for i, advertiserAddress in enumerate( addresses ):

            advertiser.ownAddress = advertiserAddress;
            if advertiserAddress.type == ExtendedAddressType.RANDOM:
                success = preamble_set_random_address(transport, lowerTester, toNumber(advertiserAddress.address), trace) and success;
            else:
                success = preamble_set_public_address(transport, lowerTester, toNumber(advertiserAddress.address), trace) and success;

            success = advertiser.enable() and success;
            connected = initiator.connect();
            success = (connected if i == 2 else not connected) and success;

            if connected:
                success = initiator.disconnect(0x13) and success;
            else:
                """
                    Need to stop connection attempt - otherwise following commands will fail with not allowed...
                """
                success = initiator.cancelConnect() and success;
                success = advertiser.disable() and success;

            if not success:
                break

    return success;

"""
    LL/CON/INI/BV-07-C [Filtered Connection to Advertiser using Directed Advertising Packets]

    Last modified: 09-12-2019
    Reviewed and verified: 09-12-2019 Henrik Eriksen
"""
def ll_con_ini_bv_07_c(transport, upperTester, lowerTester, trace):

    success = True;
    for j in range(2):
        if j == 0:
            advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED, \
                                                       AdvertisingFilterPolicy.FILTER_NONE, AdvertiseChannel.CHANNEL_38, InitiatorFilterPolicy.FILTER_WHITE_LIST_ONLY);
        else:
            advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED, \
                                                        ExtendedAddressType.RANDOM, ExtendedAddressType.RANDOM, AdvertisingFilterPolicy.FILTER_NONE, \
                                                        AdvertiseChannel.CHANNEL_38, InitiatorFilterPolicy.FILTER_WHITE_LIST_ONLY);
        """
            Place Public|Random address of lowerTester in the White List
        """
        whiteListAddress = publicIdentityAddress(lowerTester) if j == 0 else randomIdentityAddress(lowerTester);

        success = addAddressesToWhiteList(transport, upperTester, [ whiteListAddress ], trace) and success;

        addresses = [ Address( ExtendedAddressType.RANDOM if whiteListAddress.type == SimpleAddressType.PUBLIC \
                                                          else ExtendedAddressType.PUBLIC, whiteListAddress.address ),
                      Address( ExtendedAddressType.PUBLIC if whiteListAddress.type == SimpleAddressType.PUBLIC \
                                                          else ExtendedAddressType.RANDOM, address_scramble_LAP(toNumber(whiteListAddress.address)) ),
                      whiteListAddress ];

        for i, advertiserAddress in enumerate( addresses ):

            advertiser.ownAddress = advertiserAddress;
            if advertiserAddress.type == ExtendedAddressType.RANDOM:
                success = preamble_set_random_address(transport, lowerTester, toNumber(advertiserAddress.address), trace) and success;
            else:
                success = preamble_set_public_address(transport, lowerTester, toNumber(advertiserAddress.address), trace) and success;

            success = advertiser.enable() and success;
            connected = initiator.connect();
            success = (connected if i == 2 else not connected) and success;

            if connected:
                success = initiator.disconnect(0x13) and success;
            else:
                """
                    Need to stop connection attempt - otherwise following commands will fail with not allowed...
                """
                success = initiator.cancelConnect() and success;
                success = advertiser.disable() and success;

    return success;

"""
    LL/CON/INI/BV-08-C [Connecting to Connectable Undirected Advertiser with Network Privacy]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_con_ini_bv_08_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                ExtendedAddressType.PUBLIC, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_NONE, AdvertiseChannel.CHANNEL_38);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPA = ResolvableAddresses( transport, upperTester, trace, upperIRK );
    success = RPA.clear();
    success = RPA.add( publicIdentityAddress(lowerTester) ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPA.timeout( 60 ) and success;
    success = RPA.enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = connected and success;

    if connected:
        transport.wait(2660);
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPA.disable() and success;

    return success;

"""
    LL/CON/INI/BV-09-C [Connecting to Connectable Undirected Advertiser with Network Privacy thru Resolving List]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_con_ini_bv_09_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Add Public address of lowerTester to the Resolving List
    """
    randIRK = [ random.randint(0,255) for _ in range(16) ];

    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, randIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = initiator.preConnect() and success;
    success = advertiser.enable() and success;
    connected = initiator.postConnect();
    success = success and not connected;
    if connected:
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[lowerTester].clear() and success;
    RPAs[lowerTester].localIRK = lowerIRK[ : ];
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;

    success = advertiser.enable() and success;
    connected = initiator.postConnect();
    success = success and connected;

    if connected:
        transport.wait(2660);
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/CON/INI/BV-10-C [Connecting to Directed Advertiser with Network Privacy thru Resolving List]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen
"""
def ll_con_ini_bv_10_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED);
    """
        Add Public address of lowerTester to the Resolving List
    """
    randIRK = [ random.randint(0,255) for _ in range(16) ];

    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, randIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester) ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = initiator.preConnect() and success;
    success = advertiser.enable() and success;
    connected = initiator.postConnect();
    success = success and not connected;
    if connected:
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[lowerTester].clear() and success;
    RPAs[lowerTester].localIRK = lowerIRK[ : ];
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester) ) and success;

    success = advertiser.enable() and success;
    connected = initiator.postConnect();
    success = success and connected;

    if connected:
        transport.wait(2660);
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/CON/INI/BV-11-C [Connecting to Directed Advertiser using  wrong address with Network Privacy thru Resolving List ]

    Last modified: 02-08-2019
    Reviewed and verified: 02-08-2019 Henrik Eriksen (NOTE: Cannot confirm that the InitA used in ADV_DIRECT_INT is different from the one used in CONNECT_REQ - see Air trace)
"""
def ll_con_ini_bv_11_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED);
    """
        Add Public address of lowerTester to the Resolving List
    """
    randIRK = [ random.randint(0,255) for _ in range(16) ];

    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, randIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( three seconds and sixty seconds )
    """
    success = RPAs[upperTester].timeout( 3 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = initiator.preConnect() and success;
    success = advertiser.enable() and success;
    connected = initiator.postConnect();
    success = success and not connected;
    if connected:
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[lowerTester].clear() and success;
    RPAs[lowerTester].localIRK = lowerIRK[ : ];
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;

    success = advertiser.enable() and success;
    connected = initiator.postConnect();
    success = success and connected;

    if connected:
        transport.wait(2660);
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/CON/INI/BV-12-C [Connecting to Directed Advertiser using Identity address with Network Privacy thru Resolving List]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Cannot confirm that the InitA used in ADV_DIRECT_INT is different from the one used in CONNECT_REQ - see Air trace)
"""
def ll_con_ini_bv_12_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester) ) and success;
    """
        Set resolvable private address timeout in seconds ( three seconds and sixty seconds )
    """
    success = RPAs[upperTester].timeout( 3 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = initiator.preConnect() and success;
    success = advertiser.enable() and success;
    connected = initiator.postConnect();
    success = success and not connected;
    success = advertiser.disable() and success;

    success = RPAs[lowerTester].clear() and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;

    success = advertiser.enable() and success;
    connected = initiator.postConnect();
    success = success and connected;

    if connected:
        trace.trace(8, "Initiators local RPA: %s" % formatAddress(initiator.localRPA()));

        localRPAs = [ initiator.localRPA()[ : ], [ 0 for _ in range(6) ] ];

        transport.wait(2660);
        success = initiator.disconnect(0x13) and success;

        success = advertiser.enable() and success;
        connected = initiator.connect();
        success = success and connected;

        if connected:
            trace.trace(8, "Initiators local RPA: %s" % formatAddress(initiator.localRPA()));

            localRPAs[1] = initiator.localRPA()[ : ];

            success = initiator.disconnect(0x13) and success;
            """
                Verify that the Initiator Address (RPA) used in the CONNECT_IND has changed due to RPA timeout...
            """
            success = success and localRPAs[0] != localRPAs[1];
        else:
            success = advertiser.disable() and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/CON/INI/BV-16-C [Connecting to Advertiser with Channel Selection Algorithm #2]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing requirements cannot be verified - see Air trace)
"""
def ll_con_ini_bv_16_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
       Enable the LE Channel Selection Algorithm Event
    """
    events = [0xFF, 0xFF, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];
    success = setLEEventMask(transport, upperTester, events, trace);

    success = advertiser.enable() and success;
    initiator.checkPrematureDisconnect = False;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Check for LE Channel Selection Algorithm Event in upper Tester...
        """
        ok, handle, chSelAlgorithm = hasChannelSelectionAlgorithmEvent(transport, upperTester, trace);
        success = success and ok and (chSelAlgorithm == 1);

        transport.wait(2840);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/INI/BV-17-C [Connecting to Directed Advertiser with Channel Selection Algorithm #2]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing requirements cannot be verified - see Air trace)
"""
def ll_con_ini_bv_17_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED);
    """
       Enable the LE Channel Selection Algorithm Event
    """
    events = [0xFF, 0xFF, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];
    success = setLEEventMask(transport, upperTester, events, trace);

    success = advertiser.enable() and success;
    initiator.checkPrematureDisconnect = False;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Check for LE Channel Selection Algorithm Event in upper Tester...
        """
        ok, handle, chSelAlgorithm = hasChannelSelectionAlgorithmEvent(transport, upperTester, trace);
        success = success and ok and (chSelAlgorithm == 1);

        transport.wait(2840);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/INI/BV-18-C [Don't connect to Advertiser using Identity address with Network Privacy thru Resolving List]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_ini_bv_18_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, ExtendedAddressType.PUBLIC);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPA = ResolvableAddresses( transport, upperTester, trace, upperIRK );
    success = RPA.clear();
    success = RPA.add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPA.timeout( 60 ) and success;
    success = RPA.enable() and success;

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and not connected;

    if connected:
        success = initiator.disconnect(0x13) and success;
    else:
        success = initiator.cancelConnect();
        success = advertiser.disable() and success;

    success = RPA.disable() and success;

    return success;

"""
    LL/CON/INI/BV-19-C [Don't connect to Directed Advertiser using Identity address with Network Privacy thru Resolving List]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_ini_bv_19_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPA = ResolvableAddresses( transport, upperTester, trace );
    success = RPA.clear();
    success = RPA.add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPA.timeout( 60 ) and success;
    success = RPA.enable() and success;

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and not connected;

    if connected:
        success = initiator.disconnect(0x13) and success;
    else:
        success = initiator.cancelConnect();
        success = advertiser.disable() and success;

    success = RPA.disable() and success;

    return success;

"""
    LL/CON/INI/BV-20-C [Connect to Advertiser using Identity address with Device Privacy thru Resolving List]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_ini_bv_20_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;
    """
        Set Privacy Mode
    """
    success = setPrivacyMode(transport, upperTester, publicIdentityAddress(lowerTester), PrivacyMode.DEVICE_PRIVACY, trace) and success;

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(2660);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/CON/INI/BV-21-C [Connect to Directed Advertiser using Identity address with Device Privacy thru Resolving List]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_ini_bv_21_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPA = ResolvableAddresses( transport, upperTester, trace );
    success = RPA.clear();
    success = RPA.add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPA.timeout( 60 ) and success;
    success = RPA.enable() and success;
    """
        Set Privacy Mode
    """
    success = setPrivacyMode(transport, upperTester, publicIdentityAddress(lowerTester), PrivacyMode.DEVICE_PRIVACY, trace) and success;

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(2660);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPA.disable() and success;

    return success;

"""
    LL/CON/INI/BV-23-C [Network Privacy - Connection Establishment using whitelist and resolving list with address resolution disabled]

    Last modified: 17-12-2019
    Reviewed and verified: 17-12-2019 Henrik Eriksen
"""
def ll_con_ini_bv_23_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, ExtendedAddressType.PUBLIC,
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, AdvertisingFilterPolicy.FILTER_NONE,
                                                AdvertiseChannel.ALL_CHANNELS, InitiatorFilterPolicy.FILTER_WHITE_LIST_ONLY);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester) ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Add two more entries not equal to lower tester with different local IRK for each entry
    """
    extraAddressses = [ Address( SimpleAddressType.PUBLIC, address_scramble_OUI(toNumber(publicIdentityAddress(lowerTester).address)) ),
                        Address( SimpleAddressType.PUBLIC, address_scramble_LAP(toNumber(publicIdentityAddress(lowerTester).address)) ) ];
    RPAs[upperTester].localIRK = [ random.randint(0,255) for _ in range(16) ];
    success = RPAs[upperTester].add( extraAddressses[0] ) and success;
    RPAs[upperTester].localIRK = [ random.randint(0,255) for _ in range(16) ];
    success = RPAs[upperTester].add( extraAddressses[1] ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[lowerTester].enable() and success;
    """
        Add Lower tester identity address to plus two more to White List
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester), extraAddressses[0], extraAddressses[1] ], trace);

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(200);
        """
            Check that the InitA from the connect indication is a RPA
        """
        success = Address( None, initiator.localRPA() ).isResolvablePrivate() and success;
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/CON/INI/BV-24-C [Network Privacy - Connection Establishment using resolving list with address resolution disabled]

    Last modified: 17-12-2019
    Reviewed and verified: 17-12-2019 Henrik Eriksen
"""
def ll_con_ini_bv_24_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, ExtendedAddressType.PUBLIC);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPA = ResolvableAddresses( transport, upperTester, trace, upperIRK );
    success = RPA.clear();
    success = RPA.add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPA.timeout( 60 ) and success;
    success = RPA.disable() and success;

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and not connected;

    if connected:
        success = initiator.disconnect(0x13) and success;
    else:
        success = initiator.cancelConnect();
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-04-C [Connection where Slave sends data to Master]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_04_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, upperTester, trace);

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        txData = [0 for _ in range(10)];
        pbFlags = 1;
        """
            Sending Data Packets with a fixed length less than 27...
        """
        for count in [ 100, 100, 1, 99 ]:
            pbFlags ^= 1;
            for j in range(count):

                dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, lowerTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);

        if maxPacketLength > 27:
            """
                Sending Data Packets with a random length greater than 27...
            """
            pbFlags, count = 0, 0;

            while count < 1000:
                txData = [0 for _ in range(random.randint(28, maxPacketLength))];

                dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);

                count += len(txData);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-05-C [Connection where Slave receives data from Master]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_05_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        txData = [0 for _ in range(10)];
        pbFlags = 1;
        """
            Sending Data Packets with a fixed length less than 27...
        """
        for count in [ 100, 100, 1, 99 ]:
            pbFlags ^= 1;
            trace.trace(7, '-'*77);
            for j in range(count):
                dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
        trace.trace(7, '-'*77);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-06-C [Connection where Slave sends and receives data to and from Master]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_06_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        txData = [0 for _ in range(10)];
        pbFlags = 0;
        """
            Sending Data Packets with a fixed length less than 27...
        """
        for j in range(100):
            """
                Upper Tester is sending Data...
            """
            pbFlags ^= 1;
            trace.trace(7, '-'*77);
            dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readData(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
            """
                Lower Tester is sending Data...
            """
            pbFlags ^= 1;
            dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readData(transport, upperTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
        trace.trace(7, '-'*77);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-10-C [Slave accepting Connection Parameter Update from Master]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing cannot be verified - see Air trace)
"""
def ll_con_sla_bv_10_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(100);

        for interval, timeout in zip([ 6, 3200, 6 ], [ 300, 3200, 300 ]):
            """
                Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            """
            success = initiator.update(interval, interval, initiator.latency, timeout) and success;
            """
                Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
            """
            success = initiator.acceptUpdate() and success;
            """
                Both lower and upper Tester should receive a LE Connection Update Complete Event...
            """
            success = initiator.updated() and success;

            transport.wait(int(4 * interval * 1.25));

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-11-C [Slave sending Termination to Master]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing cannot be verified - see Air trace)
"""
def ll_con_sla_bv_11_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and (initiator.reasons[0] == 0x16) and (initiator.reasons[1] == 0x13) and success;
        initiator.resetRoles();
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-12-C [Slave accepting Termination from Master]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing cannot be verified - see Air trace)
"""
def ll_con_sla_bv_12_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        success = initiator.disconnect(0x13) and (initiator.reasons[0] == 0x16) and (initiator.reasons[1] == 0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-13-C [Slave Terminating Connection on Supervision Timer]
"""
def ll_con_sla_bv_13_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    initiator.supervisionTimer = 3200;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(3200);
        hasEvent = has_event(transport, upperTester, 3200)[0];
        success = success and hasEvent;
        if hasEvent:
            event = get_event(transport, upperTester, 100);
            trace.trace(7, str(event));
        else:
            success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-14-C [Slave performs Feature Setup procedure]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_14_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Send LL_FEATURE_REQ to IUT
        """
        success = readRemoteFeatures(transport, lowerTester, initiator.handles[0], trace) and success;
        """
            Verify if lower tester received LE Read Remote Features Complete Event
        """
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, lowerTester, trace);
        success = hasFeatures and success;
        if hasFeatures:
            showFeatures(features, trace);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-19-C [Slave requests Version Exchange procedure]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_19_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        success = readRemoteVersionInformation(transport, upperTester, initiator.handles[1], trace) and success;

        hasVersion, handle, version, manufacturer, subVersion = hasReadRemoteVersionInformationCompleteEvent(transport, upperTester, trace);
        success = success and hasVersion;
        if hasVersion:
            trace.trace(8, "     version: 0x%02x" % version);
            trace.trace(8, " sub-version: 0x%04x" % subVersion);
            trace.trace(8, "manufacturer: 0x%04x" % manufacturer);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-20-C [Slave responds to Version Exchange procedure]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_20_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        success = readRemoteVersionInformation(transport, lowerTester, initiator.handles[0], trace) and success;

        hasVersion, handle, version, manufacturer, subVersion = hasReadRemoteVersionInformationCompleteEvent(transport, lowerTester, trace);
        success = success and hasVersion;
        if hasVersion:
            trace.trace(8, "     version: 0x%02x" % version);
            trace.trace(8, " sub-version: 0x%04x" % subVersion);
            trace.trace(8, "manufacturer: 0x%04x" % manufacturer);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-22-C [Slave requests Feature Exchange procedure]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_22_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Upper Tester sends an HCI_LE_Read_Local_Supported_Features command...
        """
        success = readLocalFeatures(transport, upperTester, trace)[0] and success;
        """
            Upper Tester sends an HCI_LE_Read_Remote_Features command...
        """
        success = readRemoteFeatures(transport, upperTester, initiator.handles[0], trace) and success;
        """
            Upper tester expects LE Read Remote Features Complete event...
        """
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, upperTester, trace);
        success = hasFeatures and success;
        if hasFeatures:
            showFeatures(features, trace);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-24-C [Slave requests Connection Parameters - Master Accepts]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing not verified - see Air trace)
"""
def ll_con_sla_bv_24_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        initiator.switchRoles();
        """
            The test consists of 3 cases for specific connection intervals and supervision timeouts
        """
        for interval, timeout in zip([ 6, 3200, 6 ], [ 300, 3200, 300 ]):
            """
                Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            """
            success = initiator.update(interval, interval, initiator.latency, timeout) and success;
            """
                Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
            """
            success = initiator.acceptUpdate() and success;
            """
                Both lower and upper Tester should receive a LE Connection Update Complete Event...
            """
            success = initiator.updated() and success;

            transport.wait(int(4 * interval * 1.25));

        initiator.resetRoles();
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-25-C [Slave requests Connection Parameters - Master Rejects]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing not verified - see Air trace)
"""
def ll_con_sla_bv_25_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        initiator.switchRoles();

        interval, timeout = 6, 300;
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECTEXT_IND...
        """
        success = initiator.rejectUpdate(0x0C) and success;
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event... if request was accepted
        """
        success = not initiator.updated() and initiator.status == 0x0C and success;

        transport.wait(int(4 * interval * 1.25));

        initiator.resetRoles();
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-26-C [Slave requests Connection Parameters - same procedure collision]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing not verified - see Air trace)
"""
def ll_con_sla_bv_26_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        initiator.switchRoles();

        interval, timeout, errCode = 6, 300, 0x23;
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECTEXT_IND...
            NOTE: Not according to test specification, LL_CONNECTION_PARAM_REQ should be issued prior to LL_REJECTEXT_IND,
                  but Zephyr is preventing us from sending the the LL_CONNECTION_PARAM_REQ first, returning COMMAND DISALLOWED
        """
        success = initiator.rejectUpdate(errCode) and success;

        initiator.resetRoles();
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        updInitiatorRequest = initiator.update(interval, interval, initiator.latency, timeout);
        updPeerRequest = initiator.updPeerRequest;
        success = success and updInitiatorRequest and updPeerRequest;

        initiator.switchRoles();
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event... if request was accepted
        """
        updated = initiator.updated();
        success = success and not updated and (initiator.status == errCode);

        initiator.resetRoles();
        """
            Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
        """
        initiator.updInitiatorRequest, initiator.updPeerRequest = updInitiatorRequest, updPeerRequest;
        success = initiator.acceptUpdate() and success;
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event...
        """
        success = initiator.updated() and success;

        transport.wait(int(4 * interval * 1.25));

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-27-C [Slave requests Connection Parameters - channel map update procedure collision]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing not verified - see Air trace)
"""
def ll_con_sla_bv_27_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        initiator.switchRoles();

        interval, timeout, errCode, channelMap = 6, 300, 0x2A, 0x1555555555;
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Request an update of used channels - sends an LL_CHANNEL_MAP_IND...
        """
        success = channelMapUpdate(transport, lowerTester, channelMap, trace) and success;
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECTEXT_IND...
        """
        success = initiator.rejectUpdate(errCode) and success;
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event... if request was accepted
        """
        success = not initiator.updated() and (initiator.status == errCode) and success;

        initiator.resetRoles();

        transport.wait(int(4 * interval * 1.25));

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-29-C [Slave responds to Connection Parameters - Master no Preferred Periodicity]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen (NOTE: Timing not verified - see Air trace)
"""
def ll_con_sla_bv_29_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        for interval, timeout in zip([6, 3200, 6], [300, 3200, 200]):
            """
                Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            """
            success = initiator.update(interval, interval, initiator.latency, timeout) and success;
            """
                Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
            """
            success = initiator.acceptUpdate() and success;
            """
                Both lower and upper Tester should receive a LE Connection Update Complete Event... if request was accepted
            """
            success = initiator.updated() and success;

            transport.wait(int(4 * interval * 1.25));

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-33-C [Slave responds to Connection Parameters request - event masked]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_33_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
    """
        Mask LE Remote Connection Parameter Request Event
    """
    events = [0x1F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    success = setLEEventMask(transport, upperTester, events, trace) and success;

    if connected:
        interval, timeout, errCode = 6, 300, 0x1A;
        """
            Send LL_CONNECTION_PARAM_REQ to IUT...
        """
        success = initiator.update(interval, interval, initiator.latency, timeout) and not initiator.updPeerRequest and success;
        """
            Verify that lower tester receives a LL_REJECT_EXT_IND... unfortunately we cannot verify that (but it appears in the Air trace)!
        """
        success = initiator.updated() and success;

        transport.wait(int(4 * interval * 1.25))

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-34-C [Slave responds to Connection Parameters request - Host rejects]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_34_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        interval, timeout, errCode = 6, 300, 0x3B;
        """
            Send LL_CONNECTION_PARAM_REQ to IUT...
        """
        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECT_EXT_IND...
        """
        success = initiator.rejectUpdate(errCode) and success;
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event... if request was accepted
        """
        success = not initiator.updated() and (initiator.status == errCode) and success;

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-40-C [Slave requests PHY Update procedure]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_40_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    columns = defaultdict(list); # each value in each column is appended to a list

    with open('src/tests/params_con_sla_bv_40.csv') as f:
        reader = csv.reader(f);
        next(reader);
        for row in reader:
            for (i,v) in enumerate(row):
                columns[i].append(int(v, 16));

    all_phys, tx_phys, rx_phys = columns[1], columns[2], columns[3];

    if connected:
        initiator.switchRoles();

        for i in range(0, len(columns[0])):
            if (tx_phys[i] == 0) or (tx_phys[i] > 3) or (rx_phys[i] == 0) or (rx_phys[i] > 3):
                continue

            trace.trace(7, "Execute PHY Update with the following parameters:\tALL_PHYS: %s\tTX: %s\tRX: %s" % (str(all_phys[i]), str(tx_phys[i]), str(rx_phys[i])));

            success = initiator.updatePhys(all_phys[i], tx_phys[i], rx_phys[i], 0) and success;

            trace.trace(4, "Updated PHYs:\tTX: %s\tRX: %s\n" % (str(initiator.txPhys), str(initiator.rxPhys)))

        transport.wait(int(4 * initiator.intervalMin * 1.25))

        initiator.resetRoles()

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-42-C [Slave responds to PHY Update procedure]

    Last modified: 05-08-2019
    Reviewed and verified: 05-08-2019 Henrik Eriksen
"""
def ll_con_sla_bv_42_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        initiator.switchRoles();

        success = initiator.updatePhys( 3, 0, 0, 0 ) and success;

        initiator.resetRoles();

        tabel = list(zip( [2, 1, 2, 1, 3, 3, 1, 2, 3], [2, 2, 1, 1, 2, 1, 3, 3, 3], [2, 1, 2, 1, 2, 2, 1, 2, 2], [2, 2, 1, 1, 2, 1, 2, 2, 2] ));

        for i in range(2):
            for txPhys, rxPhys, expTxPhys, expRxPhys in tabel:
                success = initiator.updatePhys(0, txPhys, rxPhys, 0) and success;
                success = success and (initiator.txPhys == expTxPhys) and (initiator.rxPhys == expRxPhys);
            random.shuffle(tabel)

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-77-C [Slave Packet Data Length Update - Responding to Packet Data Length Update Procedure; LE 1M PHY]

    Last modified: 09-08-2019
    Reviewed and verified: 09-08-2019 Henrik Eriksen (Note: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.)
"""
def ll_con_sla_bv_77_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);
    maxPacketTime, cmaxTxOctets, cmaxTxTime = calcMaxPacketTime(maxPacketLength), 27, 328;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Feature exchange as specified in LL.TS.5.1.1, chapter 4.1.5
        """
        success = readRemoteFeatures(transport, lowerTester, initiator.handles[0], trace) and success;
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, lowerTester, trace);
        showLEFeatures(features, trace);

        """
            Exchange data...
        """
        lenValues  = list(range(28, maxPacketLength-1)) + list(range(maxPacketLength+1, 250));
        timeValues = list(range(329, maxPacketTime-1)) + list(range(maxPacketTime+1, 2119));

        for txOctets, txTime in zip( [ 27, 251, maxPacketLength, 27, 27, 27, 251, 251, 251, maxPacketLength, maxPacketLength, maxPacketLength, \
                                       random.choice(lenValues), random.choice(lenValues), random.choice(lenValues), random.choice(lenValues) ], \
                                     [ 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, \
                                       random.choice(timeValues), random.choice(timeValues), random.choice(timeValues), random.choice(timeValues) ] ):

            success = setDataLength(transport, upperTester, initiator.handles[1], txOctets, txTime, trace) and success;
            requested = success;
            success = success or (not success and ((txOctets > maxPacketLength) or (txTime > maxPacketTime)));

            changed = not ((cmaxTxOctets == min(txOctets, maxPacketLength)) and ((cmaxTxTime == max(txTime, 328)) or (cmaxTxTime == min(txTime, 328))));

            if requested and changed:
                gotEvent, handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = hasDataLengthChangedEvent(transport, upperTester, trace);
                success = success and gotEvent;
                gotEvent = hasDataLengthChangedEvent(transport, lowerTester, trace)[0];
                success = success and gotEvent;

            pbFlags = 0;
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)];
            dataSent = writeData(transport, lowerTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readDataFragments(transport, upperTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
            """
                Lower Tester is sending Data...
            """
            txData = [_ for _ in range(27)];
            for i in range(20):
                dataSent = writeData(transport, upperTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, lowerTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-78-C [Slave requests Packet Data Length Update procedure; LE 1M PHY]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.)
"""
def ll_con_sla_bv_78_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);
    cmaxTxOctets, cmaxTxTime, maxPacketTime = 27, 328, int(2120 * maxPacketLength / 251);

    trace.trace(8, "Max supported packet length: %d octets. Max supported transmit time: %d micro seconds" % (maxPacketLength, maxPacketTime));

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Feature exchange as specified in LL.TS.5.1.1, chapter 4.1.5
        """
        success = readRemoteFeatures(transport, lowerTester, initiator.handles[0], trace) and success;
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, lowerTester, trace);
        showLEFeatures(features, trace);

        for txOctets, txTime in zip([ maxPacketLength, 27, 251, maxPacketLength, 27, 251, maxPacketLength, 27, 251, maxPacketLength, 27, 251 ], \
                                    [ maxPacketTime, maxPacketTime, maxPacketTime, 328, 328, 328, 2120, 2120, 2120, 2120, 2120, 2120 ]):

            success = setDataLength(transport, upperTester, initiator.handles[1], txOctets, txTime, trace) and success;
            requested = success;
            success = success or (not success and ((txOctets > maxPacketLength) or (txTime > maxPacketTime)));

            changed = not ((cmaxTxOctets == min(txOctets, maxPacketLength)) and ((cmaxTxTime == max(txTime, 328)) or (cmaxTxTime == min(txTime, 328))));

            if requested and changed:
                gotEvent, handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = hasDataLengthChangedEvent(transport, upperTester, trace);
                if not gotEvent:
                    trace.trace(7, "Missing Data Length Changed event from upperTester!");
                success = success and gotEvent;
                gotEvent = hasDataLengthChangedEvent(transport, lowerTester, trace)[0];
                if not gotEvent:
                    trace.trace(7, "Missing Data Length Changed event from lowerTester!");
                success = success and gotEvent;

            pbFlags = 0;
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)];
            dataSent = writeData(transport, upperTester, initiator.handles[1], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData));
            """
                Lower Tester is sending Data...
            """
            txData = [_ for _ in range(27)];
            for i in range(20):
                dataSent = writeData(transport, lowerTester, initiator.handles[0], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData));
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-80-C [Slave Packet Data Length Update - Responding to Packet Data Length Update Procedure; LE 2M PHY]

    Last modified: 09-08-2019
    Reviewed and verified: 09-08-2019 Henrik Eriksen (Note: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.)
"""
def ll_con_sla_bv_80_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);
    maxPacketTime, cmaxTxOctets, cmaxTxTime = calcMaxPacketTime(maxPacketLength), 27, 328;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Feature exchange as specified in LL.TS.5.1.1, chapter 4.1.5
        """
        success = readRemoteFeatures(transport, lowerTester, initiator.handles[0], trace) and success;
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, lowerTester, trace);
        showLEFeatures(features, trace);

        """
            Switch to LE 2M PHY channel...
        """
        allPhys, txPhys, rxPhys, optionPhys = 0, 2, 2, 0;

        success = initiator.updatePhys(allPhys, txPhys, rxPhys, optionPhys) and success;
        success = (initiator.txPhys == txPhys) and (initiator.rxPhys == rxPhys) and success
        """
            Exchange data...
        """
        lenValues  = list(range(28, maxPacketLength-1)) + list(range(maxPacketLength+1, 250));
        timeValues = list(range(329, maxPacketTime-1)) + list(range(maxPacketTime+1, 2119));

        for txOctets, txTime in zip( [ 27, 251, maxPacketLength, 27, 27, 27, 251, 251, 251, maxPacketLength, maxPacketLength, maxPacketLength, \
                                       random.choice(lenValues), random.choice(lenValues), random.choice(lenValues), random.choice(lenValues) ], \
                                     [ 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, \
                                       random.choice(timeValues), random.choice(timeValues), random.choice(timeValues), random.choice(timeValues) ] ):

            success = setDataLength(transport, upperTester, initiator.handles[1], txOctets, txTime, trace) and success;
            requested = success;
            success = success or (not success and ((txOctets > maxPacketLength) or (txTime > maxPacketTime)));

            changed = not ((cmaxTxOctets == min(txOctets, maxPacketLength)) and ((cmaxTxTime == max(txTime, 328)) or (cmaxTxTime == min(txTime, 328))));

            if requested and changed:
                gotEvent, handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = hasDataLengthChangedEvent(transport, upperTester, trace);
                success = success and gotEvent;
                gotEvent = hasDataLengthChangedEvent(transport, lowerTester, trace)[0];
                success = success and gotEvent;

            pbFlags = 0;
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)];
            dataSent = writeData(transport, lowerTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readDataFragments(transport, upperTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
            """
                Lower Tester is sending Data...
            """
            txData = [_ for _ in range(27)];
            for i in range(20):
                dataSent = writeData(transport, upperTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, lowerTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BV-81-C [Slave requests Packet Data Length Update procedure; LE 2M PHY]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.)
"""
def ll_con_sla_bv_81_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);
    cmaxTxOctets, cmaxTxTime, maxPacketTime = 27, 328, int(2120 * maxPacketLength / 251);

    trace.trace(8, "Max supported packet length: %d octets. Max supported transmit time: %d micro seconds" % (maxPacketLength, maxPacketTime));

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Feature exchange as specified in LL.TS.5.1.1, chapter 4.1.5
        """
        success = readRemoteFeatures(transport, lowerTester, initiator.handles[0], trace) and success;
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, lowerTester, trace);
        showLEFeatures(features, trace);

        initiator.switchRoles();
        """
            Switch to the 2M PHY channel
        """
        txPhys, rxPhys, allPhys, optionPhys = 2, 2, 0, 0;
        success = initiator.updatePhys(allPhys, txPhys, rxPhys, optionPhys) and success;
        success = success and (initiator.txPhys == txPhys) and (initiator.rxPhys == rxPhys);

        initiator.resetRoles();

        for txOctets, txTime in zip([ maxPacketLength, 27, 251, maxPacketLength, 27, 251, maxPacketLength, 27, 251, maxPacketLength, 27, 251 ], \
                                    [ maxPacketTime, maxPacketTime, maxPacketTime, 328, 328, 328, 2120, 2120, 2120, 2120, 2120, 2120 ]):

            success = setDataLength(transport, upperTester, initiator.handles[1], txOctets, txTime, trace) and success;
            requested = success;
            success = success or (not success and ((txOctets > maxPacketLength) or (txTime > maxPacketTime)));

            changed = not ((cmaxTxOctets == min(txOctets, maxPacketLength)) and ((cmaxTxTime == max(txTime, 328)) or (cmaxTxTime == min(txTime, 328))));

            if requested and changed:
                gotEvent, handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = hasDataLengthChangedEvent(transport, upperTester, trace);
                success = success and gotEvent;
                gotEvent = hasDataLengthChangedEvent(transport, lowerTester, trace)[0];
                success = success and gotEvent;

            pbFlags = 0;
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)];
            dataSent = writeData(transport, upperTester, initiator.handles[1], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData));
            """
                Lower Tester is sending Data...
            """
            txData = [_ for _ in range(27)];
            for i in range(20):
                dataSent = writeData(transport, lowerTester, initiator.handles[0], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData));
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/SLA/BI-08-C [Slave responds to Connection Parameters request - Illegal Parameters]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_sla_bi_08_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        interval, errCode = 4, 0x1E;
        """
            Send LL_CONNECTION_PARAM_REQ to IUT...
        """
        success = initiator.update(interval, interval, initiator.latency, 300) and success;
        """
            Verify that lower tester receives a CONNECTION UPDATE COMPLETE Event...
        """
        success = not initiator.updated() and (initiator.status == errCode) and success;

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-03-C [Master sending Data packets to Slave]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_03_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
       Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        txData = [0 for _ in range(10)];
        pbFlags = 1;
        """
            Sending Data Packets with a fixed length less than 27...
        """
        for count in [ 100, 100, 1, 99 ]:
            pbFlags ^= 1;
            for j in range(count):
                dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, lowerTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);

        if maxPacketLength > 27:
            """
                Sending Data Packets with a random length greater than 27...
            """
            pbFlags, count = 0, 0;

            while count < 1000:
                txData = [0 for _ in range(random.randint(28, maxPacketLength))];

                dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
                success = success and dataSent;
                count += len(txData);
                if dataSent:
                    dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
                else:
                    break;

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-04-C [Master receiving Data packets from Slave]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_04_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        txData = [0 for _ in range(10)];
        pbFlags = 1;
        """
            Sending Data Packets with a fixed length less than 27...
        """
        for count in [ 100, 100, 1, 99 ]:
            pbFlags ^= 1;
            trace.trace(7, '-'*77);
            for j in range(count):
                dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
        trace.trace(7, '-'*77);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-05-C [Master sending and receiving Data packets to and form Slave]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_05_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        pbFlags = 0;
        """
            Sending Data Packets with a fixed length less than 27...
        """
        for j in range(100):
            """
                Upper Tester is sending Data...
            """
            trace.trace(7, '-'*77);
            txData = [0x00 for _ in range(10)];
            dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readData(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
            """
                Lower Tester is sending Data...
            """
            txData = [0xFF for _ in range(10)];
            dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readData(transport, upperTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);

            if j == 0:
                pbFlags = 1;
        trace.trace(7, '-'*77);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-07-C [Master requests Connection Parameter Update]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: connection event where change take place cannot be verified - see Air trace)
"""
def ll_con_mas_bv_07_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        interval, timeout = 64, 3200;
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
        """
        success = initiator.acceptUpdate() and success;
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event...
        """
        success = initiator.updated() and success;
        """
            Wait for change to take place...
        """
        transport.wait(int(4 * interval * 1.25));

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success

"""
    LL/CON/MAS/BV-08-C [Master Terminating Connection]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Not verified that IUT stops sending empty data packets - see Air trace)
"""
def ll_con_mas_bv_08_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        success = initiator.disconnect(0x13) and (initiator.reasons[0] == 0x16) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-09-C [Master accepting Connection Termination]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Not verified that IUT stops sending empty data packets - see Air trace)
"""
def ll_con_mas_bv_09_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and (initiator.reasons[1] == 0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-13-C [Master requests Feature Setup procedure]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_13_c(transport, upperTester, lowerTester, trace):

    LL_FEAT_BIT_MASK_VALID = 0x1CF2F # Bitmask for features not impacting feature masking (ll_feat.h)

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Read local features from lower- and upperTester to establish expected remote read
            result
        """
        hasFeatures, expectedFeatures = readLocalFeatures(transport, lowerTester, trace)
        hasFeatures, upperFeatures    = readLocalFeatures(transport, upperTester, trace)
        upperLocalFeatures = toNumber(upperFeatures)
        """
            Keep octets 1-7, and do the logical and on octet 0; also ignore the non-valid bits
            See BT Core spec V5.2, Vol 6. Part B chapter 4.6
        """
        expectedMaskedFeatures = toNumber([upperFeatures[0] & expectedFeatures[0]] + list(expectedFeatures[1:7]))
        expectedMaskedFeatures = expectedMaskedFeatures & LL_FEAT_BIT_MASK_VALID
        """
            Issue the LE Read Remote Features Command, verify the reception of a Command Status Event
        """
        success = readRemoteFeatures(transport, upperTester, initiator.handles[0], trace) and success;
        """
            Await the reception of a LE Read Remote Features Command Complete Event
        """
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, upperTester, trace);
        success = success and hasFeatures;
        if hasFeatures:
            showLEFeatures(features, trace)
            receivedMaskedFeatures = toNumber(features) & LL_FEAT_BIT_MASK_VALID
            success = (receivedMaskedFeatures == expectedMaskedFeatures) and success

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-20-C [Master requests Version Exchange procedure]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_20_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Issue the Read Remote Version Information Command, verify the reception of a Command Status Event
        """
        success = readRemoteVersionInformation(transport, upperTester, initiator.handles[0], trace) and success;
        """
            Await the reception of a Read Remote Version Information Complete Event
        """
        hasVersion, handle, version, manufacturer, subVersion = hasReadRemoteVersionInformationCompleteEvent(transport, upperTester, trace);
        success = success and hasVersion;
        if hasVersion:
            trace.trace(8, "     version: 0x%02x" % version);
            trace.trace(8, " sub-version: 0x%04x" % subVersion);
            trace.trace(8, "manufacturer: 0x%04x" % manufacturer);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-21-C [Master responds to Version Exchange procedure]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_21_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Issue the Read Remote Version Information Command, verify the reception of a Command Status Event
        """
        success = readRemoteVersionInformation(transport, lowerTester, initiator.handles[1], trace) and success;
        """
            Await the reception of a Read Remote Version Information Complete Event
        """
        hasVersion, handle, version, manufacturer, subVersion = hasReadRemoteVersionInformationCompleteEvent(transport, lowerTester, trace);
        success = success and hasVersion;
        if hasVersion:
            trace.trace(8, "     version: 0x%02x" % version);
            trace.trace(8, " sub-version: 0x%04x" % subVersion);
            trace.trace(8, "manufacturer: 0x%04x" % manufacturer);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-23-C [Master responds to Feature Exchange procedure]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_23_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Issue the LE Read Remote Features Command, verify the reception of a Command Status Event
        """
        success = success and readRemoteFeatures(transport, lowerTester, initiator.handles[1], trace);
        """
            Await the reception of a LE Read Remote Features Command Complete Event
        """
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, lowerTester, trace);
        success = success and hasFeatures;
        if hasFeatures:
            showLEFeatures(features, trace);
            # Bit 27 is "Masked to Peer" an must be cleared
            success = ((toNumber(features) & (1 << 27)) == 0) and success;

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-24-C [Master requests Connection Parameters - Slave Accepts]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Actual effect of change cannot be verified - see Air trace)
"""
def ll_con_mas_bv_24_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        for interval, timeout in zip([ 6, 3200, 6 ], [ 300, 3200, 300 ]):
            """
                Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            """
            success = initiator.update(interval, interval, initiator.latency, timeout) and success;
            """
                Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
            """
            success = initiator.acceptUpdate() and success;
            """
                Both lower and upper Tester should receive a LE Connection Update Complete Event...
            """
            success = initiator.updated() and success;
            """
                Wait for change to take place...
            """
            transport.wait(int(4 * interval * 1.25));

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-25-C [Master requests Connection Parameters - Slave Rejects]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Actual effect of change cannot be verified - see Air trace)
"""
def ll_con_mas_bv_25_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        interval, timeout = 6, 300;
        for reject in [ True, False ]:
            """
                Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            """
            success = initiator.update(interval, interval, initiator.latency, timeout) and success;
            """
                Accept or Reject the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP or a LL_REJECT_EXT_IND...
            """
            success = (initiator.rejectUpdate(0x3B) if reject else initiator.acceptUpdate()) and success;
            """
                Both lower and upper Tester should receive a LE Connection Update Complete Event... if request was accepted
            """
            if reject:
                success = not initiator.updated() and (initiator.status == 0x3B) and success;
            else:
                success = initiator.updated() and success;
            """
                Wait for optional change to take place...
            """
            transport.wait(int(4 * interval * 1.25));

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-26-C [Master requests Connection Parameters - same procedure collision]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Test not according to specs - not possible!)
"""
def ll_con_mas_bv_26_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        interval, timeout = 6, 300;
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        updRequested = initiator.update(interval, interval, initiator.latency, timeout);
        success = success and updRequested;
        """
            Verify that the lower tester receives a LE Remote Connection Parameter Request Event...
        """
        updPeerInvolved = initiator.updPeerRequest;
        success = success and updPeerInvolved;
        """
            Send a LL_CONNECTION_PARAM_REQ as a reaction to the LE Remote Connection Parameter Request Event...
            NOTE: We use a little nasty trick here. Swap the roles of initiator and peer and swap assigned handles...
        """
        initiator.switchRoles();
        """
            Update request will be rejected with an error code 0x0C - command disallowed...
        """
        success = success and not initiator.update(interval, interval, initiator.latency, timeout) and initiator.status == 0x0C;
        """
            Get back to original roles of initiator and peer...
        """
        initiator.resetRoles();
        """
            Send a LL_CONNECTION_PARAM_RSP as a reaction to the original LE Remote Connection Parameter Request Event...
        """
        initiator.updInitiatorRequest, initiator.updPeerRequest = updRequested, updPeerInvolved;
        success = success and initiator.acceptUpdate();
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event...
        """
        success = success and initiator.updated();
        """
            Wait for change to take place...
        """
        transport.wait(int(4 * interval * 1.25));

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-27-C [Master requests Connection Parameters - Channel Map Update procedure collision]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Switch to only even channels cannot be verified - see Air trace)
"""
def ll_con_mas_bv_27_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        interval, timeout = 6, 300;
        """
            Use only even channels...
        """
        success = channelMapUpdate(transport, upperTester, 0x1555555555, trace) and success;
        """
            Lower tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            NOTE: We use a little nasty trick here. Swap the roles of initiator and peer and swap assigned handles...
        """
        initiator.switchRoles();
        transport.wait(20); # FIXME: Avoid test failure due to Zephyr controller occasionally generating Different Transaction Collision
        """
            Lower tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECT_EXT_IND...
        """
        success = initiator.rejectUpdate(0x2A) and success;
        """
            Verify that the update was rejected with error code 0x2A
        """
        success = not initiator.updated() and (initiator.status == 0x2A) and success;
        """
            Get back to original roles of initiator and peer...
        """
        initiator.resetRoles();
        initiator.pre_updated = True;
        interval = 24;
        """
            Wait for change to take place...
        """
        transport.wait(int(8 * interval * 1.25));

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-29-C [Master requests Connection Parameters - Slave unsupported]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Change to connection interval cannot be verified - see Air trace)
"""
def ll_con_mas_bv_29_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        interval, timeout = 6, 300;
        """
            Upper tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECT_EXT_IND... (update will take place)
        """
        success = initiator.rejectUpdate(0x1A) and success;
        """
            Verify that the update was accepted
        """
        success = initiator.updated() and success;
        """
            Wait for change to take place...
        """
        transport.wait(int(8 * interval * 1.25));

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-30-C [Master responds to Connection Parameters request - no Preferred_Periodicity]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (NOTE: Change to connection interval cannot be verified - see Air trace)
"""
def ll_con_mas_bv_30_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        for interval, timeout in zip([ 6, 3200, 6 ], [ 300, 3200, 300 ]):
            """
                Lower tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
                NOTE: We use a little nasty trick here. Swap the roles of initiator and peer and swap assigned handles...
            """
            initiator.switchRoles();

            success = initiator.update(interval, interval, initiator.latency, timeout) and success;
            """
                Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
            """
            success = initiator.acceptUpdate() and success;
            """
                Both lower and upper Tester should receive a LE Connection Update Complete Event...
            """
            success = initiator.updated() and success;
            """
                Wait for change to take place...
            """
            transport.wait(int(4 * interval * 1.25));

            initiator.resetRoles();

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-34-C [Master responds to Connection Parameters request - event masked]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_34_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
    """
        Disable the LE Remote Connection Parameter Request event (Bit 5)
    """
    events = [0xDF, 0xFF, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];
    success = setLEEventMask(transport, upperTester, events, trace) and success;

    if connected:
        interval, timeout = 6, 300;
        """
            Lower tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            NOTE: We use a little nasty trick here. Swap the roles of initiator and peer and swap assigned handles...
        """
        initiator.switchRoles();

        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Update request should be rejected with a LL_REJECT_EXT_IND...
        """
        success = not initiator.updated() and (initiator.status == 0x1A) and success;

        initiator.resetRoles();

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-35-C [Master responds to Connection Parameters request - Host rejects]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_35_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        interval, timeout = 6, 300;
        """
            Lower tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            NOTE: We use a little nasty trick here. Swap the roles of initiator and peer and swap assigned handles...
        """
        initiator.switchRoles();

        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECT_EXT_IND...
        """
        success = initiator.rejectUpdate(0x3B) and success;
        """
            Verify that the update was rejected...
        """
        success = not initiator.updated() and success;

        initiator.resetRoles();

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-41-C [Master requests PHY Update procedure]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_41_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        optionPhys = 0;

        table = list(zip( [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3], \
                     [2, 1, 2, 1, 3, 3, 1, 2, 3, 0, 2, 0], \
                     [2, 2, 1, 1, 2, 1, 3, 3, 3, 2, 0, 0], \
                     [2, 1, 2, 1, 2, 2, 1, 2, 2, 2, 2, 2], \
                     [2, 2, 1, 1, 2, 1, 2, 2, 2, 2, 2, 2] ));

        for i in range(2):
            for allPhys, txPhys, rxPhys, expTxPhys, expRxPhys in table:
                success = initiator.updatePhys(allPhys, txPhys, rxPhys, optionPhys) and success;
                success = success and (initiator.txPhys == expTxPhys) and (initiator.rxPhys == expRxPhys);
            random.shuffle(table);

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-43-C [Master responds to PHY Update procedure]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bv_43_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        allPhys, optionPhys, expTxPhys, expRxPhys = 3, 0, 2, 2;

        success = initiator.updatePhys(allPhys, 1, 1, optionPhys) and success;
        success = success and (initiator.txPhys == expTxPhys) and (initiator.rxPhys == expRxPhys);

        table = list(zip( [2, 1, 2, 1, 3, 3, 1, 2, 3], \
                     [2, 2, 1, 1, 2, 1, 3, 3, 3], \
                     [2, 1, 2, 1, 2, 2, 1, 2, 2], \
                     [2, 2, 1, 1, 2, 1, 2, 2, 2] ));
        allPhys = 0;

        initiator.switchRoles();

        for i in range(2):
            for txPhys, rxPhys, expTxPhys, expRxPhys in table:
                success = initiator.updatePhys(allPhys, txPhys, rxPhys, optionPhys) and success;
                success = success and (initiator.txPhys == expTxPhys) and (initiator.rxPhys == expRxPhys);
            random.shuffle(table);

        initiator.resetRoles();

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-73-C [Master Packet Data Length Update - Responding to Packet Data Length Update Procedure; LE 1M PHY]

    Last modified: 08-08-2019
    Reviewed and verified: 08-08-2019 Henrik Eriksen (Note: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.)
"""
def ll_con_mas_bv_73_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);
    maxPacketTime, cmaxTxOctets, cmaxTxTime = calcMaxPacketTime(maxPacketLength), 27, 328;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Feature exchange as specified in LL.TS.5.1.1, chapter 4.1.5
        """
        success = readRemoteFeatures(transport, upperTester, initiator.handles[0], trace) and success;
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, upperTester, trace);
        showLEFeatures(features, trace);

        """
            Exchange data...
        """
        lenValues  = list(range(28, maxPacketLength-1)) + list(range(maxPacketLength+1, 250));
        timeValues = list(range(329, maxPacketTime-1)) + list(range(maxPacketTime+1, 2119));

        for txOctets, txTime in zip( [ 27, 251, maxPacketLength, 27, 27, 27, 251, 251, 251, maxPacketLength, maxPacketLength, maxPacketLength, \
                                       random.choice(lenValues), random.choice(lenValues), random.choice(lenValues), random.choice(lenValues) ], \
                                     [ 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, \
                                       random.choice(timeValues), random.choice(timeValues), random.choice(timeValues), random.choice(timeValues) ] ):

            success = setDataLength(transport, lowerTester, initiator.handles[1], txOctets, txTime, trace) and success;
            trace.trace(6, "Setting TX Data Length %d and TX Data Time %d" % (txOctets, txTime));
            changed = not ((cmaxTxOctets == min(txOctets, maxPacketLength)) and ((cmaxTxTime == max(txTime, 328)) or (cmaxTxTime == min(txTime, 328))));

            if changed:
                gotEvent, handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = hasDataLengthChangedEvent(transport, lowerTester, trace);
                success = success and gotEvent;
                if not gotEvent:
                    trace.trace(6, "Error: Missed Data Length Changed Event from lowerTester");
                gotEvent = hasDataLengthChangedEvent(transport, upperTester, trace)[0];
                success = success and gotEvent;
                if not gotEvent:
                    trace.trace(6, "Error: Missed Data Length Changed Event from upperTester");

            pbFlags = 0;
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)];
            dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
            """
                Lower Tester is sending Data...
            """
            txData = [_ for _ in range(27)];
            for i in range(20):
                dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-74-C [Master Packet Data Length Update - Initiating Packet Data Length Update Procedure; LE 1M PHY]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (Note: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.)
"""
def ll_con_mas_bv_74_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);
    maxPacketTime, cmaxTxOctets, cmaxTxTime = calcMaxPacketTime(maxPacketLength), 27, 328;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Feature exchange as specified in LL.TS.5.1.1, chapter 4.1.5
        """
        success = readRemoteFeatures(transport, upperTester, initiator.handles[0], trace) and success;
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, upperTester, trace);
        showLEFeatures(features, trace);

        for txOctets, txTime in zip( [ maxPacketLength, 27, 251, maxPacketLength, 27, 251, maxPacketLength, 27, 251, 60, 27, 251 ], \
                                     [ maxPacketTime, maxPacketTime, maxPacketTime, 328, 328, 328, 2120, 2120, 2120, 2120, 2120, 2120 ] ):

            success = setDataLength(transport, upperTester, initiator.handles[0], txOctets, txTime, trace) and success;
            requested = success;
            success = success or (not success and ((txOctets > maxPacketLength) or (txTime > maxPacketTime)));

            changed = not ((cmaxTxOctets == min(txOctets, maxPacketLength)) and ((cmaxTxTime == max(txTime, 328)) or (cmaxTxTime == min(txTime, 328))));

            if requested and changed:
                gotEvent, handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = hasDataLengthChangedEvent(transport, upperTester, trace);
                success = success and gotEvent;
                gotEvent = hasDataLengthChangedEvent(transport, lowerTester, trace)[0];
                success = success and gotEvent;

            pbFlags = 0;
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)];
            dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
            """
                Lower Tester is sending Data...
            """
            txData = [_ for _ in range(27)];
            for i in range(20):
                dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-76-C [Master Packet Data Length Update - Responding to Packet Data Length Update Procedure; LE 2M PHY]

    Last modified: 08-08-2019
    Reviewed and verified: 08-08-2019 Henrik Eriksen (Note: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.)
"""
def ll_con_mas_bv_76_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);
    maxPacketTime, cmaxTxOctets, cmaxTxTime = calcMaxPacketTime(maxPacketLength), 27, 328;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Feature exchange as specified in LL.TS.5.1.1, chapter 4.1.5
        """
        success = readRemoteFeatures(transport, upperTester, initiator.handles[0], trace) and success;
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, upperTester, trace);
        showLEFeatures(features, trace);

        """
            Switch to LE 2M PHY channel...
        """
        allPhys, txPhys, rxPhys, optionPhys = 0, 2, 2, 0;

        success = initiator.updatePhys(allPhys, txPhys, rxPhys, optionPhys) and success;
        success = (initiator.txPhys == txPhys) and (initiator.rxPhys == rxPhys) and success
        """
            Exchange data...
        """
        lenValues  = list(range(28, maxPacketLength-1)) + list(range(maxPacketLength+1, 250));
        timeValues = list(range(329, maxPacketTime-1)) + list(range(maxPacketTime+1, 2119));

        for txOctets, txTime in zip( [ 27, 251, maxPacketLength, 27, 27, 27, 251, 251, 251, maxPacketLength, maxPacketLength, maxPacketLength, \
                                       random.choice(lenValues), random.choice(lenValues), random.choice(lenValues), random.choice(lenValues) ], \
                                     [ 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, 328, 2120, maxPacketTime, \
                                       random.choice(timeValues), random.choice(timeValues), random.choice(timeValues), random.choice(timeValues) ] ):

            success = setDataLength(transport, lowerTester, initiator.handles[1], txOctets, txTime, trace) and success;

            changed = not ((cmaxTxOctets == min(txOctets, maxPacketLength)) and ((cmaxTxTime == max(txTime, 328)) or (cmaxTxTime == min(txTime, 328))));

            if changed:
                gotEvent, handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = hasDataLengthChangedEvent(transport, lowerTester, trace);
                success = success and gotEvent;
                gotEvent = hasDataLengthChangedEvent(transport, upperTester, trace)[0];
                success = success and gotEvent;

            pbFlags = 0;
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)];
            dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
            """
                Lower Tester is sending Data...
            """
            txData = [_ for _ in range(27)];
            for i in range(20):
                dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData)) and (rxData == txData);
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BV-77-C [Master Packet Data Length Update - Initiating Packet Data Length Update Procedure; LE 2M PHY]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen (Note: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.)
"""
def ll_con_mas_bv_77_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);
    maxPacketTime, cmaxTxOctets, cmaxTxTime = calcMaxPacketTime(maxPacketLength), 27, 328;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Feature exchange as specified in LL.TS.5.1.1, chapter 4.1.5
        """
        success = readRemoteFeatures(transport, upperTester, initiator.handles[0], trace) and success;
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, upperTester, trace);
        showLEFeatures(features, trace);

        allPhys, txPhys, rxPhys, optionPhys = 0, 2, 2, 0;

        success = initiator.updatePhys(allPhys, txPhys, rxPhys, optionPhys) and success;
        success = (initiator.txPhys == txPhys) and (initiator.rxPhys == rxPhys) and success

        for txOctets, txTime in zip( [ maxPacketLength, 27, 251, maxPacketLength, 27, 251, maxPacketLength, 27, 251, maxPacketLength, 27, 251 ], \
                                     [ maxPacketTime, maxPacketTime, maxPacketTime, 328, 328, 328, 2120, 2120, 2120, 2120, 2120, 2120 ] ):

            success = setDataLength(transport, upperTester, initiator.handles[0], txOctets, txTime, trace) and success;
            requested = success;
            success = success or (not success and ((txOctets > maxPacketLength) or (txTime > maxPacketTime)));

            changed = not ((cmaxTxOctets == min(txOctets, maxPacketLength)) and ((cmaxTxTime == max(txTime, 328)) or (cmaxTxTime == min(txTime, 328))));

            if requested and changed:
                gotEvent, handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = hasDataLengthChangedEvent(transport, upperTester, trace);
                if not gotEvent:
                    trace.trace(7, "Missing Data Length Changed Event from upperTester!");
                success = success and gotEvent;
                gotEvent = hasDataLengthChangedEvent(transport, lowerTester, trace)[0];
                if not gotEvent:
                    trace.trace(7, "Missing Data Length Changed Event from lowerTester!");
                success = success and gotEvent;

            pbFlags = 0
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)]
            dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData));
            """
                Lower Tester is sending Data...
            """
            txData = [_ for _ in range(27)]
            for i in range(20):
                dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData));
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/CON/MAS/BI-06-C [Master responds to Connection Parameter Request - illegal parameters]

    Last modified: 06-08-2019
    Reviewed and verified: 06-08-2019 Henrik Eriksen
"""
def ll_con_mas_bi_06_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPublicInitiator(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED);

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        interval, timeout = 4, 300;
        """
            Lower tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            NOTE: We use a little nasty trick here. Swap the roles of initiator and peer and swap assigned handles...
        """
        initiator.switchRoles();

        success = initiator.update(interval, interval, initiator.latency, timeout) and success;
        """
            Verify that the update was rejected...
        """
        success = not initiator.updated() and (initiator.status == 0x1E) and success;

        initiator.resetRoles();

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-01-C [Changing Static Address while Advertising]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen (NOTE: Test fails - test specification is omitting White List addition!)
"""
def ll_sec_adv_bv_01_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivateActiveScanning(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 30, 5, \
                                                   ExtendedAddressType.RANDOM, ExtendedAddressType.RANDOM, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IUT' );
    """
        Adding lowerTester address to the White List
    """
    success = addAddressesToWhiteList(transport, upperTester, [ randomIdentityAddress(lowerTester) ], trace);

    success = advertiser.enable();
    success = scanner.enable() and success;
    scanner.monitor();
    """
        Attempt to change advertiser (upperTester) address...
    """
    status = le_set_random_address(transport, upperTester, toArray(address_scramble_OUI( toNumber(tests.test_utils.upperRandomAddress) ), 6), 100);
    trace.trace(6, "LE Set Random Address Command returns status: 0x%02X" % status);
    success = getCommandCompleteEvent(transport, upperTester, trace) and (status == 0x0C) and success;

    success = scanner.disable() and success;
    success = success and scanner.qualifyReports( 5 );
    success = success and scanner.qualifyResponses( 5, advertiser.responseData);

    success = advertiser.disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-02-C [Non Connectable Undirected Advertising with non-resolvable private address]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_02_c(transport, upperTester, lowerTester, trace):

    """
        Make sure that random address for upperTester is a non-resolvable private addresses
    """
    setNonResolvableRandomAddress(transport, upperTester, trace);

    advertiser, scanner = setPrivatePassiveScanning(transport, lowerTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 100, \
                                                    ExtendedAddressType.RESOLVABLE_OR_RANDOM, ExtendedAddressType.PUBLIC);
    """
        Add Random address of upperTester to the Resolving List
    """
    RPA = ResolvableAddresses( transport, upperTester, trace );
    success = RPA.add( publicIdentityAddress( lowerTester ) );
    """
        Enable Private Address Resolution
     """
    success = RPA.timeout( 60 ) and success;
    success = RPA.enable() and success;

    """
        Start NON_CONNECTABLE_ADVERTISING using non-resolvable private adddress
    """
    success = advertiser.enable() and success;
    success = scanner.enable() and success;
    scanner.monitor()
    success = scanner.disable() and success;
    success = success and scanner.qualifyReports( 100, randomIdentityAddress(upperTester) );

    success = advertiser.disable() and success;
    success = RPA.disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-03-C [Non Connectable Undirected Advertising with resolvable private address]

    Last modified: 21-08-2019
    Reviewed and verified: 21-08-2019 Henrik Eriksen
    Change: ReadLocalResolvableAddress() -> ReadPeerResolvableAddress()
"""
def ll_sec_adv_bv_03_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivatePassiveScanning(transport, lowerTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 20);
    """
        Add Public address of lowerTester to the Resolving List with the upperIRK
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester) ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( two and sixty seconds )
    """
    success = RPAs[upperTester].timeout( 2 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    resolvableAddresses = [ 0, 0 ];
    success = advertiser.enable() and success;

    for n in range(2):
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = success and scanner.qualifyReports( 20, resolvablePublicAddress(upperTester) );
        """
            Read local address in resolving list.
        """
        addressRead, resolvableAddresses[n] = readPeerResolvableAddress(transport, lowerTester, publicIdentityAddress(upperTester), trace);
        trace.trace(6, "Local Resolvable Address: %s" % formatAddress(resolvableAddresses[n]));

        if n == 0:
            transport.wait(2000); # Wait for RPA timeout to expire

    success = advertiser.disable() and success;
    success = success and toNumber(resolvableAddresses[0]) != toNumber(resolvableAddresses[1]);
    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-04-C [Scannable Undirected Advertising with non-resolvable private address]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_04_c(transport, upperTester, lowerTester, trace):

    """
        Make sure that random addresses for lower- and upper-Tester are non-resolvable private addresses
    """
    setNonResolvableRandomAddress(transport, lowerTester, trace);
    setNonResolvableRandomAddress(transport, upperTester, trace);

    advertiser, scanner = setPrivateActiveScanning(transport, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 100, 5, \
                                                   ExtendedAddressType.RANDOM, ExtendedAddressType.RANDOM);

    success = advertiser.enable();
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = advertiser.disable() and success;
    success = scanner.qualifyReports( 100, randomIdentityAddress(upperTester) ) and success;
    success = scanner.qualifyResponses( 5, advertiser.responseData) and success;

    return success;

"""
    LL/SEC/ADV/BV-05-C [Scannable Undirected Advertising with resolvable private address]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_05_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivateActiveScanning(transport, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 20, 1, \
                                                   ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                                                   AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS);

    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Adding lowerTester address to the White List
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;
    """
        Set resolvable private address timeout in seconds ( two and sixty seconds )
    """
    success = RPAs[upperTester].timeout( 2 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = success and advertiser.enable();

    resolvableAddresses = [ 0, 0 ];
    for n in range(2):
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = scanner.qualifyReports( 20, resolvablePublicAddress(upperTester) ) and success;
        success = scanner.qualifyResponses( 1, advertiser.responseData ) and success;

        addressRead, resolvableAddresses[n] = readLocalResolvableAddress(transport, upperTester, publicIdentityAddress(lowerTester), trace);
        trace.trace(6, "AdvA: %s" % formatAddress(resolvableAddresses[n]));
        if n == 0:
            transport.wait(2000); # Wait for RPA timeout

    success = advertiser.disable() and success;
    success = success and toNumber(resolvableAddresses[0]) != toNumber(resolvableAddresses[1]);
    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-06-C [Connecting with Undirected Connectable Advertiser using non-resolvable private address]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_06_c(transport, upperTester, lowerTester, trace):

    """
        Make sure that random address for upperTester is a non-resolvable private addresses
    """
    setNonResolvableRandomAddress(transport, upperTester, trace);

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_RANDOM, ExtendedAddressType.PUBLIC);

    lowerAddresses = [ publicIdentityAddress(lowerTester), \
                       Address( ExtendedAddressType.PUBLIC, toNumber(tests.test_utils.lowerRandomAddress) | 0xC00000000000 ), \
                       Address( ExtendedAddressType.PUBLIC, toNumber(tests.test_utils.lowerRandomAddress) & 0x3FFFFFFFFFFF ) ];

    success = True;
    for lowerAddress in lowerAddresses:
        advertiser.peerAddress = lowerAddress;
        initiator.initiatorAddress = lowerAddress;
        initiator.peerAddress = randomIdentityAddress(upperTester);

        if lowerAddress.type == ExtendedAddressType.PUBLIC:
            success = preamble_set_public_address(transport, lowerTester, toNumber(lowerAddress.address), trace) and success;
        else:
            success = preamble_set_random_address(transport, lowerTester, toNumber(lowerAddress.address), trace) and success;

        success = advertiser.enable() and success;
        connected = initiator.connect();
        success = connected and success;
        if connected:
            success = initiator.disconnect(0x13) and success;
        else:
            success = advertiser.disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-07-C [Connecting with Undirected Connectable Advertiser with Local IRK but no Peer IRK]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen (NOTE: Test fails - filtering doesn't work!)
"""
def ll_sec_adv_bv_07_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_CONNECTION_REQUESTS);
    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester) ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Adding lowerTester address to the White List
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Upper tester terminates the connection
        """
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and success;
        initiator.resetRoles();
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-08-C [Connecting with Undirected Connectable Advertiser with both Local and Peer IRK]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_08_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Adding lowerTester address to the White List
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and success;
        initiator.resetRoles();
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-09-C [Connecting with Undirected Connectable Advertiser with no Local IRK but peer IRK]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_09_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester) ) and success;
    """
        Adding lowerTester address to the White List
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and success;
        initiator.resetRoles();
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success

    return success;

"""
    LL/SEC/ADV/BV-10-C [Connecting with Undirected Connectable Advertiser where no match for Peer Device Identity]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_10_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    """
        Add Identity Addresses to Resolving Lists
    """
    bogusIRK = [ random.randint(0,255) for _ in range(16) ];
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), bogusIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Add Identity Address of lower Tester to White List to enable responding to Scan Requests
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;

    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;

    for n in range(10):
        connected = initiator.connect();
        success = success and not connected;
        if connected:
            success = initiator.disconnect(0x13) and success;
            break;

    success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-11-C [Connecting with Directed Connectable Advertiser using local and remote IRK]

    Last modified: 17-12-2019
    Reviewed and verified: 17-12-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_11_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_HDC_DIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Verify that connection was established with resolvable private addresses
        """
        isRPA = Address( None, initiator.localRPA() ).isResolvablePrivate();
        isRPA = Address( None, initiator.peerRPA() ).isResolvablePrivate() and isRPA;
        success = isRPA and success;
        if not isRPA:
            trace.trace(6, "Wrong RPAs - local RPA: %s peer RPA: %s" %(Address( None, initiator.localRPA() ), Address( None, initiator.peerRPA() )));
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and success;
        initiator.resetRoles();
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and success;

    advertiserTimeout = False;
    success = advertiser.enable() and success;
    initiator.checkPrematureDisconnect = False;
    """
        Retry connection 20 times.
    """
    for i in range(20):
        connected = initiator.connect();
        success = success and not connected;
        if connected:
            success = initiator.disconnect(0x13) and success;
            break;
        else:
            advertiserTimeout, waitTime = False, 0;
            while not advertiserTimeout:
                flush_events(transport, lowerTester, 100);
                advertiserTimeout = advertiser.timeout();
                waitTime += 100;
                if waitTime >= 1300:
                    break;
            if advertiserTimeout:
                trace.trace(7, "Advertising done!");
                success = advertiser.enable(True) and success;
            else:
                break;

    if not advertiserTimeout:
        success = advertiser.disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-12-C [Connecting with Directed Connectable Advertising with local IRK but without remote IRK]

    Last modified: 21-08-2019
    Reviewed and verified: 21-08-2019 Henrik Eriksen
    Change: ReadLocalResolvableAddress() -> ReadPeerResolvableAddress()
"""
def ll_sec_adv_bv_12_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_HDC_DIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.PUBLIC);
    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester) ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( two seconds )
    """
    success = RPAs[upperTester].timeout( 2 ) and RPAs[lowerTester].timeout( 2 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    privateAddresses = [ 0, 0 ];

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Read the resolvable address used in the AdvA field
        """
        addressRead, privateAddresses[0] = readPeerResolvableAddress(transport, lowerTester, publicIdentityAddress(upperTester), trace);
        trace.trace(6, "AdvA Address: %s" % formatAddress(privateAddresses[0]));
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and success;
        initiator.resetRoles();

        transport.wait( 2000 ); # wait for RPA to timeout
        """
            Extra connect step is necassary in order to the read the
        """
        success = advertiser.enable() and success;
        connected = initiator.connect();
        success = success and connected;

        if connected:
            """
                Read the resolvable address used in the AdvA field
            """
            addressRead, privateAddresses[1] = readPeerResolvableAddress(transport, lowerTester, publicIdentityAddress(upperTester), trace);
            trace.trace(6, "AdvA Address: %s" % formatAddress(privateAddresses[1]));

            success = initiator.disconnect(0x13) and success;
        else:
            success = advertiser.disable() and success;
    else:
        success = advertiser.disable() and success;

    success = success and (privateAddresses[0] != privateAddresses[1]);
    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-13-C [Directed Connectable Advertising without local IRK but with remote IRK]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen (NOTE: Test fails!)
"""
def ll_sec_adv_bv_13_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_HDC_DIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester) ) and success;
    """
        Set resolvable private address timeout in seconds ( two seconds )
    """
    success = RPAs[upperTester].timeout( 2 ) and RPAs[lowerTester].timeout( 2 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    privateAddresses = [ 0, 0 ];

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Read the resolvable address used in the AdvA field
        """
        addressRead, privateAddresses[0] = readLocalResolvableAddress(transport, lowerTester, publicIdentityAddress(upperTester), trace);
        trace.trace(6, "InitA Address: %s" % formatAddress(privateAddresses[0]));
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and success;
        initiator.resetRoles();

        transport.wait( 2000 ); # wait for RPA to timeout

        success = advertiser.enable() and success;
        connected = initiator.connect();
        success = success and connected;
        """
            Read the resolvable address used in the AdvA field
        """
        addressRead, privateAddresses[1] = readLocalResolvableAddress(transport, lowerTester, publicIdentityAddress(upperTester), trace);
        trace.trace(6, "InitA Address: %s" % formatAddress(privateAddresses[1]));

        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = success and (privateAddresses[0] != privateAddresses[1]);
    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-14-C [Directed Connectable Advertising using Resolving List and Peer Device Identity not in the List]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_14_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_HDC_DIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    """
        Add Identity Addresses to Resolving Lists
    """
    bogusIRK = [ random.randint(0,255) for _ in range(16) ];
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), bogusIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Add Identity Address of lower Tester to White List to enable responding to Scan Requests
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;

    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and not connected;

    if connected:
        success = initiator.disconnect(0x13) and success;
    else:
        """
            Need to stop connection attempt - otherwies Resolvable List disable will fail with command not allowed...
        """
        success = initiator.cancelConnect() and success;
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-15-C [Scannable Advertising with resolvable private address, no Scan Response to Identity Address]

    Last modified: 07-08-2019
    Reviewed and verified: 07-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_15_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivateActiveScanning(transport, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 20, 1, \
                                                   ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.PUBLIC, AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS);
    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Adding lowerTester address to the White List
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;

    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.qualifyReports( 20, resolvablePublicAddress(upperTester) ) and success;
    success = not scanner.qualifyResponses( 1 ) and success;
    success = scanner.disable() and success;
    success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-16-C [Undirected Connectable Advertising with resolvable private address; no Connection to Identity Address]

    Last modified: 10-09-2019
    Reviewed and verified: 10-09-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_16_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Adding lowerTester address to the White List
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and not connected;
    if connected:
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-17-C [Directed Connectable Advertising using local and remote IRK, Ignore Identity Address]

    Last modified: 08-08-2019
    Reviewed and verified: 08-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_17_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_HDC_DIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and not connected;
    if connected:
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success

"""
    LL/SEC/ADV/BV-18-C [Scannable Advertising with resolvable private address, accept Identity Address]

    Last modified: 08-08-2019
    Reviewed and verified: 08-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_18_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivateActiveScanning(transport, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 20, 1, \
                                                   ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.PUBLIC);
    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set Device Privacy
    """
    success = setPrivacyMode(transport, upperTester, publicIdentityAddress(lowerTester), PrivacyMode.DEVICE_PRIVACY, trace) and success;
    """
        Add Identity Address of lower Tester to White List to enable responding to Scan Requests
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = advertiser.disable() and success;
    success = scanner.qualifyReports( 20, resolvablePublicAddress(upperTester) ) and success;
    success = scanner.qualifyResponses( 1, advertiser.responseData ) and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-19-C [Undirected Connectable Advertising with Local IRK and Peer IRK, accept Identity Address]

    Last modified: 08-08-2019
    Reviewed and verified: 08-08-2019 Henrik Eriksen (NOTE: Test fails!)
"""
def ll_sec_adv_bv_19_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set Device Privacy
    """
    success = setPrivacyMode(transport, upperTester, publicIdentityAddress(lowerTester), PrivacyMode.DEVICE_PRIVACY, trace) and success;
    """
        Add Identity Address of lower Tester to White List to enable responding to Scan Requests
    """
    success = addAddressesToWhiteList(transport, upperTester, [ publicIdentityAddress(lowerTester) ], trace) and success;
    """
        Set resolvable private address timeout in seconds ( two and sixty seconds )
    """
    success = RPAs[upperTester].timeout( 2 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(2100); # Wait for address renewal
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-20-C [Directed Connectable Advertising with resolvable private address; Connect to Identity Address]

    Last modified: 08-08-2019
    Reviewed and verified: 08-08-2019 Henrik Eriksen
"""
def ll_sec_adv_bv_20_c(transport, upperTester, lowerTester, trace):

    advertiser, initiator = setPrivateInitiator(transport, lowerTester, trace, Advertising.CONNECTABLE_HDC_DIRECTED, \
                                                ExtendedAddressType.RESOLVABLE_OR_PUBLIC, ExtendedAddressType.PUBLIC, \
                                                AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = RPAs[upperTester].add( publicIdentityAddress(lowerTester), lowerIRK ) and success;
    success = RPAs[lowerTester].add( publicIdentityAddress(upperTester), upperIRK ) and success;
    """
        Set Device Privacy
    """
    success = setPrivacyMode(transport, upperTester, publicIdentityAddress(lowerTester), PrivacyMode.DEVICE_PRIVACY, trace) and success;
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 ) and success;
    success = RPAs[upperTester].enable() and RPAs[lowerTester].enable() and success;

    success = advertiser.enable() and success;
    connected = initiator.connect();
    success = success and connected;

    if connected:
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success

"""
    LL/SEC/SCN/BV-01-C [Changing Static Address while Scanning]

    Last modified: 08-08-2019
    Reviewed and verified: 08-08-2019 Henrik Eriksen
"""
def ll_sec_scn_bv_01_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPrivateActiveScanning(transport, upperTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 20, 1, \
                                                   ExtendedAddressType.RANDOM, ExtendedAddressType.RANDOM);
    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'IUT' );

    success = advertiser.enable();
    success = scanner.enable() and success;
    scanner.monitor();
    """
        Attempt to change scanner (upperTester) address...
    """
    status = le_set_random_address(transport, upperTester, toArray(address_scramble_OUI( toNumber(tests.test_utils.upperRandomAddress) ), 6), 100);
    trace.trace(6, "LE Set Random Address Command returns status: 0x%02X" % status);
    """
        Event queue may hold several Advertising Events...
    """
    while not getCommandCompleteEvent(transport, upperTester, trace):
        pass;
    success = (status == 0x0C) and success;

    success = scanner.disable() and success;
    success = scanner.qualifyReports( 20, randomIdentityAddress(lowerTester) ) and success;
    success = scanner.qualifyResponses( 5, advertiser.responseData) and success;

    success = advertiser.disable() and success;

    address = toNumber( randomIdentityAddress(lowerTester).address );
    randAddr = (address >> 24) & 0xFFFFFF;
    hashAddr = address & 0xFFFFFF;

    trace.trace(8, "Address parts: rand: 0x%06X hash: 0x%06X" % (randAddr, hashAddr));
    ok, localHash = encrypt(transport, upperTester, lowerIRK, toArray(randAddr, 16), trace);
    success = success and ok and (toNumber(localHash) & 0xFFFFFF == hashAddr);
    trace.trace(8, "Regenerated: hash: 0x%06X" % (toNumber(localHash) & 0xFFFFFF));

    return success;


def cis_setup_response_procedure_peripheral(transport, upper_tester, lower_tester, trace, params):
    """
    [CIS Setup Response Procedure, Peripheral]
    """
    success, initiator, _, (cisConnectionHandle,) = \
        state_connected_isochronous_stream(transport, upper_tester, lower_tester, trace, params)

    # 10. The Lower Tester sends data packets to the IUT.
    # 11. The Upper Tester IUT sends an ISO data packet to the Upper Tester.
    def lt_send_data_packet(pkt_seq_num):
        return iso_send_payload_pdu(transport, lower_tester, upper_tester, trace, cisConnectionHandle,
                                    params.Max_SDU_C_To_P[0], params.SDU_Interval_C_To_P, pkt_seq_num)

    # 12. Perform either Alternative 12A or 12B depending on whether P_To_C Payload (PDU) in Table 4.146 is 0:
    #     Alternative 12A (P_To_C Payload (PDU) is not equal to 0):
    #       12A.1. TODO: The IUT sends an Ack to the Lower Tester.
    #     Alternative 12B (P_To_C Payload (PDU) is equal to 0):
    #       12B.1. TODO: The IUT sends a CIS Null PDU to the Lower Tester.

    # 13. Repeat steps 10-12 a total of 50 times.
    for j in range(50):
        success = lt_send_data_packet(j) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


"""
    LL/CIS/PER/BV-01-C [CIS Setup Response Procedure, Peripheral]
"""
def ll_cis_per_bv_01_c(transport, upperTester, lowerTester, trace):
    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 7500, # 7.5 ms
        SDU_Interval_P_To_C     = 7500, # 7.5 ms
        ISO_Interval            = int(7.5 // 1.25), # 7.5
        NSE                     = 2,
        Max_PDU_C_To_P          = 60, # TODO: Supposed to be 160
        Max_PDU_P_To_C          = 60, # TODO: Supposed to be 160
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        BN_P_To_C               = 1,
    )

    return cis_setup_response_procedure_peripheral(transport, upperTester, lowerTester, trace, params)


def cis_setup_peripheral_rejected(transport, peripheral, central, trace):
    success = True

    status = le_set_host_feature(transport, central, FeatureSupport.ISOCHRONOUS_CHANNELS, 1, 100)
    success = getCommandCompleteEvent(transport, central, trace) and (status == 0x00) and success

    status = le_set_host_feature(transport, peripheral, FeatureSupport.ISOCHRONOUS_CHANNELS, 1, 100)
    success = getCommandCompleteEvent(transport, peripheral, trace) and (status == 0x00) and success

    advertiser, initiator = setPublicInitiator(transport, central, trace, Advertising.CONNECTABLE_UNDIRECTED)
    success = advertiser.enable() and success
    connected = initiator.connect()
    success = success and connected

    if not connected:
        success = advertiser.disable() and success
        return success

    # 1. The Upper Tester sends an HCI_LE_Set_Event_Mask command with all events enabled,
    #    including the HCI_LE_CIS_Request event. The IUT sends a successful
    #    HCI_Command_Complete in response.
    #
    # NOTE: This is already performed during the preamble step

    # 2. The Lower Tester sends an LL_CIS_REQ PDU with valid data as specified for the Set CIG
    #    Parameters command in Section 4.10.1.3 Default Values for Set CIG Parameters Commands to
    #    the IUT.
    # NOTE: CIG_ID is hardcoded to 0
    params = SetCIGParameters()

    status, cigId, cisCount, cis_handle_central = \
    le_set_cig_parameters_test(transport, central, 0, *params.get_cig_parameters_test(), 100)
    success = getCommandCompleteEvent(transport, central, trace) and (status == 0x00) and success

    status = le_create_cis(transport, central, 1, cis_handle_central, [initiator.handles[0]], 100)
    success = verifyAndShowEvent(transport, central, Events.BT_HCI_EVT_CMD_STATUS, trace) and (status == 0) and success

    # 3. The Upper Tester receives an HCI_LE_CIS_Request event from the IUT.
    s, event = verifyAndFetchMetaEvent(transport, peripheral, MetaEvents.BT_HCI_EVT_LE_CIS_REQUEST, trace)
    success = s and success
    aclConnectionHandle, cis_handle_peripheral, cigId, cisId = event.decode()

    # 4. The Upper Tester sends an HCI_LE_Reject_CIS_Request command to the IUT with a valid
    #    reason code and receives a successful return status.
    status, _ = le_reject_cis_request(transport, peripheral, cis_handle_peripheral, 0x0D, 100)

    # 5. The Upper Tester receives an HCI_Command_Complete event from the IUT.
    success = getCommandCompleteEvent(transport, peripheral, trace) and (status == 0x00) and success

    # 6. The Lower Tester receives an LL_REJECT_EXT_IND from the IUT with a valid reason code.
    s, event = verifyAndFetchMetaEvent(transport, central, MetaEvents.BT_HCI_EVT_LE_CIS_ESTABLISHED, trace)
    success = s and (event.decode()[0] == 0x0D) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def ll_cis_per_bv_02_c(transport, upperTester, lowerTester, trace):
    """LL/CIS/PER/BV-02-C [CIS Setup Response Procedure, Peripheral, Reject Response]"""
    return cis_setup_peripheral_rejected(transport, upperTester, lowerTester, trace)


def test_cis_map_update(transport, peripheral, central, trace, bn_c_to_p, nse, sdu_interval_c_to_p):
    params = SetCIGParameters(
        SDU_Interval_C_To_P     = sdu_interval_c_to_p,
        ISO_Interval            = int(100 // 1.25),  # 100 ms
        NSE                     = nse,
        Max_PDU_P_To_C          = 0,
        BN_C_To_P               = bn_c_to_p,
        BN_P_To_C               = 0,
    )

    success, initiator, _, (cis_conn_handle,) = \
        state_connected_isochronous_stream(transport, peripheral, central, trace, params)
    if not initiator:
        return success

    acl_handle = initiator.handles[1]
    channel_map_new = 0x1249249249
    success = channelMapUpdate(transport, central, channel_map_new, trace) and success

    instant_to = initiator.prevInterval * 10  # TODO: calculate based on LL_CHANNEL_MAP_IND PDU instant
    transport.wait(instant_to)
    status, handle, channel_map = le_read_channel_map(transport, peripheral, acl_handle, 100)
    success = getCommandCompleteEvent(transport, peripheral, trace) and status == 0x00 and handle == acl_handle and success

    success = channel_map == channel_map_new and success

    # 4. The Lower Tester sends data packets to the IUT.
    for pkt_seq_num in range(50):
        success = iso_send_payload_pdu(transport, central, peripheral, trace, cis_conn_handle,
                                       params.Max_SDU_C_To_P[0], params.SDU_Interval_C_To_P, pkt_seq_num) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


"""
    LL/CIS/PER/BV-03-C [CIS Map Update]
"""
def ll_cis_per_bv_03_c(transport, upper_tester, lower_tester, trace):
    return test_cis_map_update(transport, upper_tester, lower_tester, trace, 0x01, 0x01, 100000)


"""
    LL/CIS/PER/BV-37-C [CIS Map Update]
"""
def ll_cis_per_bv_37_c(transport, upper_tester, lower_tester, trace):
    return test_cis_map_update(transport, upper_tester, lower_tester, trace, 0x02, 0x02, 50000)


"""
    LL/CIS/PER/BV-05-C [Receiving data in Unidirectional CIS]
"""
def ll_cis_per_bv_05_c(transport, upperTester, lowerTester, trace):
    # Establish Initial Condition
    #
    # Connected in the relevant role as defined in the following initial states:
    #
    # Note: “default” refers to values specified in Section 4.10.1.3 Default Values for Set CIG Parameters
    # Commands.

    # Table 4.126: State Variable Values
    # NOTE: As the IUT is the Peripheral, the CIG Parameters are those of the Central
    max_cis_nse = get_ixit_value(transport, upperTester, IXITS["TSPX_max_cis_nse"], 100)

    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 50000,  # 50 ms
        SDU_Interval_P_To_C     = 50000,  # 50 ms
        ISO_Interval            = int(50 // 1.25), # 50 ms
        NSE                     = min(max_cis_nse, 4),  # Note 1: TSPX_max_cis_nse or 0x04, whichever is less
        # Max_PDU_P_To_C          = 0,  # TODO: Supposed to be 0
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 2,
        BN_P_To_C               = 1, # TODO: Supposed to be 0
    )

    success, initiator, _, (cisConnectionHandle,) = \
        state_connected_isochronous_stream(transport, upperTester, lowerTester, trace, params)
    if not initiator:
        return success

    for pkt_seq_num in range(3):
        success = iso_send_payload_pdu(transport, lowerTester, upperTester, trace, cisConnectionHandle,
                                       params.Max_SDU_C_To_P[0], params.SDU_Interval_C_To_P, pkt_seq_num) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def sending_and_receiving_data_complete(transport, central, peripheral, trace, params, packets_sent):
    # Fetch all the EDTT Write ISO Data command responses
    success = le_iso_data_write_complete(transport, peripheral, trace, len(packets_sent[peripheral]), 100)
    success = le_iso_data_write_complete(transport, central, trace, len(packets_sent[central]), 100) and success

    # Fetch all the HCI Number of Completed Packets events
    _, conn_handles_p, num_packets_p = \
        fetch_number_of_completed_packets(transport, peripheral, trace, len(packets_sent[peripheral]),
                                          params.SDU_Interval_P_To_C)
    success = len(packets_sent[peripheral]) == sum(num_packets_p) and success

    _, conn_handles_c, num_packets_c = \
        fetch_number_of_completed_packets(transport, central, trace, len(packets_sent[central]),
                                          params.SDU_Interval_C_To_P)
    success = len(packets_sent[central]) == sum(num_packets_c) and success

    # Fetch and verify the payloads received
    for conn_handle_p, payload_sent_p in packets_sent[peripheral]:
        s, payload_received_c = iso_receive_sdu(transport, central, trace, params.SDU_Interval_P_To_C)
        success = s and success and payload_sent_p == payload_received_c

    for conn_handle_c, payload_sent_c in packets_sent[central]:
        s, payload_received_p = iso_receive_sdu(transport, peripheral, trace, params.SDU_Interval_C_To_P)
        success = s and success and payload_sent_c == payload_received_p

    return success


def test_sending_and_receiving_data_in_multiple_cises(transport, central, peripheral, trace, params,
                                                      num_iso_data_packets_per_cis, send_delay_c=0):
    success, initiator, peripheral_cis_handles, central_cis_handles = \
        state_connected_isochronous_stream(transport, peripheral, central, trace, params)
    if not initiator:
        return success

    # Repeat all steps 3 times
    for round_num in range(3):
        if not success:
            break

        packets_sent = {
            peripheral: [],
            central: [],
        }

        for i in range(num_iso_data_packets_per_cis):
            pkt_seq_num = round_num * num_iso_data_packets_per_cis + i
            for j in range(len(peripheral_cis_handles)):
                s, sdu = le_iso_data_write_nbytes(transport, peripheral, trace, peripheral_cis_handles[j],
                                                  params.Max_SDU_P_To_C[j], pkt_seq_num, 0)
                success = s and success
                packets_sent[peripheral].append((peripheral_cis_handles[j], sdu))

            if send_delay_c:
                # wait some time so that ISO event begins with central's Null PDU
                transport.wait(send_delay_c)

            for j in range(len(central_cis_handles)):
                s, sdu = le_iso_data_write_nbytes(transport, central, trace, central_cis_handles[j],
                                                  params.Max_SDU_C_To_P[j], pkt_seq_num, 0)
                success = s and success
                packets_sent[central].append((central_cis_handles[j], sdu))

        success = sending_and_receiving_data_complete(transport, central, peripheral, trace, params,
                                                      packets_sent) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def test_sending_and_receiving_data_in_bidirectional_cis(transport, central, peripheral, trace, enc_keys=None):
    # Establish Initial Condition
    #
    # Connected in the relevant role as defined in the following initial states.
    # Note 2: TSPX_max_cis_bn, or 0x03, whichever is less.
    cis_nse = min(0x06, get_ixit_value(transport, peripheral, IXITS["TSPX_max_cis_nse"], 100))
    cis_bn = min(0x03, get_ixit_value(transport, peripheral, IXITS["TSPX_max_cis_bn"], 100))

    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 100000,  # 100 ms
        SDU_Interval_P_To_C     = 100000,  # 100 ms
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        ISO_Interval            = int(300 // 1.25),  # 300 ms
        NSE                     = cis_nse,
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        BN_C_To_P               = cis_bn,
        BN_P_To_C               = cis_bn,
    )

    success, initiator, (peripheral_cis_handle,), (central_cis_handle,) = \
        state_connected_isochronous_stream(transport, peripheral, central, trace, params, enc_keys=enc_keys)
    if not initiator:
        return success

    for round_num in range(cis_bn):
        if not success:
            break

        packets_sent = {
            peripheral: [],
            central: [],
        }

        success = True
        s, sdu = le_iso_data_write_nbytes(transport, central, trace, central_cis_handle, params.Max_SDU_C_To_P[0],
                                          round_num, 0)
        success = s and success
        packets_sent[central].append((central_cis_handle, sdu))

        s, sdu = le_iso_data_write_nbytes(transport, peripheral, trace, peripheral_cis_handle, params.Max_SDU_P_To_C[0],
                                          round_num, 0)
        success = s and success
        packets_sent[peripheral].append((peripheral_cis_handle, sdu))

        success = sending_and_receiving_data_complete(transport, central, peripheral, trace, params,
                                                      packets_sent) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


"""
    LL/CIS/PER/BV-06-C [Sending and Receiving Data in Bidirectional CIS]
"""
def ll_cis_per_bv_06_c(transport, upper_tester, lower_tester, trace):
    return test_sending_and_receiving_data_in_bidirectional_cis(transport, lower_tester, upper_tester, trace)


"""
    LL/CIS/PER/BV-27-C [Sending and Receiving Data in Bidirectional CIS]
"""
def ll_cis_per_bv_27_c(transport, upper_tester, lower_tester, trace):
    return test_sending_and_receiving_data_in_bidirectional_cis(transport, lower_tester, upper_tester, trace, ENC_KEYS)


"""
    LL/CIS/PER/BV-07-C [Sending and Receiving Data in Multiple CISes, Single CIG, Single Connection, Interleaved CIG,
                        Peripheral]
"""
def ll_cis_per_bv_07_c(transport, upper_tester, lower_tester, trace):
    # Establish Initial Condition
    #
    # State: Connected Isochronous Stream, Peripheral
    max_cis_nse = get_ixit_value(transport, upper_tester, IXITS["TSPX_max_cis_nse"], 100)

    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 50000,  # 50 ms
        SDU_Interval_P_To_C     = 50000,  # 50 ms
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        ISO_Interval            = int(100 // 1.25),  # 100 ms
        Packing                 = 1,
        CIS_Count               = 2,
        NSE                     = min(max_cis_nse, 4),  # Note 1: TSPX_max_cis_nse or 0x04, whichever is less
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        BN_C_To_P               = 2,
        BN_P_To_C               = 2,
    )

    # The Lower Tester sends Null PDU to the IUT on CISes first, so lets wait a specific time prior sending ISO Data PDU
    lower_tester_send_delay = int(params.ISO_Interval / (params.NSE[0] + params.NSE[1])) + 1

    success = test_sending_and_receiving_data_in_multiple_cises(transport, lower_tester, upper_tester, trace, params, 2,
                                                                lower_tester_send_delay)

    return success


def cis_updating_peer_clock_accuracy(transport, upper_tester, lower_tester, trace, role):
    assert role == "Peripheral" or role == "Central"
    # Initial Condition

    # Connected in the relevant role.
    # An ACL connection has been established between the IUT and Lower Tester with a valid Connection Handle.
    if role == "Peripheral":
        success, advertiser, initiator = establish_acl_connection(transport, lower_tester, upper_tester, trace)
        acl_conn_handle = initiator.handles[1]
    else:
        success, advertiser, initiator = establish_acl_connection(transport, upper_tester, lower_tester, trace)
        acl_conn_handle = initiator.handles[0]

    # 1. The Upper Tester sends an HCI_LE_Request_Peer_SCA command to the IUT with a valid Connection_Handle.
    # 2. The Upper Tester receives the Command Status event.
    status = le_request_peer_sca(transport, upper_tester, acl_conn_handle, 100)
    s = verifyAndShowEvent(transport, upper_tester, Events.BT_HCI_EVT_CMD_STATUS, trace)
    success = s and status == 0x00 and success

    # 3. The Lower Tester receives an LL_CLOCK_ACCURACY_REQ PDU from the IUT and sends back an LL_CLOCK_ACCURACY_RSP
    #    PDU with a valid Peer_Clock_Accuracy value.
    # 4. The Upper Tester receives an HCI_LE_Request_Peer_SCA_Complete event with the Connection_Handle of the ACL and
    #    the Peer_Clock_Accuracy parameter when the HCI_LE_Request_Peer_SCA command completes.
    s, event = verifyAndFetchMetaEvent(transport, upper_tester, MetaEvents.BT_HCI_EVT_LE_REQUEST_PEER_SCA_COMPLETE,
                                       trace, 1000)
    status, conn_handle, peer_clock_accuracy = event.decode()
    success = s and status == 0x00 and conn_handle == acl_conn_handle and success

    # 5. The Upper Tester sends an HCI_LE_Request_Peer_SCA command to the IUT with a valid, but
    # non-existent Connection_Handle and receives the error code Unknown Connection Identifier
    # (0x02).
    acl_conn_handle_non_existent = (acl_conn_handle + 1) % 0x0EFF
    status = le_request_peer_sca(transport, upper_tester, acl_conn_handle_non_existent, 100)
    s = verifyAndShowEvent(transport, upper_tester, Events.BT_HCI_EVT_CMD_STATUS, trace)
    success = s and status == 0x02 and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def ll_cis_per_bv_18_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/PER/BV-18-C [CIS Updating Peer Clock Accuracy]"""
    return cis_updating_peer_clock_accuracy(transport, upper_tester, lower_tester, trace, "Peripheral")


"""
    LL/CIS/PER/BV-08-C [Sending and Receiving Data in Multiple CISes, Single CIG, Single Connection, Sequential,
                        Peripheral]
"""
def ll_cis_per_bv_08_c(transport, upper_tester, lower_tester, trace):
    # Establish Initial Condition
    #
    # State: Connected Isochronous Stream, Peripheral
    max_cis_nse = get_ixit_value(transport, upper_tester, IXITS["TSPX_max_cis_nse"], 100)

    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 100000,  # 100 ms
        SDU_Interval_P_To_C     = 50000,  # 50 ms
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        ISO_Interval            = int(100 // 1.25),  # 100 ms
        Packing                 = 0,  # Sequential
        CIS_Count               = 2,
        NSE                     = min(max_cis_nse, 4),  # Note 1: TSPX_max_cis_nse or 0x04, whichever is less
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        BN_C_To_P               = 1,
        BN_P_To_C               = 2,
    )

    # The Lower Tester sends Null PDU to the IUT on CISes first, so lets wait a specific time prior sending ISO Data PDU
    lower_tester_send_delay = int(params.ISO_Interval / (params.NSE[0] + params.NSE[1])) + 1

    success = test_sending_and_receiving_data_in_multiple_cises(transport, lower_tester, upper_tester, trace, params, 2,
                                                                lower_tester_send_delay)

    return success


"""
    LL/CIS/PER/BV-19-C [CIS Setup Response Procedure, Peripheral]
"""
def ll_cis_per_bv_19_c(transport, upperTester, lowerTester, trace):
    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 11250, # 11.25 ms
        SDU_Interval_P_To_C     = 11250, # 11.25 ms
        ISO_Interval            = int(11.25 // 1.25), # 11.25 ms
        NSE                     = 4,
        Max_PDU_C_To_P          = 200,
        Max_PDU_P_To_C          = 200,
        PHY_C_To_P              = 2,
        PHY_P_To_C              = 2,
        FT_C_To_P               = 3,
        FT_P_To_C               = 2,
        BN_C_To_P               = 3,
        BN_P_To_C               = 1,
    )

    return cis_setup_response_procedure_peripheral(transport, upperTester, lowerTester, trace, params)


"""
    LL/CIS/PER/BV-22-C [CIS Request Event Not Set]
"""
def ll_cis_per_bv_22_c(transport, upper_tester, lower_tester, trace):
    # Initial Condition
    #
    # The Isochronous Channels (Host Support) FeatureSet bit is clear.
    success = set_isochronous_channels_host_support(transport, upper_tester, trace, 0)
    success = set_isochronous_channels_host_support(transport, lower_tester, trace, 1) and success

    # An ACL connection has been established between the IUT and Lower Tester with the IUT acting as the Peripheral.
    s, advertiser, initiator = establish_acl_connection(transport, lower_tester, upper_tester, trace)
    success = s and success
    if not initiator:
        return success

    # 1. The Lower Tester sends an LL_CIS_REQ to the IUT with the contents specified per Section 4.10.1.3 Default Values
    #    for Set CIG Parameters Commands.
    params = SetCIGParameters()

    status, cig_id, cis_count, cis_conn_handle = \
        le_set_cig_parameters_test(transport, lower_tester, 0, *params.get_cig_parameters_test(), 100)
    success = getCommandCompleteEvent(transport, lower_tester, trace) and status == 0x00 and success

    def lt_send_ll_cis_req(acl_conn_handle):
        status = le_create_cis(transport, lower_tester, cis_count, cis_conn_handle, [acl_conn_handle] * cis_count, 100)
        return verifyAndShowEvent(transport, lower_tester, Events.BT_HCI_EVT_CMD_STATUS, trace) and status == 0 and success

    success = lt_send_ll_cis_req(initiator.handles[0]) and success

    # 2. The IUT responds to the Lower Tester with an LL_REJECT_EXT_IND with error code Unsupported Remote Feature
    #    (0x1A).
    s, event = verifyAndFetchMetaEvent(transport, lower_tester, MetaEvents.BT_HCI_EVT_LE_CIS_ESTABLISHED, trace)
    success = s and (event.decode()[0] == 0x1A) and success

    # 3. The IUT disconnects the ACL connection from the Lower Tester.
    # TSE ID: 17099: Core does not mandate IUT to disconnect ACL when CIS Request has been rejected.
    #                The TS shall be clear that, it is Upper Tester initiated operation, not autonomous IUT operation.
    status = disconnect(transport, upper_tester, initiator.handles[1], 0x13, 200)
    success = verifyAndShowEvent(transport, upper_tester, Events.BT_HCI_EVT_CMD_STATUS, trace) and (status == 0) \
              and success

    s, event = verifyAndFetchEvent(transport, lower_tester, Events.BT_HCI_EVT_DISCONN_COMPLETE, trace)
    status, handle, reason = event.decode()
    success = s and (status == 0x00) and handle == initiator.handles[0] and success

    s, event = verifyAndFetchEvent(transport, upper_tester, Events.BT_HCI_EVT_DISCONN_COMPLETE, trace)
    status, handle, reason = event.decode()
    success = s and (status == 0x00) and handle == initiator.handles[1] and success

    # 4. The Upper Tester sends an HCI_LE_Set_Host_Feature command to the IUT with the Bit_Number set to 32 (Isochronous
    #    Channels) and the Bit_Value set to 0b1. The Upper Tester receives an HCI_Command_Complete event from the IUT.
    success = set_isochronous_channels_host_support(transport, upper_tester, trace, 1) and success

    # 5. The IUT establishes an ACL connection with the Lower Tester as Peripheral.
    s, advertiser, initiator = establish_acl_connection(transport, lower_tester, upper_tester, trace)
    success = s and success
    if not initiator:
        return success

    # 6. The Upper Tester sends an HCI_LE_Set_Event_Mask command with all events enabled except the HCI_LE_CIS_Request
    #    event. The IUT sends a successful HCI_Command_Complete in response.
    def ut_set_event_mask(event_mask):
        status = le_set_event_mask(transport, upper_tester, event_mask, 100)
        return getCommandCompleteEvent(transport, upper_tester, trace) and status == 0x00

    success = ut_set_event_mask([0xFF, 0xFF, 0xFF, 0xFD, 0x07, 0x00, 0x00, 0x00]) and success

    # 7. Repeat step 1.
    success = lt_send_ll_cis_req(initiator.handles[0]) and success

    # 8. The IUT responds to the Lower Tester with an LL_REJECT_EXT_IND with a valid reason code.
    s, event = verifyAndFetchMetaEvent(transport, lower_tester, MetaEvents.BT_HCI_EVT_LE_CIS_ESTABLISHED, trace)
    success = s and (event.decode()[0] != 0x00) and success

    # 9. The Upper Tester does not receive an HCI_LE_CIS_Request event. Confirm for at least 5 seconds.
    s, _, _, _, _ = hasLeCisRequestMetaEvent(transport, upper_tester, trace, 5000)
    success = not s and success

    # 10. The Upper Tester sends an HCI_LE_Set_Event_Mask command with all events enabled including the
    #     HCI_LE_CIS_Request event. The IUT sends a successful HCI_Command_Complete in response.
    success = ut_set_event_mask([0xFF, 0xFF, 0xFF, 0xFF, 0x07, 0x00, 0x00, 0x00]) and success

    # 11. Repeat step 1.
    success = lt_send_ll_cis_req(initiator.handles[0]) and success

    # 12. The Upper Tester receives an HCI_LE_CIS_Request event.
    s, _, _, _, _ = hasLeCisRequestMetaEvent(transport, upper_tester, trace, 5000)
    success = s and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


"""
    LL/CIS/PER/BV-23-C [CIS Setup Response Procedure, Peripheral]
"""
def ll_cis_per_bv_23_c(transport, upper_tester, lower_tester, trace):
    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 11250,  # 11.25 ms
        SDU_Interval_P_To_C     = 11250,  # 11.25 ms
        ISO_Interval            = int(11.25 // 1.25),  # 11.25 ms
        NSE                     = 4,
        Max_PDU_C_To_P          = 100,
        Max_PDU_P_To_C          = 100,
        PHY_C_To_P              = 2,
        PHY_P_To_C              = 1,
        FT_C_To_P               = 3,
        FT_P_To_C               = 2,
        BN_C_To_P               = 3,
        BN_P_To_C               = 2,
    )

    return cis_setup_response_procedure_peripheral(transport, upper_tester, lower_tester, trace, params)


"""
    LL/CIS/PER/BV-29-C [CIS Setup Response Procedure, Peripheral]
"""
def ll_cis_per_bv_29_c(transport, upper_tester, lower_tester, trace):
    params = SetCIGParameters(
        Max_PDU_C_To_P          = 128,
        Max_PDU_P_To_C          = 128,
        PHY_C_To_P              = 2,
        PHY_P_To_C              = 2,
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        BN_P_To_C               = 1,
    )

    return cis_setup_response_procedure_peripheral(transport, upper_tester, lower_tester, trace, params)


"""
    LL/CIS/PER/BV-31-C [Sending and Receiving Data in Multiple CISes, Single CIG, Single Connection, Interleaved CIG,
                        Peripheral, NSE=2]
"""
def ll_cis_per_bv_31_c(transport, upper_tester, lower_tester, trace):
    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 50000,  # 50 ms
        SDU_Interval_P_To_C     = 50000,  # 50 ms
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        ISO_Interval            = int(100 // 1.25),  # 100 ms
        Packing                 = 1,
        CIS_Count               = 2,
        NSE                     = 2,
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        BN_C_To_P               = 2,
        BN_P_To_C               = 2,
    )

    success = test_sending_and_receiving_data_in_multiple_cises(transport, lower_tester, upper_tester, trace, params, 2)

    return success


"""
    LL/CIS/PER/BV-32-C [Sending and Receiving Data in Multiple CISes, Single CIG, Single Connection, Peripheral, BN=1]
"""
def ll_cis_per_bv_32_c(transport, upper_tester, lower_tester, trace):
    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 50000,  # 50 ms
        SDU_Interval_P_To_C     = 50000,  # 50 ms
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        ISO_Interval            = int(50 // 1.25),  # 50 ms
        Packing                 = 1,  # Interleaved
        CIS_Count               = 2,
        NSE                     = 1,
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        BN_C_To_P               = 1,
        BN_P_To_C               = 1,
    )

    success = test_sending_and_receiving_data_in_multiple_cises(transport, lower_tester, upper_tester, trace, params, 1)

    return success


def test_sending_and_receiving_data_in_bidirectional_cis_bn_1(transport, central, peripheral, trace, enc_keys=None):
    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 100000,  # 100 ms
        SDU_Interval_P_To_C     = 100000,  # 100 ms
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        ISO_Interval            = int(100 // 1.25),  # 100 ms
        NSE                     = 1,
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        BN_C_To_P               = 1,
        BN_P_To_C               = 1,
    )

    success, initiator, (peripheral_cis_handle,), (central_cis_handle,) = \
        state_connected_isochronous_stream(transport, peripheral, central, trace, params, enc_keys=enc_keys)
    if not initiator:
        return success

    # The SDU is equal for both devices
    assert params.Max_SDU_C_To_P[0] == params.Max_SDU_P_To_C[0]

    iso_data_sdu = tuple([0xD7] * params.Max_SDU_C_To_P[0])

    success = iso_send_payload_pdu(transport, peripheral, central, trace, peripheral_cis_handle,
                                   params.Max_SDU_P_To_C[0], params.SDU_Interval_P_To_C, 0, iso_data_sdu) and success

    success = iso_send_payload_pdu(transport, central, peripheral, trace, central_cis_handle,
                                   params.Max_SDU_C_To_P[0], params.SDU_Interval_C_To_P, 0, iso_data_sdu) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


"""
    LL/CIS/PER/BV-35-C [Sending and Receiving Data in Bidirectional CIS, BN = 1]
"""
def ll_cis_per_bv_35_c(transport, upper_tester, lower_tester, trace):
    return test_sending_and_receiving_data_in_bidirectional_cis_bn_1(transport, lower_tester, upper_tester, trace)


"""
    LL/CIS/PER/BV-36-C [Sending and Receiving Data in Bidirectional CIS, BN = 1, Encrypted]
"""
def ll_cis_per_bv_36_c(transport, upper_tester, lower_tester, trace):
    return test_sending_and_receiving_data_in_bidirectional_cis_bn_1(transport, lower_tester, upper_tester, trace,
                                                                     ENC_KEYS)


"""
    LL/CIS/PER/BV-33-C [Sending Data in Unidirectional CIS, BN = 1, Peripheral]
"""
def ll_cis_per_bv_33_c(transport, upper_tester, lower_tester, trace):
    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 100000,  # 100 ms
        SDU_Interval_P_To_C     = 100000,  # 100 ms
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        ISO_Interval            = int(100 // 1.25),  # 100 ms
        CIS_Count               = 1,
        NSE                     = 1,
        Max_PDU_C_To_P          = 0,
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        BN_C_To_P               = 0,
        BN_P_To_C               = 1,
    )

    success, initiator, (cis_conn_handle,), _ = \
        state_connected_isochronous_stream(transport, upper_tester, lower_tester, trace, params)
    if not initiator:
        return success

    success = iso_send_payload_pdu(transport, upper_tester, lower_tester, trace, cis_conn_handle,
                                   params.Max_SDU_P_To_C[0], params.SDU_Interval_P_To_C, 0) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


"""
    LL/CIS/PER/BV-34-C [Receiving Data in Unidirectional CIS, BN = 1, Peripheral]
"""
def ll_cis_per_bv_34_c(transport, upper_tester, lower_tester, trace):
    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 100000,  # 100 ms
        SDU_Interval_P_To_C     = 100000,  # 100 ms
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        ISO_Interval            = int(100 // 1.25),  # 100 ms
        CIS_Count               = 1,
        NSE                     = 1,
        Max_PDU_P_To_C          = 0,
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        BN_C_To_P               = 1,
        BN_P_To_C               = 0,
    )

    success, initiator, _, (cis_conn_handle,) = \
        state_connected_isochronous_stream(transport, upper_tester, lower_tester, trace, params)
    if not initiator:
        return success

    success = iso_send_payload_pdu(transport, lower_tester, upper_tester, trace, cis_conn_handle,
                                   params.Max_SDU_C_To_P[0], params.SDU_Interval_C_To_P, 0) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


"""
    LL/CIS/PER/BV-39-C [CIS Peripheral Accepts All Supported NSE Values]
"""
def ll_cis_per_bv_39_c(transport, upper_tester, lower_tester, trace):
    # Initial Condition
    #
    # The Isochronous Channels (Host Support) FeatureSet bit is set.
    success = set_isochronous_channels_host_support(transport, upper_tester, trace, 1)
    success = set_isochronous_channels_host_support(transport, lower_tester, trace, 1) and success

    # An ACL connection has been established between the IUT and the Lower Tester with a valid Connection Handle.
    s, advertiser, initiator = establish_acl_connection(transport, lower_tester, upper_tester, trace)
    success = s and success
    if not initiator:
        return success

    max_sdu_length = get_ixit_value(transport, upper_tester, IXITS["TSPX_max_sdu_length"], 100)
    max_cis_bn = get_ixit_value(transport, upper_tester, IXITS["TSPX_max_cis_bn"], 100)

    # 1. Test_BN represents the BN and NSE values for each round, and its initial value is 1.
    test_bn = 1
    while True:
        # 2. The Lower Tester sends an LL_CIS_REQ to the IUT with BN_C_To_P, BN_P_To_C, and NSE set to Test_BN.
        #    FT_C_To_P and FT_P_To_C are 1. ISO_Interval is a valid value and at least 200 ms. All other values are
        #    valid values, and Max_SDU_C_To_P and Max_SDU_P_To_C are no greater than TSPX_max_sdu_length.
        #    The parameters are configured such that each PDU contains a single SDU.
        max_pdu = min(64, max_sdu_length)

        # BN = ceil(Max_SDU / Max_PDU) * (ISO_Interval / SDU_Interval), where Max_SDU == Max_PDU, thus
        iso_interval = 200
        r = iso_interval % test_bn
        if r != 0:
            iso_interval += (test_bn - r)

        sdu_interval = int(iso_interval / test_bn)

        params = SetCIGParameters(
            SDU_Interval_C_To_P = sdu_interval * 1000,
            SDU_Interval_P_To_C = sdu_interval * 1000,
            ISO_Interval        = int(iso_interval // 1.25),
            NSE                 = test_bn,  # NSE set to Test_BN
            Max_PDU_C_To_P      = max_pdu,
            Max_PDU_P_To_C      = max_pdu,
            FT_C_To_P           = 1,
            FT_P_To_C           = 1,
            BN_C_To_P           = test_bn,
            BN_P_To_C           = test_bn,
            Max_SDU_Supported   = max_pdu,  # Each PDU contains a single SDU
        )

        # 3-10.
        s, (lower_tester_cis_handle,), (upper_tester_cis_handle,) = \
            establish_cis_connection(transport, lower_tester, upper_tester, trace, params, initiator.handles[0])
        success = s and success
        if not initiator:
            return success

        def iso_send_and_receive_payload_pdu(pkt_seq_num):
            # 11. The Lower Tester sends data packets to the IUT. All data packets contain data , and there are no
            #     zero length data packets.
            # 12. The Upper Tester receives ISO data from the IUT.
            success = iso_send_payload_pdu(transport, lower_tester, upper_tester, trace, lower_tester_cis_handle,
                                           params.Max_PDU_C_To_P[0], params.SDU_Interval_C_To_P, pkt_seq_num)

            # 13. The Upper Tester sends ISO data to the IUT sufficient to ensure that all data PDUs contain data
            #     and there are no zero length PDUs.
            # 14. The Lower Tester receives ISO data from the IUT.
            return iso_send_payload_pdu(transport, upper_tester, lower_tester, trace, upper_tester_cis_handle,
                                        params.Max_PDU_P_To_C[0], params.SDU_Interval_P_To_C, pkt_seq_num) and success

        # 15. Repeat steps 11–15 for 20 ISO intervals.
        for pkt_seq_num in range(20):
            success = iso_send_and_receive_payload_pdu(pkt_seq_num) and success
            if not success:
                break

        # 16. The Lower Tester sends an LL_CIS_TERMINATE_IND PDU to the IUT and receives an Ack from
        # the IUT.
        # LT - Initiate CIS Disconnection and verify command status
        status = disconnect(transport, lower_tester, lower_tester_cis_handle, 0x13, 200)
        success = verifyAndShowEvent(transport, lower_tester, Events.BT_HCI_EVT_CMD_STATUS, trace) and (status == 0) \
                  and success

        # LT - Verify HCI Disconnection Complete event parameters
        s, event = verifyAndFetchEvent(transport, lower_tester, Events.BT_HCI_EVT_DISCONN_COMPLETE, trace)
        status, handle, reason = event.decode()
        success = s and (status == 0x00) and handle == lower_tester_cis_handle and success

        # 17. The Upper Tester receives an HCI_Disconnection_Complete event from the IUT.
        s, event = verifyAndFetchEvent(transport, upper_tester, Events.BT_HCI_EVT_DISCONN_COMPLETE, trace)
        status, handle, reason = event.decode()
        success = s and (status == 0x00) and handle == upper_tester_cis_handle and success

        # Remove the CIG, since we are going to create the CIG with different parameters
        status, _ = le_remove_cig(transport, lower_tester, 0, 100)
        success = verifyAndShowEvent(transport, lower_tester, Events.BT_HCI_EVT_CMD_COMPLETE, trace) and status == 0 \
                  and success

        # 18. Test_BN is incremented by 1. If Test_BN exceeds TSPX_max_cis_bn, then the test is complete.
        #     If not, go to step 2 to execute the next round.
        test_bn += 1
        if test_bn > max_cis_bn or not success:
            break

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


"""
    LL/CIS/PER/BV-40-C [CIS Setup Response Procedure, Peripheral]
"""
def ll_cis_per_bv_40_c(transport, upper_tester, lower_tester, trace):
    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 7500,  # 7.5 ms
        SDU_Interval_P_To_C     = 7500,  # 7.5 ms
        ISO_Interval            = int(7.5 // 1.25),  # 7.5
        NSE                     = 2,
        Max_PDU_C_To_P          = 160,
        Max_PDU_P_To_C          = 0,
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        BN_P_To_C               = 0,
    )

    return cis_setup_response_procedure_peripheral(transport, upper_tester, lower_tester, trace, params)


def cis_terminate_procedure_initiated(transport, upper_tester, lower_tester, trace, role, packets):
    assert role == "Peripheral" or role == "Central"
    params = SetCIGParameters(
            SDU_Interval_C_To_P     = 20000,
            SDU_Interval_P_To_C     = 20000,
            ISO_Interval            = int(20 // 1.25),
            NSE                     = 1,
            Max_SDU_C_To_P          = 130,
            Max_SDU_P_To_C          = 130,
            Max_PDU_C_To_P          = 130,
            Max_PDU_P_To_C          = 130,
            PHY_C_To_P              = 1,
            PHY_P_To_C              = 1,
            FT_C_To_P               = 1,
            FT_P_To_C               = 1,
            BN_C_To_P               = 1,
            BN_P_To_C               = 1,
    )

    if role == "Peripheral":
        success, initiator, (upper_tester_cis_handle,), (lower_tester_cis_handle,) = \
            state_connected_isochronous_stream(transport, upper_tester, lower_tester, trace, params)
    else:
        success, initiator, (lower_tester_cis_handle,), (upper_tester_cis_handle,) = \
            state_connected_isochronous_stream(transport, lower_tester, upper_tester, trace, params)

    if not initiator:
        return success

    # Test procedure
    # 1. A payload PDU and Ack is sent between the IUT and Lower Tester
    success = iso_send_payload_pdu(transport, lower_tester, upper_tester, trace, lower_tester_cis_handle,
                                   params.Max_SDU_C_To_P[0], params.SDU_Interval_C_To_P, 0) and success

    # 2. If IUT is Peripheral, skip to step 5.
    if role == "Central":
        # 3. The Upper Tester sends an HCI_LE_Remove_CIG command with the CIG_ID value obtained when the CIG was
        #       established.
        status, _ = le_remove_cig(transport, upper_tester, 0, 100)  # CIG_ID is hardcoded to 0
        # 4. The Upper Tester receives an HCI_Command_Complete event with error code Command Disallowed (0x0C).
        success = verifyAndShowEvent(transport, upper_tester, Events.BT_HCI_EVT_CMD_COMPLETE, trace) and success
        success = status == 0x0C and success

    # 5. The Upper Tester sends an HCI_Disconnect to the IUT and receives HCI_Command_status IUT.
    reason_code = 0x13
    status = disconnect(transport, upper_tester, upper_tester_cis_handle, reason_code, 200)
    success = verifyAndShowEvent(transport, upper_tester, Events.BT_HCI_EVT_CMD_STATUS, trace) and (status == 0) and success

    # 6. The Lower Tester receives an LL_CIS_TERMINATE_IND PDU from the IUT and the ErrorCode
    #        field in the CtrData field matches the Reason code value the Upper Tester sent in step 45.
    def check_ll_cis_terminate_ind():
        packet = packets.find('LL_CIS_TERMINATE_IND')
        return packet and packet.payload.CtrData.ErrorCode == reason_code
    # 7. The Lower Tester sends an Ack to the IUT.

    # 8. The Upper Tester receives an HCI_Disconnection_Complete event from the IUT.
    s, event = verifyAndFetchEvent(transport, upper_tester, Events.BT_HCI_EVT_DISCONN_COMPLETE, trace)
    status, handle, reason = event.decode()
    success = s and (status == 0x00) and handle == upper_tester_cis_handle and success

    success = verifyAndShowEvent(transport, lower_tester, Events.BT_HCI_EVT_DISCONN_COMPLETE, trace) and success

    # 9. If IUT is Central, proceed to step 10. If IUT is Peripheral, test is complete.
    if role == "Central":
        # 10. The Upper Tester sends an HCI_LE_Create_CIS command to the IUT with the CIS Connection_Handle in step 5
        #       and receives a successful HCI_Command_Status event from the IUT in response.
        success = le_create_cis(transport, upper_tester, 1, [upper_tester_cis_handle], [initiator.handles[0]], 100) == 0
        success = verifyAndShowEvent(transport, upper_tester, Events.BT_HCI_EVT_CMD_STATUS, trace) and success
        # 11. The IUT sends an LL_CIS_REQ PDU to the Lower Tester with all fields set to valid values.
        # 12. The Lower Tester sends an LL_CIS_RSP PDU to the IUT.
        # 13. The IUT sends an LL_CIS_IND PDU to the Lower Tester.
        # 14. The IUT sends a Null ISO Data packet to the Lower Tester.
        # 15. The Lower Tester sends an LL ACK to the IUT.
        # LT: Wait for HCI_EVT_LE_CIS_REQUEST
        s, event = verifyAndFetchMetaEvent(transport, lower_tester, MetaEvents.BT_HCI_EVT_LE_CIS_REQUEST, trace)
        success = s and success
        lower_tester_cis_handle = event.decode()[1]

        # LT: Accept CIS Request
        success = le_accept_cis_request(transport, lower_tester, lower_tester_cis_handle, 100) == 0 and success
        success = verifyAndShowEvent(transport, lower_tester, Events.BT_HCI_EVT_CMD_STATUS, trace) and success

        # 16. The IUT sends an HCI_LE_CIS_Established event to the Upper Tester with the CIS_Connection_Handle set to
        #       the value in step 10.
        s, event = verifyAndFetchMetaEvent(transport, upper_tester, MetaEvents.BT_HCI_EVT_LE_CIS_ESTABLISHED, trace, 2000)
        success = s and (event.decode()[0] == 0x00) and (event.decode()[1] == upper_tester_cis_handle) and success

        # LT: Wait for HCI_EVT_LE_CIS_ESTABLISHED
        s, event = verifyAndFetchMetaEvent(transport, lower_tester, MetaEvents.BT_HCI_EVT_LE_CIS_ESTABLISHED, trace)
        success = s and (event.decode()[0] == 0x00) and success

        # 17. The Upper Tester begins providing data to the IUT to send to the Lower Tester.
        # 18. The IUT sends the data to the Lower Tester.
        # 19. The Lower Tester sends isochronous data to the IUT.
        # 20. The IUT provides the Lower Tester’s isochronous data to the Upper Tester.
        success = iso_send_payload_pdu_parallel(transport, upper_tester, lower_tester, trace, upper_tester_cis_handle,
                                                lower_tester_cis_handle, params.Max_SDU_C_To_P[0],
                                                params.SDU_Interval_C_To_P, 0) and success

    ### LL VERIFICATION ###
    success = check_ll_cis_terminate_ind() and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def ll_cis_per_bv_12_c(transport, upper_tester, lower_tester, trace, packets):
    """LL/CIS/PER/BV-12-C [Cis Terminate Procedure, Initiated - Peripheral]"""
    return cis_terminate_procedure_initiated(transport, upper_tester, lower_tester, trace, "Peripheral", packets)


def cis_terminate_procedure_accepting(transport, upper_tester, lower_tester, trace, role):
    assert role == "Peripheral" or role == "Central"
    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 20000,  # 20 ms
        SDU_Interval_P_To_C     = 20000,  # 20 ms
        ISO_Interval            = int(20 // 1.25),  # 20 ms
        NSE                     = 1,
        Max_PDU_C_To_P          = 130,
        Max_PDU_P_To_C          = 130,
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        BN_P_To_C               = 1,
    )

    if role == "Peripheral":
        success, initiator, (upper_tester_cis_handle,), (lower_tester_cis_handle,) = \
            state_connected_isochronous_stream(transport, upper_tester, lower_tester, trace, params)
    else:
        success, initiator, (lower_tester_cis_handle,), (upper_tester_cis_handle,) = \
            state_connected_isochronous_stream(transport, lower_tester, upper_tester, trace, params)

    if not initiator:
        return success

    # Test Procedure
    # 1. A payload PDU and Ack is sent between the IUT and Lower Tester.
    success = iso_send_payload_pdu(transport, lower_tester, upper_tester, trace, lower_tester_cis_handle,
                                   params.Max_SDU_C_To_P[0], params.SDU_Interval_C_To_P, 0) and success

    # 2. The Lower Tester sends an LL_CIS_TERMINATE_IND PDU to the IUT and receives an Ack from the IUT.
    # LT - Initiate CIS Disconnection and verify command status
    status = disconnect(transport, lower_tester, lower_tester_cis_handle, 0x13, 200)
    success = verifyAndShowEvent(transport, lower_tester, Events.BT_HCI_EVT_CMD_STATUS, trace) and (status == 0) \
              and success

    # LT - Verify HCI Disconnection Complete event parameters
    s, event = verifyAndFetchEvent(transport, lower_tester, Events.BT_HCI_EVT_DISCONN_COMPLETE, trace)
    status, handle, reason = event.decode()
    success = s and (status == 0x00) and handle == lower_tester_cis_handle and success

    # 3. The Upper Tester receives an HCI_Disconnection_Complete event from the IUT.
    s, event = verifyAndFetchEvent(transport, upper_tester, Events.BT_HCI_EVT_DISCONN_COMPLETE, trace)
    status, handle, reason = event.decode()
    success = s and (status == 0x00) and handle == upper_tester_cis_handle and success

    # Pass verdict:
    # - In step 2, the IUT sends an Ack.
    # TODO: Verify Ack

    # - In step 3, the IUT sends an HCI_Disconnection_Complete event to the Upper Tester.
    # PASS

    # - The Lower Tester does not receive any payload PDUs from the IUT after step 3.
    success = not le_iso_data_ready(transport, lower_tester, 100) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def ll_cis_per_bv_13_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/PER/BV-13-C [CIS Terminate Procedure, Accepting, Peripheral]"""
    return cis_terminate_procedure_accepting(transport, upper_tester, lower_tester, trace, "Peripheral")


def iso_test_mode_common_procedure(transport, transmitter, receiver, trace, transmitter_cis_handle, receiver_cis_handle,
                                   payload_type):
    # 1. The Transmitter sends the HCI_LE_ISO_Transmit_Test command with PayloadType as specified in Table and
    # receives a successful HCI_Command_Complete event from the IUT in response.
    status, conn_handle = hci_le_iso_transmit_test(transport, transmitter, transmitter_cis_handle, payload_type, 100)
    success = (conn_handle == transmitter_cis_handle)

    success = getCommandCompleteEvent(transport, transmitter, trace) and success and status == 0x00

    # 1.X The Receiver sends the HCI_LE_ISO_Receive_Test command to the IUT with Payload_Type as specified in Table
    # and receives a successful HCI_Command_Complete event from the IUT in response.
    status, conn_handle = hci_le_iso_receive_test(transport, receiver, receiver_cis_handle, payload_type, 100)
    success = (conn_handle == receiver_cis_handle) and success

    success = getCommandCompleteEvent(transport, receiver, trace) and success and status == 0x00

    # 2. The IUT sends isochronous data PDUs with Payload.
    # The controller generates and sends test payloads

    # 3. Repeat step 2 for a total of 5 rounds of payloads.
    received_sdu_count = 0
    missed_sdu_count = 0
    failed_sdu_count = 0
    while ((received_sdu_count + missed_sdu_count + failed_sdu_count) < 5) and success:
        # The Receiver sends the HCI_LE_ISO_Read_Test_Counters command to the IUT.
        status, connection_handle, received_sdu_count, missed_sdu_count, failed_sdu_count = \
            hci_le_iso_read_test_counters_test(transport, receiver, receiver_cis_handle, 100)
        success = getCommandCompleteEvent(transport, receiver, trace) and success and status == 0x00

        # Core Version Sydney r11 | | Vol 6, Part B
        # Because the transmitter and receiver do not enter test mode simultaneously, it is not possible to
        # determine whether the first test SDU received was the first one sent. As a consequence, at the moment the
        # first valid test SDU is received (indicated by either Received_SDU_Count or Failed_SDU_Count being
        # incremented), the value of Missed_SDU_Count is unpredictable. Once a valid test SDU has been received,
        # any further changes in Missed_SDU_Count will be correct.
        if received_sdu_count == 0 and failed_sdu_count == 0:
            missed_sdu_count = 0

    success = received_sdu_count >= 5 and missed_sdu_count == 0 and failed_sdu_count == 0 and success

    # 4. The Receiver sends the HCI_LE_ISO_Test_End command to the IUT and receives an HCI_Command_Status event
    # from the IUT with the Status field set to Success.
    status, connection_handle, _, _, _ = hci_le_iso_test_end(transport, receiver, receiver_cis_handle, 100)
    success = getCommandCompleteEvent(transport, receiver, trace) and success and status == 0x00

    # 4.X The Transmitter sends the HCI_LE_ISO_Test_End command to the IUT and receives an HCI_Command_Status event
    # from the IUT with the Status field set to Success.
    status, connection_handle, _, _, _ = hci_le_iso_test_end(transport, transmitter, transmitter_cis_handle, 100)
    success = getCommandCompleteEvent(transport, transmitter, trace) and success and status == 0x00

    return success, received_sdu_count, missed_sdu_count, failed_sdu_count


def iso_transmit_test_mode_cis(transport, upper_tester, lower_tester, trace, is_upper_tester_central):
    params = SetCIGParameters()

    if is_upper_tester_central:
        success, initiator, (lower_tester_cis_handle,), (upper_tester_cis_handle,) = \
            state_connected_isochronous_stream(transport, lower_tester, upper_tester, trace, params,
                                               setup_iso_data_path=False)
    else:
        success, initiator, (upper_tester_cis_handle,), (lower_tester_cis_handle,) = \
            state_connected_isochronous_stream(transport, upper_tester, lower_tester, trace, params,
                                               setup_iso_data_path=False)
    if not initiator:
        return success

    testData = namedtuple('testData', 'Name, Payload_Type')
    rounds = [
        testData("Zero length payload", 0x00),
        testData("Variable length payload", 0x01),
        testData("Maximum length payload", 0x02),
    ]
    for name, payload_type in rounds:
        success, received_sdu_count, missed_sdu_count, failed_sdu_count = \
            iso_test_mode_common_procedure(transport, upper_tester, lower_tester, trace, upper_tester_cis_handle,
                                           lower_tester_cis_handle, payload_type)

        trace.trace(5, "%s done, received_sdu_count=%d missed_sdu_count=%d failed_sdu_count=%d" %
                    (name, received_sdu_count, missed_sdu_count, failed_sdu_count))

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def ll_ist_per_bv_01_c(transport, upper_tester, lower_tester, trace):
    """LL/IST/PER/BV-01-C [ISO Transmit Test Mode, CIS]"""
    return iso_transmit_test_mode_cis(transport, upper_tester, lower_tester, trace, False)


def iso_receive_test_mode_cis(transport, upper_tester, lower_tester, trace, is_upper_tester_central):
    def establish_acl_and_cis(framing):
        params = SetCIGParameters(
            Framing                 = framing,
            SDU_Interval_C_To_P     = 400000,  # 400 ms
            SDU_Interval_P_To_C     = 400000,  # 400 ms
            ISO_Interval            = int(400 // 1.25),  # 400 ms
        )

        if is_upper_tester_central:
            success, initiator, (lower_tester_cis_handle,), (upper_tester_cis_handle,) = \
                state_connected_isochronous_stream(transport, lower_tester, upper_tester, trace, params,
                                                   setup_iso_data_path=False)
        else:
            success, initiator, (upper_tester_cis_handle,), (lower_tester_cis_handle,) = \
                state_connected_isochronous_stream(transport, upper_tester, lower_tester, trace, params,
                                                   setup_iso_data_path=False)

        return success and initiator, initiator, upper_tester_cis_handle, lower_tester_cis_handle

    testData = namedtuple('testData', 'Name, Framing, Payload_Type')
    rounds = [
        testData("Zero length payload unframed", 0, 0x00),
        testData("Variable length payload unframed", 0, 0x01),
        testData("Maximum length payload unframed", 0, 0x02),
        testData("Maximum length payload framed", 1, 0x02),
        testData("Variable length payload framed", 1, 0x01),
    ]
    previous = rounds[0]
    success, initiator, upper_tester_cis_handle, lower_tester_cis_handle = establish_acl_and_cis(previous.Framing)
    for current in rounds:
        # When Framing is changing between rounds, Isochronous link needs to be terminated and re-established with
        # correct Framing, as framing cannot be changed after creation.
        if current.Framing != previous.Framing:
            success = initiator.disconnect(0x13) and success

            if is_upper_tester_central:
                status, _ = le_remove_cig(transport, upper_tester, 0, 100)
                success = getCommandCompleteEvent(transport, upper_tester, trace) and status == 0x00 and success
            else:
                status, _ = le_remove_cig(transport, lower_tester, 0, 100)
                success = getCommandCompleteEvent(transport, lower_tester, trace) and status == 0x00 and success

            s, initiator, upper_tester_cis_handle, lower_tester_cis_handle = establish_acl_and_cis(current.Framing)
            success = s and success

        s, received_sdu_count, missed_sdu_count, failed_sdu_count = \
            iso_test_mode_common_procedure(transport, lower_tester, upper_tester, trace, lower_tester_cis_handle,
                                           upper_tester_cis_handle, current.Payload_Type)
        success = s and success

        previous = current

        trace.trace(5, "%s done, received_sdu_count=%d missed_sdu_count=%d failed_sdu_count=%d" %
                    (current.Name, received_sdu_count, missed_sdu_count, failed_sdu_count))

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def ll_ist_per_bv_03_c(transport, upper_tester, lower_tester, trace):
    """LL/IST/PER/BV-03-C [ISO Receive Test Mode, CIS]"""
    return iso_receive_test_mode_cis(transport, upper_tester, lower_tester, trace, False)


def cis_setup_procedure_central_initiated(transport, upper_tester, lower_tester, trace, params):
    success, initiator, (cis_handle,), _ = \
        state_connected_isochronous_stream(transport, lower_tester, upper_tester, trace, params)

    def lt_send_data_packet(pkt_seq_num):
        return iso_send_payload_pdu(transport, upper_tester, lower_tester, trace, cis_handle,
                                    params.Max_SDU_C_To_P[0], params.SDU_Interval_C_To_P, pkt_seq_num)

    for j in range(50 // params.BN_C_To_P[0]):
        success = lt_send_data_packet(j) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def ll_cis_cen_bv_01_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-01-C [CIS Setup Procedure, Central Initiated]"""
    max_cis_nse = get_ixit_value(transport, upper_tester, IXITS["TSPX_max_cis_nse"], 100)
    params = SetCIGParameters(
        PHY_C_To_P              = 1,
        BN_C_To_P               = 2,
        FT_C_To_P               = 1,
        Max_PDU_C_To_P          = 130,
        PHY_P_To_C              = 1,
        BN_P_To_C               = 2,
        FT_P_To_C               = 1,
        Max_PDU_P_To_C          = 130,
        NSE                     = min(4, max_cis_nse),
        SDU_Interval_C_To_P     = 0x2710,  # 10 ms
        SDU_Interval_P_To_C     = 0x2710,  # 10 ms
        ISO_Interval            = 0x10,  # 20 ms
    )

    return cis_setup_procedure_central_initiated(transport, upper_tester, lower_tester, trace, params)


def ll_cis_cen_bv_02_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-02-C [CIS Setup Procedure, Central Initiated]"""
    max_cis_nse = get_ixit_value(transport, upper_tester, IXITS["TSPX_max_cis_nse"], 100)
    params = SetCIGParameters(
        PHY_C_To_P              = 2,
        BN_C_To_P               = 2,
        FT_C_To_P               = 2,
        Max_PDU_C_To_P          = 251,
        PHY_P_To_C              = 2,
        BN_P_To_C               = 2,
        FT_P_To_C               = 1,
        Max_PDU_P_To_C          = 251,
        NSE                     = min(4, max_cis_nse),
        SDU_Interval_C_To_P     = 0x4E20,  # 20 ms
        SDU_Interval_P_To_C     = 0x2710,  # 10 ms
        ISO_Interval            = 0x10,  # 20 ms
    )

    return cis_setup_procedure_central_initiated(transport, upper_tester, lower_tester, trace, params)


def ll_cis_cen_bv_31_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-31-C [CIS Setup Procedure, Central Initiated]"""
    max_cis_nse = get_ixit_value(transport, upper_tester, IXITS["TSPX_max_cis_nse"], 100)
    params = SetCIGParameters(
        PHY_C_To_P              = 2,
        BN_C_To_P               = 2,
        FT_C_To_P               = 1,
        Max_PDU_C_To_P          = 130,
        PHY_P_To_C              = 1,
        BN_P_To_C               = 2,
        FT_P_To_C               = 1,
        Max_PDU_P_To_C          = 130,
        NSE                     = min(4, max_cis_nse),
        SDU_Interval_C_To_P     = 0x2710,  # 10 ms
        SDU_Interval_P_To_C     = 0x2710,  # 10 ms
        ISO_Interval            = 0x10,  # 20 ms
    )

    return cis_setup_procedure_central_initiated(transport, upper_tester, lower_tester, trace, params)


def ll_cis_cen_bv_39_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-39-C [CIS Setup Procedure, Central Initiated]"""
    params = SetCIGParameters(
        PHY_C_To_P              = 2,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        Max_PDU_C_To_P          = 130,
        PHY_P_To_C              = 2,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        Max_PDU_P_To_C          = 50,
        NSE                     = 1,
        SDU_Interval_C_To_P     = 0x4E20,  # 20 ms
        SDU_Interval_P_To_C     = 0x4E20,  # 20 ms
        ISO_Interval            = 0x10,  # 20 ms
    )

    return cis_setup_procedure_central_initiated(transport, upper_tester, lower_tester, trace, params)


def ll_cis_cen_bv_03_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-03-C [CIS Setup Procedure, Central Initiated, Rejected]"""
    return cis_setup_peripheral_rejected(transport, lower_tester, upper_tester, trace)


def ll_cis_cen_bv_04_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-04-C [New Channel Map]"""
    max_cis_nse = get_ixit_value(transport, upper_tester, IXITS["TSPX_max_cis_nse"], 100)
    return test_cis_map_update(transport, lower_tester, upper_tester, trace, 2, min(3, max_cis_nse), 100000)


def ll_cis_cen_bv_40_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-40-C [New Channel Map]"""
    return test_cis_map_update(transport, lower_tester, upper_tester, trace, 1, 1, 200000)


def ll_cis_cen_bv_07_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-07-C [Sending and Receiving Data in Bidirectional CIS]"""
    return test_sending_and_receiving_data_in_bidirectional_cis(transport, upper_tester, lower_tester, trace)


def ll_cis_cen_bv_35_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-35-C [Sending and Receiving Data in Bidirectional CIS, Encryption]"""
    return test_sending_and_receiving_data_in_bidirectional_cis(transport, upper_tester, lower_tester, trace, ENC_KEYS)


def ll_cis_cen_bv_47_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-47-C [Sending and Receiving Data in Bidirectional CIS, BN = 1]"""
    return test_sending_and_receiving_data_in_bidirectional_cis_bn_1(transport, upper_tester, lower_tester, trace)


def ll_cis_cen_bv_48_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-48-C [Sending and Receiving Data in Bidirectional CIS, BN = 1, Encryption]"""
    return test_sending_and_receiving_data_in_bidirectional_cis_bn_1(transport, upper_tester, lower_tester, trace,
                                                                     ENC_KEYS)


def ll_cis_cen_bv_45_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-45-C [Sending Data in Unidirectional CIS, BN = 1]"""
    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 0x186A0,  # 100 ms
        SDU_Interval_P_To_C     = 0x186A0,  # 100 ms
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        ISO_Interval            = 0x50,  # 100 ms
        CIS_Count               = 1,
        NSE                     = 1,
        Max_PDU_C_To_P          = 251,
        Max_PDU_P_To_C          = 0,
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        BN_C_To_P               = 1,
        BN_P_To_C               = 0,
    )

    success, initiator, _, (cis_conn_handle,) = \
        state_connected_isochronous_stream(transport, lower_tester, upper_tester, trace, params)
    if not initiator:
        return success

    success = iso_send_payload_pdu(transport, upper_tester, lower_tester, trace, cis_conn_handle,
                                   params.Max_SDU_C_To_P[0], params.SDU_Interval_C_To_P, 0) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def ll_cis_cen_bv_06_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-06-C [Receiving Data in Unidirectional CIS]"""
    max_cis_nse = get_ixit_value(transport, upper_tester, IXITS["TSPX_max_cis_nse"], 100)
    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 0xC350,  # 50 ms
        SDU_Interval_P_To_C     = 0xC350,  # 50 ms
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        ISO_Interval            = 0x50,  # 100 ms
        CIS_Count               = 1,
        NSE                     = min(4, max_cis_nse),
        Max_PDU_C_To_P          = 0,
        # Max_PDU_P_To_C          = default,
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        BN_C_To_P               = 0,
        BN_P_To_C               = 2,
    )

    success, initiator, (cis_conn_handle,), _ = \
        state_connected_isochronous_stream(transport, lower_tester, upper_tester, trace, params)
    if not initiator:
        return success

    for seq_num in range(2):
        success = iso_send_payload_pdu(transport, lower_tester, upper_tester, trace, cis_conn_handle,
                                       params.Max_SDU_P_To_C[0], params.SDU_Interval_P_To_C, seq_num) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def ll_cis_cen_bv_46_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-46-C [Receiving Data in Unidirectional CIS, BN = 1]"""
    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 0x186A0,  # 100 ms
        SDU_Interval_P_To_C     = 0x186A0,  # 100 ms
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        ISO_Interval            = 0x50,  # 100 ms
        CIS_Count               = 1,
        NSE                     = 1,
        Max_PDU_C_To_P          = 0,
        Max_PDU_P_To_C          = 251,
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        BN_C_To_P               = 0,
        BN_P_To_C               = 1,
    )

    success, initiator, (cis_conn_handle,), _ = \
        state_connected_isochronous_stream(transport, lower_tester, upper_tester, trace, params)
    if not initiator:
        return success

    success = iso_send_payload_pdu(transport, lower_tester, upper_tester, trace, cis_conn_handle,
                                   params.Max_SDU_P_To_C[0], params.SDU_Interval_P_To_C, 0) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def central_send_and_receive_data_in_multi_cises_single_cig_single_conn_interleaved(transport, central, peripheral,
                                                                                    trace, bn, sdu_interval, nse):
    params = SetCIGParameters(
        SDU_Interval_C_To_P     = sdu_interval,
        SDU_Interval_P_To_C     = sdu_interval,
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        ISO_Interval            = 0x50,  # 100 ms
        Packing                 = 1,  # Interleaved
        CIS_Count               = 2,
        NSE                     = nse,
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        BN_C_To_P               = bn,
        BN_P_To_C               = bn,
    )

    return test_sending_and_receiving_data_in_multiple_cises(transport, central, peripheral, trace, params, 1)


def ll_cis_cen_bv_08_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-08-C [Sending and Receiving Data in Multiple CISes, Single CIG, Single Connection, Interleaved CIG,
     Central]"""
    return central_send_and_receive_data_in_multi_cises_single_cig_single_conn_interleaved(
        transport, upper_tester, lower_tester, trace, 2, 0xC350, 4)


def ll_cis_cen_bv_43_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-43-C [Sending and Receiving Data in Multiple CISes, Single CIG, Single Connection, Interleaved CIG,
     Central]"""
    return central_send_and_receive_data_in_multi_cises_single_cig_single_conn_interleaved(
        transport, upper_tester, lower_tester, trace, 1, 0x186A0, 1)


def ll_cis_cen_bv_44_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-44-C [Sending and Receiving Data in Multiple CISes, Single CIG, Single Connection, Interleaved CIG,
     Central, BN > 1, NSE = 2]"""
    return central_send_and_receive_data_in_multi_cises_single_cig_single_conn_interleaved(
        transport, upper_tester, lower_tester, trace, 2, 0x0C350, 2)


def ll_cis_cen_bv_09_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-09-C [Sending and Receiving Data in Multiple CISes, Single CIG, Single Connection, Sequential,
     Central]"""
    max_cis_nse = get_ixit_value(transport, upper_tester, IXITS["TSPX_max_cis_nse"], 100)
    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 0x0C350,  # 50 ms
        SDU_Interval_P_To_C     = 0x186A0,  # 100 ms
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        ISO_Interval            = 0x50,  # 100 ms
        Packing                 = 0,  # Sequential
        CIS_Count               = 2,
        NSE                     = min(max_cis_nse, 4),
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        BN_C_To_P               = 2,
        BN_P_To_C               = 1,
    )

    return test_sending_and_receiving_data_in_multiple_cises(transport, upper_tester, lower_tester, trace, params, 2)


def ll_cis_cen_bv_24_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-24-C [CIS Updating Peer Clock Accuracy]"""
    return cis_updating_peer_clock_accuracy(transport, upper_tester, lower_tester, trace, "Central")


def ll_cis_cen_bv_15_c(transport, upper_tester, lower_tester, trace, packets):
    """LL/CIS/CEN/BV-15-C [CIS Terminate Procedure, Initiated]"""
    return cis_terminate_procedure_initiated(transport, upper_tester, lower_tester, trace, "Central", packets)


def ll_cis_cen_bv_16_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-16-C [CIS Terminate Procedure, Accepting]"""
    return cis_terminate_procedure_accepting(transport, upper_tester, lower_tester, trace, "Central")


def ll_cis_cen_bv_30_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-30-C [Isochronous Channels Host Support Feature Bit]"""
    params = SetCIGParameters()
    success = set_isochronous_channels_host_support(transport, lower_tester, trace, 0b1)

    # 1. The Upper Tester sends an HCI_LE_Set_Host_Feature with Bit_Number set to 30 (not a host controlled feature bit)
    #       and Bit_Value set to 0b1. The Upper Tester receives an HCI_Command_Complete response with an error code
    #       Unsupported Feature or Parameter Value (0x11).
    status = le_set_host_feature(transport, upper_tester, FeatureSupport.ISOCHRONOUS_BROADCASTER, 0b1, 100)
    success = getCommandCompleteEvent(transport, upper_tester, trace) and status == 0x11 and success

    # 2. The IUT establishes an ACL connection with the Lower Tester as Peripheral.
    s, _, initiator = establish_acl_connection(transport, upper_tester, lower_tester, trace)
    success = s and success
    if not initiator:
        return False

    # 3. The Upper Tester sends an HCI_LE_Set_Host_Feature with Bit_Number set to 32 (Isochronous Channels feature bit)
    #       and Bit_Value set to 0b1. The Upper Tester receives an HCI_Command_Complete response with an error code
    #       Command Disallowed (0x0C).
    status = le_set_host_feature(transport, upper_tester, FeatureSupport.ISOCHRONOUS_CHANNELS, 0b1, 100)
    success = getCommandCompleteEvent(transport, upper_tester, trace) and status == 0x0C and success

    # 4. The IUT disconnects the ACL connection from the Lower Tester.
    success = initiator.disconnect(0x13) and success

    testData = namedtuple('testData', 'Set_Feature_Enable, Bit_Value, CIS_Created')
    table = [
        testData(False, None, False),
        testData(True, 0b1, True),
        testData(True, 0b0, False),
    ]

    # 5. Repeat steps 6–13 for each round specified in Table
    for set_feature_enable, bit_value, cis_created in table:
        # 6. If the table indicates “Set Feature Enable” is true for this round, then the Upper Tester sends an
        #       HCI_LE_Set_Host_Feature command to the IUT with the Bit_Number set to 32 (Isochronous Channels) and the
        #       Bit_Value set to the value specified in the table. The Upper Tester receives an HCI_Command_Complete
        #       event from the IUT.
        if set_feature_enable:
            status = le_set_host_feature(transport, upper_tester, FeatureSupport.ISOCHRONOUS_CHANNELS, bit_value, 100)
            success = getCommandCompleteEvent(transport, upper_tester, trace) and status == 0x00 and success

        # 7. The IUT establishes an ACL connection with the Lower Tester as Peripheral.
        s, _, initiator = establish_acl_connection(transport, upper_tester, lower_tester, trace)
        success = s and success
        if not initiator:
            return False

        # 8. The Upper Tester sends an HCI_LE_Set_CIG_Parameters command to the IUT using the default parameters
        #       specified in Section 4.10.1.3 Default Values for Set CIG Parameters Commands and receives a successful
        #       HCI_Command_Complete event.
        status, cig_id, cis_count, cis_handles = le_set_cig_parameters_test(transport, upper_tester, 0,
                                                                            *params.get_cig_parameters_test(), 100)
        success = getCommandCompleteEvent(transport, upper_tester, trace) and status == 0x00 and success

        # 9. The Upper Tester sends an HCI_LE_Create_CIS command with the ACL_Connection_Handle of the established ACL
        #       and valid Connection_Handle
        status = le_create_cis(transport, upper_tester, cis_count, cis_handles, cis_count * [initiator.handles[0]], 100)
        success = verifyAndShowEvent(transport, upper_tester, Events.BT_HCI_EVT_CMD_STATUS, trace) and success

        if cis_created:
           # 10. The Upper Tester receives a successful HCI_Command_Status event.
           success = status == 0x00 and success

           # 11. The IUT establishes a CIS with the Lower Tester.
           s, event = verifyAndFetchMetaEvent(transport, lower_tester, MetaEvents.BT_HCI_EVT_LE_CIS_REQUEST, trace)
           success = s and success

           status = le_accept_cis_request(transport, lower_tester, event.decode()[1], 100)
           s = verifyAndShowEvent(transport, lower_tester, Events.BT_HCI_EVT_CMD_STATUS, trace)
           success = status == 0 and s and success

           s, event = verifyAndFetchMetaEvent(transport, upper_tester, MetaEvents.BT_HCI_EVT_LE_CIS_ESTABLISHED, trace,
                                              2000)
           success = s and (event.decode()[0] == 0x00) and success

           s, event = verifyAndFetchMetaEvent(transport, lower_tester, MetaEvents.BT_HCI_EVT_LE_CIS_ESTABLISHED, trace)
           success = s and (event.decode()[0] == 0x00) and success
        else:
            # 10. The Upper Tester receives an HCI_Command_Status event with the status set to error code Command
            #       Disallowed (0x0C).
            success = status == 0x0C and success

        # 12. The IUT disconnects the ACL connection from the Lower Tester.
        success = initiator.disconnect(0x13) and success

        # 13. If the table indicates that a CIS is not created this round, then the Upper Tester sends an
        #       HCI_LE_Remove_CIG command to the IUT with the CIG_ID set to the CIG_ID in step 8 and receives
        #       a successful HCI_Command_Complete event.
        if not cis_created:
            status, _ = le_remove_cig(transport, upper_tester, 0, 100)
            success = getCommandCompleteEvent(transport, upper_tester, trace) and status == 0x00 and success

    return success


def ll_cis_cen_bv_20_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-20-C [Set Encryption After CIS Established]"""
    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 0x4E20,  # 20 ms
        SDU_Interval_P_To_C     = 0x4E20,  # 20 ms
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        ISO_Interval            = 0x10,  # 20 ms
        CIS_Count               = 1,
        NSE                     = 1,
        Max_PDU_C_To_P          = 130,
        Max_PDU_P_To_C          = 130,
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        BN_C_To_P               = 1,
        BN_P_To_C               = 1,
    )

    success, initiator, _, _ = \
        state_connected_isochronous_stream(transport, lower_tester, upper_tester, trace, params,
                                           setup_iso_data_path=False, enc_keys=None)
    if not initiator:
        return False

    rand, ediv, ltk = ENC_KEYS
    status = le_start_encryption(transport, upper_tester, initiator.handles[0], rand, ediv, ltk, 100)
    success = verifyAndShowEvent(transport, upper_tester, Events.BT_HCI_EVT_CMD_STATUS, trace, 1000) and status == 0x0C

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def ll_cis_cen_bv_51_c(transport, upper_tester, lower_tester, trace):
    """LL/CIS/CEN/BV-51-C [CIS Setup Procedure, Central Initiated, CIG ID Reuse]"""
    params = SetCIGParameters(
        CIS_Count               = 2,
    )

    success, initiator, _, (connection_handle_1, connection_handle_2) = \
        state_connected_isochronous_stream(transport, lower_tester, upper_tester, trace, params)

    if not initiator:
        return False

    # 2. The Upper Tester sends an HCI_Disconnect command to the IUT with Connection_Handle_1 and Reason Code set to
    #       any valid value.
    # 3. The IUT sends a successful HCI_Command_Status event to the Upper Tester.
    # 4. The IUT sends an LL_CIS_TERMINATE_IND PDU to the Lower Tester with the ErrorCode field in the CtrData field
    #       set to match the Reason Code value in step 2.
    # 5. The Lower Tester sends an Ack to the IUT.
    success = disconnect(transport, upper_tester, connection_handle_1, 0x13, 200) == 0 and success
    success = verifyAndShowEvent(transport, upper_tester, Events.BT_HCI_EVT_CMD_STATUS, trace) and success

    # 6. The IUT sends a successful HCI_Disconnection_Complete event to the Upper Tester with Connection_Handle_1
    #       and Reason Code set to Connection Terminated by Local Host (0x16).
    s, event = verifyAndFetchEvent(transport, upper_tester, Events.BT_HCI_EVT_DISCONN_COMPLETE, trace)
    status, handle, reason = event.decode()
    success = s and status == 0x00 and handle == connection_handle_1 and success and reason == 0x16

    success = verifyAndShowEvent(transport, lower_tester, Events.BT_HCI_EVT_DISCONN_COMPLETE, trace) and success

    # 8. The IUT sends an LL_CIS_REQ PDU to the Lower Tester with CIG_ID set to CIG_ID_1 and CIS_ID set to CIS_ID_1.
    #       The re-created CIS may be different from the CIS disconnected previously using Connection_Handle_1,
    #       but it still complies with the Default Values for Set CIG Parameters Commands.
    status = le_create_cis(transport, lower_tester, 1, [connection_handle_1], [initiator.handles[0]], 100)
    success = status == 0 and success
    success = verifyAndShowEvent(transport, lower_tester, Events.BT_HCI_EVT_CMD_STATUS, trace) and success

    # 9. The Lower Tester sends an LL_CIS_RSP PDU to the IUT.
    # 10. The IUT sends an LL_CIS_IND PDU to the Lower Tester. The Access Address provided in CtrData is different from
    #       AA_1. The new Access Address is identified as AA_1new.
    # 11. The IUT sends an ISO Data Packet to the Lower Tester.
    # 12. The Lower Tester sends an LL Ack to the IUT.
    # 13. The IUT sends an HCI_LE_CIS_Established event to the Upper Tester with Status set to 0x00 and
    #       Connection_Handle set to Connection_Handle_1.
    s, event = verifyAndFetchMetaEvent(transport, lower_tester, MetaEvents.BT_HCI_EVT_LE_CIS_REQUEST, trace)
    success = s and success

    status = le_accept_cis_request(transport, lower_tester, event.decode()[1], 100)
    s = verifyAndShowEvent(transport, lower_tester, Events.BT_HCI_EVT_CMD_STATUS, trace)
    success = status == 0 and s and success

    s, event = verifyAndFetchMetaEvent(transport, upper_tester, MetaEvents.BT_HCI_EVT_LE_CIS_ESTABLISHED, trace,
                                       2000)
    success = s and (event.decode()[0] == 0x00) and success

    s, event = verifyAndFetchMetaEvent(transport, lower_tester, MetaEvents.BT_HCI_EVT_LE_CIS_ESTABLISHED, trace)
    success = s and (event.decode()[0] == 0x00) and success

    # 14. The Upper Tester sends an HCI_Disconnect command to the IUT with Connection_Handle_1 and Reason Code set to
    #       any valid value.
    # 15. The IUT sends a successful HCI_Command_Status event to the Upper Tester.
    success = disconnect(transport, upper_tester, connection_handle_1, 0x13, 200) == 0 and success
    success = verifyAndShowEvent(transport, upper_tester, Events.BT_HCI_EVT_CMD_STATUS, trace) and success

    # 16. The IUT sends an LL_CIS_TERMINATE_IND PDU to the Lower Tester with the ErrorCode field in the CtrData field
    #       set to match the Reason Code value in step 14.
    # 17. The Lower Tester sends an Ack to the IUT.
    # 18. The IUT sends a successful HCI_Disconnection_Complete event to the Upper Tester with Connection_Handle_1 and
    #       Reason Code set to Connection Terminated by Local Host (0x16).
    s, event = verifyAndFetchEvent(transport, upper_tester, Events.BT_HCI_EVT_DISCONN_COMPLETE, trace)
    status, handle, reason = event.decode()
    success = s and status == 0x00 and handle == connection_handle_1 and reason == 0x16 and success

    success = verifyAndShowEvent(transport, lower_tester, Events.BT_HCI_EVT_DISCONN_COMPLETE, trace) and success

    # 19. The Upper Tester sends an HCI_Disconnect command to the IUT with Connection_Handle_2 and Reason Code set to
    #       any valid value.
    # 20. The IUT sends a successful HCI_Command_Status event to the Upper Tester.
    success = disconnect(transport, upper_tester, connection_handle_2, 0x13, 200) == 0 and success
    success = verifyAndShowEvent(transport, upper_tester, Events.BT_HCI_EVT_CMD_STATUS, trace) and success

    # 21. The IUT sends an LL_CIS_TERMINATE_IND PDU to the Lower Tester with the ErrorCode field in the CtrData field
    #       set to match the Reason code value the Upper Tester sent in step 19.
    # 22. The Lower Tester sends an Ack to the IUT.
    # 23. The IUT sends a successful HCI_Disconnection_Complete event to the Upper Tester with Connection_Handle_2 and
    #       Reason Code set to Connection Terminated by Local Host (0x16).
    s, event = verifyAndFetchEvent(transport, upper_tester, Events.BT_HCI_EVT_DISCONN_COMPLETE, trace)
    status, handle, reason = event.decode()
    success = s and status == 0x00 and handle == connection_handle_2 and success and reason == 0x16

    success = verifyAndShowEvent(transport, lower_tester, Events.BT_HCI_EVT_DISCONN_COMPLETE, trace) and success

    # 24. The Upper Tester sends an HCI_LE_Remove_CIG command to the IUT with CIG_ID set to the value of CIG_ID_1
    #       and receives a successful HCI_Command_Complete event from the IUT in response.
    status, _ = le_remove_cig(transport, upper_tester, 0, 100)
    success = getCommandCompleteEvent(transport, upper_tester, trace) and status == 0x00 and success

    # 25. The Upper Tester sends an HCI_LE_Set_CIG_Parameters command to the IUT with values as specified in Section 4.10.1.3, Default Values for Set CIG Parameters Commands. The CIG_ID is
    # to be set to CIG_ID_1 in step 1, CIS_ID is set to CIS_ID_1.
    params = SetCIGParameters()
    status, cig_id, cis_count, (connection_handle_3,) = \
        le_set_cig_parameters_test(transport, lower_tester, 0, *params.get_cig_parameters_test(), 100)

    # 26. The IUT sends a successful HCI_Command_Complete event to the Upper Tester with CIG_ID set to CIG_ID_1,
    #       CIS_Count set to 1, and the connection handle for CIS_ID_1, which is saved and referenced as
    #       Connection_Handle_3 in the following steps.
    success = cig_id == 0 and cis_count == 1 and success
    success = getCommandCompleteEvent(transport, lower_tester, trace) and status == 0x00 and success

    # 27. The Upper Tester sends an HCI_LE_Create_CIS command to the IUT with CIS_Count set to 1 and Connection_Handle
    #       set to Connection_Handle_3 from step 26, and it receives a successful HCI_Command_Status in response.
    status = le_create_cis(transport, lower_tester, 1, [connection_handle_3], [initiator.handles[0]], 100)
    success = status == 0 and success
    success = verifyAndShowEvent(transport, lower_tester, Events.BT_HCI_EVT_CMD_STATUS, trace) and success

    # 28. The IUT sends an LL_CIS_REQ PDU to the Lower Tester with CIG_ID set to CIG_ID_1 and CIS_ID set to CIS_ID_3.
    # 29. The Lower Tester sends an LL_CIS_RSP PDU to the IUT.
    # 30. The IUT sends an LL_CIS_IND PDU to the Lower Tester. The Access Address provided in CtrData is different from
    #       AA_1, AA_1new, and AA_2.
    # 31. The IUT sends an ISO Data Packet to the Lower Tester.
    # 32. The Lower Tester sends an LL Ack to the IUT.
    # 33. The IUT sends an HCI_LE_CIS_Established event to the Upper Tester with Status set to 0x00 and
    #       Connection_Handle set to Connection_Handle_3.
    s, event = verifyAndFetchMetaEvent(transport, lower_tester, MetaEvents.BT_HCI_EVT_LE_CIS_REQUEST, trace)
    success = s and success

    status = le_accept_cis_request(transport, lower_tester, event.decode()[1], 100)
    s = verifyAndShowEvent(transport, lower_tester, Events.BT_HCI_EVT_CMD_STATUS, trace)
    success = status == 0 and s and success

    s, event = verifyAndFetchMetaEvent(transport, upper_tester, MetaEvents.BT_HCI_EVT_LE_CIS_ESTABLISHED, trace,
                                       2000)
    success = s and (event.decode()[0] == 0x00) and success

    s, event = verifyAndFetchMetaEvent(transport, lower_tester, MetaEvents.BT_HCI_EVT_LE_CIS_ESTABLISHED, trace)
    success = s and (event.decode()[0] == 0x00) and success

    if connection_handle_3 == connection_handle_1:
        # Alternative 34A (The value of Connection_Handle_3 equals the value of Connection_Handle_1):
        # 34A.1. The Upper Tester sends an HCI_LE_Create_CIS command to the IUT with CIS_Count set to 1,
        #       ACL_Connection_Handle set to the current ACL Connection Handle value, and CIS_Connection_Handle set to
        #       Connection_Handle_2.
        status = le_create_cis(transport, lower_tester, 1, [connection_handle_2], [initiator.handles[0]], 100)
        success = verifyAndShowEvent(transport, lower_tester, Events.BT_HCI_EVT_CMD_STATUS, trace) and success

        # 34A.2. The IUT sends an HCI_Command_Status event to the Upper Tester with Status set to Unknown Connection
        #       Identifier (0x02).
        success = status == 0x02 and success
    elif connection_handle_3 == connection_handle_2:
        # Alternative 34B (The value of Connection_Handle_3 equals the value of Connection_Handle_2):
        # 34B.1. The Upper Tester sends an HCI_LE_Create_CIS command to the IUT with CIS_Count set to 1,
        #       ACL_Connection_Handle set to the current ACL Connection Handle value, and CIS_Connection_Handle set to
        #       the value of Connection_Handle_1.
        status = le_create_cis(transport, lower_tester, 1, [connection_handle_1], [initiator.handles[0]], 100)
        success = verifyAndShowEvent(transport, lower_tester, Events.BT_HCI_EVT_CMD_STATUS, trace) and success

        # 34B.2 The IUT sends an HCI_Command_Status event to the Upper Tester with Status set to Unknown Connection
        #       Identifier (0x02).
        success = status == 0x02 and success
    else:
        # Alternative 34C (The value of Connection_Handle is different than Connection_Handle_1 or Connection_Handle_2):
        # 34C.1 The test ends with a Pass verdict.
        pass

    # TODO: Verify CIS Access Addresses

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def connected_isochronous_stream_using_non_test_command(transport, upper_tester, lower_tester, trace, packets, phy,
                                                        max_transport_latency):
    params = SetCIGParameters(
        Framing                         = 1,
        PHY_C_To_P                      = phy,
        PHY_P_To_C                      = phy,
        Max_Transport_Latency_C_To_P    = max_transport_latency,
        Max_Transport_Latency_P_To_C    = max_transport_latency,
        Max_SDU_C_To_P                  = 16,
        Max_SDU_P_To_C                  = 16,
    )

    success, initiator, _, (cis_handle_upper_tester,) = \
        state_connected_isochronous_stream(transport, lower_tester, upper_tester, trace, params, use_test_cmd=False)
    if not initiator:
        return False

    for seq_num in range(3):
        success = iso_send_payload_pdu(transport, upper_tester, lower_tester, trace, cis_handle_upper_tester,
                                       params.Max_SDU_C_To_P[0], params.SDU_Interval_C_To_P, seq_num) and success

    success = disconnect(transport, upper_tester, cis_handle_upper_tester, 0x13, 200) == 0 and success
    success = verifyAndShowEvent(transport, upper_tester, Events.BT_HCI_EVT_CMD_STATUS, trace) and success
    success = verifyAndShowEvent(transport, upper_tester, Events.BT_HCI_EVT_DISCONN_COMPLETE, trace) and success
    success = verifyAndShowEvent(transport, lower_tester, Events.BT_HCI_EVT_DISCONN_COMPLETE, trace) and success

    status, cig_id = le_remove_cig(transport, upper_tester, 0, 100)
    success = getCommandCompleteEvent(transport, upper_tester, trace) and status == 0x00 and cig_id == 0 and success

    params = SetCIGParameters(
        Framing                         = 1,
        PHY_C_To_P                      = phy,
        PHY_P_To_C                      = phy,
        Max_Transport_Latency_C_To_P    = max_transport_latency,
        Max_Transport_Latency_P_To_C    = max_transport_latency,
        Max_SDU_C_To_P                  = 0,
        Max_SDU_P_To_C                  = 16,
    )

    s, _, (cis_handle_lower_tester,) = establish_cis_connection(transport, upper_tester, lower_tester, trace, params,
                                                                initiator.handles[0], use_test_cmd=False)
    success = s and success

    for seq_num in range(50):
        success = iso_send_payload_pdu(transport, lower_tester, upper_tester, trace, cis_handle_lower_tester,
                                       params.Max_SDU_P_To_C[0], params.SDU_Interval_P_To_C, seq_num) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    trace.trace(4, "Host verification " + ("PASS" if success else "FAIL"))

    ### LL VERIFICATION ###
    isoc_framed_pdu_num = 0
    for packet in packets.fetch(packet_filter=('LL_CIS_REQ', 'ISOC_FRAMED_PDU')):
        if packet.type.name == 'LL_CIS_REQ':
            success = packet.payload.CtrData.Framed == 1 and success
        elif packet.payload.SegmentationHeader.CMPLT == 1:
            isoc_framed_pdu_num += 1

    success = isoc_framed_pdu_num == 53 and success

    trace.trace(4, "LL verification " + ("PASS" if success else "FAIL"))

    return success


def ll_cis_cen_bv_26_c(transport, upper_tester, lower_tester, trace, packets):
    """LL/CIS/CEN/BV-26-C [Connected Isochronous Stream Using Non-Test Command, Central Initiated]"""
    return connected_isochronous_stream_using_non_test_command(transport, upper_tester, lower_tester, trace, packets,
                                                               1, 60)


def ll_cis_cen_bv_27_c(transport, upper_tester, lower_tester, trace, packets):
    """LL/CIS/CEN/BV-27-C [Connected Isochronous Stream Using Non-Test Command, Central Initiated]"""
    return connected_isochronous_stream_using_non_test_command(transport, upper_tester, lower_tester, trace, packets,
                                                               2, 60)


def connected_isochronous_stream_using_non_test_command_force_framed_pdus(transport, upper_tester, lower_tester, trace,
                                                                          packets, phy):
    params = SetCIGParameters(
        SDU_Interval_C_To_P             = 10884,  # 10.884 ms
        SDU_Interval_P_To_C             = 10884,  # 10.884 ms
        Max_SDU_C_To_P                  = 0x20,
        Max_SDU_P_To_C                  = 0x20,
        RTN_C_To_P                      = 0x03,
        RTN_P_To_C                      = 0x03,
        Max_Transport_Latency_C_To_P    = 40,
        Max_Transport_Latency_P_To_C    = 40,
        Framing                         = 0,  # Unframed
        PHY_C_To_P                      = phy,
        PHY_P_To_C                      = phy,
    )

    success, initiator, _, (cis_handle_upper_tester,) = \
        state_connected_isochronous_stream(transport, lower_tester, upper_tester, trace, params, use_test_cmd=False)
    if not initiator:
        return False

    for seq_num in range(3):
        success = iso_send_payload_pdu(transport, upper_tester, lower_tester, trace, cis_handle_upper_tester,
                                       params.Max_SDU_C_To_P[0], params.SDU_Interval_C_To_P, seq_num) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    trace.trace(4, "Host verification " + ("PASS" if success else "FAIL"))

    ### LL VERIFICATION ###
    isoc_framed_pdu_num = 0
    for packet in packets.fetch(packet_filter=('LL_CIS_REQ', 'ISOC_FRAMED_PDU')):
        if packet.type.name == 'LL_CIS_REQ':
            success = packet.payload.CtrData.Framed == 1 and success
        elif packet.payload.SegmentationHeader.CMPLT == 1:
            isoc_framed_pdu_num += 1

    success = isoc_framed_pdu_num == 3 and success

    trace.trace(4, "LL verification " + ("PASS" if success else "FAIL"))

    return success


def ll_cis_cen_bv_36_c(transport, upper_tester, lower_tester, trace, packets):
    """LL/CIS/CEN/BV-36-C [Connected Isochronous Stream Using Non-Test Command, Force Framed PDUs]"""
    return connected_isochronous_stream_using_non_test_command_force_framed_pdus(transport, upper_tester, lower_tester,
                                                                                 trace, packets, 1)


def ll_cis_cen_bv_37_c(transport, upper_tester, lower_tester, trace, packets):
    """LL/CIS/CEN/BV-37-C [Connected Isochronous Stream Using Non-Test Command, Force Framed PDUs]"""
    return connected_isochronous_stream_using_non_test_command_force_framed_pdus(transport, upper_tester, lower_tester,
                                                                                 trace, packets, 2)


def ll_ist_cen_bv_01_c(transport, upper_tester, lower_tester, trace):
    """LL/IST/CEN/BV-01-C [ISO Transmit Test Mode, CIS]"""
    return iso_transmit_test_mode_cis(transport, upper_tester, lower_tester, trace, True)


def ll_ist_cen_bv_03_c(transport, upper_tester, lower_tester, trace):
    """LL/IST/CEN/BV-03-C [ISO Receive Test Mode, CIS]"""
    return iso_receive_test_mode_cis(transport, upper_tester, lower_tester, trace, True)


__tests__ = {
    "LL/CON/ADV/BV-01-C": [ ll_con_adv_bv_01_c, "Accepting Connection Request" ],
    "LL/CON/ADV/BV-04-C": [ ll_con_adv_bv_04_c, "Accepting Connection Request after Directed Advertising" ],
    "LL/CON/ADV/BV-09-C": [ ll_con_adv_bv_09_c, "Accepting Connection Request using Channel Selection Algorithm #2" ],
    "LL/CON/ADV/BV-10-C": [ ll_con_adv_bv_10_c, "Accepting Connection Request after Directed Advertising using Channel Selection Algorithm #2" ],
    "LL/CON/INI/BV-01-C": [ ll_con_ini_bv_01_c, "Connection Initiation rejects Address change" ],
    "LL/CON/INI/BV-02-C": [ ll_con_ini_bv_02_c, "Connecting to Advertiser using Directed Advertising Packets" ],
    "LL/CON/INI/BV-06-C": [ ll_con_ini_bv_06_c, "Filtered Connection to Advertiser using Undirected Advertising Packets" ],
    "LL/CON/INI/BV-07-C": [ ll_con_ini_bv_07_c, "Filtered Connection to Advertiser using Directed Advertising Packets" ],
    "LL/CON/INI/BV-08-C": [ ll_con_ini_bv_08_c, "Connecting to Connectable Undirected Advertiser with Network Privacy" ],
    "LL/CON/INI/BV-09-C": [ ll_con_ini_bv_09_c, "Connecting to Connectable Undirected Advertiser with Network Privacy thru Resolving List" ],
    "LL/CON/INI/BV-10-C": [ ll_con_ini_bv_10_c, "Connecting to Directed Advertiser with Network Privacy thru Resolving List" ],
    "LL/CON/INI/BV-11-C": [ ll_con_ini_bv_11_c, "Connecting to Directed Advertiser using  wrong address with Network Privacy thru Resolving List " ],
    "LL/CON/INI/BV-12-C": [ ll_con_ini_bv_12_c, "Connecting to Directed Advertiser using Identity address with Network Privacy thru Resolving List" ],
    "LL/CON/INI/BV-16-C": [ ll_con_ini_bv_16_c, "Connecting to Advertiser with Channel Selection Algorithm #2" ],
    "LL/CON/INI/BV-17-C": [ ll_con_ini_bv_17_c, "Connecting to Directed Advertiser with Channel Selection Algorithm #2" ],
    "LL/CON/INI/BV-18-C": [ ll_con_ini_bv_18_c, "Don't connect to Advertiser using Identity address with Network Privacy thru Resolving List" ],
    "LL/CON/INI/BV-19-C": [ ll_con_ini_bv_19_c, "Don't connect to Directed Advertiser using Identity address with Network Privacy thru Resolving List" ],
    "LL/CON/INI/BV-20-C": [ ll_con_ini_bv_20_c, "Connect to Advertiser using Identity address with Device Privacy thru Resolving List" ],
    "LL/CON/INI/BV-21-C": [ ll_con_ini_bv_21_c, "Connect to Directed Advertiser using Identity address with Device Privacy thru Resolving List" ],
    "LL/CON/INI/BV-23-C": [ ll_con_ini_bv_23_c, "Network Privacy - Connection Establishment using whitelist and resolving list with address resolution disabled" ],
    "LL/CON/INI/BV-24-C": [ ll_con_ini_bv_24_c, "Network Privacy - Connection Establishment using resolving list with address resolution disabled" ],
    "LL/CON/MAS/BI-06-C": [ ll_con_mas_bi_06_c, "Master responds to Connection Parameter Request - illegal parameters" ],
    "LL/CON/MAS/BV-03-C": [ ll_con_mas_bv_03_c, "Master sending Data packets to Slave" ],
    "LL/CON/MAS/BV-04-C": [ ll_con_mas_bv_04_c, "Master receiving Data packets from Slave" ],
    "LL/CON/MAS/BV-05-C": [ ll_con_mas_bv_05_c, "Master sending and receiving Data packets to and form Slave" ],
    "LL/CON/MAS/BV-07-C": [ ll_con_mas_bv_07_c, "Master requests Connection Parameter Update" ],
    "LL/CON/MAS/BV-08-C": [ ll_con_mas_bv_08_c, "Master Terminating Connection" ],
    "LL/CON/MAS/BV-09-C": [ ll_con_mas_bv_09_c, "Master accepting Connection Termination" ],
    "LL/CON/MAS/BV-13-C": [ ll_con_mas_bv_13_c, "Master requests Feature Setup procedure" ],
    "LL/CON/MAS/BV-20-C": [ ll_con_mas_bv_20_c, "Master requests Version Exchange procedure" ],
    "LL/CON/MAS/BV-21-C": [ ll_con_mas_bv_21_c, "Master responds to Version Exchange procedure" ],
    "LL/CON/MAS/BV-23-C": [ ll_con_mas_bv_23_c, "Master responds to Feature Exchange procedure" ],
    "LL/CON/MAS/BV-24-C": [ ll_con_mas_bv_24_c, "Master requests Connection Parameters - Slave Accepts" ],
    "LL/CON/MAS/BV-25-C": [ ll_con_mas_bv_25_c, "Master requests Connection Parameters - Slave Rejects" ],
    "LL/CON/MAS/BV-26-C": [ ll_con_mas_bv_26_c, "Master requests Connection Parameters - same procedure collision" ],
    "LL/CON/MAS/BV-27-C": [ ll_con_mas_bv_27_c, "Master requests Connection Parameters - Channel Map Update procedure collision" ],
    "LL/CON/MAS/BV-29-C": [ ll_con_mas_bv_29_c, "Master requests Connection Parameters - Slave unsupported" ],
    "LL/CON/MAS/BV-30-C": [ ll_con_mas_bv_30_c, "Master responds to Connection Parameters request - no Preferred_Periodicity" ],
    "LL/CON/MAS/BV-34-C": [ ll_con_mas_bv_34_c, "Master responds to Connection Parameters request - event masked" ],
    "LL/CON/MAS/BV-35-C": [ ll_con_mas_bv_35_c, "Master responds to Connection Parameters request - Host rejects" ],
    "LL/CON/MAS/BV-41-C": [ ll_con_mas_bv_41_c, "Master requests PHY Update procedure" ],
    "LL/CON/MAS/BV-43-C": [ ll_con_mas_bv_43_c, "Master responds to PHY Update procedure" ],
    "LL/CON/MAS/BV-73-C": [ ll_con_mas_bv_73_c, "Master Packet Data Length Update - Responding to Packet Data Length Update Procedure; LE 1M PHY" ],
    "LL/CON/MAS/BV-74-C": [ ll_con_mas_bv_74_c, "Master Packet Data Length Update - Initiating Packet Data Length Update Procedure; LE 1M PHY" ],
    "LL/CON/MAS/BV-76-C": [ ll_con_mas_bv_76_c, "Master Packet Data Length Update - Responding to Packet Data Length Update Procedure; LE 2M PHY" ],
    "LL/CON/MAS/BV-77-C": [ ll_con_mas_bv_77_c, "Master Packet Data Length Update - Initiating Packet Data Length Update Procedure; LE 2M PHY" ],
    "LL/CON/SLA/BI-08-C": [ ll_con_sla_bi_08_c, "Slave responds to Connection Parameters request - Illegal Parameters" ],
    "LL/CON/SLA/BV-04-C": [ ll_con_sla_bv_04_c, "Connection where Slave sends data to Master" ],
    "LL/CON/SLA/BV-05-C": [ ll_con_sla_bv_05_c, "Connection where Slave receives data from Master" ],
    "LL/CON/SLA/BV-06-C": [ ll_con_sla_bv_06_c, "Connection where Slave sends and receives data to and from Master" ],
    "LL/CON/SLA/BV-10-C": [ ll_con_sla_bv_10_c, "Slave accepting Connection Parameter Update from Master" ],
    "LL/CON/SLA/BV-11-C": [ ll_con_sla_bv_11_c, "Slave sending Termination to Master" ],
    "LL/CON/SLA/BV-12-C": [ ll_con_sla_bv_12_c, "Slave accepting Termination from Master" ],
#   "LL/CON/SLA/BV-13-C": [ ll_con_sla_bv_13_c, "Slave Terminating Connection on Supervision Timer" ],
    "LL/CON/SLA/BV-14-C": [ ll_con_sla_bv_14_c, "Slave performs Feature Setup procedure" ],
    "LL/CON/SLA/BV-19-C": [ ll_con_sla_bv_19_c, "Slave requests Version Exchange procedure" ],
    "LL/CON/SLA/BV-20-C": [ ll_con_sla_bv_20_c, "Slave responds to Version Exchange procedure" ],
    "LL/CON/SLA/BV-22-C": [ ll_con_sla_bv_22_c, "Slave requests Feature Exchange procedure" ],
    "LL/CON/SLA/BV-24-C": [ ll_con_sla_bv_24_c, "Slave requests Connection Parameters - Master Accepts" ],
    "LL/CON/SLA/BV-25-C": [ ll_con_sla_bv_25_c, "Slave requests Connection Parameters - Master Rejects" ],
    "LL/CON/SLA/BV-26-C": [ ll_con_sla_bv_26_c, "Slave requests Connection Parameters - same procedure collision" ],
    "LL/CON/SLA/BV-27-C": [ ll_con_sla_bv_27_c, "Slave requests Connection Parameters - channel map update procedure collision" ],
    "LL/CON/SLA/BV-29-C": [ ll_con_sla_bv_29_c, "Slave responds to Connection Parameters - Master no Preferred Periodicity" ],
    "LL/CON/SLA/BV-33-C": [ ll_con_sla_bv_33_c, "Slave responds to Connection Parameters request - event masked" ],
    "LL/CON/SLA/BV-34-C": [ ll_con_sla_bv_34_c, "Slave responds to Connection Parameters request - Host rejects" ],
    "LL/CON/SLA/BV-40-C": [ ll_con_sla_bv_40_c, "Slave requests PHY Update procedure" ],
    "LL/CON/SLA/BV-42-C": [ ll_con_sla_bv_42_c, "Slave responds to PHY Update procedure" ],
    "LL/CON/SLA/BV-77-C": [ ll_con_sla_bv_77_c, "Slave Packet Data Length Update - Responding to Packet Data Length Update Procedure; LE 1M PHY" ],
    "LL/CON/SLA/BV-78-C": [ ll_con_sla_bv_78_c, "Slave requests Packet Data Length Update procedure; LE 1M PHY" ],
    "LL/CON/SLA/BV-80-C": [ ll_con_sla_bv_80_c, "Slave Packet Data Length Update - Responding to Packet Data Length Update Procedure; LE 2M PHY" ],
    "LL/CON/SLA/BV-81-C": [ ll_con_sla_bv_81_c, "Slave requests Packet Data Length Update procedure; LE 2M PHY" ],
    "LL/DDI/ADV/BV-01-C": [ ll_ddi_adv_bv_01_c, "Non-Connectable Advertising Packets on one channel" ],
    "LL/DDI/ADV/BV-02-C": [ ll_ddi_adv_bv_02_c, "Undirected Advertising Packets on one channel" ],
    "LL/DDI/ADV/BV-03-C": [ ll_ddi_adv_bv_03_c, "Non-Connectable Advertising Packets on all channels" ],
    "LL/DDI/ADV/BV-04-C": [ ll_ddi_adv_bv_04_c, "Undirected Advertising with Data on all channels " ],
    "LL/DDI/ADV/BV-05-C": [ ll_ddi_adv_bv_05_c, "Undirected Connectable Advertising with Scan Request/Response " ],
    "LL/DDI/ADV/BV-06-C": [ ll_ddi_adv_bv_06_c, "Stop Advertising on Connection Request" ],
    "LL/DDI/ADV/BV-07-C": [ ll_ddi_adv_bv_07_c, "Scan Request/Response followed by Connection Request" ],
    "LL/DDI/ADV/BV-08-C": [ ll_ddi_adv_bv_08_c, "Advertiser Filtering Scan requests" ],
    "LL/DDI/ADV/BV-09-C": [ ll_ddi_adv_bv_09_c, "Advertiser Filtering Connection requests" ],
    "LL/DDI/ADV/BV-11-C": [ ll_ddi_adv_bv_11_c, "High Duty Cycle Connectable Directed Advertising on all channels" ],
    "LL/DDI/ADV/BV-15-C": [ ll_ddi_adv_bv_15_c, "Discoverable Undirected Advertising on all channels" ],
    "LL/DDI/ADV/BV-16-C": [ ll_ddi_adv_bv_16_c, "Discoverable Undirected Advertising with Data on all channels" ],
    "LL/DDI/ADV/BV-17-C": [ ll_ddi_adv_bv_17_c, "Discoverable Undirected Advertising with Scan Request/Response" ],
    "LL/DDI/ADV/BV-18-C": [ ll_ddi_adv_bv_18_c, "Discoverable Undirected Advertiser Filtering Scan requests " ],
    "LL/DDI/ADV/BV-19-C": [ ll_ddi_adv_bv_19_c, "Low Duty Cycle Directed Advertising on all channels" ],
    "LL/DDI/ADV/BV-20-C": [ ll_ddi_adv_bv_20_c, "Advertising on the LE 1M PHY on all channels" ],
#   "LL/DDI/ADV/BV-21-C": [ ll_ddi_adv_bv_21_c, "Non-Connectable Extended Legacy Advertising with Data on all channels" ],
    "LL/DDI/SCN/BV-01-C": [ ll_ddi_scn_bv_01_c, "Passive Scanning of Non-Connectable Advertising Packets" ],
    "LL/DDI/SCN/BV-02-C": [ ll_ddi_scn_bv_02_c, "Filtered Passive Scanning of Non-Connectable Advertising Packets" ],
    "LL/DDI/SCN/BV-03-C": [ ll_ddi_scn_bv_03_c, "Active Scanning of Connectable Undirected Advertising Packets" ],
    "LL/DDI/SCN/BV-04-C": [ ll_ddi_scn_bv_04_c, "Filtered Active Scanning of Connectable Undirected Advertising Packets" ],
    "LL/DDI/SCN/BV-05-C": [ ll_ddi_scn_bv_05_c, "Scanning for different Advertiser types with and without Data" ],
    "LL/DDI/SCN/BV-10-C": [ ll_ddi_scn_bv_10_c, "Passive Scanning for Undirected Advertising Packets with Data" ],
    "LL/DDI/SCN/BV-11-C": [ ll_ddi_scn_bv_11_c, "Passive Scanning for Directed Advertising Packets" ],
    "LL/DDI/SCN/BV-12-C": [ ll_ddi_scn_bv_12_c, "Passive Scanning for Discoverable Undirected Advertising Packets" ],
    "LL/DDI/SCN/BV-13-C": [ ll_ddi_scn_bv_13_c, "Passive Scanning for Non-Connectable Advertising Packets using Network Privacy" ],
    "LL/DDI/SCN/BV-14-C": [ ll_ddi_scn_bv_14_c, "Passive Scanning for Connectable Directed Advertising Packets using Network Privacy" ],
    "LL/DDI/SCN/BV-15-C": [ ll_ddi_scn_bv_15_c, "Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with no Local or Peer IRK" ],
    "LL/DDI/SCN/BV-16-C": [ ll_ddi_scn_bv_16_c, "Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with Local and no Peer IRK" ],
    "LL/DDI/SCN/BV-17-C": [ ll_ddi_scn_bv_17_c, "Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with no Local and a Peer IRK" ],
    "LL/DDI/SCN/BV-18-C": [ ll_ddi_scn_bv_18_c, "Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with both Local and Peer IRKs" ],
    "LL/DDI/SCN/BV-26-C": [ ll_ddi_scn_bv_26_c, "Passive Scanning for Non-Connectable Advertising Packets using Network Privacy" ],
    "LL/DDI/SCN/BV-28-C": [ ll_ddi_scn_bv_28_c, "Passive Scanning for Non-Connectable Advertising Packets using Device Privacy" ],
#   "LL/SEC/ADV/BV-01-C": [ ll_sec_adv_bv_01_c, "Changing Static Address while Advertising" ],
    "LL/SEC/ADV/BV-02-C": [ ll_sec_adv_bv_02_c, "Non Connectable Undirected Advertising with non-resolvable private address" ],
    "LL/SEC/ADV/BV-03-C": [ ll_sec_adv_bv_03_c, "Non Connectable Undirected Advertising with resolvable private address" ],
    "LL/SEC/ADV/BV-04-C": [ ll_sec_adv_bv_04_c, "Scannable Undirected Advertising with non-resolvable private address" ],
    "LL/SEC/ADV/BV-05-C": [ ll_sec_adv_bv_05_c, "Scannable Undirected Advertising with resolvable private address" ],
    "LL/SEC/ADV/BV-06-C": [ ll_sec_adv_bv_06_c, "Connecting with Undirected Connectable Advertiser using non-resolvable private address" ],
#   "LL/SEC/ADV/BV-07-C": [ ll_sec_adv_bv_07_c, "Connecting with Undirected Connectable Advertiser with Local IRK but no Peer IRK" ],
    "LL/SEC/ADV/BV-08-C": [ ll_sec_adv_bv_08_c, "Connecting with Undirected Connectable Advertiser with both Local and Peer IRK" ],
    "LL/SEC/ADV/BV-09-C": [ ll_sec_adv_bv_09_c, "Connecting with Undirected Connectable Advertiser with no Local IRK but peer IRK" ],
    "LL/SEC/ADV/BV-10-C": [ ll_sec_adv_bv_10_c, "Connecting with Undirected Connectable Advertiser where no match for Peer Device Identity" ],
    "LL/SEC/ADV/BV-11-C": [ ll_sec_adv_bv_11_c, "Connecting with Directed Connectable Advertiser using local and remote IRK" ],
    "LL/SEC/ADV/BV-12-C": [ ll_sec_adv_bv_12_c, "Connecting with Directed Connectable Advertising with local IRK but without remote IRK" ],
    "LL/SEC/ADV/BV-13-C": [ ll_sec_adv_bv_13_c, "Directed Connectable Advertising without local IRK but with remote IRK" ],
    "LL/SEC/ADV/BV-14-C": [ ll_sec_adv_bv_14_c, "Directed Connectable Advertising using Resolving List and Peer Device Identity not in the List" ],
    "LL/SEC/ADV/BV-15-C": [ ll_sec_adv_bv_15_c, "Scannable Advertising with resolvable private address, no Scan Response to Identity Address" ],
    "LL/SEC/ADV/BV-16-C": [ ll_sec_adv_bv_16_c, "Undirected Connectable Advertising with resolvable private address; no Connection to Identity Address" ],
    "LL/SEC/ADV/BV-17-C": [ ll_sec_adv_bv_17_c, "Directed Connectable Advertising using local and remote IRK, Ignore Identity Address" ],
    "LL/SEC/ADV/BV-18-C": [ ll_sec_adv_bv_18_c, "Scannable Advertising with resolvable private address, accept Identity Address" ],
#   "LL/SEC/ADV/BV-19-C": [ ll_sec_adv_bv_19_c, "Undirected Connectable Advertising with Local IRK and Peer IRK, accept Identity Address" ],
    "LL/SEC/ADV/BV-20-C": [ ll_sec_adv_bv_20_c, "Directed Connectable Advertising with resolvable private address; Connect to Identity Address" ],
    "LL/SEC/SCN/BV-01-C": [ ll_sec_scn_bv_01_c, "Changing Static Address while Scanning" ],
    "LL/CIS/CEN/BV-01-C": [ ll_cis_cen_bv_01_c, "CIS Setup Procedure, Central Initiated" ],
    "LL/CIS/CEN/BV-02-C": [ ll_cis_cen_bv_02_c, "CIS Setup Procedure, Central Initiated" ],
    "LL/CIS/CEN/BV-31-C": [ ll_cis_cen_bv_31_c, "CIS Setup Procedure, Central Initiated" ],
    "LL/CIS/CEN/BV-39-C": [ ll_cis_cen_bv_39_c, "CIS Setup Procedure, Central Initiated" ],
    "LL/CIS/CEN/BV-03-C": [ ll_cis_cen_bv_03_c, "CIS Setup Procedure, Central Initiated, Rejected" ],
    "LL/CIS/CEN/BV-04-C": [ ll_cis_cen_bv_04_c, "New Channel Map" ],
    "LL/CIS/CEN/BV-40-C": [ ll_cis_cen_bv_40_c, "New Channel Map" ],
    "LL/CIS/CEN/BV-20-C": [ ll_cis_cen_bv_20_c, "Set Encryption After CIS Established" ],
    "LL/CIS/CEN/BV-26-C": [ ll_cis_cen_bv_26_c, "Connected Isochronous Stream Using Non-Test Command, Central Initiated" ],
    "LL/CIS/CEN/BV-27-C": [ ll_cis_cen_bv_27_c, "Connected Isochronous Stream Using Non-Test Command, Central Initiated" ],
    "LL/CIS/CEN/BV-30-C": [ ll_cis_cen_bv_30_c, "Isochronous Channels Host Support Feature Bit" ],
    # "LL/CIS/CEN/BV-08-C": [ ll_cis_cen_bv_08_c, "Sending and Receiving Data in Multiple CISes, Single CIG, Single Connection, Interleaved CIG, Central" ],
    "LL/CIS/CEN/BV-43-C": [ ll_cis_cen_bv_43_c, "Sending and Receiving Data in Multiple CISes, Single CIG, Single Connection, Interleaved CIG, Central" ],
    # "LL/CIS/CEN/BV-09-C": [ ll_cis_cen_bv_09_c, "Sending and Receiving Data in Multiple CISes, Single CIG, Single Connection, Sequential, Central" ],
    "LL/CIS/CEN/BV-36-C": [ ll_cis_cen_bv_36_c, "Connected Isochronous Stream Using Non-Test Command, Force Framed PDUs" ],
    "LL/CIS/CEN/BV-37-C": [ ll_cis_cen_bv_37_c, "Connected Isochronous Stream Using Non-Test Command, Force Framed PDUs" ],
    "LL/CIS/CEN/BV-44-C": [ ll_cis_cen_bv_44_c, "Sending and Receiving Data in Multiple CISes, Single CIG, Single Connection, Interleaved CIG, Central, BN > 1, NSE = 2" ],
    # "LL/CIS/CEN/BV-51-C": [ ll_cis_cen_bv_51_c, "CIS Setup Procedure, Central Initiated, CIG ID Reuse" ],
    "LL/CIS/CEN/BV-06-C": [ ll_cis_cen_bv_06_c, "Receiving data in Unidirectional CIS" ],
    "LL/CIS/CEN/BV-07-C": [ ll_cis_cen_bv_07_c, "Sending and Receiving Data in Bidirectional CIS" ],
    "LL/CIS/CEN/BV-35-C": [ ll_cis_cen_bv_35_c, "Sending and Receiving Data in Bidirectional CIS, Encryption" ],
    # "LL/CIS/CEN/BV-15-C": [ ll_cis_cen_bv_15_c, "CIS Terminate Procedure, Initiated" ],
    "LL/CIS/CEN/BV-16-C": [ ll_cis_cen_bv_16_c, "CIS Terminate Procedure, Accepting" ],
    "LL/CIS/CEN/BV-24-C": [ ll_cis_cen_bv_24_c, "CIS Updating Peer Clock Accuracy" ],
    "LL/CIS/CEN/BV-45-C": [ ll_cis_cen_bv_45_c, "Sending Data in Unidirectional CIS, BN = 1" ],
    "LL/CIS/CEN/BV-46-C": [ ll_cis_cen_bv_46_c, "Receiving Data in Unidirectional CIS, BN = 1" ],
    "LL/CIS/CEN/BV-47-C": [ ll_cis_cen_bv_47_c, "Sending and Receiving Data in Bidirectional CIS, BN = 1" ],
    "LL/CIS/CEN/BV-48-C": [ ll_cis_cen_bv_48_c, "Sending and Receiving Data in Bidirectional CIS, BN = 1, Encryption" ],
    "LL/CIS/PER/BV-01-C": [ ll_cis_per_bv_01_c, "CIS Setup Response Procedure, Peripheral" ],
    "LL/CIS/PER/BV-02-C": [ ll_cis_per_bv_02_c, "CIS Setup Response Procedure, Peripheral, Reject Response" ],
    "LL/CIS/PER/BV-03-C": [ ll_cis_per_bv_03_c, "CIS Map Update" ],
    "LL/CIS/PER/BV-05-C": [ ll_cis_per_bv_05_c, "Receiving data in Unidirectional CIS" ],
    "LL/CIS/PER/BV-06-C": [ ll_cis_per_bv_06_c, "Sending and Receiving Data in Bidirectional CIS" ],
#   "LL/CIS/PER/BV-07-C": [ ll_cis_per_bv_07_c, "Sending and Receiving Data in Multiple CISes, Single CIG, Single Connection, Interleaved CIG, Peripheral" ],  # https://github.com/EDTTool/packetcraft/issues/12, https://github.com/EDTTool/packetcraft/issues/15
#   "LL/CIS/PER/BV-08-C": [ ll_cis_per_bv_08_c, "Sending and Receiving Data in Multiple CISes, Single CIG, Single Connection, Sequential, Peripheral" ],  # https://github.com/EDTTool/EDTT-le-audio/issues/72
    "LL/CIS/PER/BV-18-C": [ ll_cis_per_bv_18_c, "CIS Updating Peer Clock Accuracy" ],
    "LL/CIS/PER/BV-19-C": [ ll_cis_per_bv_19_c, "CIS Setup Response Procedure, Peripheral" ],
    "LL/CIS/PER/BV-22-C": [ ll_cis_per_bv_22_c, "CIS Request Event Not Set" ],
    "LL/CIS/PER/BV-23-C": [ ll_cis_per_bv_23_c, "CIS Setup Response Procedure, Peripheral" ],
#   "LL/CIS/PER/BV-27-C": [ ll_cis_per_bv_27_c, "Sending and Receiving Data in Bidirectional CIS, Encryption" ],  # https://github.com/EDTTool/EDTT-le-audio/issues/75
    "LL/CIS/PER/BV-29-C": [ ll_cis_per_bv_29_c, "CIS Setup Response Procedure, Peripheral" ],
    "LL/CIS/PER/BV-31-C": [ ll_cis_per_bv_31_c, "Sending and Receiving Data in Multiple CISes, Single CIG, Single Connection, Interleaved CIG, Peripheral, NSE=2" ],
    "LL/CIS/PER/BV-32-C": [ ll_cis_per_bv_32_c, "Sending and Receiving Data in Multiple CISes, Single CIG, Single Connection, Peripheral, BN=1" ],
    "LL/CIS/PER/BV-33-C": [ ll_cis_per_bv_33_c, "Sending Data in Unidirectional CIS, BN = 1" ],
    "LL/CIS/PER/BV-34-C": [ ll_cis_per_bv_34_c, "Receiving Data in Unidirectional CIS, BN = 1" ],
    "LL/CIS/PER/BV-35-C": [ ll_cis_per_bv_35_c, "Sending and Receiving Data in Bidirectional CIS, BN = 1" ],
    "LL/CIS/PER/BV-36-C": [ ll_cis_per_bv_36_c, "Sending and Receiving Data in Bidirectional CIS, BN = 1, Encryption "],
    "LL/CIS/PER/BV-37-C": [ ll_cis_per_bv_37_c, "CIS Map Update" ],
#   "LL/CIS/PER/BV-39-C": [ ll_cis_per_bv_39_c, "CIS Peripheral Accepts All Supported NSE Values" ],  # https://github.com/EDTTool/EDTT-le-audio/issues/84
#   "LL/CIS/PER/BV-40-C": [ ll_cis_per_bv_40_c, "CIS Setup Response Procedure, Peripheral" ],  # https://github.com/EDTTool/EDTT-le-audio/issues/85
    "LL/CIS/PER/BV-12-C": [ ll_cis_per_bv_12_c, "CIS Terminate Procedure, Initiated - Peripheral" ],
    "LL/CIS/PER/BV-13-C": [ ll_cis_per_bv_13_c, "CIS Terminate Procedure, Accepting, Peripheral" ],
#   "LL/IST/CEN/BV-01-C": [ ll_ist_cen_bv_01_c, "ISO Transmit Test Mode, CIS" ],  # https://github.com/EDTTool/EDTT-le-audio/issues/86
#   "LL/IST/PER/BV-01-C": [ ll_ist_per_bv_01_c, "ISO Transmit Test Mode, CIS" ],  # https://github.com/EDTTool/EDTT-le-audio/issues/86
#   "LL/IST/CEN/BV-03-C": [ ll_ist_cen_bv_03_c, "ISO Receive Test Mode, CIS" ],  # https://github.com/EDTTool/packetcraft/issues/10
#   "LL/IST/PER/BV-03-C": [ ll_ist_per_bv_03_c, "ISO Receive Test Mode, CIS" ],  # https://github.com/EDTTool/packetcraft/issues/10
};

_maxNameLength = max([ len(key) for key in __tests__ ]);

_spec = {key: TestSpec(name=key, number_devices=2, description="#[" + __tests__[key][1] + "]",
                       test_private=__tests__[key][0]) for key in __tests__}

"""
    Return the test spec which contains info about all the tests
    this test module provides
"""
def get_tests_specs():
    return _spec;

def preamble(transport, trace):
    global lowerIRK, upperIRK, ENC_KEYS

    ok = success = preamble_standby(transport, 0, trace);
    trace.trace(4, "preamble Standby " + ("PASS" if success else "FAIL"));
    success = preamble_standby(transport, 1, trace);
    ok = ok and success;
    trace.trace(4, "preamble Standby " + ("PASS" if success else "FAIL"));
    success, upperIRK, tests.test_utils.upperRandomAddress = preamble_device_address_set(transport, 0, trace);
    trace.trace(4, "preamble Device Address Set " + ("PASS" if success else "FAIL"));
    ok = ok and success;
    success, lowerIRK, tests.test_utils.lowerRandomAddress = preamble_device_address_set(transport, 1, trace);
    trace.trace(4, "preamble Device Address Set " + ("PASS" if success else "FAIL"));
    ok = ok and success
    success, *ENC_KEYS = preamble_encryption_keys_calculated(transport, 1, trace)
    trace.trace(4, "preamble Encryption Keys Calculated " + ("PASS" if success else "FAIL"))
    return ok and success;

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

