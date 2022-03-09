# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

import statistics;
import os;
import numpy;
from enum import IntEnum;
from components.utils import *;
from components.basic_commands import *;
from components.address import *;
from components.resolvable import *;
from components.advertiser import *;
from components.scanner import *;
from components.initiator import *;
from components.preambles import *;
from components.addata import *;
from components.pairing import *;
from components.test_spec import TestSpec;

global lowerIRK, upperIRK, lowerRandomAddress, upperRandomAddress;

"""
    GAP/DISC/NONM/BV-01-C [Non-discoverable Mode and Non-Connectable Mode]
"""
def gap_disc_nonm_bv_01_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
        success = not success;
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/DISC/NONM/BV-02-C [Non-discoverable Mode and Undirected Connectable Mode]
"""
def gap_disc_nonm_bv_02_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
        success = not success;
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/DISC/LIMM/BV-01-C [Limited Discoverable Mode and Non-Connectable Mode in BR/EDR/LE configuration]
"""
def gap_disc_limm_bv_01_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
           
    success = success and advertiser.disable();

    return success;

"""
    GAP/DISC/LIMM/BV-02-C [Limited Discoverable Mode and Undirected Connectable Mode in BR/EDR/LE configuration]
"""
def gap_disc_limm_bv_02_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/DISC/LIMM/BV-03-C [Limited Discoverable Mode and Non-Connectable Mode in LE Only configuration]
"""
def gap_disc_limm_bv_03_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));

    success = success and advertiser.disable();

    return success;

"""
    GAP/DISC/LIMM/BV-04-C [Limited Discoverable Mode and Undirected Connectable Mode in LE Only configuration]
"""
def gap_disc_limm_bv_04_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/DISC/GENM/BV-01-C [General Discoverable Mode and Non-Connectable Mode in BR/EDR/LE configuration]
"""
def gap_disc_genm_bv_01_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE);
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
           
    success = success and advertiser.disable();

    return success;

"""
    GAP/DISC/GENM/BV-02-C [General Discoverable Mode and Undirected Connectable Mode in BR/EDR/LE configuration]
"""
def gap_disc_genm_bv_02_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));

    success = success and advertiser.disable();

    return success;

"""
    GAP/DISC/GENM/BV-03-C [General Discoverable Mode and Non-Connectable Mode in LE Only configuration]
"""
def gap_disc_genm_bv_03_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
           
    success = success and advertiser.disable();

    return success;

"""
    GAP/DISC/GENM/BV-04-C [General Discoverable Mode and Undirected Connectable Mode in LE Only configuration]
"""
def gap_disc_genm_bv_04_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));

    success = success and advertiser.disable();

    return success;

"""
    GAP/DISC/LIMP/BV-01-C [Limited Discovery finding Limited Discoverable Device]
"""
def gap_disc_limp_bv_01_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);

    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.responseData  = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/DISC/LIMP/BV-02-C [Limited Discovery not finding General Discoverable Device]
"""
def gap_disc_limp_bv_02_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.responseData  = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
        success = not success;

    success = success and advertiser.disable();

    return success;

"""
    GAP/DISC/LIMP/BV-04-C [Limited Discovery not finding Undirected Connectable device]
"""
def gap_disc_limp_bv_04_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
        success = not success;

    success = success and advertiser.disable();

    return success;

"""
    GAP/DISC/LIMP/BV-05-C [Limited Discovery not finding Directed Connectable device]
"""
def gap_disc_limp_bv_05_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
        success = not success;

    success = success and advertiser.disable();

    return success;

"""
    GAP/DISC/GENP/BV-01-C [General Discovery finding General Discoverable Device]
"""
def gap_disc_genp_bv_01_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.responseData  = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/DISC/GENP/BV-02-C [General Discovery finding Limited Discoverable Device]
"""
def gap_disc_genp_bv_02_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.responseData  = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/DISC/GENP/BV-04-C [General Discovery not finding Undirected Connectable device]
"""
def gap_disc_genp_bv_04_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData  = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
        success = not success;
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/DISC/GENP/BV-05-C [General Discovery not finding Directed Connectable device]
"""
def gap_disc_genp_bv_05_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
        success = not success;
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/DISC/RPA/BV-01-C [Find Discoverable Device using Resolvable Private Address]
"""
def gap_disc_rpa_bv_01_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to upperTesters Resolving List
        Add Public address of upperTester to lowerTesters Resolving List (to allow the Controller to generate a Private Resolvable Address)
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[lowerTester].add( Address( SimpleAddressType.PUBLIC, 0x123456789ABC ) );
    success = success and RPAs[upperTester].add( Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF ), lowerIRK );
    """
        Set Resolvable Private Address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout(60);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    
    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );
        trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
            
    success = success and advertiser.disable();
    success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    return success;

