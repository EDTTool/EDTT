# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

from components.basic_commands import le_receiver_test;
from components.basic_commands import le_transmitter_test;
from components.basic_commands import le_test_end;
import time;
from components.test_spec import TestSpec;

"""
    Run the command...
"""
def LE_Transceiver_Test(transport, trace):
    trace.trace(3, "Starting le transceiver test");

    RxCh = 0;

    try:
        le_receiver_test(transport, 0, RxCh, 100);
        le_transmitter_test(transport, 1, RxCh, 32, 0, 100);
        transport.wait(3000);
        RxCount = le_test_end(transport, 0, 100);
        TxCount = le_test_end(transport, 1, 100);
    except Exception as e:
        trace.trace(1, "LE Transceiver Test failed: %s" %str(e));
        return 1;

    print((RxCount, TxCount));

    success = True if RxCount[0] == 0 and RxCount[1] > 3200 else False;
    success = success and True if TxCount[0] == 0 and TxCount[1] > 3200 else False;
    trace.trace(3, "LE Transceiver Test " + ("PASSED" if success else "FAILED") + " with %i device(s)" %transport.n_devices);
    return 0 if success else -1;

_spec = {};
_spec["LE_Transceiver_Test"] = \
    TestSpec(name = "LE Transceiver Test",
             number_devices = 2,
             description = "Test that we can execute the LE Transceiver Test.",
             test_private = LE_Transceiver_Test);

"""
    Return the test spec which contains info about all the tests
    this test module provides
"""
def get_tests_specs():
    return _spec;

"""
    Run a test given its test_spec
"""
def run_a_test(args, transport, trace, test_spec):
    return not test_spec.test_private(transport, trace);
