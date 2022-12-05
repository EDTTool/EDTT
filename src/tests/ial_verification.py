# -*- coding: utf-8 -*-
# Copyright 2021 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

import numpy
import random
import math
from components.addata import *
from components.address import *
from components.advertiser import *
from components.basic_commands import *
from components.initiator import *
from components.pairing import *
from components.preambles import *
from components.resolvable import *
from components.scanner import *
from components.test_spec import TestSpec
from components.utils import *
from collections import namedtuple

from tests.test_utils import *

global lowerIRK, upperIRK, lowerRandomAddress, upperRandomAddress


def peripheral_send_single_sdu_cis(transport, peripheral, central, trace, params):
    success, initiator, (cis_conn_handle,), _ = \
        state_connected_isochronous_stream(transport, peripheral, central, trace, params)
    if not initiator:
        return success

    # Test procedure
    # 1.The Upper Tester sends an HCI ISO Data Packet to the IUT with data length less than or equal to
    #   the Max Data Length
    # 2.The IUT sends a single ISO Data PDU to the Lower Tester with the specified LLID
    #   and Payload Data identical to the data in step 1. Framing shall be 0 if LLID is 0b00
    #   and shall be 1 if LLID is 0b10

    # Maximum data size to fit into a single PDU/SDU
    if params.Framing == 1:
        max_data_size = params.Max_SDU_P_To_C[0] - 5
    else:
        max_data_size = params.Max_SDU_P_To_C[0]

    success = iso_send_payload_pdu(transport, peripheral, central, trace, cis_conn_handle,
                                   max_data_size, params.SDU_Interval_P_To_C, 1) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def central_receive_single_sdu_cis(transport, central, peripheral, trace, params):
    return peripheral_send_single_sdu_cis(transport, peripheral, central, trace, params)


def peripheral_receive_single_sdu_cis(transport, peripheral, central, trace, params):
    success, initiator, _, (cis_conn_handle,) = \
        state_connected_isochronous_stream(transport, peripheral, central, trace, params)
    if not initiator:
        return success

    # Maximum data size to fit into a single PDU/SDU
    if params.Framing == 1:
        max_data_size = params.Max_SDU_C_To_P[0] - 5
    else:
        max_data_size = params.Max_SDU_C_To_P[0]

    success = iso_send_payload_pdu(transport, central, peripheral, trace, cis_conn_handle,
                                   max_data_size, params.SDU_Interval_C_To_P, 1) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def central_send_single_sdu_cis(transport, central, peripheral, trace, params):
    return peripheral_receive_single_sdu_cis(transport, peripheral, central, trace, params)


def peripheral_simultanous_sending_and_receiving_sdus(transport, peripheral, central, trace, params):
    success, initiator, (peripheral_cis_handle,), (central_cis_handle,) = \
        state_connected_isochronous_stream(transport, peripheral, central, trace, params)
    if not initiator:
        return success

    # Test procedure
    # 1. The Upper Tester sends HCI ISO Data Packets to the IUT.
    # 2. The IUT sends ISO Data PDUs to the Lower Tester.
    # 3. At the same time, the Lower Tester sends ISO Data PDUs to the IUT.
    # 4. The IUT sends Isochronous Data SDUs to the Upper Tester.

    # Maximum data size to fit into a single PDU/SDU
    if params.Framing == 1:
        max_data_size = params.Max_SDU_C_To_P[0] - 5
    else:
        max_data_size = params.Max_SDU_C_To_P[0]

    success = iso_send_payload_pdu_parallel(transport, central, peripheral, trace, central_cis_handle,
                                            peripheral_cis_handle, max_data_size,
                                            params.SDU_Interval_C_To_P, 1) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def central_simultanous_sending_and_receiving_sdus(transport, central, peripheral, trace, params):
    return peripheral_simultanous_sending_and_receiving_sdus(transport, peripheral, central, trace, params)


def send_multiple_small_sdu_cis(transport, transmitter, receiver, trace, cis_handle, iso_interval, sdu_interval):
    # Create a ISO_SDUs of TS defined size
    tx_sdu_1 = tuple([0] * 20)
    tx_sdu_2 = tuple([1] * 25)

    # Pack the ISO_Data_Load (no Time_Stamp) of an HCI ISO Data packet
    # <Packet_Sequence_Number, ISO_SDU_Length, ISO_SDU>
    iso_data_pkt_1 = struct.pack(f'<HH{len(tx_sdu_1)}B', 1, len(tx_sdu_1), *tx_sdu_1)
    iso_data_pkt_2 = struct.pack(f'<HH{len(tx_sdu_2)}B', 2, len(tx_sdu_2), *tx_sdu_2)

    # Test procedure
    # 1. The Upper Tester sends to the IUT a small SDU1 with data length of 20 bytes.
    # 2. The Upper Tester sends to the IUT a small SDU2 with data length of 25 bytes.
    # 3. The IUT sends a single PDU with SDU1 followed by SDU2 to the Lower Tester. Each SDU
    #       header has SC = 0 and CMPT = 1.
    success, _, _, iso_buffer_len, _ = readBufferSizeV2(transport, transmitter, trace)
    s, fragments_1 = le_iso_data_write_fragments(transport, transmitter, trace, cis_handle, iso_data_pkt_1, iso_buffer_len)
    success = s and success
    s, fragments_2 = le_iso_data_write_fragments(transport, transmitter, trace, cis_handle, iso_data_pkt_2, iso_buffer_len)
    success = s and success

    # Wait for data to be sent; fetch EDTT command response and Number of Completed packets event
    success = le_iso_data_write_complete(transport, transmitter, trace, fragments_1 + fragments_2, 100) and success

    # The ISO interval is significant in those test cases (few seconds) thus we wait here long enough to be sure the
    # packet has been sent. The timeout equal to four ISO Intervals is determined experimentally.
    transport.wait(int(4 * iso_interval * 1.25))

    success = verifyAndShowEvent(transport, transmitter, Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS, trace) and success

    # Shall receive only one Number of Completed Packets event
    success = not has_event(transport, transmitter, 100)[0] and success

    # Check the data received
    s, _, rx_sdu = iso_receive_sdu(transport, receiver, trace, sdu_interval)
    success = s and tx_sdu_1 == rx_sdu and success

    s, _, rx_sdu = iso_receive_sdu(transport, receiver, trace, sdu_interval)
    success = s and tx_sdu_2 == rx_sdu and success

    return success


def peripheral_send_multiple_small_sdu_cis(transport, peripheral, central, trace, params):
    success, initiator, (cis_handle,), _ = \
        state_connected_isochronous_stream(transport, peripheral, central, trace, params)
    if not initiator:
        return success

    success = send_multiple_small_sdu_cis(transport, peripheral, central, trace, cis_handle, params.ISO_Interval,
                                          params.SDU_Interval_P_To_C) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def central_receive_multiple_small_sdu_cis(transport, central, peripheral, trace, params):
    return peripheral_send_multiple_small_sdu_cis(transport, peripheral, central, trace, params)


def peripheral_receive_multiple_small_sdu_cis(transport, peripheral, central, trace, params):
    success, initiator, _, (cis_handle,) = \
        state_connected_isochronous_stream(transport, peripheral, central, trace, params)
    if not initiator:
        return success

    success = send_multiple_small_sdu_cis(transport, central, peripheral, trace, cis_handle, params.ISO_Interval,
                                          params.SDU_Interval_C_To_P) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def central_send_multiple_small_sdu_cis(transport, central, peripheral, trace, params):
    return peripheral_receive_multiple_small_sdu_cis(transport, peripheral, central, trace, params)


