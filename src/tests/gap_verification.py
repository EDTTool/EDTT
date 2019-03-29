# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

import random;
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
    GAP/DMP/NDM/1-C [Non-discoverable Mode and Non-Connectable Mode]
"""
def gap_dmp_ndm_1_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/DMP/NDM/2-C [Non-discoverable Mode and Undirected Connectable Mode]
"""
def gap_dmp_ndm_2_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/DMP/LDM/1-C [Limited Discoverable Mode and Non-Connectable Mode in BR/EDR/LE configuration]
"""
def gap_dmp_ldm_1_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/DMP/LDM/2-C [Limited Discoverable Mode and Undirected Connectable Mode in BR/EDR/LE configuration]
"""
def gap_dmp_ldm_2_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/DMP/LDM/3-C [Limited Discoverable Mode and Non-Connectable Mode in LE Only configuration]
"""
def gap_dmp_ldm_3_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/DMP/LDM/4-C [Limited Discoverable Mode and Undirected Connectable Mode in LE Only configuration]
"""
def gap_dmp_ldm_4_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/DMP/GDM/1-C [General Discoverable Mode and Non-Connectable Mode in BR/EDR/LE configuration]
"""
def gap_dmp_gdm_1_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/DMP/GDM/2-C [General Discoverable Mode and Undirected Connectable Mode in BR/EDR/LE configuration]
"""
def gap_dmp_gdm_2_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/DMP/GDM/3-C [General Discoverable Mode and Non-Connectable Mode in LE Only configuration]
"""
def gap_dmp_gdm_3_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/DMP/GDM/4-C [General Discoverable Mode and Undirected Connectable Mode in LE Only configuration]
"""
def gap_dmp_gdm_4_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/DMP/LDP/1-C [Limited Discovery finding Limited Discoverable Device]
"""
def gap_dmp_ldp_1_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);

    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.responseData  = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/DMP/LDP/2-C [Limited Discovery not finding General Discoverable Device]
"""
def gap_dmp_ldp_2_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.responseData  = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/DMP/LDP/4-C [Limited Discovery not finding Undirected Connectable device]
"""
def gap_dmp_ldp_4_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/DMP/LDP/5-C [Limited Discovery not finding Directed Connectable device]
"""
def gap_dmp_ldp_5_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/DMP/GDP/1-C [General Discovery finding General Discoverable Device]
"""
def gap_dmp_gdp_1_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.responseData  = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/DMP/GDP/2-C [General Discovery finding Limited Discoverable Device]
"""
def gap_dmp_gdp_2_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.responseData  = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/DMP/GDP/4-C [General Discovery not finding Undirected Connectable device]
"""
def gap_dmp_gdp_4_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData  = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/DMP/GDP/5-C [General Discovery not finding Directed Connectable device]
"""
def gap_dmp_gdp_5_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/DMP/RPA/1-C [Find Discoverable Device using Resolvable Private Address]
"""
def gap_dmp_rpa_1_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to upperTesters Resolving List
        Add Public address of upperTester to lowerTesters Resolving List (to allow the Controller to generate a Private Resolvable Address)
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[lowerTester].add( Address( SimpleAddressType.PUBLIC, 0x123456789ABCL ) );
    success = success and RPAs[upperTester].add( Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL ), lowerIRK );
    """
        Set Resolvable Private Address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout(60);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
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
    GAP/CMP/NCM/1-C [Non-Connectable Mode]
"""
def gap_cmp_ncm_1_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ));

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
    """
        Attempt to initiate connection with Advertiser
    """
    success = advertiser.enable();
    connected = initiator.connect();
    success = success and not connected;
    success = success and advertiser.disable();

    return success;

"""
    GAP/CMP/NCM/2-C [Non-Connectable Mode and  General Discoverable Mode]
"""
def gap_cmp_ncm_2_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );

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
    GAP/CMP/NCM/3-C [Non-Connectable Mode and  Limited Discoverable Mode]
"""
def gap_cmp_ncm_3_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );

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
    GAP/CMP/DCM/1-C [Directed Connectable Mode]
"""
def gap_cmp_dcm_1_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
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
                connected = not initiator.disconnect(0x3E);
                success = success and not connected;

    if advertising:             
        advertiser.disable();

    return success;

"""
    GAP/CMP/UCM/1-C [Undirected Connectable Mode and Non-Discoverable Mode]