"""
    GAP/CONN/NCON/BV-01-C [Non-Connectable Mode]
"""
def gap_conn_ncon_bv_01_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x123456789ABC ));

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );
    """
        Attempt to initiate connection with Advertiser
    """
    success = advertiser.enable();
    connected = initiator.connect();
    success = success and not connected;
    success = success and advertiser.disable();

    return success;

"""
    GAP/CONN/NCON/BV-02-C [Non-Connectable Mode and  General Discoverable Mode]
"""
def gap_conn_ncon_bv_02_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );

    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );

        if success:
            address = next(iter(devices));
            """
                Attempt to initiate connection with Advertiser
            """
            initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( devices[address]["type"], address ));
            connected = initiator.connect();
            success = success and not connected;
    
    success = success and advertiser.disable();

    return success;

"""
    GAP/CONN/NCON/BV-03-C [Non-Connectable Mode and  Limited Discoverable Mode]
"""
def gap_conn_ncon_bv_03_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );

    success = advertiser.enable();
    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );

        if success:
            address = next(iter(devices));
            """
                Attempt to initiate connection with Advertiser
            """
            initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( devices[address]["type"], address ));
            connected = initiator.connect();
            success = success and not connected;
    
    success = success and advertiser.disable();

    return success;

"""
    GAP/CONN/DCON/BV-01-C [Directed Connectable Mode]
"""
def gap_conn_dcon_bv_01_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_DIRECT_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    success = advertising = advertiser.enable();

    if success:
        success, devices = scanner.discover( 2000 );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );

        if success:
            address = next(iter(devices));
            """
                Attempt to initiate connection with Advertiser
            """
            initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( devices[address]["type"], address ));
            connected = initiator.connect();
            success = success and connected;
            advertising = not connected;

            if connected:
                connected = not initiator.disconnect(0x13);
                success = success and not connected;

    if advertising:         
        advertiser.disable();

    return success;

"""
    GAP/CONN/UCON/BV-01-C [Undirected Connectable Mode and Non-Discoverable Mode]
"""
def gap_conn_ucon_bv_01_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );

    success = advertising = advertiser.enable();

    if success:
        success, devices = scanner.discover( 2000 );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );

        if success:
            address = next(iter(devices));
            """
                Attempt to initiate connection with Advertiser
            """
            initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( devices[address]["type"], address ));
            connected = initiator.connect();
            success = success and connected;
            advertising = not connected;

            connected = not initiator.disconnect(0x13);
            success = success and not connected;

    if advertising:         
        advertiser.disable();

    return success;

"""
    GAP/CONN/UCON/BV-02-C [Undirected Connectable Mode and General Discoverable Mode]
"""
def gap_conn_ucon_bv_02_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );

    success = advertising = advertiser.enable();

    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );

        if success:
            address = next(iter(devices));
            """
                Attempt to initiate connection with Advertiser
            """
            initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( devices[address]["type"], address ));
            connected = initiator.connect();
            success = success and connected;
            advertising = not connected;

            connected = not initiator.disconnect(0x13);
            success = success and not connected;

    if advertising:         
        advertiser.disable();

    return success;

"""
    GAP/CONN/UCON/BV-03-C [Undirected Connectable Mode and Limited Discoverable Mode]
"""
def gap_conn_ucon_bv_03_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Flødebolle' );

    success = advertising = advertiser.enable();

    if success:
        success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
        for address in devices:
            trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), \
                                                                                      devices[address]["type"] ), devices[address]["name"]) );

        if success:
            address = next(iter(devices));
            """
                Attempt to initiate connection with Advertiser
            """
            initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( devices[address]["type"], address ));
            connected = initiator.connect();
            success = success and connected;
            advertising = not connected;

            connected = not initiator.disconnect(0x13);
            success = success and not connected;

    if advertising:
        advertiser.disable();

    return success;

"""
    GAP/CONN/ACEP/BV-01-C [Auto Connection Establishment with Directed Connectable Mode]
"""
def gap_conn_acep_bv_01_c(transport, upperTester, lowerTester, trace):

    """
        Place Public address of lowerTester in the Filter Accept List for the Scanner
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEF ]];
    success = preamble_specific_filter_accept_listed(transport, upperTester, addresses, trace);

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), \
                          Address( IdentityAddressType.PUBLIC, 0x456789ABCDEF ), InitiatorFilterPolicy.FILTER_ACCEPT_LIST_ONLY);

    advertising = advertiser.enable();
    success = success and advertising;

    if success:
        connected = initiator.connect();
        success = success and connected;
        advertising = not connected;

        connected = not initiator.disconnect(0x13);
        success = success and not connected;

    if advertising:         
        advertiser.disable();

    return success;

"""
    GAP/CONN/ACEP/BV-03-C [Auto Connection Establishment with Directed Connectable Mode, Resolvable Private Address, Central Address Resolution]