def central_send_large_sdu_cis(transport, central, peripheral, trace, params):
    # As per TS:
    # "Max_SDU is set to 503 when the corresponding BN is not 0. Max_SDU is set to 0 when the corresponding BN is 0."
    # "Max_PDU is set to 251 when the corresponding BN is not 0. Max_PDU is set to 0 when the corresponding BN is 0."
    for i in range(params.CIS_Count):
        if params.BN_C_To_P[i] == 0:
            params.Max_SDU_C_To_P[i] = 0
            params.Max_PDU_C_To_P[i] = 0
        else:
            params.Max_SDU_C_To_P[i] = 503
            params.Max_PDU_C_To_P[i] = 251

        if params.BN_P_To_C[i] == 0:
            params.Max_SDU_P_To_C[i] = 0
            params.Max_PDU_P_To_C[i] = 0
        else:
            params.Max_SDU_P_To_C[i] = 503
            params.Max_PDU_P_To_C[i] = 251

    success, initiator, _, (cis_handle,) = \
        state_connected_isochronous_stream(transport, peripheral, central, trace, params)
    if not initiator:
        return success

    # Test procedure
    # 1.The Upper Tester sends an HCI ISO Data Packet to the IUT with specified data length
    # 2.The IUT sends the specified number of Start/Continuation packets
    #   of ISO Data PDUs to the Lower Tester with the LLID=0b01 for unframed data and LLID=0b10 for
    #   framed data. Payload Data every 251 bytes offset in step 1. If the BN value is not 0 in the
    #   direction from the Lower Tester to the IUT, then the Lower Tester sends payloads as configured
    # 3. The IUT sends the last ISO Data PDU to the Lower Tester with the LLID=0b00 for unframed data
    #   and LLID=0b10 for framed data with the remaining Payload Data.
    testData = namedtuple('testData', 'SDU_Data_Length, Start_Continuation_Packets')
    rounds = {
        '1': testData(495, 1),
        '2': testData(503, 2),
    }

    for _, (sdu_data_len, start_cont_pkts) in rounds.items():
        success = iso_send_payload_pdu(transport, central, peripheral, trace, cis_handle, sdu_data_len,
                                       params.SDU_Interval_C_To_P, 1) and success
        # TODO: Verify Start/Continuation Packets

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def peripheral_send_large_sdu_cis(transport, peripheral, central, trace, params):
    # As per TS:
    # "Max_SDU is set to 503 when the corresponding BN is not 0. Max_SDU is set to 0 when the corresponding BN is 0."
    # "Max_PDU is set to 251 when the corresponding BN is not 0. Max_PDU is set to 0 when the corresponding BN is 0."
    for i in range(params.CIS_Count):
        if params.BN_C_To_P[i] == 0:
            params.Max_SDU_C_To_P[i] = 0
            params.Max_PDU_C_To_P[i] = 0
        else:
            params.Max_SDU_C_To_P[i] = 503
            params.Max_PDU_C_To_P[i] = 251

        if params.BN_P_To_C[i] == 0:
            params.Max_SDU_P_To_C[i] = 0
            params.Max_PDU_P_To_C[i] = 0
        else:
            params.Max_SDU_P_To_C[i] = 503
            params.Max_PDU_P_To_C[i] = 251

    success, initiator, (cis_conn_handle,), _ = \
        state_connected_isochronous_stream(transport, peripheral, central, trace, params)
    if not initiator:
        return success

    # Test procedure
    # 1.The Upper Tester sends an HCI ISO Data Packet to the IUT with specified data length
    # 2.The IUT sends the specified number of Start/Continuation packets
    #   of ISO Data PDUs to the Lower Tester with the LLID=0b01 for unframed data and LLID=0b10 for
    #   framed data. Payload Data every 251 bytes offset in step 1. If the BN value is not 0 in the
    #   direction from the Lower Tester to the IUT, then the Lower Tester sends payloads as configured
    # 3. The IUT sends the last ISO Data PDU to the Lower Tester with the LLID=0b00 for unframed data
    #   and LLID=0b10 for framed data with the remaining Payload Data.
    testData = namedtuple('testData', 'SDU_Data_Length, Start_Continuation_Packets')
    rounds = {
        '1': testData(495, 1),
        '2': testData(503, 2),
    }

    for _, (sdu_data_len, start_cont_pkts) in rounds.items():
        success = iso_send_payload_pdu(transport, peripheral, central, trace, cis_conn_handle, sdu_data_len,
                                       params.SDU_Interval_P_To_C, 1) and success
        # TODO: Verify Start/Continuation Packets

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def central_receive_large_sdu_cis_framed(transport, central, peripheral, trace, params, adjust_conn_interval=False):
    # As per TS:
    # "If the corresponding BN is not 0, then Max_SDU is set to 251 and Max_PDU is set to 251."
    # "If the corresponding BN is 0, then Max_SDU is set to 0 and Max_PDU is set to 0."
    for i in range(params.CIS_Count):
        if params.BN_C_To_P[i] == 0:
            params.Max_SDU_C_To_P[i] = 0
            params.Max_PDU_C_To_P[i] = 0
        else:
            params.Max_SDU_C_To_P[i] = 251
            params.Max_PDU_C_To_P[i] = 251

        if params.BN_P_To_C[i] == 0:
            params.Max_SDU_P_To_C[i] = 0
            params.Max_PDU_P_To_C[i] = 0
        else:
            params.Max_SDU_P_To_C[i] = 251
            params.Max_PDU_P_To_C[i] = 251

    success, initiator, (cis_handle,), _ = \
        state_connected_isochronous_stream(transport, peripheral, central, trace, params,
                                           adjust_conn_interval=adjust_conn_interval)
    if not initiator:
        return success

    # Test procedure
    # 1.The Upper Tester sends an HCI ISO Data Packet to the IUT with specified data length
    # 2.The IUT sends the specified number of Start/Continuation packets
    #   of ISO Data PDUs to the Lower Tester with the LLID=0b01 for unframed data and LLID=0b10 for
    #   framed data. Payload Data every 251 bytes offset in step 1. If the BN value is not 0 in the
    #   direction from the Lower Tester to the IUT, then the Lower Tester sends payloads as configured
    # 3. The IUT sends the last ISO Data PDU to the Lower Tester with the LLID=0b00 for unframed data
    #   and LLID=0b10 for framed data with the remaining Payload Data.
    testData = namedtuple('testData', 'SDU_Data_Length, Number_of_Fragments')
    rounds = {
        '1': testData(744, 3),
        '2': testData(745, 4),
    }

    for _, (sdu_data_len, num_of_fragments) in rounds.items():
        success = iso_send_payload_pdu(transport, peripheral, central, trace, cis_handle, sdu_data_len,
                                       params.SDU_Interval_C_To_P, 1) and success
        # TODO: Verify Number of Fragments

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def peripheral_receive_large_sdu_cis_framed(transport, peripheral, central, trace, params):
    # As per TS:
    # "If the corresponding BN is not 0, then Max_SDU is set to 251 and Max_PDU is set to 251."
    # "If the corresponding BN is 0, then Max_SDU is set to 0 and Max_PDU is set to 0."
    for i in range(params.CIS_Count):
        if params.BN_C_To_P[i] == 0:
            params.Max_SDU_C_To_P[i] = 0
            params.Max_PDU_C_To_P[i] = 0
        else:
            params.Max_SDU_C_To_P[i] = 251
            params.Max_PDU_C_To_P[i] = 251

        if params.BN_P_To_C[i] == 0:
            params.Max_SDU_P_To_C[i] = 0
            params.Max_PDU_P_To_C[i] = 0
        else:
            params.Max_SDU_P_To_C[i] = 251
            params.Max_PDU_P_To_C[i] = 251

    success, initiator, _, (cis_conn_handle,) = \
        state_connected_isochronous_stream(transport, peripheral, central, trace, params)
    if not initiator:
        return success

    # Test procedure
    # 1.The Upper Tester sends an HCI ISO Data Packet to the IUT with specified data length
    # 2.The IUT sends the specified number of Start/Continuation packets
    #   of ISO Data PDUs to the Lower Tester with the LLID=0b01 for unframed data and LLID=0b10 for
    #   framed data. Payload Data every 251 bytes offset in step 1. If the BN value is not 0 in the
    #   direction from the Lower Tester to the IUT, then the Lower Tester sends payloads as configured
    # 3. The IUT sends the last ISO Data PDU to the Lower Tester with the LLID=0b00 for unframed data
    #   and LLID=0b10 for framed data with the remaining Payload Data.
    testData = namedtuple('testData', 'SDU_Data_Length, Number_of_Fragments')
    rounds = {
        '1': testData(744, 3),
        '2': testData(745, 4),
    }

    for _, (sdu_data_len, num_of_fragments) in rounds.items():
        success = iso_send_payload_pdu(transport, central, peripheral, trace, cis_conn_handle, sdu_data_len,
                                       params.SDU_Interval_C_To_P, 1) and success
        # TODO: Verify Number of Fragments

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def central_receive_large_sdu_cis_unframed(transport, central, peripheral, trace, params):
    # As per TS:
    # "If the corresponding BN is not 0, then Max_SDU is set to 251 and Max_PDU is set to 251."
    # "If the corresponding BN is 0, then Max_SDU is set to 0 and Max_PDU is set to 0."
    for i in range(params.CIS_Count):
        if params.BN_C_To_P[i] == 0:
            params.Max_SDU_C_To_P[i] = 0
            params.Max_PDU_C_To_P[i] = 0
        else:
            params.Max_SDU_C_To_P[i] = 754
            params.Max_PDU_C_To_P[i] = 251

        if params.BN_P_To_C[i] == 0:
            params.Max_SDU_P_To_C[i] = 0
            params.Max_PDU_P_To_C[i] = 0
        else:
            params.Max_SDU_P_To_C[i] = 754
            params.Max_PDU_P_To_C[i] = 251

    success, initiator, (cis_handle,), _, = \
        state_connected_isochronous_stream(transport, peripheral, central, trace, params)
    if not initiator:
        return success

    testData = namedtuple('testData', 'SDU_Data_Length, Start_Continutation_Packets')
    rounds = {
        '1': testData(753, 2),
        '2': testData(754, 3),
    }

    for _, (sdu_data_len, start_cont_pkts) in rounds.items():
        success = iso_send_payload_pdu(transport, peripheral, central, trace, cis_handle, sdu_data_len,
                                       params.SDU_Interval_P_To_C, 1) and success
        # TODO: Verify Start/Continutation Packets

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def peripheral_receive_large_sdu_cis_unframed(transport, peripheral, central, trace, params):
    # As per TS:
    # "If the corresponding BN is not 0, then Max_SDU is set to 251 and Max_PDU is set to 251."
    # "If the corresponding BN is 0, then Max_SDU is set to 0 and Max_PDU is set to 0."
    for i in range(params.CIS_Count):
        if params.BN_C_To_P[i] == 0:
            params.Max_SDU_C_To_P[i] = 0
            params.Max_PDU_C_To_P[i] = 0
        else:
            params.Max_SDU_C_To_P[i] = 754
            params.Max_PDU_C_To_P[i] = 251

        if params.BN_P_To_C[i] == 0:
            params.Max_SDU_P_To_C[i] = 0
            params.Max_PDU_P_To_C[i] = 0
        else:
            params.Max_SDU_P_To_C[i] = 754
            params.Max_PDU_P_To_C[i] = 251

    success, initiator, _, (cis_conn_handle,) = \
        state_connected_isochronous_stream(transport, peripheral, central, trace, params)
    if not initiator:
        return success

    testData = namedtuple('testData', 'SDU_Data_Length, Start_Continutation_Packets')
    rounds = {
        '1': testData(753, 2),
        '2': testData(754, 3),
    }

    for _, (sdu_data_len, start_cont_pkts) in rounds.items():
        success = iso_send_payload_pdu(transport, central, peripheral, trace, cis_conn_handle, sdu_data_len,
                                       params.SDU_Interval_C_To_P, 1) and success
        # TODO: Verify Start/Continutation Packets

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def peripheral_send_zero_length_sdu_cis(transport, peripheral, central, trace, params):
    success, initiator, (cis_conn_handle,), _ = \
        state_connected_isochronous_stream(transport, peripheral, central, trace, params)
    if not initiator:
        return success

    # Test procedure
    # 1. The Upper Tester sends an HCI ISO Data Packet to the IUT with zero data length.
    # 2. The IUT sends a single ISO Data PDU to the Lower Tester with the specidied LLID, segmentation header
    #   and time offset.
    success = iso_send_payload_pdu(transport, peripheral, central, trace, cis_conn_handle, 0,
                                   params.SDU_Interval_P_To_C, 1) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def central_receive_zero_length_sdu_cis(transport, central, peripheral, trace, params):
    return peripheral_send_zero_length_sdu_cis(transport, peripheral, central, trace, params)


