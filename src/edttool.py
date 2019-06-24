#! /usr/bin/env python2
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

import os;
import random;

def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(description="EDTT (Embedded Device Test Tool)",
                                     epilog="Note: A transport can have its own options")

    parser.add_argument("-v", "--verbose", default=2, type=int, help="Verbosity level");

    parser.add_argument("-t", "--transport", required=True,
                        help="Type of transport to connect to the devices (the "
                             "transport module must either exist as "
                             "src/components/edtt_<transport>.py, or be a path "
                             "to an importable transport module");

    parser.add_argument("-T", "--test", required=True,
                        help="Which test module to run. This can either be a module in "
                        " src/tests, or a file path (relative or absolute)");

    parser.add_argument("-C", "--case", required=False,
                        help='Which testcase to run in that module.'
                        'Options are: A real test name, "all", "randomize",'
                        'or a file name containing a list of test names (default "all")')

    parser.add_argument("--seed", required=False, default=0x1234, help='Random generator seed (0x1234 by default)')

    return parser.parse_known_args()

def try_to_import(module_path, type, def_path):
    try:
        if (("." not in module_path) and ("/" not in module_path)):
            from importlib import import_module;
            loaded_module = import_module(def_path + module_path)
        else: #The user seems to want to load the module from a place off-tree
            #If the user forgot Let's fill in the extension
            if module_path[-3:] != ".py":
                module_path = module_path + ".py"
            import imp;
            loaded_module = imp.load_source('%s', module_path);

        return loaded_module;
    except ImportError as e:
        print("\n Could not load the %s %s . Does it exist?\n"% (type, module_path))
        raise;

# Initialize the transport and connect to devices
def init_transport(transport, xtra_args, trace):
    transport_module = try_to_import(transport, "transport", "components.edttt_");
    transport = transport_module.EDTTT(xtra_args, trace);
    transport.connect();
    return transport;

def run_one_test(args, xtra_args, transport, trace, test_mod, test_spec, nameLen):
    trace.trace(4, test_spec);
    trace.trace(4, "");
    if test_spec.number_devices > transport.n_devices:
        raise Exception("This test needs %i connected devices but you only connected to %i" %
                        (test_spec.number_devices, transport.n_devices));

    result = test_mod.run_a_test(args, transport, trace, test_spec);
    trace.trace(2, "%-*s %s %s" % (nameLen, test_spec.name, test_spec.description[1:], ("PASSED" if result == 0 else "FAILED")));

    return result;

# Attempt to load and run the tests
def run_tests(args, xtra_args, transport, trace):
    passed = 0;
    total = 0;

    test_mod = try_to_import(args.test, "test", "tests.");
    test_specs = test_mod.get_tests_specs();
    nameLen = max([ len(test_specs[key].name) for key in test_specs ]); 

    t = "all" if args.case is None else args.case

    if t.lower() == "all" or t.lower() == "randomize":
        tests_list = list(test_specs.iteritems());
        if t.lower() == "randomize":
            random.shuffle(tests_list)

        for _,test_spec in tests_list:
            result = run_one_test(args, xtra_args, transport, trace, test_mod, test_spec, nameLen);
            passed += 1 if result == 0 else 0;
            total += 1;

    elif t in test_specs:
        result = run_one_test(args, xtra_args, transport, trace, test_mod, test_specs[t], nameLen);
        passed += 1 if result == 0 else 0;
        total += 1;

    elif os.path.isfile(t):
        file = open(t, "r");
        for line in file:
            t = line.strip().upper();
            if (t[0] == "#"): #Skip commented lines
                continue
            if t in test_specs:
                result = run_one_test(args, xtra_args, transport, trace, test_mod, test_specs[t], nameLen);
                passed += 1 if result == 0 else 0;
                total += 1;
            else:
                print("unkown test " + t + ". Skipping")
        file.close();

    else:
        trace.trace(1, "Test '%s' not found!" % t);
        total += 1;

    failed = total - passed;
    if total:
        trace.trace(2, "\nSummary:\n\nStatus   Count\n%s" % ('='*14));
        if passed > 0:
            trace.trace(2, "PASS%10d" % passed);
        
        if failed > 0:
            trace.trace(2, "FAIL%10d" % failed);
        trace.trace(2, "%s\nTotal%9d" % ('='*14, total));

    return failed

class Trace():
    def __init__(self, level):
        self.level = level;

    def trace(self, level, msg):
        if ( level <= self.level ):
            print(msg);

def main():
    transport = None;
    try:
        (args, xtra_args) = parse_arguments();
        
        random.seed(args.seed);

        trace = Trace(args.verbose);

        transport = init_transport(args.transport, xtra_args, trace);

        result = run_tests(args, xtra_args, transport, trace);

        transport.close();

        from sys import exit;
        exit(result);

    except:
        if transport:
            transport.close();
        raise;

if __name__ == "__main__":
    main();