"""
def gap_conn_acep_bv_03_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to upperTesters Resolving List
        Add Public address of upperTester to lowerTesters Resolving List (to allow the Controller to generate a Private Resolvable Address)
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[lowerTester].add( Address( SimpleAddressType.PUBLIC, 0x123456789ABC ) );
    success = success and RPAs[upperTester].add( Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF ), lowerIRK );
    """
        Set Resolvable Private Address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout(60);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();
    """
        Place Public address of lowerTester in the Filter Accept List for the Scanner
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEF ]];
    success = preamble_specific_filter_accept_listed(transport, upperTester, addresses, trace);

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), \
                          Address( IdentityAddressType.PUBLIC, 0x456789ABCDEF ), InitiatorFilterPolicy.FILTER_ACCEPT_LIST_ONLY);

    advertising = advertiser.enable();
    success = success and advertising;

    if success:
        connected = initiator.connect();
        success = success and connected;
        advertising = not connected;

        connected = not initiator.disconnect(0x13);
        success = success and not connected;

    if advertising:         
        advertiser.disable();

    success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    return success;

"""
    GAP/CONN/ACEP/BV-04-C [Auto Connection Establishment with Undirected Connectable Mode, Resolvable Private Address]
"""
def gap_conn_acep_bv_04_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to upperTesters Resolving List
        Add Public address of upperTester to lowerTesters Resolving List (to allow the Controller to generate a Private Resolvable Address)
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[lowerTester].add( Address( SimpleAddressType.PUBLIC, 0x123456789ABC ) );
    success = success and RPAs[upperTester].add( Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF ), lowerIRK );
    """
        Set Resolvable Private Address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout(60);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();
    """
        Place Public address of lowerTester in the Filter Accept List for the Scanner
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEF ]];
    success = preamble_specific_filter_accept_listed(transport, upperTester, addresses, trace);

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), \
                          Address( IdentityAddressType.PUBLIC, 0x456789ABCDEF ), InitiatorFilterPolicy.FILTER_ACCEPT_LIST_ONLY);

    advertising = advertiser.enable();
    success = success and advertising;

    if success:
        connected = initiator.connect();
        success = success and connected;
        advertising = not connected;

        connected = not initiator.disconnect(0x13);
        success = success and not connected;

    if advertising:         
        advertiser.disable();

    success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    return success;

"""
    GAP/CONN/GCEP/BV-01-C [General Connection Establishment with Directed Connectable Mode]
"""
def gap_conn_gcep_bv_01_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEF ));

    success = advertising = advertiser.enable();
    connected = initiator.connect()
    success = success and connected;
    advertising = not connected;

    if connected:
        connected = not initiator.disconnect(0x13);
        success = success and not connected;

    if advertising:         
        advertiser.disable();

    return success;

"""
    GAP/CONN/GCEP/BV-02-C [General Connection Establishment with Undirected Connectable Mode]
"""
def gap_conn_gcep_bv_02_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEF ));

    success = advertising = advertiser.enable();
    connected = initiator.connect()
    success = success and connected;
    advertising = not connected;

    if connected:
        connected = not initiator.disconnect(0x13);
        success = success and not connected;

    if advertising:         
        advertiser.disable();

    return success;

"""
    GAP/CONN/GCEP/BV-05-C [General Connection Establishment with Directed Connectable Mode, Resolvable Private Address, Central Address Resolution]
"""
def gap_conn_gcep_bv_05_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to upperTesters Resolving List
        Add Public address of upperTester to lowerTesters Resolving List (to allow the Controller to generate a Private Resolvable Address)
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[lowerTester].add( Address( SimpleAddressType.PUBLIC, 0x123456789ABC ) );
    success = success and RPAs[upperTester].add( Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF ), lowerIRK );
    """
        Set Resolvable Private Address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout(60);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEF ));

    success = advertising = advertiser.enable();
    connected = initiator.connect()
    success = success and connected;
    advertising = not connected;

    if connected:
        connected = not initiator.disconnect(0x13);
        success = success and not connected;

    if advertising:         
        advertiser.disable();

    success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    return success;

