# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

import statistics;
from enum import IntEnum;
from components.utils import *;
from components.basic_commands import *;
from components.address import *;
from components.addata import *;
from components.events import *;

class ScanningFilterPolicy(IntEnum):
    FILTER_NONE          = 0       # Accept all advertising packets except directed advertising packets not addressed to this device (default).
    FILTER_ACCEPT_LIST    = 1       # Accept only advertising packets from devices where the advertiser’s address is in the Filter Accept List.
                                   # Directed advertising packets which are not addressed to this device shall be ignored.
    FILTER_ID_DIRECTED   = 2       # Accept all advertising packets except directed advertising packets where the initiator's identity address does not address this device.
                                   # Note: Directed advertising packets where the initiator's address is a resolvable private address that cannot be resolved are also accepted.
    FILTER_ID_FILTER_ACCEPT_LIST = 3       # Accept all advertising packets except:
                                   # • advertising packets where the advertiser's identity address is not in the Filter Accept List; and
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
        self.reportAddress = None;
        self.responseData = [];
        self.responseAddress = None;
        self.targetAddress = None;

        self.firstTime = 0;
        self.lastTime = 0;
        self.pivot = 0;
    
    def __verifyAndShowEvent(self, expectedEvent):
        event = get_event(self.transport, self.idx, 200);
        self.trace.trace(7, str(event));
        return event.event == expectedEvent;

    def __commandCompleteEvent(self):
        return self.__verifyAndShowEvent(Events.BT_HCI_EVT_CMD_COMPLETE);

    def __scan_parameters(self):
        status = le_set_scan_parameters(self.transport, self.idx, self.scanType, self.scanInterval, self.scanWindow, self.ownAddress.type, self.filterPolicy, 200);
        self.trace.trace(6, "LE Set Scan Parameters Command returns status: 0x%02X" % status);
        return self.__commandCompleteEvent() and (status == 0);

    def __scan_enable(self, enable):
        status = le_set_scan_enable(self.transport, self.idx, enable, ScanFilterDuplicate.DISABLE, 200);
        self.trace.trace(6, "LE Set Scan Enable Command (%s) returns status: 0x%02X" % ("Enabling" if enable else "Disabling", status));
        while not self.__commandCompleteEvent():
            pass;
        return status == 0;

    def clear(self):
        flush_events(self.transport, self.idx, 200);

    """
        Enable scanning...
    """
    def enable(self):
        success = self.__scan_parameters();
        return success and self.__scan_enable(Scan.ENABLE);

    """
        Disable scanning...
    """
    def disable(self):
        self.clear();
        return self.__scan_enable(Scan.DISABLE);

    def __updateDeltas(self, count, thisTime, prevTime):
        if count > 1:
            self.deltas += [thisTime - prevTime];
        else:
            self.firstTime = thisTime;

    def __handleReport(self, prevTime):

        for event in get_event(self.transport, self.idx, 200, True):

            if event.subEvent == MetaEvents.BT_HCI_EVT_LE_ADVERTISING_REPORT:

                eventType, address, data = event.decode()[0:3];
                if   eventType == self.reportType:
                    self.reports += 1;
                    self.reportData = data[:];
                    self.reportAddress = address;
                    self.__updateDeltas(self.reports, event.time, prevTime);
                    prevTime = event.time;
                elif eventType == AdvertisingReport.SCAN_RSP:
                    self.responses += 1;
                    self.responseData = data[:];
                    self.responseAddress = address;

            elif event.subEvent == MetaEvents.BT_HCI_EVT_LE_DIRECT_ADV_REPORT:

                eventType, address, targetAddress = event.decode()[0:3];
                if eventType == self.reportType:
                    self.directReports += 1;
                    self.reportData = [];
                    self.reportAddress = address;
                    self.targetAddress = targetAddress;
                    self.__updateDeltas(self.directReports, event.time, prevTime);
                    prevTime = event.time;

        return prevTime;

    def __monitorReports(self):
    
        prevTime = 0;
        while max(self.reports, self.directReports, self.counts/2) < self.expectedReports:

            if has_event(self.transport, self.idx, 200)[0]:
                prevTime = self.__handleReport(prevTime);
            else:
                if self.lastTime == 0:
                    self.lastTime = prevTime;
                self.counts += 1;
    
    def __monitorResponses(self):
    
        prevTime = 0;
        while (max(self.reports, self.directReports, self.counts/2) < self.expectedReports) or \
              (max(self.responses, self.reports/5, self.counts) < self.expectedResponses):

            if has_event(self.transport, self.idx, 200)[0]:
                prevTime = self.__handleReport(prevTime);
            else:
                if self.lastTime == 0:
                    self.lastTime = prevTime;
                self.counts += 1;
    
    def __monitorReportTime(self):
        """
            Advertising with connectable high duty cycle directed advertising packages (ADV_DIRECT_IND, high duty cycle) is time limited.
            Advertising should stop after approx. 1280 ms.
            When Advertsing stops a LE Connection Complete Event with status := 0x3C is generated on the Advertiser side.
            Status 0x3C means 'directed advertising timeout'.
        """
        prevTime = 0;
        while self.lastTime == 0:

            if has_event(self.transport, self.idx, 200)[0]:
                prevTime = self.__handleReport(prevTime);
            else:
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
    
        self.clear();

    """
        Qualify advertising reports received; count, from address and content
    """
    def qualifyReports(self, count, address=None, data=None):
        if self.reports > 0:
            self.trace.trace(7, "Received %d %s Advertise reports." % (self.reports, self.reportType.name) );
            if (self.reports > 1):
                self.trace.trace(7, "Advertise Events spacing in range [%d, %d] ms. with mean value %d ms. and std. deviation %.1f ms." % \
                                    (min(self.deltas), max(self.deltas), statistics.mean(self.deltas), statistics.pstdev(self.deltas)));
            success = True;
            if not address is None:
                self.trace.trace(5, "Reported address %s / Expected address %s" % (str(self.reportAddress), str(address)));
                success = success and (self.reportAddress == address);
            if not data is None:
                success = success and (self.reportData == data);
                if not self.reportData == data:
                    self.trace.trace(5, "Reported data: %s / Expected data: %s" % (self.reportData, data));
            self.clear();
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
                self.trace.trace(7, "Mean distance between directed Advertise Events %d ms., std. deviation %.1f ms." % \
                                    (statistics.mean(self.deltas), statistics.pstdev(self.deltas)));
            success = True
            if not address is None:
                self.trace.trace(5, "Reported address %s / Expected address %s" % (str(self.reportAddress), str(address)));
                success = success and (self.reportAddress == address);
            if not directAddress is None:
                self.trace.trace(5, "Reported direct address %s / Expected direct address %s" % (str(self.reportAddress), str(directAddress)));
                success = success and (self.targetAddress == directAddress);
            self.clear();
        else:
            self.trace.trace(7, "Received no %s directed Advertise reports." % self.reportType.name);
            success = address is None and directAddress is None;
        return success and (self.directReports >= count);

    """
        Qualify advertising responses received; count and content
    """
    def qualifyResponses(self, count, data=None):
        if self.responses > 0:
            self.trace.trace(7, "Received %d SCAN_RSP Advertise reports." % self.responses );
            success = True if data is None else (self.responseData == data);
            if not success:
                self.trace.trace(5, "Data MisMatch:");
                self.trace.trace(5, self.responseData);
                self.trace.trace(5, data);
            self.clear();
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
                self.trace.trace(7, "Mean distance between Advertise Events %d ms., std. deviation %.1f ms." % \
                                    (statistics.mean(self.deltas), statistics.pstdev(self.deltas)));
            self.trace.trace(7, "Advertising stopped after %d ms." % (self.lastTime - self.firstTime) );
            success = time >= (self.lastTime - self.firstTime);
            self.clear();
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
                if has_event(self.transport, self.idx, 200)[0]:
                    event = get_event(self.transport, self.idx, 200);

                    if event.subEvent == MetaEvents.BT_HCI_EVT_LE_ADVERTISING_REPORT:
                        eventType, address, data, rssi = event.decode();
                        addressNo = toNumber(address.address);
                        """
                            eventType - can be any one of the following:
                               ADV_IND         - Connectable undirected advertising event     { AdvA, AdvData }
                               ADV_DIRECT_IND  - Connectable directed advertising event       { AdvA, TargetA }
                               ADV_SCAN_IND    - Scannable undirected advertising event       { AdvA, AdvData }
                               ADV_NONCONN_IND - Non connectable undirected advertising event { AdvA, AdvData }
                               SCAN_RSP        - Scan response event                          { AdvA, ScanRspData }
                        """
                        if prevTime > 0:
                            deltaTime += event.time - prevTime;

                        if not (eventType == AdvertisingReport.ADV_DIRECT_IND):
                            elements = adData.decode(data);

                            if not (addressNo in devices):
                                # if (eventType == AdvertisingReport.SCAN_RSP) or \
                                if (flags is None) or ((ADType.FLAGS in elements) and (elements[ADType.FLAGS] & flags)):
                                    devices[addressNo] = { "type": address.type, "rssi": rssi, "name": '?' };

                            if addressNo in devices:
                                if (eventType == AdvertisingReport.SCAN_RSP):
                                    devices[addressNo]["resp"] = data;
                                else:
                                    devices[addressNo]["data"] = data;
                                if ADType.COMPLETE_LOCAL_NAME in elements:
                                    devices[addressNo]["name"] = elements[ADType.COMPLETE_LOCAL_NAME];
                                elif ADType.SHORTENED_LOCAL_NAME in elements:
                                    devices[addressNo]["name"] = elements[ADType.SHORTENED_LOCAL_NAME];
                        else:
                            if not (addressNo in devices):
                                if flags is None:
                                    devices[addressNo] = { "type": address.type, "rssi": rssi, "name": '?' };

                        if eventType == AdvertisingReport.SCAN_RSP:
                            self.responses += 1;
                        else:
                            self.reports += 1;

                    prevTime = event.time;
                else:
                    deltaTime += 100;

            success = self.disable();

        return success and (len(devices) > 0), devices;
