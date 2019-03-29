# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

import statistics;
from enum import IntEnum;
from components.utils import *;
from components.basic_commands import *;
from components.address import *;
from components.addata import *;

class ScanningFilterPolicy(IntEnum):
    FILTER_NONE          = 0       # Accept all advertising packets except directed advertising packets not addressed to this device (default).
    FILTER_WHITE_LIST    = 1       # Accept only advertising packets from devices where the advertiser’s address is in the White List.
                                   # Directed advertising packets which are not addressed to this device shall be ignored.
    FILTER_ID_DIRECTED   = 2       # Accept all advertising packets except directed advertising packets where the initiator's identity address does not address this device.
                                   # Note: Directed advertising packets where the initiator's address is a resolvable private address that cannot be resolved are also accepted.
    FILTER_ID_WHITE_LIST = 3       # Accept all advertising packets except:
                                   # • advertising packets where the advertiser's identity address is not in the White List; and
                                   # • directed advertising packets where the initiator's identity address does not address this device.
                                   # Note: Directed advertising packets where the initiator's address is a resolvable private address that cannot be resolved are also accepted.

class ScanType(IntEnum):
    PASSIVE = 0                    # Use PASSIVE Scanning
    ACTIVE  = 1                    # Use ACTIVE Scanning

class ScanFilterDuplicate(IntEnum):
    DISABLE = 0                    # Don't filter duplicate Advertisers
    ENABLE  = 1                    # Do filter duplicate Advertisers

class Scan(IntEnum):
    DISABLE = 0                    # Disable Scanning
    ENABLE  = 1                    # Enable Scanning
    
class AdvertisingReport(IntEnum):
    ADV_IND         = 0            # Connectable undirected advertising
    ADV_DIRECT_IND  = 1            # Connectable directed advertising
    ADV_SCAN_IND    = 2            # Scannable undirected advertising
    ADV_NONCONN_IND = 3            # Non connectable undirected advertising
    SCAN_RSP        = 4            # Scan Response
    