"""
    GAP/CONN/GCEP/BV-06-C [General Connection Establishment with Undirected Connectable Mode, Resolvable Private Address]
"""
def gap_conn_gcep_bv_06_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to upperTesters Resolving List
        Add Public address of upperTester to lowerTesters Resolving List (to allow the Controller to generate a Private Resolvable Address)
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[lowerTester].add( Address( SimpleAddressType.PUBLIC, 0x123456789ABC ) );
    success = success and RPAs[upperTester].add( Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF ), lowerIRK );
    """
        Set Resolvable Private Address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout(60);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEF ));

    success = advertising = advertiser.enable();
    connected = initiator.connect()
    success = success and connected;
    advertising = not connected;

    if connected:
        connected = not initiator.disconnect(0x13);
        success = success and not connected;

    if advertising:         
        advertiser.disable();

    success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    return success;

"""
    GAP/CONN/CPUP/BV-01-C [Successful Peripheral initiated Connection Parameter Update]
"""
def gap_conn_cpup_bv_01_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x123456789ABC ))

    success = advertising = advertiser.enable()
    connected = initiator.connect()
    success = success and connected

    if connected:
        transport.wait(100)
        """
            Switch the roles, so that the upperTester initiates the Connection Parameter Update Procedure
        """
        initiator.switchRoles()
        """
            Setting new connection update parameters and send a LL_CONNECTION_PARAM_REQ
        """
        interval = 30
        timeout = 3000
        success = success and initiator.update(interval, interval, initiator.latency, timeout)
        """
            Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
        """
        success = success and initiator.acceptUpdate()
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event...
        """
        success = success and initiator.updated()

        transport.wait(100)
        initiator.resetRoles()
        disconnected = initiator.disconnect(0x13)
        success = success and disconnected
    else:
        advertiser.disable()

    return success

"""
    GAP/CONN/CPUP/BV-02-C [Timeout during Peripheral initiated Connection Parameter Update]
"""
def gap_conn_cpup_bv_02_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x123456789ABC ))

    success = advertising = advertiser.enable()
    connected = initiator.connect()
    success = success and connected

    if connected:
        transport.wait(100)
        """
            Switch the roles, so that the upperTester initiates the Connection Parameter Update Procedure
        """
        initiator.switchRoles()
        """
            Setting new connection update parameters and send a LL_CONNECTION_PARAM_REQ
        """
        interval = 30
        timeout = 3000
        success = success and initiator.update(interval, interval, initiator.latency, timeout)
        """
            Verify if initiator received an LE Connection Update Complete Event
        """
        transport.wait(200)
        success = success and not initiator.updated()
        """
            IUT ignores error case and continues normal operation
        """
        initiator.resetRoles()
        disconnected = initiator.disconnect(0x13)
        success = success and disconnected
    else:
        advertiser.disable()

    return success

"""
    GAP/CONN/CPUP/BV-03-C [Invalid Parameters in Peripheral initiated Connection Parameter Update]
"""
def gap_conn_cpup_bv_03_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x123456789ABC ))

    success = advertising = advertiser.enable()
    connected = initiator.connect()
    success = success and connected

    if connected:
        transport.wait(100)
        initiator.switchRoles()
        """
            Setting invalid connection update parameters (timeout > max_timeout) and send a LL_CONNECTION_PARAM_REQ
        """
        interval = 30
        timeout = 3300
        success = success and initiator.update(interval, interval, initiator.latency, timeout)
        """
            Try to accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
        """
        success = success and not initiator.acceptUpdate()
        """
            The tester should not receive any LE Connection Update Complete Event...
        """
        success = success and not initiator.updated()
        """
            Close connection
        """
        initiator.resetRoles()
        disconnected = initiator.disconnect(0x13)
        success = success and disconnected
    else:
        advertiser.disable()

    return success

"""
    GAP/CONN/CPUP/BV-04-C [Successful Peripheral accepts Connection Parameter Update]
"""
def gap_conn_cpup_bv_04_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC )
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEF ))

    success = advertising = advertiser.enable()
    connected = initiator.connect()
    success = success and connected

    if connected:
        transport.wait(100)
        initiator.switchRoles()
        """
            Setting invalid connection update parameters (timeout > max_timeout) and send a LL_CONNECTION_PARAM_REQ
        """
        interval = 30
        timeout = 3000
        success = success and initiator.update(interval, interval, initiator.latency, timeout)
        """
            Try to accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
        """
        success = success and initiator.acceptUpdate()
        """
            The testers should receive a Connection Update Complete Event...
        """
        success = success and initiator.updated()
        """
            Close connection
        """
        initiator.resetRoles()
        disconnected = initiator.disconnect(0x13)
        success = success and disconnected
    else:
        advertiser.disable()

    return success

