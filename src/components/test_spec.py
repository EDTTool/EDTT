# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

class TestSpec():
    
    def __init__(self, name = "", number_devices = 2, description = "", test_private =""):
        self.name = name;
        self.number_devices = number_devices;
        self.description = description;
        self.test_private = test_private;

    def __repr__(self):
        return "Test '%s'\n"%self.name + \
               " Requires %i device(s)\n"%self.number_devices + \
               " Description: %s"%self.description;