"""
def gap_cmp_ucm_1_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );

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

            connected = not initiator.disconnect(0x3E);
            success = success and not connected;

    if advertising:             
        advertiser.disable();

    return success;

"""
    GAP/CMP/UCM/2-C [Undirected Connectable Mode and General Discoverable Mode]
"""
def gap_cmp_ucm_2_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );

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

            connected = not initiator.disconnect(0x3E);
            success = success and not connected;

    if advertising:             
        advertiser.disable();

    return success;

"""
    GAP/CMP/UCM/3-C [Undirected Connectable Mode and Limited Discoverable Mode]
"""
def gap_cmp_ucm_3_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

    adData = ADData();
    advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
    advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
    advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );

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

            connected = not initiator.disconnect(0x3E);
            success = success and not connected;

    if advertising:
        advertiser.disable();

    return success;

"""
    GAP/CMP/ACEP/1-C [Auto Connection Establishment with Directed Connectable Mode]
"""
def gap_cmp_acep_1_c(transport, upperTester, lowerTester, trace):

    """
        Place Public address of lowerTester in the White List for the Scanner
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
    success = preamble_specific_white_listed(transport, upperTester, addresses, trace);

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), \
                          Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ), InitiatorFilterPolicy.FILTER_WHITE_LIST_ONLY);

    advertising = advertiser.enable();
    success = success and advertising;

    if success:
        connected = initiator.connect();
        success = success and connected;
        advertising = not connected;

        connected = not initiator.disconnect(0x3E);
        success = success and not connected;

    if advertising:             
        advertiser.disable();

    return success;

"""
    GAP/CMP/ACEP/3-C [Auto Connection Establishment with Directed Connectable Mode, Resolvable Private Address, Central Address Resolution]
"""
def gap_cmp_acep_3_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to upperTesters Resolving List
        Add Public address of upperTester to lowerTesters Resolving List (to allow the Controller to generate a Private Resolvable Address)
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[lowerTester].add( Address( SimpleAddressType.PUBLIC, 0x123456789ABCL ) );
    success = success and RPAs[upperTester].add( Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL ), lowerIRK );
    """
        Set Resolvable Private Address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout(60);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();
    """
        Place Public address of lowerTester in the White List for the Scanner
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
    success = preamble_specific_white_listed(transport, upperTester, addresses, trace);

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), \
                          Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ), InitiatorFilterPolicy.FILTER_WHITE_LIST_ONLY);

    advertising = advertiser.enable();
    success = success and advertising;

    if success:
        connected = initiator.connect();
        success = success and connected;
        advertising = not connected;

        connected = not initiator.disconnect(0x3E);
        success = success and not connected;

    if advertising:             
        advertiser.disable();

    success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    return success;

"""
    GAP/CMP/ACEP/4-C [Auto Connection Establishment with Undirected Connectable Mode, Resolvable Private Address]
"""
def gap_cmp_acep_4_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to upperTesters Resolving List
        Add Public address of upperTester to lowerTesters Resolving List (to allow the Controller to generate a Private Resolvable Address)
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[lowerTester].add( Address( SimpleAddressType.PUBLIC, 0x123456789ABCL ) );
    success = success and RPAs[upperTester].add( Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL ), lowerIRK );
    """
        Set Resolvable Private Address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout(60);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();
    """
        Place Public address of lowerTester in the White List for the Scanner
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
    success = preamble_specific_white_listed(transport, upperTester, addresses, trace);

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), \
                          Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ), InitiatorFilterPolicy.FILTER_WHITE_LIST_ONLY);

    advertising = advertiser.enable();
    success = success and advertising;

    if success:
        connected = initiator.connect();
        success = success and connected;
        advertising = not connected;

        connected = not initiator.disconnect(0x3E);
        success = success and not connected;

    if advertising:             
        advertiser.disable();

    success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    return success;

"""
    GAP/CMP/GCEP/1-C [General Connection Establishment with Directed Connectable Mode]
"""
def gap_cmp_gcep_1_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ));
 
    success = advertising = advertiser.enable();
    connected = initiator.connect()
    success = success and connected;
    advertising = not connected;

    if connected: 
        connected = not initiator.disconnect(0x3E);
        success = success and not connected;

    if advertising:             
        advertiser.disable();

    return success;