"""
    GAP/CONN/CPUP/BV-05-C [Invalid Parameters in Peripheral receives Connection Parameter Update]
"""
def gap_conn_cpup_bv_05_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC )
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEF ))

    success = advertising = advertiser.enable()
    connected = initiator.connect()
    success = success and connected

    if connected:
        transport.wait(100)
        initiator.switchRoles()
        """
            Setting invalid connection update parameters (timeout > max_timeout) and send a LL_CONNECTION_PARAM_REQ
        """
        interval = 30
        timeout = 3300
        success = success and initiator.update(interval, interval, initiator.latency, timeout)
        """
            Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
        """
        success = success and not initiator.acceptUpdate()
        """
            The tester should not receive any LE Connection Update Complete Event...
        """
        success = success and not initiator.updated()
        """
            Close connection
        """
        initiator.resetRoles()
        disconnected = initiator.disconnect(0x13)
        success = success and disconnected
    else:
        advertiser.disable()

    return success

"""
    GAP/CONN/CPUP/BV-06-C [Successful Central initiated Connection Parameter Update]
"""
def gap_conn_cpup_bv_06_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC )
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEF ))

    success = advertising = advertiser.enable()
    connected = initiator.connect()
    success = success and connected

    if connected:
        transport.wait(100)
        """
            Setting invalid connection update parameters (timeout > max_timeout) and send a LL_CONNECTION_PARAM_REQ
        """
        interval = 30
        timeout = 3000
        success = success and initiator.update(interval, interval, initiator.latency, timeout)
        """
            Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
        """
        success = success and initiator.acceptUpdate()
        """
            The testers should receive LE Connection Update Complete Events...
        """
        success = success and initiator.updated()
        """
            Close connection
        """
        disconnected = initiator.disconnect(0x13)
        success = success and disconnected
    else:
        advertiser.disable()

    return success