def peripheral_receive_zero_length_sdu_cis(transport, peripheral, central, trace, params):
    success, initiator, _, (cis_conn_handle,) = \
        state_connected_isochronous_stream(transport, peripheral, central, trace, params)
    if not initiator:
        return success

    success = iso_send_payload_pdu(transport, central, peripheral, trace, cis_conn_handle, 0,
                                   params.SDU_Interval_C_To_P, 1) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def central_send_zero_length_sdu_cis(transport, central, peripheral, trace, params):
    return peripheral_receive_zero_length_sdu_cis(transport, peripheral, central, trace, params)


def peripheral_sending_and_receiving_unframed_empty_pdu_llid_0b01_cis(transport, peripheral, central, trace, bn, nse):
    params = SetCIGParameters(
        SDU_Interval_C_To_P     = 0x186A0,  # 100 ms
        SDU_Interval_P_To_C     = 0x186A0,  # 100 ms
        FT_C_To_P               = 1,
        FT_P_To_C               = 1,
        ISO_Interval            = 0x50,  # 100 ms
        Packing                 = 0,  # Sequential
        Framing                 = 0,  # Unframed
        CIS_Count               = 1,
        NSE                     = nse,
        Max_SDU_Supported       = 128,  # Force Max SDU to be 128 bytes
        Max_PDU_C_To_P          = 128,
        Max_PDU_P_To_C          = 128,
        PHY_C_To_P              = 1,
        PHY_P_To_C              = 1,
        BN_P_To_C               = bn,
        BN_C_To_P               = bn,
    )

    success, initiator, (peripheral_cis_handle,), (central_cis_handle,) = \
        state_connected_isochronous_stream(transport, peripheral, central, trace, params, adjust_conn_interval=True)
    if not initiator:
        return success

    # Packet sequence numbers require an offset so that the first SDU doesn't get flushed.
    # The original implementation reused the SDU length ranging from 4 to 128 as the packet
    # sequence number. The same starting offset is reused below.
    start_pkt_seq_num_P_To_C = 4
    start_pkt_seq_num_C_To_P = 4

    # Although the packet sequence number is intialized to 0 it will be reset in the loop below by the outcome of max()
    pkt_seq_num_P_To_C = 0
    pkt_seq_num_C_To_P = 0

    SDU_Interval_C_To_P_ms = params.SDU_Interval_C_To_P / 1000
    SDU_Interval_P_To_C_ms = params.SDU_Interval_P_To_C / 1000

    # Log start time
    start_time = transport.get_time()

    for sdu_len in range(4, 128 + 1):
        # Update packet sequence number according to the number of SDU intervals being delayed
        now = transport.get_time()
        pkt_seq_num_P_To_C = max(pkt_seq_num_P_To_C + 1,
                                start_pkt_seq_num_P_To_C + math.ceil((now - start_time) / SDU_Interval_P_To_C_ms))

        # Test procedure
        # 1.The Upper Tester submits an SDU at its SDU interval of variable length, ranging from 4 to 128 octets.
        # 2.The Lower Tester receives PDUs from the IUT. When the required number of PDUs to transmit
        #       the SDU is less than BN PDUs, the remainder of BN PDUs are empty PDUs with LLID=0b01
        success = iso_send_payload_pdu(transport, peripheral, central, trace, peripheral_cis_handle,
                                       sdu_len, params.SDU_Interval_P_To_C, pkt_seq_num_P_To_C) and success

        # Update packet sequence number according to the number of SDU intervals being delayed
        now = transport.get_time()
        pkt_seq_num_C_To_P = max(pkt_seq_num_C_To_P + 1,
                                start_pkt_seq_num_C_To_P + math.ceil((now - start_time) / SDU_Interval_C_To_P_ms))

        # 3.The Lower Tester sends PDUs based on an SDU of variable length, ranging from 4 to 128
        #       octets. When the required number of PDUs to transmit the SDU is less than BN PDUs, the
        #       remainder of BN PDUs are empty PDUs with LLID=0b01.
        # 4. The IUT sends the variable length SDUs from the Lower Tester to the Upper Tester.
        success = iso_send_payload_pdu(transport, central, peripheral, trace, central_cis_handle,
                                       sdu_len, params.SDU_Interval_C_To_P, pkt_seq_num_C_To_P) and success

    ### TERMINATION ###
    success = initiator.disconnect(0x13) and success

    return success


def central_sending_and_receiving_unframed_empty_pdu_llid_0b01_cis(transport, central, peripheral, trace, bn, nse):
    return peripheral_sending_and_receiving_unframed_empty_pdu_llid_0b01_cis(transport, peripheral, central, trace, bn,
                                                                             nse)