"""
    GAP/CMP/GCEP/2-C [General Connection Establishment with Undirected Connectable Mode]
"""
def gap_cmp_gcep_2_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ));
 
    success = advertising = advertiser.enable();
    connected = initiator.connect()
    success = success and connected;
    advertising = not connected;

    if connected: 
        connected = not initiator.disconnect(0x3E);
        success = success and not connected;

    if advertising:             
        advertiser.disable();

    return success;

"""
    GAP/CMP/GCEP/5-C [General Connection Establishment with Directed Connectable Mode, Resolvable Private Address, Central Address Resolution]
"""
def gap_cmp_gcep_5_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to upperTesters Resolving List
        Add Public address of upperTester to lowerTesters Resolving List (to allow the Controller to generate a Private Resolvable Address)
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[lowerTester].add( Address( SimpleAddressType.PUBLIC, 0x123456789ABCL ) );
    success = success and RPAs[upperTester].add( Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL ), lowerIRK );
    """
        Set Resolvable Private Address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout(60);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ));
 
    success = advertising = advertiser.enable();
    connected = initiator.connect()
    success = success and connected;
    advertising = not connected;

    if connected: 
        connected = not initiator.disconnect(0x3E);
        success = success and not connected;

    if advertising:             
        advertiser.disable();

    success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    return success;

"""
    GAP/CMP/GCEP/6-C [General Connection Establishment with Undirected Connectable Mode, Resolvable Private Address]
"""
def gap_cmp_gcep_6_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to upperTesters Resolving List
        Add Public address of upperTester to lowerTesters Resolving List (to allow the Controller to generate a Private Resolvable Address)
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[lowerTester].add( Address( SimpleAddressType.PUBLIC, 0x123456789ABCL ) );
    success = success and RPAs[upperTester].add( Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL ), lowerIRK );
    """
        Set Resolvable Private Address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout(60);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ));
 
    success = advertising = advertiser.enable();
    connected = initiator.connect()
    success = success and connected;
    advertising = not connected;

    if connected: 
        connected = not initiator.disconnect(0x3E);
        success = success and not connected;

    if advertising:             
        advertiser.disable();

    success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    return success;

"""
    GAP/CMP/CPUP/1-C [Successful Peripheral initiated Connection Parameter Update]
"""
def gap_cmp_cpup_1_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ))
 
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
        disconnected = initiator.disconnect(0x3E)
        success = success and disconnected
    else:
        advertiser.disable()

    return success

"""
    GAP/CMP/CPUP/2-C [Timeout during Peripheral initiated Connection Parameter Update]
"""
def gap_cmp_cpup_2_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ))
 
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
        disconnected = initiator.disconnect(0x3E)
        success = success and disconnected
    else:
        advertiser.disable()

    return success

"""
    GAP/CMP/CPUP/3-C [Invalid Parameters in Peripheral initiated Connection Parameter Update]
"""
def gap_cmp_cpup_3_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ))
 
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
        disconnected = initiator.disconnect(0x3E)
        success = success and disconnected
    else:
        advertiser.disable()

    return success

"""
    GAP/CMP/CPUP/4-C [Successful Peripheral accepts Connection Parameter Update]
"""
def gap_cmp_cpup_4_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL )
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ))
 
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
        disconnected = initiator.disconnect(0x3E)
        success = success and disconnected
    else:
        advertiser.disable()

    return success

"""
    GAP/CMP/CPUP/5-C [Invalid Parameters in Peripheral receives Connection Parameter Update]
"""
def gap_cmp_cpup_5_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL )
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ))
 
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
        disconnected = initiator.disconnect(0x3E)
        success = success and disconnected
    else:
        advertiser.disable()

    return success

"""
    GAP/CMP/CPUP/6-C [Successful Central initiated Connection Parameter Update]
"""
def gap_cmp_cpup_6_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL )
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ))
 
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
        disconnected = initiator.disconnect(0x3E)
        success = success and disconnected
    else:
        advertiser.disable()

    return success

"""
    GAP/ASPD/1-C [Advertising with AD Type – Service UUID]
"""
def gap_aspd_1_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
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

    advertiser.advertiseData = adData.encode( ADType.ILIST_UUIDS_128, 0x1429304977D74244AE6AD3873E4A3184L );
    advertiser.responseData = adData.encode( ADType.ILIST_UUIDS_128, 0x1429304977D74244AE6AD3873E4A3184L );
        
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
    success = success and advertiser.disable();

    return success;

