# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

from components.basic_commands import echo;
from components.test_spec import TestSpec;

def _echo_test(transport, trace):
    trace.trace(3, "Starting echo test");

    try:
        for i in range(0,transport.n_devices):
            echo(transport, i, str.encode("A random test string"), 100);
    except Exception as e:
        trace.trace(1,"Echo test failed: %s"%str(e));
        return 1;

    trace.trace(3,"Echo test passed with %i device(s)"% transport.n_devices);
    return 0;

_spec = {};
_spec["Echo_test"] = \
    TestSpec(name = "Echo_test",
             number_devices = 1,
             description = "Test that we can echo to any connected device",
             test_private = _echo_test);

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
    return test_spec.test_private(transport, trace);