def ial_cis_unf_per_bv_01_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-01-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 3,
        BN_P_To_C               = 2,
        FT_P_To_C               = 1,
        # Max_PDU_P_To_C          = default,
        BN_C_To_P               = 0,
        # FT_C_To_P               = N/A,
        # Max_PDU_C_To_P          = N/A,
        SDU_Interval_P_To_C     = 0x186A,  # 6.25 ms
        # SDU_Interval_C_To_P     = N/A,
        ISO_Interval            = 0x0A,  # 12,5 ms
        Max_SDU_Supported       = 100,  # Force Max SDU to be 100 bytes
    )

    return peripheral_send_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_per_bv_04_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-04-C"""
    params = SetCIGParameters(
        NSE                     = 4,
        Framing                 = 0,
        BN_P_To_C               = 3,
        FT_P_To_C               = 2,
        BN_C_To_P               = 0,
        SDU_Interval_P_To_C     = 0x61A8,  # 25 ms
        ISO_Interval            = 0x14,  # 25 ms
    )

    return peripheral_send_large_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_per_bv_17_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-17-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 7,
        BN_P_To_C               = 3,
        FT_P_To_C               = 4,
        BN_C_To_P               = 0,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_C_To_P          = 0,
        Max_PDU_P_To_C          = 20,
    )

    return peripheral_send_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_per_bv_21_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-21-C"""
    params = SetCIGParameters(
        NSE                 = 2,
        Framing             = 0,
        FT_P_To_C           = 1,
        BN_P_To_C           = 1,
        FT_C_To_P           = 1,
        BN_C_To_P           = 1,
    )

    return peripheral_simultanous_sending_and_receiving_sdus(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_22_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-22-C"""
    params = SetCIGParameters(
        NSE                 = 5,
        Framing             = 1,
        BN_P_To_C           = 1,
        FT_P_To_C           = 2,
        BN_C_To_P           = 3,
        FT_C_To_P           = 3,
    )

    return peripheral_simultanous_sending_and_receiving_sdus(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_per_bv_24_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-24-C"""
    params = SetCIGParameters(
        NSE                 = 3,
        Framing             = 0,
        BN_P_To_C           = 1,
        FT_P_To_C           = 2,
        BN_C_To_P           = 2,
        FT_C_To_P           = 3,
    )

    return peripheral_simultanous_sending_and_receiving_sdus(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_per_bv_25_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-25-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 5,
        BN_P_To_C               = 1,
        FT_P_To_C               = 2,
        # Max_PDU_P_To_C          = default,
        BN_C_To_P               = 3,
        FT_C_To_P               = 3,
        # Max_PDU_C_To_P          = default,
        SDU_Interval_C_To_P     = 0x7530,  # 30 ms
        SDU_Interval_P_To_C     = 0x7530,  # 30 ms
        ISO_Interval            = 0x18,  # 30 ms
        Max_SDU_Supported       = 125,  # Force Max SDU to be 125 bytes
    )

    return peripheral_send_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_per_bv_28_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-28-C"""
    params = SetCIGParameters(
        NSE                     = 5,
        Framing                 = 0,
        BN_P_To_C               = 3,
        FT_P_To_C               = 3,
        BN_C_To_P               = 0,
        SDU_Interval_P_To_C     = 0x88B8,  # 35 ms
        ISO_Interval            = 0x1C,  # 35 ms
    )

    return peripheral_send_large_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_per_bv_41_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-41-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 2,
        BN_P_To_C               = 1,
        FT_P_To_C               = 3,
        BN_C_To_P               = 1,
        FT_C_To_P               = 2,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_C_To_P          = 20,
        Max_PDU_P_To_C          = 20,
    )

    return peripheral_send_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_per_bv_45_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-45-C"""
    return peripheral_sending_and_receiving_unframed_empty_pdu_llid_0b01_cis(transport, upper_tester, lower_tester,
                                                                             trace, 0x04, 0x08)


def ial_cis_unf_per_bv_46_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-46-C"""
    return peripheral_sending_and_receiving_unframed_empty_pdu_llid_0b01_cis(transport, upper_tester, lower_tester,
                                                                             trace, 0x06, 0x0c)


def ial_cis_unf_per_bv_47_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-47-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        # Max_PDU_P_To_C          = default,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        # Max_PDU_C_To_P          = default,
        SDU_Interval_P_To_C     = 0x4E20,  # 20 ms
        SDU_Interval_C_To_P     = 0x4E20,  # 20 ms
        ISO_Interval            = 0x10,  # 20 ms
        Max_SDU_Supported       = 251,  # Force Max SDU to be 251 bytes
    )

    return peripheral_send_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_per_bv_49_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-49-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_C_To_P          = 20,
        Max_PDU_P_To_C          = 20,
    )

    return peripheral_send_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_03_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-03-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 4,
        BN_P_To_C               = 2,
        FT_P_To_C               = 2,
        # Max_PDU_P_To_C          = default,
        BN_C_To_P               = 0,
        # FT_C_To_P               = N/A,
        # Max_PDU_C_To_P          = N/A,
        SDU_Interval_P_To_C     = 0x4E20,  # 20 ms
        # SDU_Interval_C_To_P     = N/A,
        ISO_Interval            = 0x14,  # 25 ms
        Max_SDU_Supported       = 192,  # Force Max SDU to be 192 bytes
    )

    return peripheral_send_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_05_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-05-C"""
    params = SetCIGParameters (
        NSE                     = 8,
        Framing                 = 1,
        BN_P_To_C               = 5,
        FT_P_To_C               = 2,
        BN_C_To_P               = 0,
        SDU_Interval_P_To_C     = 0x61A8,  # 25 ms
        ISO_Interval            = 0x28,  # 50 ms
    )

    return peripheral_send_large_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_07_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-07-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 2,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 0,
        SDU_Interval_C_To_P     = 0x7A120,  # 500 ms
        SDU_Interval_P_To_C     = 0x7A120,  # 500 ms
        ISO_Interval            = 0x320,  # 1000 ms
        Max_PDU_C_To_P          = 0,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_PDU_P_To_C          = 63,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_SDU_Supported       = 25,  # NOTE: Max_SDU is set to 25 when the corresponding BN is not 0
    )

    return peripheral_send_multiple_small_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_18_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-18-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 2,
        BN_P_To_C               = 1,
        FT_P_To_C               = 4,
        BN_C_To_P               = 0,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_C_To_P          = 0,
        Max_PDU_P_To_C          = 20,
    )

    return peripheral_send_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_26_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-26-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 2,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        Max_PDU_P_To_C          = 208,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        Max_PDU_C_To_P          = 208,
        SDU_Interval_P_To_C     = 0x14D5,  # 5.333 ms
        SDU_Interval_C_To_P     = 0x14D5,  # 5.333 ms
        ISO_Interval            = 0x08,  # 10 ms
        Max_SDU_Supported       = 102,  # Force Max SDU to be 102 bytes
    )

    return peripheral_send_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_29_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-29-C"""
    params = SetCIGParameters(
        NSE                     = 6,
        Framing                 = 1,
        BN_P_To_C               = 4,
        FT_P_To_C               = 2,
        BN_C_To_P               = 4,
        FT_C_To_P               = 3,
        SDU_Interval_C_To_P     = 0x55F0,  # 22 ms
        SDU_Interval_P_To_C     = 0x55F0,  # 22 ms
        ISO_Interval            = 0x1C,  # 35 ms
    )

    return peripheral_send_large_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_31_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-31-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 4,
        BN_P_To_C               = 2,
        FT_P_To_C               = 1,
        BN_C_To_P               = 2,
        FT_C_To_P               = 2,
        SDU_Interval_C_To_P     = 0xF4240,  # 1000 ms
        SDU_Interval_P_To_C     = 0xF4240,  # 1000 ms
        ISO_Interval            = 0x640,  # 2000 ms
        Max_PDU_C_To_P          = 63,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_PDU_P_To_C          = 63,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_SDU_Supported       = 25,  # NOTE: Max_SDU is set to 25 when the corresponding BN is not 0
    )

    return peripheral_send_multiple_small_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_42_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-42-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 5,
        BN_P_To_C               = 1,
        FT_P_To_C               = 2,
        BN_C_To_P               = 3,
        FT_C_To_P               = 3,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_C_To_P          = 20,
        Max_PDU_P_To_C          = 20,
    )

    return peripheral_send_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_45_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-45-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        # Max_PDU_P_To_C          = default,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        # Max_PDU_C_To_P          = default,
        SDU_Interval_P_To_C     = 0x2710,  # 10 ms
        SDU_Interval_C_To_P     = 0x2710,  # 10 ms
        ISO_Interval            = 0x08,  # 10 ms
        Max_SDU_Supported       = 192,  # Force Max SDU to be 192 bytes
    )

    return peripheral_send_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_46_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-46-C"""
    params = SetCIGParameters(
        NSE                     = 1,
        Framing                 = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        SDU_Interval_C_To_P     = 0x7530,  # 30 ms
        SDU_Interval_P_To_C     = 0x7530,  # 30 ms
        ISO_Interval            = 0x08,  # 10 ms
    )

    return peripheral_send_large_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_47_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-47-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        SDU_Interval_C_To_P     = 0x7A120,  # 500 ms
        SDU_Interval_P_To_C     = 0x7A120,  # 500 ms
        ISO_Interval            = 0x320,  # 1000 ms
        Max_PDU_C_To_P          = 63,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_PDU_P_To_C          = 63,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_SDU_Supported       = 25,  # NOTE: Max_SDU is set to 25 when the corresponding BN is not 0
    )

    return peripheral_send_multiple_small_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_51_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-51-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_C_To_P          = 20,
        Max_PDU_P_To_C          = 20,
    )

    return peripheral_send_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_10_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-10-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 7,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        BN_C_To_P               = 3,
        FT_C_To_P               = 4,
        SDU_Interval_P_To_C     = 0x9C40,  # 40 ms
        SDU_Interval_C_To_P     = 0x9C40,  # 40 ms
        ISO_Interval            = 0x20,  # 40 ms
        Max_PDU_P_To_C          = 0,
        Max_PDU_C_To_P          = 251,
        Max_SDU_Supported       = 251,  # Force Max SDU to be 251 bytes
    )

    return peripheral_receive_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_35_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-35-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 4,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        BN_C_To_P               = 3,
        FT_C_To_P               = 3,
        SDU_Interval_P_To_C     = 0x2710,  # 10 ms
        SDU_Interval_C_To_P     = 0x2710,  # 10 ms
        ISO_Interval            = 0x10,  # 20 ms
        Max_PDU_P_To_C          = 0,
        Max_PDU_C_To_P          = 251,
        Max_SDU_Supported       = 251,  # Force Max SDU to be 251 bytes
    )

    return peripheral_receive_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_48_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-48-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        SDU_Interval_P_To_C     = 0x7530,  # 30 ms
        SDU_Interval_C_To_P     = 0x7530,  # 30 ms
        ISO_Interval            = 0x18,  # 30 ms
        Max_PDU_P_To_C          = 251,
        Max_PDU_C_To_P          = 251,
        Max_SDU_Supported       = 251,  # Force Max SDU to be 251 bytes
    )

    return peripheral_receive_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_13_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-13-C"""
    params = SetCIGParameters (
        NSE                     = 6,
        Framing                 = 1,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        BN_C_To_P               = 4,
        FT_C_To_P               = 1,
        # SDU_Interval_P_To_C     = N/A,
        SDU_Interval_C_To_P     = 0x4E20,  # 20 ms
        ISO_Interval            = 0x14,  # 25 ms
    )

    return peripheral_receive_large_sdu_cis_framed(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_38_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-38-C"""
    params = SetCIGParameters (
        NSE                     = 7,
        Framing                 = 1,
        BN_P_To_C               = 4,
        FT_P_To_C               = 1,
        BN_C_To_P               = 4,
        FT_C_To_P               = 2,
        SDU_Interval_P_To_C     = 0x9C40,  # 40 ms
        SDU_Interval_C_To_P     = 0x9C40,  # 40 ms
        ISO_Interval            = 0x20,  # 40 ms
    )

    return peripheral_receive_large_sdu_cis_framed(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_49_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-49-C"""
    params = SetCIGParameters (
        NSE                     = 1,
        Framing                 = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        SDU_Interval_P_To_C     = 0x30D40,  # 200 ms
        SDU_Interval_C_To_P     = 0x30D40,  # 200 ms
        ISO_Interval            = 0x28,  # 50 ms
    )

    return peripheral_receive_large_sdu_cis_framed(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_15_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-15-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 2,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        BN_C_To_P               = 1,
        FT_C_To_P               = 4,
        SDU_Interval_C_To_P     = 0x2710,  # 10 ms
        SDU_Interval_P_To_C     = 0x2710,  # 10 ms
        ISO_Interval            = 0x04,  # 5 ms
        Max_PDU_C_To_P          = 63,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_PDU_P_To_C          = 0,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_SDU_Supported       = 25,  # NOTE: Max_SDU is set to 25 when the corresponding BN is not 0
    )

    return peripheral_receive_multiple_small_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_39_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-39-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 7,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        BN_C_To_P               = 3,
        FT_C_To_P               = 4,
        SDU_Interval_C_To_P     = 0x2710,  # 10 ms
        SDU_Interval_P_To_C     = 0x2710,  # 10 ms
        ISO_Interval            = 0x08,  # 10 ms
        Max_PDU_C_To_P          = 63,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_PDU_P_To_C          = 0,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_SDU_Supported       = 25,  # NOTE: Max_SDU is set to 25 when the corresponding BN is not 0
    )

    return peripheral_receive_multiple_small_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_50_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-50-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        SDU_Interval_C_To_P     = 0x2710,  # 10 ms
        SDU_Interval_P_To_C     = 0x2710,  # 10 ms
        ISO_Interval            = 0x10,  # 20 ms
        Max_PDU_C_To_P          = 63,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_PDU_P_To_C          = 63,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_SDU_Supported       = 25,  # NOTE: Max_SDU is set to 25 when the corresponding BN is not 0
    )

    return peripheral_receive_multiple_small_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_20_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-20-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 5,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        BN_C_To_P               = 2,
        FT_C_To_P               = 2,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_C_To_P          = 20,
        Max_PDU_P_To_C          = 0,
    )

    return peripheral_receive_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_44_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-44-C"""
    params = SetCIGParameters(
        Framing                 = 0x01,
        NSE                     = 2,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_C_To_P          = 20,
        Max_PDU_P_To_C          = 20,
    )

    return peripheral_receive_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_per_bv_52_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/PER/BV-52-C"""
    params = SetCIGParameters(
        Framing                 = 0x01,
        NSE                     = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_C_To_P          = 20,
        Max_PDU_P_To_C          = 20,
    )

    return peripheral_receive_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_per_bv_09_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-09-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 2,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        SDU_Interval_P_To_C     = 0x3A98,  # 15 ms
        SDU_Interval_C_To_P     = 0x3A98,  # 15 ms
        ISO_Interval            = 0x0C,  # 15 ms
        Max_PDU_P_To_C          = 0,
        Max_PDU_C_To_P          = 251,
        Max_SDU_Supported       = 251,  # Force Max SDU to be 251 bytes
    )

    return peripheral_receive_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_per_bv_33_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-33-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 4,
        BN_P_To_C               = 3,
        FT_P_To_C               = 1,
        BN_C_To_P               = 3,
        FT_C_To_P               = 1,
        SDU_Interval_P_To_C     = 0x2710,  # 10 ms
        SDU_Interval_C_To_P     = 0x2710,  # 10 ms
        ISO_Interval            = 0x18,  # 30 ms
        Max_PDU_P_To_C          = 251,
        Max_PDU_C_To_P          = 251,
        Max_SDU_Supported       = 251,  # Force Max SDU to be 251 bytes
    )

    return peripheral_receive_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_per_bv_48_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-48-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        SDU_Interval_P_To_C     = 0x2710,  # 10 ms
        SDU_Interval_C_To_P     = 0x2710,  # 10 ms
        ISO_Interval            = 0x08,  # 10 ms
        Max_PDU_P_To_C          = 251,
        Max_PDU_C_To_P          = 251,
        Max_SDU_Supported       = 251,  # Force Max SDU to be 251 bytes
    )

    return peripheral_receive_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_per_bv_12_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-12-C"""
    params = SetCIGParameters (
        NSE                     = 10,
        Framing                 = 0,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        BN_C_To_P               = 8,
        FT_C_To_P               = 2,
        # SDU_Interval_P_To_C     = N/A,
        SDU_Interval_C_To_P     = 0x4E20,  # 20 ms
        ISO_Interval            = 0x20,  # 40 ms
    )

    return peripheral_receive_large_sdu_cis_unframed(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_per_bv_36_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-36-C"""
    params = SetCIGParameters (
        NSE                     = 6,
        Framing                 = 0,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        BN_C_To_P               = 4,
        FT_C_To_P               = 3,
        # SDU_Interval_P_To_C     = N/A,
        SDU_Interval_C_To_P     = 0x61A8,  # 25 ms
        ISO_Interval            = 0x14,  # 25 ms
    )

    return peripheral_receive_large_sdu_cis_unframed(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_per_bv_19_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-19-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 4,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        BN_C_To_P               = 2,
        FT_C_To_P               = 2,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_C_To_P          = 20,
        Max_PDU_P_To_C          = 0,
    )

    return peripheral_receive_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_per_bv_43_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/PER/BV-43-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 1,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_C_To_P          = 20,
        Max_PDU_P_To_C          = 0,
    )

    return peripheral_receive_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_cen_bv_01_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/CEN/BV-01-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 2,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        # Max_PDU_P_To_C          = N/A,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        # Max_PDU_C_To_P          = default,
        # SDU_Interval_P_To_C     = N/A,
        SDU_Interval_C_To_P     = 0x3A98,  # 15 ms
        ISO_Interval            = 0x0C,  # 15 ms
        Max_SDU_Supported       = 251,  # Force Max SDU to be 251 bytes
    )

    return central_send_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_cen_bv_25_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/CEN/BV-25-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 4,
        BN_P_To_C               = 3,
        FT_P_To_C               = 1,
        Max_PDU_P_To_C          = 180,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        Max_PDU_C_To_P          = 180,
        SDU_Interval_P_To_C     = 0x1388,  # 5 ms
        SDU_Interval_C_To_P     = 0x3A98,  # 15 ms
        ISO_Interval            = 0x0C,  # 15 ms
        Max_SDU_Supported       = 83,  # Force Max SDU to be 83 bytes
    )

    return central_send_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_03_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-03-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 7,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        # Max_PDU_P_To_C          = N/A,
        BN_C_To_P               = 3,
        FT_C_To_P               = 4,
        # Max_PDU_C_To_P          = default,
        # SDU_Interval_P_To_C     = N/A,
        SDU_Interval_C_To_P     = 0x9C40,  # 40 ms
        ISO_Interval            = 0x20,  # 40 ms
        Max_SDU_Supported       = 180,  # Force Max SDU to be 180 bytes
    )

    return central_send_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_26_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-26-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 3,
        BN_P_To_C               = 1,
        FT_P_To_C               = 2,
        # Max_PDU_P_To_C          = default,
        BN_C_To_P               = 2,
        FT_C_To_P               = 3,
        # Max_PDU_C_To_P          = default,
        SDU_Interval_P_To_C     = 0x4E20,  # 20 ms
        SDU_Interval_C_To_P     = 0x2710,  # 10 ms
        ISO_Interval            = 0x10,  # 20 ms
        Max_SDU_Supported       = 78,  # Force Max SDU to be 78 bytes
    )

    return central_send_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_cen_bv_46_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/CEN/BV-46-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        # Max_PDU_P_To_C          = default,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        # Max_PDU_C_To_P          = default,
        SDU_Interval_P_To_C     = 0x2710,  # 10 ms
        SDU_Interval_C_To_P     = 0x2710,  # 10 ms
        ISO_Interval            = 0x08,  # 10 ms
        Max_SDU_Supported       = 192,  # Force Max SDU to be 192 bytes
    )

    return central_send_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_45_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-45-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        # Max_PDU_P_To_C          = default,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        # Max_PDU_C_To_P          = default,
        SDU_Interval_P_To_C     = 0x4E20,  # 20 ms
        SDU_Interval_C_To_P     = 0x4E20,  # 20 ms
        ISO_Interval            = 0x10,  # 20 ms
        Max_SDU_Supported       = 180,  # Force Max SDU to be 180 bytes
    )

    return central_send_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_cen_bv_04_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/CEN/BV-04-C"""
    params = SetCIGParameters(
        NSE                     = 8,
        Framing                 = 0,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        BN_C_To_P               = 6,
        FT_C_To_P               = 2,
        SDU_Interval_P_To_C     = 0x4E20,  # 20 ms
        SDU_Interval_C_To_P     = 0x4E20,  # 20 ms
        ISO_Interval            = 0x20,  # 40 ms
    )

    return central_send_large_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_cen_bv_28_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/CEN/BV-28-C"""
    params = SetCIGParameters(
        NSE                     = 4,
        Framing                 = 0,
        BN_P_To_C               = 3,
        FT_P_To_C               = 3,
        BN_C_To_P               = 3,
        FT_C_To_P               = 2,
        SDU_Interval_P_To_C     = 0x61A8,  # 25 ms
        SDU_Interval_C_To_P     = 0x61A8,  # 25 ms
        ISO_Interval            = 0x14,  # 25 ms
    )

    return central_send_large_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_05_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-05-C"""
    params = SetCIGParameters(
        NSE                     = 5,
        Framing                 = 1,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        BN_C_To_P               = 3,
        FT_C_To_P               = 1,
        SDU_Interval_P_To_C     = 0x4E20,  # 20 ms
        SDU_Interval_C_To_P     = 0x4E20,  # 20 ms
        ISO_Interval            = 0x14,  # 25 ms
    )

    return central_send_large_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_29_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-29-C"""
    params = SetCIGParameters(
        NSE                     = 4,
        Framing                 = 1,
        BN_P_To_C               = 3,
        FT_P_To_C               = 1,
        BN_C_To_P               = 3,
        FT_C_To_P               = 2,
        SDU_Interval_P_To_C     = 0x9C40,  # 40 ms
        SDU_Interval_C_To_P     = 0x9C40,  # 40 ms
        ISO_Interval            = 0x20,  # 40 ms
    )

    return central_send_large_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_46_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-46-C"""
    params = SetCIGParameters(
        NSE                     = 1,
        Framing                 = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        SDU_Interval_P_To_C     = 0x7530,  # 30 ms
        SDU_Interval_C_To_P     = 0x7530,  # 30 ms
        ISO_Interval            = 0x08,  # 10 ms
    )

    return central_send_large_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_07_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-07-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 2,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        BN_C_To_P               = 1,
        FT_C_To_P               = 4,
        SDU_Interval_C_To_P     = 0x7A120,  # 500 ms
        SDU_Interval_P_To_C     = 0x7A120,  # 500 ms
        ISO_Interval            = 0x320,  # 1000 ms
        Max_PDU_C_To_P          = 63,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_PDU_P_To_C          = 0,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_SDU_Supported       = 25,  # NOTE: Max_SDU is set to 25 when the corresponding BN is not 0
    )

    return central_send_multiple_small_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_31_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-31-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 7,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        BN_C_To_P               = 2,
        FT_C_To_P               = 4,
        SDU_Interval_C_To_P     = 0xF4240,  # 1000 ms
        SDU_Interval_P_To_C     = 0xF4240,  # 1000 ms
        ISO_Interval            = 0x640,  # 2000 ms
        Max_PDU_C_To_P          = 63,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_PDU_P_To_C          = 0,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_SDU_Supported       = 25,  # NOTE: Max_SDU is set to 25 when the corresponding BN is not 0
    )

    return central_send_multiple_small_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_47_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-47-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        SDU_Interval_C_To_P     = 0x7A120,  # 500 ms
        SDU_Interval_P_To_C     = 0x7A120,  # 500 ms
        ISO_Interval            = 0x320,  # 1000 ms
        Max_PDU_C_To_P          = 63,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_PDU_P_To_C          = 63,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_SDU_Supported       = 25,  # NOTE: Max_SDU is set to 25 when the corresponding BN is not 0
    )

    return central_send_multiple_small_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_cen_bv_09_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/CEN/BV-09-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 4,
        BN_P_To_C               = 3,
        FT_P_To_C               = 1,
        BN_C_To_P               = 0,
        # FT_C_To_P               = N/A,
        SDU_Interval_P_To_C     = 0x1388,  # 5 ms
        SDU_Interval_C_To_P     = 0x1388,  # 5 ms
        ISO_Interval            = 0x0C,  # 15 ms
        Max_PDU_P_To_C          = 251,
        Max_PDU_C_To_P          = 0,
        Max_SDU_Supported       = 251,  # Force Max SDU to be 251 bytes
    )

    return central_receive_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_cen_bv_33_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/CEN/BV-33-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 5,
        BN_P_To_C               = 3,
        FT_P_To_C               = 3,
        BN_C_To_P               = 3,
        FT_C_To_P               = 2,
        SDU_Interval_P_To_C     = 0x7530,  # 30 ms
        SDU_Interval_C_To_P     = 0x7530,  # 30 ms
        ISO_Interval            = 0x18,  # 30 ms
        Max_PDU_P_To_C          = 251,
        Max_PDU_C_To_P          = 251,
        Max_SDU_Supported       = 251,  # Force Max SDU to be 251 bytes
    )

    return central_receive_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_10_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-10-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 4,
        BN_P_To_C               = 2,
        FT_P_To_C               = 2,
        BN_C_To_P               = 0,
        # FT_C_To_P               = N/A,
        SDU_Interval_P_To_C     = 0x4E20,  # 20 ms
        SDU_Interval_C_To_P     = 0x4E20,  # 20 ms
        ISO_Interval            = 0x14,  # 25 ms
        Max_PDU_P_To_C          = 251,
        Max_PDU_C_To_P          = 0,
        Max_SDU_Supported       = 251,  # Force Max SDU to be 251 bytes
    )

    return central_receive_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_35_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-35-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 3,
        BN_P_To_C               = 2,
        FT_P_To_C               = 1,
        BN_C_To_P               = 0,
        # FT_C_To_P               = N/A,
        SDU_Interval_P_To_C     = 0x14D5,  # 5.333 ms
        SDU_Interval_C_To_P     = 0x14D5,  # 5.333 ms
        ISO_Interval            = 0x08,  # 10 ms
        Max_PDU_P_To_C          = 251,
        Max_PDU_C_To_P          = 0,
        Max_SDU_Supported       = 251,  # Force Max SDU to be 251 bytes
    )

    return central_receive_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_cen_bv_47_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/CEN/BV-47-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        SDU_Interval_P_To_C     = 0x3A98,  # 15 ms
        SDU_Interval_C_To_P     = 0x3A98,  # 15 ms
        ISO_Interval            = 0x0C,  # 15 ms
        Max_PDU_P_To_C          = 251,
        Max_PDU_C_To_P          = 251,
        Max_SDU_Supported       = 251,  # Force Max SDU to be 251 bytes
    )

    return central_receive_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_48_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-48-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        SDU_Interval_P_To_C     = 0x4E20,  # 20 ms
        SDU_Interval_C_To_P     = 0x4E20,  # 20 ms
        ISO_Interval            = 0x10,  # 20 ms
        Max_PDU_P_To_C          = 251,
        Max_PDU_C_To_P          = 251,
        Max_SDU_Supported       = 251,  # Force Max SDU to be 251 bytes
    )

    return central_receive_single_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_cen_bv_12_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/CEN/BV-12-C"""
    params = SetCIGParameters (
        NSE                     = 6,
        Framing                 = 0,
        BN_P_To_C               = 4,
        FT_P_To_C               = 2,
        BN_C_To_P               = 0,
        # FT_C_To_P               = N/A,
        SDU_Interval_P_To_C     = 0x61A8,  # 25 ms
        SDU_Interval_C_To_P     = 0x61A8,  # 25 ms
        ISO_Interval            = 0x14,  # 25 ms
    )

    return central_receive_large_sdu_cis_unframed(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_cen_bv_36_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/CEN/BV-36-C"""
    params = SetCIGParameters (
        NSE                     = 12,
        Framing                 = 0,
        BN_P_To_C               = 8,
        FT_P_To_C               = 3,
        BN_C_To_P               = 0,
        # FT_C_To_P               = N/A,
        SDU_Interval_P_To_C     = 0x61A8,  # 25 ms
        SDU_Interval_C_To_P     = 0x61A8,  # 25 ms
        ISO_Interval            = 0x28,  # 50 ms
    )

    return central_receive_large_sdu_cis_unframed(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_13_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-13-C"""
    params = SetCIGParameters (
        NSE                     = 12,
        Framing                 = 1,
        BN_P_To_C               = 7,
        FT_P_To_C               = 2,
        BN_C_To_P               = 0,
        # FT_C_To_P               = N/A,
        SDU_Interval_P_To_C     = 0x61A8,  # 25 ms
        SDU_Interval_C_To_P     = 0x61A8,  # 25 ms
        ISO_Interval            = 0x28,  # 50 ms
    )

    return central_receive_large_sdu_cis_framed(transport, upper_tester, lower_tester, trace, params, True)


def ial_cis_fra_cen_bv_38_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-38-C"""
    params = SetCIGParameters (
        NSE                     = 8,
        Framing                 = 1,
        BN_P_To_C               = 5,
        FT_P_To_C               = 2,
        BN_C_To_P               = 0,
        # FT_C_To_P               = N/A,
        SDU_Interval_P_To_C     = 0x55F0,  # 22 ms
        SDU_Interval_C_To_P     = 0x55F0,  # 22 ms
        ISO_Interval            = 0x1C,  # 35 ms
    )

    return central_receive_large_sdu_cis_framed(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_49_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-49-C"""
    params = SetCIGParameters (
        NSE                     = 1,
        Framing                 = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        SDU_Interval_P_To_C     = 0x30D40,  # 200 ms
        SDU_Interval_C_To_P     = 0x30D40,  # 200 ms
        ISO_Interval            = 0x28,  # 50 ms
    )

    return central_receive_large_sdu_cis_framed(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_15_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-15-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 2,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 0,
        # FT_C_To_P               = N/A,
        SDU_Interval_C_To_P     = 0x2710,  # 10 ms
        SDU_Interval_P_To_C     = 0x2710,  # 10 ms
        ISO_Interval            = 0x04,  # 5 ms
        Max_PDU_C_To_P          = 0,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_PDU_P_To_C          = 63,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_SDU_Supported       = 25,  # NOTE: Max_SDU is set to 25 when the corresponding BN is not 0
    )

    return central_receive_multiple_small_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_39_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-39-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 4,
        BN_P_To_C               = 2,
        FT_P_To_C               = 1,
        BN_C_To_P               = 2,
        FT_C_To_P               = 2,
        SDU_Interval_C_To_P     = 0x4E20,  # 20 ms
        SDU_Interval_P_To_C     = 0x4E20,  # 20 ms
        ISO_Interval            = 0x08,  # 10 ms
        Max_PDU_C_To_P          = 63,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_PDU_P_To_C          = 63,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_SDU_Supported       = 25,  # NOTE: Max_SDU is set to 25 when the corresponding BN is not 0
    )

    return central_receive_multiple_small_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_50_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-50-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        SDU_Interval_C_To_P     = 0x4E20,  # 20 ms
        SDU_Interval_P_To_C     = 0x4E20,  # 20 ms
        ISO_Interval            = 0x20,  # 40 ms
        Max_PDU_C_To_P          = 63,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_PDU_P_To_C          = 63,  # NOTE: Max_PDU is set to 63 when the corresponding BN is not 0
        Max_SDU_Supported       = 25,  # NOTE: Max_SDU is set to 25 when the corresponding BN is not 0
    )

    return central_receive_multiple_small_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_cen_bv_17_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/CEN/BV-17-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 4,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        BN_C_To_P               = 2,
        FT_C_To_P               = 2,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_P_To_C          = 0,
        Max_PDU_C_To_P          = 20,
    )

    return central_send_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_cen_bv_41_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/CEN/BV-41-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 1,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_P_To_C          = 0,
        Max_PDU_C_To_P          = 20,
    )

    return central_send_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_18_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-18-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 5,
        BN_P_To_C               = 0,
        # FT_P_To_C               = N/A,
        BN_C_To_P               = 2,
        FT_C_To_P               = 2,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_P_To_C          = 0,
        Max_PDU_C_To_P          = 20,
    )

    return central_send_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_42_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-42-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 2,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_P_To_C          = 20,
        Max_PDU_C_To_P          = 20,
    )

    return central_send_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_51_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-51-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_P_To_C          = 20,
        Max_PDU_C_To_P          = 20,
    )

    return central_send_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_cen_bv_19_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/CEN/BV-19-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 7,
        BN_P_To_C               = 3,
        FT_P_To_C               = 4,
        BN_C_To_P               = 0,
        # FT_C_To_P               = N/A,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_P_To_C          = 20,
        Max_PDU_C_To_P          = 0,
    )

    return central_receive_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_cen_bv_43_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/CEN/BV-43-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 2,
        BN_P_To_C               = 1,
        FT_P_To_C               = 3,
        BN_C_To_P               = 1,
        FT_C_To_P               = 2,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_P_To_C          = 20,
        Max_PDU_C_To_P          = 20,
    )

    return central_receive_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_20_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-20-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 2,
        BN_P_To_C               = 1,
        FT_P_To_C               = 4,
        BN_C_To_P               = 0,
        # FT_C_To_P               = N/A,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_P_To_C          = 20,
        Max_PDU_C_To_P          = 0,
    )

    return central_receive_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_44_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-44-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 5,
        BN_P_To_C               = 1,
        FT_P_To_C               = 2,
        BN_C_To_P               = 3,
        FT_C_To_P               = 3,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_P_To_C          = 20,
        Max_PDU_C_To_P          = 20,
    )

    return central_receive_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_cen_bv_48_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/CEN/BV-48-C"""
    params = SetCIGParameters(
        Framing                 = 0,
        NSE                     = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_P_To_C          = 20,
        Max_PDU_C_To_P          = 20,
    )

    return central_receive_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_52_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-52-C"""
    params = SetCIGParameters(
        Framing                 = 1,
        NSE                     = 1,
        BN_P_To_C               = 1,
        FT_P_To_C               = 1,
        BN_C_To_P               = 1,
        FT_C_To_P               = 1,
        # NOTE: ISO_Interval and SDU_Interval are both set to 10 milliseconds.
        SDU_Interval_C_To_P     = 10000,
        SDU_Interval_P_To_C     = 10000,
        ISO_Interval            = int(10 // 1.25),
        # NOTE: Max_PDU_C_to_P and Max_PDU_P_to_C are both set to 20 when BN in the corresponding direction is not 0,
        #       and to 0 when BN in the corresponding direction is 0.
        Max_PDU_P_To_C          = 20,
        Max_PDU_C_To_P          = 20,
    )

    return central_receive_zero_length_sdu_cis(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_cen_bv_21_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/CEN/BV-21-C"""
    params = SetCIGParameters(
        NSE                 = 2,
        Framing             = 0,
        BN_P_To_C           = 1,
        FT_P_To_C           = 1,
        BN_C_To_P           = 1,
        FT_C_To_P           = 1,
    )

    return central_simultanous_sending_and_receiving_sdus(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_cen_bv_24_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/CEN/BV-24-C"""
    params = SetCIGParameters(
        NSE                 = 3,
        Framing             = 0,
        BN_P_To_C           = 1,
        FT_P_To_C           = 2,
        BN_C_To_P           = 2,
        FT_C_To_P           = 3,
    )

    return central_simultanous_sending_and_receiving_sdus(transport, upper_tester, lower_tester, trace, params)


def ial_cis_fra_cen_bv_22_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/FRA/CEN/BV-22-C"""
    params = SetCIGParameters(
        NSE                 = 5,
        Framing             = 1,
        BN_P_To_C           = 1,
        FT_P_To_C           = 2,
        BN_C_To_P           = 3,
        FT_C_To_P           = 3,
    )

    return central_simultanous_sending_and_receiving_sdus(transport, upper_tester, lower_tester, trace, params)


def ial_cis_unf_cen_bv_45_c(transport, upper_tester, lower_tester, trace):
    """IAL/CIS/UNF/CEN/BV-45-C"""
    return central_sending_and_receiving_unframed_empty_pdu_llid_0b01_cis(transport, upper_tester, lower_tester,
                                                                          trace, 0x04, 0x08)


__tests__ = {
    "IAL/CIS/UNF/CEN/BV-01-C": [ial_cis_unf_cen_bv_01_c, "Send Single SDU, CIS"],
    "IAL/CIS/UNF/PER/BV-01-C": [ial_cis_unf_per_bv_01_c, "Send Single SDU, CIS"],
    # "IAL/CIS/UNF/CEN/BV-25-C": [ial_cis_unf_cen_bv_25_c, "Send Single SDU, CIS"],  # https://github.com/EDTTool/EDTT-le-audio/issues/117
    "IAL/CIS/UNF/PER/BV-25-C": [ial_cis_unf_per_bv_25_c, "Send Single SDU, CIS"],
    "IAL/CIS/FRA/CEN/BV-03-C": [ial_cis_fra_cen_bv_03_c, "Send Single SDU, CIS"],
    "IAL/CIS/FRA/PER/BV-03-C": [ial_cis_fra_per_bv_03_c, "Send Single SDU, CIS"],
    "IAL/CIS/FRA/CEN/BV-26-C": [ial_cis_fra_cen_bv_26_c, "Send Single SDU, CIS"],
    "IAL/CIS/FRA/PER/BV-26-C": [ial_cis_fra_per_bv_26_c, "Send Single SDU, CIS"],
    "IAL/CIS/UNF/CEN/BV-46-C": [ial_cis_unf_cen_bv_46_c, "Send Single SDU, CIS"],
    "IAL/CIS/UNF/PER/BV-47-C": [ial_cis_unf_per_bv_47_c, "Send Single SDU, CIS"],
    "IAL/CIS/FRA/CEN/BV-45-C": [ial_cis_fra_cen_bv_45_c, "Send Single SDU, CIS"],
    "IAL/CIS/FRA/PER/BV-45-C": [ial_cis_fra_per_bv_45_c, "Send Single SDU, CIS"],
    "IAL/CIS/UNF/CEN/BV-04-C": [ial_cis_unf_cen_bv_04_c, "Send Large SDU, CIS"],
    "IAL/CIS/UNF/PER/BV-04-C": [ial_cis_unf_per_bv_04_c, "Send Large SDU, CIS"],
    "IAL/CIS/UNF/CEN/BV-28-C": [ial_cis_unf_cen_bv_28_c, "Send Large SDU, CIS"],
    "IAL/CIS/UNF/PER/BV-28-C": [ial_cis_unf_per_bv_28_c, "Send Large SDU, CIS"],
    "IAL/CIS/FRA/CEN/BV-05-C": [ial_cis_fra_cen_bv_05_c, "Send Large SDU, CIS"],
    "IAL/CIS/FRA/PER/BV-05-C": [ial_cis_fra_per_bv_05_c, "Send Large SDU, CIS"],
    "IAL/CIS/FRA/CEN/BV-29-C": [ial_cis_fra_cen_bv_29_c, "Send Large SDU, CIS"],
    "IAL/CIS/FRA/PER/BV-29-C": [ial_cis_fra_per_bv_29_c, "Send Large SDU, CIS"],
    "IAL/CIS/FRA/CEN/BV-46-C": [ial_cis_fra_cen_bv_46_c, "Send Large SDU, CIS"],
    "IAL/CIS/FRA/PER/BV-46-C": [ial_cis_fra_per_bv_46_c, "Send Large SDU, CIS"],
    "IAL/CIS/FRA/CEN/BV-07-C": [ial_cis_fra_cen_bv_07_c, "Send Multiple, Small SDUs, CIS"],
    "IAL/CIS/FRA/PER/BV-07-C": [ial_cis_fra_per_bv_07_c, "Send Multiple, Small SDUs, CIS"],
    "IAL/CIS/FRA/CEN/BV-31-C": [ial_cis_fra_cen_bv_31_c, "Send Multiple, Small SDUs, CIS"],
    "IAL/CIS/FRA/PER/BV-31-C": [ial_cis_fra_per_bv_31_c, "Send Multiple, Small SDUs, CIS"],
    "IAL/CIS/FRA/CEN/BV-47-C": [ial_cis_fra_cen_bv_47_c, "Send Multiple, Small SDUs, CIS"],
    "IAL/CIS/FRA/PER/BV-47-C": [ial_cis_fra_per_bv_47_c, "Send Multiple, Small SDUs, CIS"],
    "IAL/CIS/UNF/CEN/BV-09-C": [ial_cis_unf_cen_bv_09_c, "Receive Single SDU, CIS"],
    "IAL/CIS/UNF/PER/BV-09-C": [ial_cis_unf_per_bv_09_c, "Receive Single SDU, CIS"],
    "IAL/CIS/UNF/CEN/BV-33-C": [ial_cis_unf_cen_bv_33_c, "Receive Single SDU, CIS"],
    "IAL/CIS/UNF/PER/BV-33-C": [ial_cis_unf_per_bv_33_c, "Receive Single SDU, CIS"],
    "IAL/CIS/FRA/CEN/BV-10-C": [ial_cis_fra_cen_bv_10_c, "Receive Single SDU, CIS"],
    "IAL/CIS/FRA/PER/BV-10-C": [ial_cis_fra_per_bv_10_c, "Receive Single SDU, CIS"],
    "IAL/CIS/FRA/CEN/BV-35-C": [ial_cis_fra_cen_bv_35_c, "Receive Single SDU, CIS"],
    "IAL/CIS/FRA/PER/BV-35-C": [ial_cis_fra_per_bv_35_c, "Receive Single SDU, CIS"],
    "IAL/CIS/UNF/CEN/BV-47-C": [ial_cis_unf_cen_bv_47_c, "Receive Single SDU, CIS"],
    "IAL/CIS/UNF/PER/BV-48-C": [ial_cis_unf_per_bv_48_c, "Receive Single SDU, CIS"],
    "IAL/CIS/FRA/CEN/BV-48-C": [ial_cis_fra_cen_bv_48_c, "Receive Single SDU, CIS"],
    "IAL/CIS/FRA/PER/BV-48-C": [ial_cis_fra_per_bv_48_c, "Receive Single SDU, CIS"],
    "IAL/CIS/UNF/CEN/BV-12-C": [ial_cis_unf_cen_bv_12_c, "Receive Large SDU, CIS, Unframed"],
    "IAL/CIS/UNF/PER/BV-12-C": [ial_cis_unf_per_bv_12_c, "Receive Large SDU, CIS, Unframed"],
    "IAL/CIS/UNF/CEN/BV-36-C": [ial_cis_unf_cen_bv_36_c, "Receive Large SDU, CIS, Unframed"],
    "IAL/CIS/UNF/PER/BV-36-C": [ial_cis_unf_per_bv_36_c, "Receive Large SDU, CIS, Unframed"],
    "IAL/CIS/FRA/CEN/BV-13-C": [ial_cis_fra_cen_bv_13_c, "Receive Large SDU, CIS, Framed"],
    "IAL/CIS/FRA/PER/BV-13-C": [ial_cis_fra_per_bv_13_c, "Receive Large SDU, CIS, Framed"],
    "IAL/CIS/FRA/CEN/BV-38-C": [ial_cis_fra_cen_bv_38_c, "Receive Large SDU, CIS, Framed"],
    "IAL/CIS/FRA/PER/BV-38-C": [ial_cis_fra_per_bv_38_c, "Receive Large SDU, CIS, Framed"],
    "IAL/CIS/FRA/CEN/BV-49-C": [ial_cis_fra_cen_bv_49_c, "Receive Large SDU, CIS, Framed"],
    "IAL/CIS/FRA/PER/BV-49-C": [ial_cis_fra_per_bv_49_c, "Receive Large SDU, CIS, Framed"],
    "IAL/CIS/FRA/CEN/BV-15-C": [ial_cis_fra_cen_bv_15_c, "Receive Multiple Small SDUs, CIS"],
    "IAL/CIS/FRA/PER/BV-15-C": [ial_cis_fra_per_bv_15_c, "Receive Multiple Small SDUs, CIS"],
    "IAL/CIS/FRA/CEN/BV-39-C": [ial_cis_fra_cen_bv_39_c, "Receive Multiple Small SDUs, CIS"],
    "IAL/CIS/FRA/PER/BV-39-C": [ial_cis_fra_per_bv_39_c, "Receive Multiple Small SDUs, CIS"],
    "IAL/CIS/FRA/CEN/BV-50-C": [ial_cis_fra_cen_bv_50_c, "Receive Multiple Small SDUs, CIS"],
    "IAL/CIS/FRA/PER/BV-50-C": [ial_cis_fra_per_bv_50_c, "Receive Multiple Small SDUs, CIS"],
    "IAL/CIS/UNF/CEN/BV-17-C": [ial_cis_unf_cen_bv_17_c, "Send a Zero-Length SDU, CIS"],
    "IAL/CIS/UNF/PER/BV-17-C": [ial_cis_unf_per_bv_17_c, "Send a Zero-Length SDU, CIS"],
    "IAL/CIS/UNF/CEN/BV-41-C": [ial_cis_unf_cen_bv_41_c, "Send a Zero-Length SDU, CIS"],
    "IAL/CIS/UNF/PER/BV-41-C": [ial_cis_unf_per_bv_41_c, "Send a Zero-Length SDU, CIS"],
    "IAL/CIS/FRA/CEN/BV-18-C": [ial_cis_fra_cen_bv_18_c, "Send a Zero-Length SDU, CIS"],
    "IAL/CIS/FRA/PER/BV-18-C": [ial_cis_fra_per_bv_18_c, "Send a Zero-Length SDU, CIS"],
    "IAL/CIS/FRA/CEN/BV-42-C": [ial_cis_fra_cen_bv_42_c, "Send a Zero-Length SDU, CIS"],
    "IAL/CIS/FRA/PER/BV-42-C": [ial_cis_fra_per_bv_42_c, "Send a Zero-Length SDU, CIS"],
    "IAL/CIS/UNF/PER/BV-49-C": [ial_cis_unf_per_bv_49_c, "Send a Zero-Length SDU, CIS"],
    "IAL/CIS/FRA/CEN/BV-51-C": [ial_cis_fra_cen_bv_51_c, "Send a Zero-Length SDU, CIS"],
    "IAL/CIS/FRA/PER/BV-51-C": [ial_cis_fra_per_bv_51_c, "Send a Zero-Length SDU, CIS"],
    "IAL/CIS/UNF/CEN/BV-19-C": [ial_cis_unf_cen_bv_19_c, "Receive a Zero-Length SDUs CIS"],
    "IAL/CIS/UNF/PER/BV-19-C": [ial_cis_unf_per_bv_19_c, "Receive a Zero-Length SDUs CIS"],
    "IAL/CIS/UNF/CEN/BV-43-C": [ial_cis_unf_cen_bv_43_c, "Receive a Zero-Length SDUs CIS"],
    "IAL/CIS/UNF/PER/BV-43-C": [ial_cis_unf_per_bv_43_c, "Receive a Zero-Length SDUs CIS"],
    "IAL/CIS/FRA/CEN/BV-20-C": [ial_cis_fra_cen_bv_20_c, "Receive a Zero-Length SDUs CIS"],
    "IAL/CIS/FRA/PER/BV-20-C": [ial_cis_fra_per_bv_20_c, "Receive a Zero-Length SDUs CIS"],
    "IAL/CIS/FRA/CEN/BV-44-C": [ial_cis_fra_cen_bv_44_c, "Receive a Zero-Length SDUs CIS"],
    "IAL/CIS/FRA/PER/BV-44-C": [ial_cis_fra_per_bv_44_c, "Receive a Zero-Length SDUs CIS"],
    "IAL/CIS/UNF/CEN/BV-48-C": [ial_cis_unf_cen_bv_48_c, "Receive a Zero-Length SDUs CIS"],
    "IAL/CIS/FRA/CEN/BV-52-C": [ial_cis_fra_cen_bv_52_c, "Receive a Zero-Length SDUs CIS"],
    "IAL/CIS/FRA/PER/BV-52-C": [ial_cis_fra_per_bv_52_c, "Receive a Zero-Length SDUs CIS"],
    "IAL/CIS/UNF/CEN/BV-21-C": [ial_cis_unf_cen_bv_21_c, "Simultaneous Sending and Receiving SDUs, CIS"],
    "IAL/CIS/UNF/PER/BV-21-C": [ial_cis_unf_per_bv_21_c, "Simultaneous Sending and Receiving SDUs, CIS"],
    "IAL/CIS/UNF/CEN/BV-24-C": [ial_cis_unf_cen_bv_24_c, "Simultaneous Sending and Receiving SDUs, CIS"],
    "IAL/CIS/UNF/PER/BV-24-C": [ial_cis_unf_per_bv_24_c, "Simultaneous Sending and Receiving SDUs, CIS"],
    # "IAL/CIS/FRA/CEN/BV-22-C": [ial_cis_fra_cen_bv_22_c, "Simultaneous Sending and Receiving SDUs, CIS"],  # https://github.com/EDTTool/EDTT-le-audio/issues/117
    # "IAL/CIS/FRA/PER/BV-22-C": [ial_cis_fra_per_bv_22_c, "Simultaneous Sending and Receiving SDUs, CIS"],  # https://github.com/EDTTool/EDTT-le-audio/issues/117
    "IAL/CIS/UNF/CEN/BV-45-C": [ial_cis_unf_cen_bv_45_c, "Sending and Receiving Unframed Empty PDUs with LLID=0b01, CIS"],
    "IAL/CIS/UNF/PER/BV-45-C": [ial_cis_unf_per_bv_45_c, "Sending and Receiving Unframed Empty PDUs with LLID=0b01, CIS"],
    "IAL/CIS/UNF/PER/BV-46-C": [ial_cis_unf_per_bv_46_c, "Sending and Receiving Unframed Empty PDUs with LLID=0b01, CIS"],
}


_maxNameLength = max([len(key) for key in __tests__])

_spec = {key: TestSpec(name=key, number_devices=2, description="#[" + __tests__[key][1] + "]",
                       test_private=__tests__[key][0]) for key in __tests__}

"""
    Return the test spec which contains info about all the tests
    this test module provides
"""
def get_tests_specs():
    return _spec


def preamble(transport, trace):
    global lowerIRK, upperIRK, lowerRandomAddress, upperRandomAddress

    ok = success = preamble_standby(transport, 0, trace)
    trace.trace(4, "preamble Standby " + ("PASS" if success else "FAIL"))
    success = preamble_standby(transport, 1, trace)
    ok = ok and success
    trace.trace(4, "preamble Standby " + ("PASS" if success else "FAIL"))
    success, upperIRK, upperRandomAddress = preamble_device_address_set(transport, 0, trace)
    trace.trace(4, "preamble Device Address Set " +
                ("PASS" if success else "FAIL"))
    ok = ok and success
    success, lowerIRK, lowerRandomAddress = preamble_device_address_set(transport, 1, trace)
    trace.trace(4, "preamble Device Address Set " +
                ("PASS" if success else "FAIL"))

    return ok and success


"""
    Run a test given its test_spec
"""
def run_a_test(args, transport, trace, test_spec, device_dumps):
    try:
        success = preamble(transport, trace)
    except Exception as e:
        trace.trace(3, "Preamble generated exception: %s" % str(e))
        success = False

    trace.trace(2, "%-*s %s test started..." % (_maxNameLength, test_spec.name, test_spec.description[1:]))
    test_f = test_spec.test_private
    try:
        if test_f.__code__.co_argcount > 4:
            success = success and test_f(transport, 0, 1, trace, device_dumps)
        elif test_f.__code__.co_argcount > 3:
            success = success and test_f(transport, 0, 1, trace)
        else:
            success = success and test_f(transport, 0, trace)
    except Exception as e:
        import traceback
        traceback.print_exc()
        trace.trace(3, "Test generated exception: %s" % str(e))
        success = False

    return not success