"""
    GAP/ASPD/2-C [Advertising with AD Type - Local Name]
"""
def gap_aspd_2_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.SHORTENED_LOCAL_NAME, u'Blåbær' );
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Rødgrød med fløde' );
        
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
    success = success and advertiser.disable();

    return success;

"""
    GAP/ASPD/3-C [Advertising with AD Type – Flags]
"""
def gap_aspd_3_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
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
    GAP/ASPD/4-C [Advertising with AD Type – Manufacturer Specific Packet Data]
"""
def gap_aspd_4_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
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
    GAP/ASPD/5-C [Advertising with AD Type – TX Power Level]
"""
def gap_aspd_5_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
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
    GAP/ASPD/6-C [Advertising with AD Type – Slave Connection Interval Range]
"""
def gap_aspd_6_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
    advertiser.responseData = adData.encode( ADType.SLAVE_CONNECT_INT, 10, 50 );
        
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
    success = success and advertiser.disable();

    return success;

"""
    GAP/ASPD/7-C [Advertising with AD Type - Service Solicitation]
"""
def gap_aspd_7_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.SS_UUIDS_16, 0x1234, 0x5678, 0x9ABC );
    advertiser.responseData = adData.encode( ADType.SS_UUIDS_128, 0x1429304977D74244AE6AD3873E4A3184L );
        
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
    success = success and advertiser.disable();

    return success;

"""
    GAP/ASPD/8-C [Advertising with AD Type – Service Packet Data]
"""
def gap_aspd_8_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.SERVICE_DATA_16, 0x1234, 0x01, 0x02, 0x03 );
    advertiser.responseData = adData.encode( ADType.SERVICE_DATA_128, 0x1429304977D74244AE6AD3873E4A3184L, 0x04, 0x05, 0x06 );
        
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
    success = success and advertiser.disable();

    return success;

"""
    GAP/ASPD/9-C [Advertising with AD Type – Appearance]
"""
def gap_aspd_9_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
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
    GAP/ASPD/10-C [Advertising with AD Type – Public Target Address]
"""
def gap_aspd_10_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.PUBLIC_ADDRESS, 0x456789ABCDEFL, 0x123456789ABCL );
    advertiser.responseData = adData.encode( ADType.PUBLIC_ADDRESS, 0x123456789ABCL, 0x456789ABCDEFL );
        
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
    success = success and advertiser.disable();

    return success;

"""
    GAP/ASPD/11-C [Advertising with AD Type – Random Target Address]
"""
def gap_aspd_11_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.RANDOM_ADDRESS, 0x456789ABCDEFL, 0x123456789ABCL );
    advertiser.responseData = adData.encode( ADType.RANDOM_ADDRESS, 0x123456789ABCL, 0x456789ABCDEFL );
        
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
    success = success and advertiser.disable();

    return success;

"""
    GAP/ASPD/12-C [Advertising with AD Type – Advertising Interval]
"""
def gap_aspd_12_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
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
    GAP/ASPD/13-C [Advertising with AD Type – LE Bluetooth Device Address]
"""
def gap_aspd_13_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.DEVICE_ADDRESS, 0x123456789ABCL, 0 ); # Public Device Address
    advertiser.responseData = adData.encode( ADType.DEVICE_ADDRESS, 0x123456789ABCL, 1 );  # Random Device Address
        
    success = advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
    success = success and advertiser.disable();

    return success;

"""
    GAP/ASPD/14-C [Advertising with AD Type – LE Role]
"""
def gap_aspd_14_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
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
    GAP/ASPD/15-C [Advertising with AD Type – URI]
"""
def gap_aspd_15_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

    adData = ADData();
    advertiser.advertiseData = adData.encode( ADType.URI, u'http://www.bluetooth.org' );
    advertiser.responseData = adData.encode( ADType.URI, u'example://z.com/Ålborg' );
        
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
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    ownAddress = Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL );
    peerAddress = Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL );
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
        connected = not initiator.disconnect(0x3E);
        success = success and not connected;

    if advertising:             
        advertiser.disable();

    return success;