"""
    GAP/ADV/BV-01-C [Advertising with AD Type - Service UUID]
"""
def gap_adv_bv_01_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.ILIST_UUIDS_16, 0x1234, 0x5678, 0x9ABC );
    advertiser.responseData = adData.encode( ADType.ILIST_UUIDS_16, 0x9ABC, 0x5678, 0x1234 );
    
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            
    success = success and advertiser.disable();

    advertiser.advertiseData = adData.encode( ADType.ILIST_UUIDS_128, 0x1429304977D74244AE6AD3873E4A3184 );
    advertiser.responseData = adData.encode( ADType.ILIST_UUIDS_128, 0x1429304977D74244AE6AD3873E4A3184 );
    
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/ADV/BV-02-C [Advertising with AD Type - Local Name]
"""
def gap_adv_bv_02_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.SHORTENED_LOCAL_NAME, 'Blåbær' );
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, 'Rødgrød med fløde' );
    
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/ADV/BV-03-C [Advertising with AD Type - Flags]
"""
def gap_adv_bv_03_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.FLAGS, 0x06 );
    advertiser.responseData = adData.encode( ADType.FLAGS, 0x1F );
    
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/ADV/BV-04-C [Advertising with AD Type - Manufacturer Specific Packet Data]
"""
def gap_adv_bv_04_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.MANUFACTURER_DATA, 0x0107, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05 ); # Manufacturer Oticon
    advertiser.responseData = adData.encode( ADType.MANUFACTURER_DATA, 0x0107, 0x05, 0x04, 0x03, 0x02, 0x01, 0x00 ); # Manufacturer Oticon
    
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/ADV/BV-05-C [Advertising with AD Type - TX Power Level]
"""
def gap_adv_bv_05_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.TX_POWER_LEVEL, -20 );
    advertiser.responseData = adData.encode( ADType.TX_POWER_LEVEL, -40 );
    
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/ADV/BV-08-C [Advertising with AD Type - Peripheral Connection Interval Range]
"""
def gap_adv_bv_08_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.PERIPHERAL_CONNECT_INT, 20, 40 );
    advertiser.responseData = adData.encode( ADType.PERIPHERAL_CONNECT_INT, 10, 50 );
    
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/ADV/BV-09-C [Advertising with AD Type - Service Solicitation]
"""
def gap_adv_bv_09_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.SS_UUIDS_16, 0x1234, 0x5678, 0x9ABC );
    advertiser.responseData = adData.encode( ADType.SS_UUIDS_128, 0x1429304977D74244AE6AD3873E4A3184 );
    
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/ADV/BV-10-C [Advertising with AD Type - Service Packet Data]
"""
def gap_adv_bv_10_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.SERVICE_DATA_16, 0x1234, 0x01, 0x02, 0x03 );
    advertiser.responseData = adData.encode( ADType.SERVICE_DATA_128, 0x1429304977D74244AE6AD3873E4A3184, 0x04, 0x05, 0x06 );
    
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/ADV/BV-11-C [Advertising with AD Type - Appearance]
"""
def gap_adv_bv_11_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.APPEARANCE, 640 );  # Media Player
    advertiser.responseData = adData.encode( ADType.APPEARANCE, 832 );   # Heart rate Sensor
    
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/ADV/BV-12-C [Advertising with AD Type - Public Target Address]
"""
def gap_adv_bv_12_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.PUBLIC_ADDRESS, 0x456789ABCDEF, 0x123456789ABC );
    advertiser.responseData = adData.encode( ADType.PUBLIC_ADDRESS, 0x123456789ABC, 0x456789ABCDEF );
    
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/ADV/BV-13-C [Advertising with AD Type - Random Target Address]
"""
def gap_adv_bv_13_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.RANDOM_ADDRESS, 0x456789ABCDEF, 0x123456789ABC );
    advertiser.responseData = adData.encode( ADType.RANDOM_ADDRESS, 0x123456789ABC, 0x456789ABCDEF );
    
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/ADV/BV-14-C [Advertising with AD Type - Advertising Interval]
"""
def gap_adv_bv_14_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.ADVERTISE_INT, 20 );
    advertiser.responseData = adData.encode( ADType.ADVERTISE_INT, 10 );
    
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/ADV/BV-15-C [Advertising with AD Type - LE Bluetooth Device Address]
"""
def gap_adv_bv_15_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.DEVICE_ADDRESS, 0x123456789ABC, 0 ); # Public Device Address
    advertiser.responseData = adData.encode( ADType.DEVICE_ADDRESS, 0x123456789ABC, 1 );  # Random Device Address
    
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/ADV/BV-16-C [Advertising with AD Type - LE Role]
"""
def gap_adv_bv_16_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.DEVICE_ROLE, ADRole.CENTRAL_PREFERRED );
    advertiser.responseData = adData.encode( ADType.DEVICE_ROLE, ADRole.PERIPHERAL_PREFERRED );
    
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/ADV/BV-17-C [Advertising with AD Type - URI]
"""
def gap_adv_bv_17_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEF );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.URI, 'http://www.bluetooth.org' );
    advertiser.responseData = adData.encode( ADType.URI, 'example://z.com/Ålborg' );
    
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            
    success = success and advertiser.disable();

    return success;

"""
    GAP/CONN/ENC [Testing encryption]
"""
def gap_conn_enc(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABC );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    ownAddress = Address( ExtendedAddressType.PUBLIC, 0x123456789ABC );
    peerAddress = Address( IdentityAddressType.PUBLIC, 0x456789ABCDEF );
    initiator = Initiator(transport, upperTester, lowerTester, trace, ownAddress, peerAddress);

    success = advertising = advertiser.enable();
    connected = initiator.connect()
    success = success and connected;
    advertising = not connected;

    pairing = Pairing(transport, trace, initiator, toNumber(upperIRK), toNumber(lowerIRK));
    success = pairing.pair();
    if success:
        trace.trace(6, "Link encrypted using LE Legacy Pairing...");
        success = pairing.pause();
        if success:
            trace.trace(6, "Link re-encrytpted using LE Legacy Pairing...");
        else:
            trace.trace(6, "Failed to re-encrypt link using LE Legacy Pairing!");
    else:
        trace.trace(6, "Failed to encrypt link using LE Legacy Pairing!");

    if connected:
        connected = not initiator.disconnect(0x13);
        success = success and not connected;

    if advertising:         
        advertiser.disable();

    return success;