class Scanner:
    """
        A Scanner handles all aspects of Scanning.
        - Set Scan parameters.
        - Enable Scanning.
        - Disable Scanning.
        - Monitor Advertising reports and Scan responses.
        - Monitor Advertising timing (for High Duty-Cycle directed Advertsing)
    """
    """
        Constructor:
            transport         - PTTT_nwtsim object
            idx               - Number; Device identifier
            trace             - Trace object
            scanType          - ScanType enum; determining whether to perform PASSIVE or ACTIVE scanning
            reportType        - AdvertisingReport enum holding the type of advertising reports to expect
            ownAddress        - Address object with an ExtendedAddressType address (only the address type is used)
            filterPolicy      - ScannningFilterPolicy enum holding the typ of scanning filter to apply
            expectedReports   - Number; holding the number of advertising reports to expect
            expectedResponses - Number; holding the number of advertising responses to expect
    """
    def __init__(self, transport, idx, trace, scanType, reportType, ownAddress, filterPolicy=ScanningFilterPolicy.FILTER_NONE, expectedReports=20, expectedResponses=None):
        self.transport = transport;
        self.idx = idx;
        self.trace = trace;
        self.scanType = scanType;
        self.reportType = reportType;
        self.ownAddress = ownAddress;
        self.filterPolicy = filterPolicy;
        self.expectedReports = expectedReports;
        self.expectedResponses = expectedResponses;
        """
            The LE_Scan_Interval and LE_Scan_Window parameters are recommendations from the Host on how long (LE_Scan_Window) and how frequently (LE_Scan_Interval) the Controller should scan
            (See [Vol 6] Part B, Section 4.5.3). The LE_Scan_Window parameter shall always be set to a value smaller or equal to the value set for the LE_Scan_Interval parameter.
            If they are set to the same value scanning should be run continuously.
        """
        self.scanInterval = 120; # Scan Interval = 120 x 0.625 ms = 75.0 ms
        self.scanWindow   = 120; # Scan Window   = 120 x 0.625 ms = 75.0 ms

        self.counts = 0
        self.reports = 0;
        self.directReports = 0;
        self.responses = 0;
        self.deltas = [];

        self.reportData = [];
        self.responseData = [];

        self.firstTime = 0;
        self.lastTime = 0;
        self.pivot = 0;
        
    def __set_scan_parameters(self):

        try:
            status = le_set_scan_parameters(self.transport, self.idx, self.scanType, self.scanInterval, self.scanWindow, self.ownAddress.type, self.filterPolicy, 100);
            self.trace.trace(6, "LE Set Scan Parameters Command returns status: 0x%02X" % status);
            success = status == 0;
            eventTime, event, subEvent, eventData = get_event(self.transport, self.idx, 100);
            success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
            showEvent(event, eventData, self.trace);
        except Exception as e: 
            self.trace.trace(3, "LE Set Scan Parameters Command failed: %s" % str(e));
            success = False;

        return success;

    def __scan_enable(self, enable):
        
        try:
            status = le_set_scan_enable(self.transport, self.idx, enable, ScanFilterDuplicate.DISABLE, 200);
            self.trace.trace(6, "LE Set Scan Enable Command (%s) returns status: 0x%02X" % ("Enabling" if enable else "Disabling", status));
            success = status == 0;
            waited = 0;
            event = Events.BT_HCI_EVT_NONE;
            while (event != Events.BT_HCI_EVT_CMD_COMPLETE) and (waited <= 1000):
                if has_event(self.transport, self.idx, 100):
                    eventTime, event, subEvent, eventData = get_event(self.transport, self.idx, 100);
                    showEvent(event, eventData, self.trace);
                else:
                    waited += 100;
            success = success and (waited <= 1000);
        except Exception as e: 
            self.trace.trace(3, "LE Set Scan Enable Command (%s) failed: %s" % ("Enabling" if enable else "Disabling", str(e)));
            success = False;

        return success;

    """
        Enable scanning...
    """
    def enable(self):
        success = self.__set_scan_parameters();
        return success and self.__scan_enable(Scan.ENABLE);

    """
        Disable scanning...
    """
    def disable(self):
        flush_events(self.transport, self.idx, 100);
        return self.__scan_enable(Scan.DISABLE);

    def __quantify_deltas(self):
        pivot = self.deltas[0] if self.deltas[0] != 0 else statistics.mean(self.deltas);
        self.deltas[ : ] = [ x for x in self.deltas if x < (pivot + pivot) ];
                    
    def __monitorReports(self):
        
        prevTime = 0;
        while max(self.reports, self.directReports, self.counts) < self.expectedReports:
            if has_event(self.transport, self.idx, 100):
                eventTime, event, subEvent, eventData = get_event(self.transport, self.idx, 100);
              # showEvent(event, eventData, self.trace);
                if subEvent == MetaEvents.BT_HCI_EVT_LE_ADVERTISING_REPORT:
                    eventType = advertiseReport(eventData)[1];
                    if eventType == self.reportType:
                        self.reports += 1;
                        self.reportData = eventData[ : ];
                        if self.reports > 1:
                            self.deltas += [eventTime - prevTime];
                        else:
                            self.firstTime = eventTime;
                        prevTime = eventTime;
                elif subEvent == MetaEvents.BT_HCI_EVT_LE_DIRECT_ADV_REPORT:
                    eventType = directedAdvertiseReport(eventData)[1];
                    if eventType == self.reportType:
                        self.directReports += 1;
                        self.reportData = eventData[ : ];
                        if self.directReports > 1:
                            self.deltas += [eventTime - prevTime];
                        else:
                            self.firstTime = eventTime;
                        prevTime = eventTime;
            else:
                if self.lastTime == 0:
                    self.lastTime = prevTime;
                self.counts += 1;
        
    def __monitorResponses(self):
        
        prevTime = 0;
        while (max(self.reports, self.directReports, self.counts) < self.expectedReports) or (max(self.responses, self.counts) < self.expectedResponses):
            if has_event(self.transport, self.idx, 100):
                eventTime, event, subEvent, eventData = get_event(self.transport, self.idx, 100);
              # showEvent(event, eventData, self.trace);
                if subEvent == MetaEvents.BT_HCI_EVT_LE_ADVERTISING_REPORT:
                    eventType = advertiseReport(eventData)[1];
                    if eventType == self.reportType:
                        self.reports += 1;
                        self.reportData = eventData[ : ];
                        if self.reports > 1:
                            self.deltas += [eventTime - prevTime];
                        else:
                            self.firstTime = eventTime;
                        prevTime = eventTime;
                    elif eventType == AdvertisingReport.SCAN_RSP:
                        self.responses += 1;
                        self.responseData = eventData[ : ];
                elif subEvent == MetaEvents.BT_HCI_EVT_LE_DIRECT_ADV_REPORT:
                    eventType = directedAdvertiseReport(eventData)[1];
                    if eventType == self.reportType:
                        self.directReports += 1;
                        self.reportData = eventData[ : ];
                        if self.directReports > 1:
                            self.deltas += [eventTime - prevTime];
                        else:
                            self.firstTime = eventTime;
                        prevTime = eventTime;
            else:
                if self.lastTime == 0:
                    self.lastTime = prevTime;
                self.counts += 1;
        
    def __monitorReportTime(self):
        """
            Advertising with connectable high duty cycle directed advertising packages (ADV_DIRECT_IND, high duty cycle) is time limited.
            Advertising should stop after approx. 1280 ms. When Advertsing stops a LE Connection Complete Event with status := 0x3C is generated on the Advertiser side.
            Status 0x3C means 'directed advertising timeout'.
        """
        prevTime = 0;
        while self.lastTime == 0:
            if has_event(self.transport, self.idx, 100):
                eventTime, event, subEvent, eventData = get_event(self.transport, self.idx, 100);
                # showEvent(event, eventData, self.trace);
                if subEvent == MetaEvents.BT_HCI_EVT_LE_ADVERTISING_REPORT:
                    eventType = advertiseReport(eventData)[1];
                    if eventType == self.reportType:
                        self.reports += 1;
                        self.reportData = eventData[ : ];
                        if self.reports > 1:
                            self.deltas += [eventTime - prevTime];
                        else:
                            self.firstTime = eventTime;
                        prevTime = eventTime;
                elif subEvent == MetaEvents.BT_HCI_EVT_LE_DIRECT_ADV_REPORT:
                    eventType = directedAdvertiseReport(eventData)[1];
                    if eventType == self.reportType:
                        self.directReports += 1;
                        self.reportData = eventData[ : ];
                        if self.directReports > 1:
                            self.deltas += [eventTime - prevTime];
                        else:
                            self.firstTime = eventTime;
                        prevTime = eventTime;
            else:
                if self.lastTime == 0:
                    self.lastTime = prevTime;
        
    """
        Monitor advertising reports / responses
    """
    def monitor(self, timeBased=None):
        self.deltas = [];
        self.responses = 0;
        self.reports = 0;
        self.counts = 0;

        self.firstTime = 0;
        self.lastTime = 0;
        
        if not timeBased is None:
            self.__monitorReportTime();
        elif self.expectedResponses is None:
            self.__monitorReports();
        else:
            self.__monitorResponses();
        
        flush_events(self.transport, self.idx, 100);
    
    """
        Qualify advertising reports received; count, from address and content
    """
    def qualifyReports(self, count, address=None, data=None):
        if self.reports > 0:
            self.trace.trace(7, "Received %d %s Advertise reports." % (self.reports, self.reportType.name) );
            if (self.reports > 1):
                self.__quantify_deltas();
                self.trace.trace(7, "Mean distance between Advertise Events %d ms., std. deviation %.1f ms." % (statistics.mean(self.deltas), statistics.pstdev(self.deltas)));
            success = True
            if not address is None:
                adrType, adrAddress = advertiseReport(self.reportData)[2:4];
                reportAddress = Address( ExtendedAddressType(adrType), toNumber(adrAddress) );
                self.trace.trace(5, "Reported address %s / Expected address %s" % (str(reportAddress), str(address)));
                success = success and (reportAddress == address);
            if not data is None:
                reportData = advertiseReport(self.reportData)[4];
                success = success and (reportData == data);
        else:
            self.trace.trace(7, "Received no %s Advertise reports." % self.reportType.name);
            success = data is None;
        return success and (self.reports >= count);
    
    """
        Qualify directed advertising reports received; count, from address and content
    """
    def qualifyDirectedReports(self, count, address=None, directAddress=None):
        if self.directReports > 0:
            self.trace.trace(7, "Received %d %s directed Advertise reports." % (self.directReports, self.reportType.name) );
            if (self.directReports > 1):
                self.__quantify_deltas();
                self.trace.trace(7, "Mean distance between directed Advertise Events %d ms., std. deviation %.1f ms." % (statistics.mean(self.deltas), statistics.pstdev(self.deltas)));
            success = True
            if not address is None:
                adrType, adrAddress = directedAdvertiseReport(self.reportData)[2:4];
                reportAddress = Address( ExtendedAddressType(adrType), toNumber(adrAddress) );
                self.trace.trace(5, "Reported address %s / Expected address %s" % (str(reportAddress), str(address.address)));
                success = success and (reportAddress == address);
            if not directAddress is None:
                adrType, adrAddress = directedAdvertiseReport(self.reportData)[4:6];
                reportAddress = Address( ExtendedAddressType(adrType), toNumber(adrAddress) );
                self.trace.trace(5, "Reported direct address %s / Expected direct address %s" % (str(reportAddress), str(directAddress.address)));
                success = success and (reportAddress == directAddress);
        else:
            self.trace.trace(7, "Received no %s directed Advertise reports." % self.reportType.name);
            success = data is None;
        return success and (self.directReports >= count);

    """
        Qualify advertising responses received; count and content
    """
    def qualifyResponses(self, count, data=None):
        if self.responses > 0:
            self.trace.trace(7, "Received %d SCAN_RSP Advertise reports." % self.responses );
            responseData = advertiseReport(self.responseData)[4];
            success = True if data is None else (responseData == data);
            if not success:
                self.trace.trace(5, "Data MisMatch:");
                self.trace.trace(5, responseData);
                self.trace.trace(5, data);
        else:
            self.trace.trace(7, "Received no SCAN_RSP Advertise reports.");
            success = data is None;
        return success and (self.responses >= count);

    """
        Qualify the  distribution of advertising reports over time...
    """
    def qualifyReportTime(self, count, time):
        if self.reports > 0:
            self.trace.trace(7, "Received %d %s Advertise reports." % (self.reports, self.reportType.name) );
            if (self.reports > 1):
                self.__quantify_deltas();
                self.trace.trace(7, "Mean distance between Advertise Events %d ms., std. deviation %.1f ms." % (statistics.mean(self.deltas), statistics.pstdev(self.deltas)));
            self.trace.trace(7, "Advertising stopped after %d ms." % (self.lastTime - self.firstTime) );
            success = time > (self.lastTime - self.firstTime);
        else:
            self.trace.trace(7, "Received no %s Advertise reports." % self.reportType.name);
            success = True;
        return success and (self.reports >= count);

    def discover(self, time, flags=None):
        devices = {};
        adData = ADData();
        success = self.enable();
        if success:
            prevTime = deltaTime = 0;
            while deltaTime < time:
                if has_event(self.transport, self.idx, 100):
                    eventTime, event, subEvent, eventData = get_event(self.transport, self.idx, 100);
                    
                    if subEvent == MetaEvents.BT_HCI_EVT_LE_ADVERTISING_REPORT:
                        eventType, addressType, addressArray, data, rssi = advertiseReport(eventData)[1:];
                        address = toNumber(addressArray);
                        """
                            eventType - can be any one of the following:
                               ADV_IND         - Connectable undirected advertising event     { AdvA, AdvData }
                               ADV_DIRECT_IND  - Connectable directed advertising event       { AdvA, TargetA }
                               ADV_SCAN_IND    - Scannable undirected advertising event       { AdvA, AdvData }
                               ADV_NONCONN_IND - Non connectable undirected advertising event { AdvA, AdvData }
                               SCAN_RSP        - Scan response event                          { AdvA, ScanRspData }
                        """
                        if prevTime > 0:
                            deltaTime += eventTime - prevTime;

                        elements = adData.decode(data);

                        if address in devices:
                            if ADType.COMPLETE_LOCAL_NAME in elements:
                                devices[address]["name"] = elements[ADType.COMPLETE_LOCAL_NAME];
                            if ADType.SHORTENED_LOCAL_NAME in elements:
                                devices[address]["short"] = elements[ADType.SHORTENED_LOCAL_NAME];
                        elif flags is None:
                            devices[address] = { "type": addressType, "data": data, "rssi": rssi, "name": '', "short": '' }; 
                        else:
                            if (ADType.FLAGS in elements) and (elements[ADType.FLAGS] & flags):
                                devices[address] = { "type": addressType, "data": data, "rssi": rssi, "name": '', "short": '' }; 

                        if eventType == AdvertisingReport.SCAN_RSP:
                            self.responses += 1;
                        else:
                            self.reports += 1;

                    prevTime = eventTime;
                else:
                    deltaTime += 100;

            success = self.disable();

        return success and (len(devices) > 0), devices;
