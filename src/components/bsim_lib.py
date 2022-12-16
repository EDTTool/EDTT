# Copyright 2022 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

# BabbleSim library functions and constants targeting the 2G4 phy

# Note: The following is a copy of the functionality in the BSim C-libraries
# If/when adding to this library try to stay as close to the C library as possible
# to make it easier to understand both worlds
# If this file grows a lot it may be a good idea to use the existing C libraries
# with a python wrapper; For now that is overkill though

import os
import platform
import pwd
import stat

### Constants ###

## BSim base message headers ##
# The device wants to wait
PB_MSG_WAIT = 0x01
# The device is disconnecting from the phy or viceversa:
PB_MSG_DISCONNECT = 0xFFFF
# The device is disconnecting from the phy, and is requesting the phy to end the simulation ASAP
PB_MSG_TERMINATE = 0xFFFE
# The requested time tick has just finished
PB_MSG_WAIT_END = 0x81

## 2G4 Message headers from device to phy ##
# The device will transmit
P2G4_MSG_TX = 0x02
# The device wants to attempt to receive
P2G4_MSG_RX = 0x11
# Continue receiving (the device likes the address and headers of the packet)
P2G4_MSG_RXCONT = 0x12
# Stop reception (the device does not likes the address or headers of the packet) => The phy will stop this reception
P2G4_MSG_RXSTOP = 0x13
# Do an RSSI measurement
P2G4_MSG_RSSIMEAS = 0x14
# Device is successfully providing a new p2G4_abort_t
P2G4_MSG_RERESP_ABORTREEVAL = 0x15

## 2G4 Message headers from phy to device ##
# Tx completed (fully or not)
P2G4_MSG_TX_END = 0x100
# Poking the device to see if it wants to change its abort time
P2G4_MSG_ABORTREEVAL = 0x101
# Matching address found while receiving
P2G4_MSG_RX_ADDRESSFOUND = 0x102
# Rx completed (successfully or not)
P2G4_MSG_RX_END = 0x103
# RSSI measurement completed
P2G4_MSG_RSSI_END = 0x104

TIME_NEVER = 0xFFFFFFFFFFFFFFFF # UINT64_MAX

# 2G4 modulations
P2G4_MOD_BLE = 0x10 # Standard 1Mbps BLE modulation
P2G4_MOD_BLE2M = 0x20 # Standard 2Mbps BLE
P2G4_MOD_PROP2M = 0x21 # Proprietary 2Mbps
P2G4_MOD_PROP3M = 0x31 # Proprietary 3Mbps
P2G4_MOD_PROP4M = 0x41 # Proprietary 4Mbps

### Functions ###

# Create folder if it does not already exist
def create_folder(path):
    if os.access(path, os.F_OK):
        return
    os.mkdir(path, stat.S_IRWXG | stat.S_IRWXU)
    if not os.access(path, os.F_OK):
        raise Exception("Failed to create folder %s" % path)

# Create
def create_com_folder(sim_id):
    pw_name = pwd.getpwuid(os.geteuid())[0]
    com_path = "/tmp/bs_%s" % pw_name
    create_folder(com_path)

    com_path = com_path + "/%s" % sim_id
    create_folder(com_path)
    return com_path

# Get process start time from /proc - note that this only works on Linux
def get_process_start_time(pid):
    filename = "/proc/%s/stat" % pid
    with open(filename, "r") as file:
        line = file.readline()
        start_time = line.split(" ")[21] # see man 5 proc
        return int(start_time)

def lock_file_fill(lock_path, pid):
    with open(lock_path, "w") as file:
        file.write(str(pid) + "\n")
        if platform.system() == "Linux":
            starttime = get_process_start_time(pid)
            file.write(str(starttime) + "\n")

def test_and_create_lock_file(com_path, device_nbr, trace):
    lock_path = "%s/%s.d%i.lock" % (com_path, "2G4", device_nbr)
    my_pid = os.getpid()
    if not os.access(lock_path, os.F_OK):
        # The file does not exist. So unless somebody is racing us, we are safe to go
        lock_file_fill(lock_path, my_pid)
        return lock_path

    corrupt_file = False
    other_dead = False
    his_starttime = 0

    with open(lock_path, "r") as file:
        try:
            his_pid = int(file.readline())
        except:
            corrupt_file = True
        if not corrupt_file and platform.system() == "Linux":
            try:
                his_starttime = int(file.readline())
            except:
                corrupt_file = True

    if corrupt_file: # We are provably racing the other process, we stop
        raise Exception("Found previous lock owned by unknown process, we may be racing each other => aborting\n")

    try:
        os.kill(his_pid, 0)
    except:
        other_dead = True

    if other_dead == False: # a process with the pid exists
        if platform.system() == "Linux":
            # To be sure the pid was not reused, let's check that the process start time matches
            other_start_time = get_process_start_time(his_pid)
            if (his_starttime == other_start_time): # it is the same process
                raise Exception("Found a previous, still RUNNING process w pid %s with the same sim_id and device port which would interfere with this one, aborting" % his_pid)
            else:
                other_dead = True
        else:
            raise Exception("Found a previous, still RUNNING process w pid %s with the same sim_id and device port which would interfere with this one, aborting" % his_pid)

    trace.trace(3, "Found previous lock owned by DEAD process (pid was %s), will attempt to take over" % his_pid)
    lock_file_fill(lock_path, my_pid)

    return lock_path

def create_fifo_if_not_there(path):
    if os.access(path, os.F_OK):
        return
    try:
        os.mkfifo(path, stat.S_IRWXG | stat.S_IRWXU)
    except:
        pass
    if not os.access(path, os.F_OK):
        raise Exception("Failed to create fifo %s" % path)

# See BLUETOOTH CORE SPECIFICATION Version 5.3, Vol 6, Part B, section 1.4.1
chIdxToCenterFreq = [
    2404, 2406, 2408, 2410, 2412, 2414, 2416, 2418, 2420, 2422, 2424,
    2428, 2430, 2432, 2434, 2436, 2438, 2440, 2442, 2444, 2446, 2448, 2450, 2452, 2454, 2456, 2458, 2460, 2462, 2464, 2466, 2468, 2470, 2472, 2474, 2476, 2478,
    2402,
    2426,
    2480
]

# Convert from BLE channel index to the corresponding 2G4 BSim phy frequency value
def ch_idx_to_2G4_freq(ch_idx):
    freq = chIdxToCenterFreq[ch_idx]
    # 2G4 frequency is offset relative to 2400 in 16 bits with fixed point notation (8.8 bits)
    return ((freq - 2400) << 8)