__tests__ = {
    "GAP/ADV/BV-01-C":       [ gap_adv_bv_01_c,       "Advertising with AD Type - Service UUID" ],
    "GAP/ADV/BV-02-C":       [ gap_adv_bv_02_c,       "Advertising with AD Type - Local Name" ],
    "GAP/ADV/BV-03-C":       [ gap_adv_bv_03_c,       "Advertising with AD Type - Flags" ],
    "GAP/ADV/BV-04-C":       [ gap_adv_bv_04_c,       "Advertising with AD Type - Manufacturer Specific Packet Data" ],
    "GAP/ADV/BV-05-C":       [ gap_adv_bv_05_c,       "Advertising with AD Type - TX Power Level" ],
    "GAP/ADV/BV-08-C":       [ gap_adv_bv_08_c,       "Advertising with AD Type - Peripheral Connection Interval Range" ],
    "GAP/ADV/BV-09-C":       [ gap_adv_bv_09_c,       "Advertising with AD Type - Service Solicitation" ],
    "GAP/ADV/BV-10-C":       [ gap_adv_bv_10_c,       "Advertising with AD Type - Service Packet Data" ],
    "GAP/ADV/BV-11-C":       [ gap_adv_bv_11_c,       "Advertising with AD Type - Appearance" ],
    "GAP/ADV/BV-12-C":       [ gap_adv_bv_12_c,       "Advertising with AD Type - Public Target Address" ],
    "GAP/ADV/BV-13-C":       [ gap_adv_bv_13_c,       "Advertising with AD Type - Random Target Address" ],
    "GAP/ADV/BV-14-C":       [ gap_adv_bv_14_c,       "Advertising with AD Type - Advertising Interval" ],
    "GAP/ADV/BV-15-C":       [ gap_adv_bv_15_c,       "Advertising with AD Type - LE Bluetooth Device Address" ],
    "GAP/ADV/BV-16-C":       [ gap_adv_bv_16_c,       "Advertising with AD Type - LE Role" ],
    "GAP/ADV/BV-17-C":       [ gap_adv_bv_17_c,       "Advertising with AD Type - URI" ],
    "GAP/CONN/ACEP/BV-01-C": [ gap_conn_acep_bv_01_c, "Auto Connection Establishment with Directed Connectable Mode" ],
    "GAP/CONN/ACEP/BV-03-C": [ gap_conn_acep_bv_03_c, "Auto Connection Establishment with Directed Connectable Mode, Resolvable Private Address, Central Address Resolution" ],
    "GAP/CONN/ACEP/BV-04-C": [ gap_conn_acep_bv_04_c, "Auto Connection Establishment with Undirected Connectable Mode, Resolvable Private Address" ],
    "GAP/CONN/DCON/BV-01-C": [ gap_conn_dcon_bv_01_c, "Directed Connectable Mode" ],
#   "GAP/CONN/ENC":          [ gap_conn_enc,          "Testing encryption" ],
    "GAP/CONN/GCEP/BV-01-C": [ gap_conn_gcep_bv_01_c, "General Connection Establishment with Directed Connectable Mode" ],
    "GAP/CONN/GCEP/BV-02-C": [ gap_conn_gcep_bv_02_c, "General Connection Establishment with Undirected Connectable Mode" ],
    "GAP/CONN/GCEP/BV-05-C": [ gap_conn_gcep_bv_05_c, "General Connection Establishment with Directed Connectable Mode, Resolvable Private Address, Central Address Resolution" ],
    "GAP/CONN/GCEP/BV-06-C": [ gap_conn_gcep_bv_06_c, "General Connection Establishment with Undirected Connectable Mode, Resolvable Private Address" ],
    "GAP/CONN/CPUP/BV-01-C": [ gap_conn_cpup_bv_01_c, "Successful Peripheral initiated Connection Parameter Update" ],
    "GAP/CONN/CPUP/BV-02-C": [ gap_conn_cpup_bv_02_c, "Timeout during Peripheral initiated Connection Parameter Update" ],
    "GAP/CONN/CPUP/BV-03-C": [ gap_conn_cpup_bv_03_c, "Invalid Parameters in Peripheral initiated Connection Parameter Update" ],
    "GAP/CONN/CPUP/BV-04-C": [ gap_conn_cpup_bv_04_c, "Successful Peripheral accepts Connection Parameter Update" ],
    "GAP/CONN/CPUP/BV-05-C": [ gap_conn_cpup_bv_05_c, "Invalid Parameters in Peripheral receives Connection Parameter Update" ],
    "GAP/CONN/CPUP/BV-06-C": [ gap_conn_cpup_bv_06_c, "Successful Central initiated Connection Parameter Update" ],
    "GAP/CONN/NCON/BV-01-C": [ gap_conn_ncon_bv_01_c, "Non-Connectable Mode" ],
    "GAP/CONN/NCON/BV-02-C": [ gap_conn_ncon_bv_02_c, "Non-Connectable Mode and  General Discoverable Mode" ],
    "GAP/CONN/NCON/BV-03-C": [ gap_conn_ncon_bv_03_c, "Non-Connectable Mode and  Limited Discoverable Mode" ],
    "GAP/CONN/UCON/BV-01-C": [ gap_conn_ucon_bv_01_c, "Undirected Connectable Mode and Non-Discoverable Mode" ],
    "GAP/CONN/UCON/BV-02-C": [ gap_conn_ucon_bv_02_c, "Undirected Connectable Mode and General Discoverable Mode" ],
    "GAP/CONN/UCON/BV-03-C": [ gap_conn_ucon_bv_03_c, "Undirected Connectable Mode and Limited Discoverable Mode" ],
    "GAP/DISC/GENM/BV-01-C": [ gap_disc_genm_bv_01_c, "General Discoverable Mode and Non-Connectable Mode in BR/EDR/LE configuration" ],
    "GAP/DISC/GENM/BV-02-C": [ gap_disc_genm_bv_02_c, "General Discoverable Mode and Undirected Connectable Mode in BR/EDR/LE configuration" ],
    "GAP/DISC/GENM/BV-03-C": [ gap_disc_genm_bv_03_c, "General Discoverable Mode and Non-Connectable Mode in LE Only configuration" ],
    "GAP/DISC/GENM/BV-04-C": [ gap_disc_genm_bv_04_c, "General Discoverable Mode and Undirected Connectable Mode in LE Only configuration" ],
    "GAP/DISC/GENP/BV-01-C": [ gap_disc_genp_bv_01_c, "General Discovery finding General Discoverable Device" ],
    "GAP/DISC/GENP/BV-02-C": [ gap_disc_genp_bv_02_c, "General Discovery finding Limited Discoverable Device" ],
    "GAP/DISC/GENP/BV-04-C": [ gap_disc_genp_bv_04_c, "General Discovery not finding Undirected Connectable device" ],
    "GAP/DISC/GENP/BV-05-C": [ gap_disc_genp_bv_05_c, "General Discovery not finding Directed Connectable device" ],
    "GAP/DISC/LIMM/BV-01-C": [ gap_disc_limm_bv_01_c, "Limited Discoverable Mode and Non-Connectable Mode in BR/EDR/LE configuration" ],
    "GAP/DISC/LIMM/BV-02-C": [ gap_disc_limm_bv_02_c, "Limited Discoverable Mode and Undirected Connectable Mode in BR/EDR/LE configuration" ],
    "GAP/DISC/LIMM/BV-03-C": [ gap_disc_limm_bv_03_c, "Limited Discoverable Mode and Non-Connectable Mode in LE Only configuration" ],
    "GAP/DISC/LIMM/BV-04-C": [ gap_disc_limm_bv_04_c, "Limited Discoverable Mode and Undirected Connectable Mode in LE Only configuration" ],
    "GAP/DISC/LIMP/BV-01-C": [ gap_disc_limp_bv_01_c, "Limited Discovery finding Limited Discoverable Device" ],
    "GAP/DISC/LIMP/BV-02-C": [ gap_disc_limp_bv_02_c, "Limited Discovery not finding General Discoverable Device" ],
    "GAP/DISC/LIMP/BV-04-C": [ gap_disc_limp_bv_04_c, "Limited Discovery not finding Undirected Connectable device" ],
    "GAP/DISC/LIMP/BV-05-C": [ gap_disc_limp_bv_05_c, "Limited Discovery not finding Directed Connectable device" ],
    "GAP/DISC/NONM/BV-01-C": [ gap_disc_nonm_bv_01_c, "Non-discoverable Mode and Non-Connectable Mode" ],
    "GAP/DISC/NONM/BV-02-C": [ gap_disc_nonm_bv_02_c, "Non-discoverable Mode and Undirected Connectable Mode" ],
    "GAP/DISC/RPA/BV-01-C":  [ gap_disc_rpa_bv_01_c,  "Find Discoverable Device using Resolvable Private Address" ]
};

_maxNameLength = max([ len(key) for key in __tests__ ]);

_spec = { key: TestSpec(name = key, number_devices = 2, description = "#[" + __tests__[key][1] + "]", test_private = __tests__[key][0]) for key in __tests__ };


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
    success = preamble_standby(transport, 1, trace);
    ok = ok and success;
    trace.trace(4, "preamble Standby " + ("PASS" if success else "FAIL"));
    success, upperIRK, upperRandomAddress = preamble_device_address_set(transport, 0, trace);
    trace.trace(4, "preamble Device Address Set " + ("PASS" if success else "FAIL"));
    ok = ok and success;        
    success, lowerIRK, lowerRandomAddress = preamble_device_address_set(transport, 1, trace);
    trace.trace(4, "preamble Device Address Set " + ("PASS" if success else "FAIL"));
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