__tests__ = {
    "GAP/ASPD/1-C":     [ gap_aspd_1_c,     "Advertising with AD Type – Service UUID" ],
    "GAP/ASPD/2-C":     [ gap_aspd_2_c,     "Advertising with AD Type - Local Name" ],
    "GAP/ASPD/3-C":     [ gap_aspd_3_c,     "Advertising with AD Type – Flags" ],
    "GAP/ASPD/4-C":     [ gap_aspd_4_c,     "Advertising with AD Type – Manufacturer Specific Packet Data" ],
    "GAP/ASPD/5-C":     [ gap_aspd_5_c,     "Advertising with AD Type – TX Power Level" ],
    "GAP/ASPD/6-C":     [ gap_aspd_6_c,     "Advertising with AD Type – Slave Connection Interval Range" ],
    "GAP/ASPD/7-C":     [ gap_aspd_7_c,     "Advertising with AD Type - Service Solicitation" ],
    "GAP/ASPD/8-C":     [ gap_aspd_8_c,     "Advertising with AD Type – Service Packet Data" ],
    "GAP/ASPD/9-C":     [ gap_aspd_9_c,     "Advertising with AD Type – Appearance" ],
    "GAP/ASPD/10-C":    [ gap_aspd_10_c,    "Advertising with AD Type – Public Target Address" ],
    "GAP/ASPD/11-C":    [ gap_aspd_11_c,    "Advertising with AD Type – Random Target Address" ],
    "GAP/ASPD/12-C":    [ gap_aspd_12_c,    "Advertising with AD Type – Advertising Interval" ],
    "GAP/ASPD/13-C":    [ gap_aspd_13_c,    "Advertising with AD Type – LE Bluetooth Device Address" ],
    "GAP/ASPD/14-C":    [ gap_aspd_14_c,    "Advertising with AD Type – LE Role" ],
    "GAP/ASPD/15-C":    [ gap_aspd_15_c,    "Advertising with AD Type – URI" ],
    "GAP/CMP/ACEP/1-C": [ gap_cmp_acep_1_c, "Auto Connection Establishment with Directed Connectable Mode" ],
    "GAP/CMP/ACEP/3-C": [ gap_cmp_acep_3_c, "Auto Connection Establishment with Directed Connectable Mode, Resolvable Private Address, Central Address Resolution" ],
    "GAP/CMP/ACEP/4-C": [ gap_cmp_acep_4_c, "Auto Connection Establishment with Undirected Connectable Mode, Resolvable Private Address" ],
    "GAP/CMP/DCM/1-C":  [ gap_cmp_dcm_1_c,  "Directed Connectable Mode" ],
#   "GAP/CONN/ENC":     [ gap_conn_enc,     "Testing encryption" ],
    "GAP/CMP/GCEP/1-C": [ gap_cmp_gcep_1_c, "General Connection Establishment with Directed Connectable Mode" ],
    "GAP/CMP/GCEP/2-C": [ gap_cmp_gcep_2_c, "General Connection Establishment with Undirected Connectable Mode" ],
    "GAP/CMP/GCEP/5-C": [ gap_cmp_gcep_5_c, "General Connection Establishment with Directed Connectable Mode, Resolvable Private Address, Central Address Resolution" ],
    "GAP/CMP/GCEP/6-C": [ gap_cmp_gcep_6_c, "General Connection Establishment with Undirected Connectable Mode, Resolvable Private Address" ],
    "GAP/CMP/CPUP/1-C": [ gap_cmp_cpup_1_c, "Successful Peripheral initiated Connection Parameter Update" ],
    "GAP/CMP/CPUP/2-C": [ gap_cmp_cpup_2_c, "Timeout during Peripheral initiated Connection Parameter Update" ],
    "GAP/CMP/CPUP/3-C": [ gap_cmp_cpup_3_c, "Invalid Parameters in Peripheral initiated Connection Parameter Update" ],
    "GAP/CMP/CPUP/4-C": [ gap_cmp_cpup_4_c, "Successful Peripheral accepts Connection Parameter Update" ],
    "GAP/CMP/CPUP/5-C": [ gap_cmp_cpup_5_c, "Invalid Parameters in Peripheral receives Connection Parameter Update" ],
    "GAP/CMP/CPUP/6-C": [ gap_cmp_cpup_6_c, "Successful Central initiated Connection Parameter Update" ],
    "GAP/CMP/NCM/1-C":  [ gap_cmp_ncm_1_c,  "Non-Connectable Mode" ],
    "GAP/CMP/NCM/2-C":  [ gap_cmp_ncm_2_c,  "Non-Connectable Mode and  General Discoverable Mode" ],
    "GAP/CMP/NCM/3-C":  [ gap_cmp_ncm_3_c,  "Non-Connectable Mode and  Limited Discoverable Mode" ],
    "GAP/CMP/UCM/1-C":  [ gap_cmp_ucm_1_c,  "Undirected Connectable Mode and Non-Discoverable Mode" ],
    "GAP/CMP/UCM/2-C":  [ gap_cmp_ucm_2_c,  "Undirected Connectable Mode and General Discoverable Mode" ],
    "GAP/CMP/UCM/3-C":  [ gap_cmp_ucm_3_c,  "Undirected Connectable Mode and Limited Discoverable Mode" ],
    "GAP/DMP/GDM/1-C":  [ gap_dmp_gdm_1_c,  "General Discoverable Mode and Non-Connectable Mode in BR/EDR/LE configuration" ],
    "GAP/DMP/GDM/2-C":  [ gap_dmp_gdm_2_c,  "General Discoverable Mode and Undirected Connectable Mode in BR/EDR/LE configuration" ],
    "GAP/DMP/GDM/3-C":  [ gap_dmp_gdm_3_c,  "General Discoverable Mode and Non-Connectable Mode in LE Only configuration" ],
    "GAP/DMP/GDM/4-C":  [ gap_dmp_gdm_4_c,  "General Discoverable Mode and Undirected Connectable Mode in LE Only configuration" ],
    "GAP/DMP/GDP/1-C":  [ gap_dmp_gdp_1_c,  "General Discovery finding General Discoverable Device" ],
    "GAP/DMP/GDP/2-C":  [ gap_dmp_gdp_2_c,  "General Discovery finding Limited Discoverable Device" ],
    "GAP/DMP/GDP/4-C":  [ gap_dmp_gdp_4_c,  "General Discovery not finding Undirected Connectable device" ],
    "GAP/DMP/GDP/5-C":  [ gap_dmp_gdp_5_c,  "General Discovery not finding Directed Connectable device" ],
    "GAP/DMP/LDM/1-C":  [ gap_dmp_ldm_1_c,  "Limited Discoverable Mode and Non-Connectable Mode in BR/EDR/LE configuration" ],
    "GAP/DMP/LDM/2-C":  [ gap_dmp_ldm_2_c,  "Limited Discoverable Mode and Undirected Connectable Mode in BR/EDR/LE configuration" ],
    "GAP/DMP/LDM/3-C":  [ gap_dmp_ldm_3_c,  "Limited Discoverable Mode and Non-Connectable Mode in LE Only configuration" ],
    "GAP/DMP/LDM/4-C":  [ gap_dmp_ldm_4_c,  "Limited Discoverable Mode and Undirected Connectable Mode in LE Only configuration" ],
    "GAP/DMP/LDP/1-C":  [ gap_dmp_ldp_1_c,  "Limited Discovery finding Limited Discoverable Device" ],
    "GAP/DMP/LDP/2-C":  [ gap_dmp_ldp_2_c,  "Limited Discovery not finding General Discoverable Device" ],
    "GAP/DMP/LDP/4-C":  [ gap_dmp_ldp_4_c,  "Limited Discovery not finding Undirected Connectable device" ],
    "GAP/DMP/LDP/5-C":  [ gap_dmp_ldp_5_c,  "Limited Discovery not finding Directed Connectable device" ],
    "GAP/DMP/NDM/1-C":  [ gap_dmp_ndm_1_c,  "Non-discoverable Mode and Non-Connectable Mode" ],
    "GAP/DMP/NDM/2-C":  [ gap_dmp_ndm_2_c,  "Non-discoverable Mode and Undirected Connectable Mode" ],
    "GAP/DMP/RPA/1-C":  [ gap_dmp_rpa_1_c,  "Find Discoverable Device using Resolvable Private Address" ]
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
def run_a_test(args, transport, trace, test_spec):
    try:
        success = preamble(transport, trace);
    except Exception as e: 
        trace.trace(3, "Preamble generated exception: %s" % str(e));
        success = False;

    trace.trace(2, "%-*s %s test started..." % (_maxNameLength, test_spec.name, test_spec.description[1:]));
    test_f = test_spec.test_private;
    try:
        if test_f.__code__.co_argcount > 3:
            success = success and test_f(transport, 0, 1, trace);
        else:
            success = success and test_f(transport, 0, trace);
    except Exception as e: 
        trace.trace(3, "Test generated exception: %s" % str(e));
        success = False;

    return not success
