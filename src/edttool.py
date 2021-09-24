#! /usr/bin/env python3
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

import os;
from components.btsnoop import Btsnoop, BtsnoopPriority
from numpy import random;
from components.dump import SortedDumps, Packets
from components.utils import toArray

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
                        default="all",
                        help='Which testcase to run in that module.'
                        'Options are: A real test name, "all", "randomize",'
                        'or a file name containing a list of test names (default "all")')

    parser.add_argument("--shuffle", required=False,
                        action='store_true',
                        help='Shuffle test order. '
                        'The order will be dependent on the random seed. '
                        'If <case> was set to all, this is equivalent to setting <case> to "randomize". '
                        'If <case> was a file name, this will shuffle the lines in the file. '
                        'If <case> was 1 particular testcase, this option has no effect.')

    parser.add_argument("-S","--stop_on_failure", required=False,
                        action='store_true',
                        help="Stop as soon as any test fails, instead of "
                        "continuing with the remaining tests")

    parser.add_argument("--seed", required=False, default=0x1234, help='Random generator seed (0x1234 by default)')

    parser.add_argument("--store_btsnoop", required=False, default=False, help="Store btsnoop to the file")

    parser.add_argument("--btmon_socket_path", required=False, default="/tmp/btmon-sock", help="path to the unix socket used by btmon")

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
        print(("\n Could not load the %s %s . Does it exist?\n"% (type, module_path)))
        raise;

# Initialize the transport and connect to devices
def init_transport(transport, xtra_args, trace):
    transport_module = try_to_import(transport, "transport", "components.edttt_");
    transport = transport_module.EDTTT(xtra_args, trace);
    transport.connect();
    return transport;

def run_one_test(args, xtra_args, transport, trace, test_mod, test_spec, nameLen, packets):
    trace.trace(4, test_spec);
    trace.trace(4, "");
    if test_spec.number_devices > transport.n_devices:
        raise Exception("This test needs %i connected devices but you only connected to %i" %
                        (test_spec.number_devices, transport.n_devices));

    trace.btsnoop.send_user_data(0, BtsnoopPriority.INFO, test_spec.name)
    result = test_mod.run_a_test(args, transport, trace, test_spec, packets);
    trace.trace(2, "%-*s %s %s" % (nameLen, test_spec.name, test_spec.description[1:], ("PASSED" if result == 0 else "FAILED")));
    trace.btsnoop.send_user_data(0, BtsnoopPriority.INFO, "%-*s %s %s" % (nameLen, test_spec.name, test_spec.description[1:], ("PASSED" if result == 0 else "FAILED")))

    return result;

# Attempt to load and run the tests
def run_tests(args, xtra_args, transport, trace, dumps):
    passed = 0;
    total = 0;
    unknown = 0;

    test_mod = try_to_import(args.test, "test", "tests.");
    test_specs = test_mod.get_tests_specs();
    nameLen = max([ len(test_specs[key].name) for key in test_specs ]);

    t = args.case

    if t.lower() == "all" or t.lower() == "randomize":
        tests_list = list(test_specs.items());
        if t.lower() == "randomize" or args.shuffle:
            random.shuffle(tests_list)

        for _,test_spec in tests_list:
            result = run_one_test(args, xtra_args, transport, trace, test_mod, test_spec, nameLen, Packets(dumps))
            passed += 1 if result == 0 else 0;
            total += 1;
            if result != 0 and args.stop_on_failure:
                break;

    elif t in test_specs:
        result = run_one_test(args, xtra_args, transport, trace, test_mod, test_specs[t], nameLen, Packets(dumps))
        passed += 1 if result == 0 else 0;
        total += 1;

    elif os.path.isfile(t):
        file = open(t, "r");
        lines = file.readlines();

        if args.shuffle:
            random.shuffle(lines);

        for line in lines:
            t = line.split("#",1)[0]; #remove comments
            t = t.strip().upper();
            if not t: #Skip empty lines, or those which had only comments
                continue
            if t in test_specs:
                result = run_one_test(args, xtra_args, transport, trace, test_mod, test_specs[t], nameLen, Packets(dumps))
                passed += 1 if result == 0 else 0;
                total += 1;
                if result != 0 and args.stop_on_failure:
                    break;
            else:
                unknown += 1;
                print(("unknown test " + t + ". Skipping"))
        file.close();

    else:
        trace.trace(1, "Test '%s' not found!" % t);
        total += 1;

    failed = total - passed;
    if total:
        trace.trace(2, "\nSummary:\n\nStatus   Count\n%s" % ('='*14));
        if passed > 0:
            trace.trace(2, "PASS%10d" % passed);
            trace.btsnoop.send_user_data(0, BtsnoopPriority.INFO, "PASS%10d" % passed)

        if failed > 0:
            trace.trace(2, "FAIL%10d" % failed);
            trace.btsnoop.send_user_data(0, BtsnoopPriority.INFO, "FAIL%10d" % failed)

        if unknown > 0:
            trace.trace(2, "UNKNOWN%7d" % unknown);

        trace.trace(2, "%s\nTotal%9d" % ('='*14, total));

    return failed + unknown

class Trace():
    def __init__(self, level):
        self.level = level;
        self.transport = None
        self.btsnoop = None

    def trace(self, level, msg):
        if ( level <= self.level ):
            if self.transport:
                from datetime import timedelta
                td = timedelta(microseconds=self.transport.get_last_t())
                mm, ss = divmod(td.seconds, 60)
                hh, mm = divmod(mm, 60)
                ts = "%02d:%02d:%02d.%06d" % (hh, mm, ss, td.microseconds)
            else:
                ts = '--:--:--.------'
            for line in str(msg).split('\n'):
                print('edtt: @{}  {}'.format(ts, line), flush=True);

def main():
    transport = None;
    try:
        (args, xtra_args) = parse_arguments();

        random.seed(int(args.seed));

        trace = Trace(args.verbose);

        transport = init_transport(args.transport, xtra_args, trace);
        trace.transport = transport;
        trace.btsnoop = Btsnoop(args.store_btsnoop, args.btmon_socket_path)
        address = 0x000000000000
        trace.btsnoop.send_index_added(0, toArray(address, 6), "UpperTester")
        trace.btsnoop.send_index_added(1, toArray(address, 6), "LowerTester")

        device_dumps = SortedDumps()
        device_dumps.add_rx(0, os.path.join(os.environ['BSIM_OUT_PATH'], 'results', transport.sim_id, 'd_2G4_00.Rx.csv'))
        device_dumps.add_tx(0, os.path.join(os.environ['BSIM_OUT_PATH'], 'results', transport.sim_id, 'd_2G4_00.Tx.csv'))
        device_dumps.add_rx(1, os.path.join(os.environ['BSIM_OUT_PATH'], 'results', transport.sim_id, 'd_2G4_01.Rx.csv'))
        device_dumps.add_tx(1, os.path.join(os.environ['BSIM_OUT_PATH'], 'results', transport.sim_id, 'd_2G4_01.Tx.csv'))

        trace.btsnoop.send_user_data(0, BtsnoopPriority.ALERT, "Testing session started")
        result = run_tests(args, xtra_args, transport, trace, device_dumps)
        trace.btsnoop.send_user_data(0, BtsnoopPriority.INFO, "Testing session completed ")
        trace.btsnoop.close()
        transport.close();

        from sys import exit;
        exit(result);

    except:
        if transport:
            transport.close();
        raise;

if __name__ == "__main__":
    main();
