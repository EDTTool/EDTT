# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

from components.utils import *;
from components.basic_commands import *;
from components.address import *;
from components.smpdata import *;
from components.events import *;

"""
    Pairing is used to establish an encrypted link between two parties.
    - The two parties can be two entities running without Host layer.
    - The two parties can also be one entity running without Host layer (initiator) and one entity running with Host layer (responder).
    - All the necessary keys willl be generated and exchanged between the parties.
    - After a successful exchange of random numbers - the link will be encrypted.
    - After the link has been encrypted - encryption keys will be exchanged.
"""
class Pairing:
    """
        Constructor:
            transport - PTTT_bsim object
            trace     - Trace object
            initiator - Initiator object representing the connection between the parties
            IRKm      - Number: Identity Resolving Key for Initiator
            IRKs      - Number: Identity Resolving Key for Responder (only needed if Responder is running without Host layer)
    """
    def __init__(self, transport, trace, initiator, IRKm, IRKs=None):
        self.transport = transport;
        self.initiator = initiator;
        self.trace = trace;
        self.IRKm = IRKm;
        self.IRKs = IRKs;
        self.rand = self.ediv = self.ltk = 0;

    """
        Send an SMP Protocol request from device with index <idx> to the other device

        Arguments:
            idx    - Number: holding the index of the device that sends the request
            txData - List:   containing the SMP PDU to send
    """
    def __request(self, idx, txData):
        status = le_data_write(self.transport, idx, self.initiator.handles[idx], 0, 0, txData, 100);
        success = status == 0;
        dataSent = False;

        while success and not dataSent:
            dataSent = has_event(self.transport, idx, 100)[0];
            success = success and dataSent;
            if dataSent:
                event = get_event(self.transport, idx, 100);
              # showEvent(event, eventData, self.trace);
                dataSent = event.event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS;

        return dataSent;

    """
        Receive a SMP Protocol request/response in device with index <idx>

        Arguments:
            idx - Number: holding the index of the device that receives the request/response
    """
    def __response(self, idx):
        success, rxData = True, [];

        dataReady = le_data_ready(self.transport, idx, 100);
        if dataReady:
            rxPBFlags, rxBCFlags, rxData = le_data_read(self.transport, idx, 100)[2:];

        return (len(rxData) > 0), rxData;

    """
        Generate an 8 octet random number...

        Arguments:
            idx - Number: holding the index of the device in which the random number is generated
    """
    def __random(self, idx):
        status, rand = le_rand(self.transport, idx, 100);
        success = status == 0;
        event = get_event(self.transport, idx, 100);
        success = success and event.isCommandComplete();
        return success, toNumber(rand);

    """
        Generate a 16 octet random number...

        Arguments:
            idx - Number: holding the index of the device in which the random number is generated
    """
    def __random128(self, idx):
        success, randL = self.__random(idx);
        if success:
            success, randU = self.__random(idx);
            randL = (randU << 64) | randL;
        return success, randL;

    """
        Encrypt <plaintext> with the key <key>...

        Arguments:
            idx       - Number: holding the index of the device in which the encryption takes place
            key       - Number: containing the key to use
            plaintext - Number: containing the message to be encrypted
    """
    def __encrypt(self, idx, key, plaintext):
        status, encrypted = le_encrypt(self.transport, idx, toArray(key, 16), toArray(plaintext, 16), 2000);
        success = status == 0;
        event = get_event(self.transport, idx, 100);
        success = success and event.isCommandComplete();
        return success, toNumber(encrypted);

    """
        Calculate the Pairing Confirm value:

        Arguments:
            idx  - Number: holding the index of the device in which the calculation takes place
            tk   - Number: containing a temporare key to use (0 for Just Works)
            rand - Number: containing a 128 bit random number
            preq - List: containing the full pairing request PDU
            pres - List: containing the full pairing response PDU
            ia   - Address object: containing the address of the initiator (address and address-type)
            ra   - Address object: containing the address of the responder (address and address-type)

        Calculations:
            p1 = pres || preq || rat || iat
            p2 = ia || ra
            c1 = e(tk, e(tk, rand XOR p1) XOR p2)
    """
    def __calcConfirm(self, idx, tk, rand, preq, pres, ia, ra):
        p1 = (((((pres << 56) | preq) << 8) | ra.type) << 8) | ia.type;
        p2 = (toNumber(ia.address) << 48) | toNumber(ra.address);
        p1 ^= rand;
        success, p1 = self.__encrypt(idx, tk, p1);
        p1 ^= p2;
        success, p1 = self.__encrypt(idx, tk, p1);
        return success, p1;

    """
        Calculate the Pairing Short Term Key (STK):

        Arguments:
            idx - Number: holding the index of the device in which the calculation takes place
            tk  - Number: containing a temporare key to use (0 for Just Works)
            r1  - Number: containing a 128 bit random number
            r2  - Number: containing a 128 bit random number

        Calculations:
            r1 = <limit to 64 bits>
            r2 = <limit to 64 bits>
             r = r1 || r2
            s1 = e(tk, r)
    """
    def __calcSTK(self, idx, tk, r1, r2):
        r1 &= 0x00FFFFFFFFFFFFFFFF;
        r2 &= 0x00FFFFFFFFFFFFFFFF;
        r1 = (r1 << 64) | r2;
        success, r1 = self.__encrypt(idx, tk, r1);
        return success, r1;

    """
        Calculate the Pairing Long Term Key (LTK):

        Arguments:
            idx - Number: holding the index of the device in which the calculation takes place
            er  - Number: containing the encryption root (128 bit)
            div - Number: containing the diversifier (16 bits)

        Calculations:
            LTK = d1(ER, DIV, 0)

            k = ER  is 128 bits
            d = DIV is 16 bits
            r = 0
            d' = padding || r || d
            d1 = e(k, d')
    """
    def __calcLTK(self, idx, er, div):
        success, d1 = self.__encrypt(idx, er, div & 0xFFFF);
        return success, d1;

    """
        Calculate DIV masking

        Arguments:
            idx - Number: holding the index of the device in which the calculation takes place
            k   - Number: containing the Diversifier Hiding Key (128 bit)
            r   - Number: containing a 64 bit random number

        Calculations:
            k is 128 bits
            r is 64 bits (padded to 128 bits)
            r' = padding || r

            dm(k, r') = e(k, r') mod 2^16
    """
    def __calcDIVMask(self, idx, k, r):
        success, dm = self.__encrypt(idx, k, r);
        return success, (dm & 0x00FFFF);

    """
        Generate EDIV for distribution (Encrypted Diversifier)

        Arguments:
            idx  - Number: holding the index of the device in which the calculation takes place
            dhk  - Number: containing the Diversifier Hiding Key (128 bit)
            rand - Number: containing a 64 bit random number
            div  - Number: containing the diversifier

        Calculations:
            k = DHK (Diversifier Hiding Key) is 128 bit
            r = Rand is 64 bit

            Y = dm(DHK, Rand)
            EDIV = Y XOR DIV
    """
    def __generateEDIV(self, idx, dhk, rand, div):
        success, y = self.__calcDIVMask(idx, dhk, rand);
        return success, (div ^ y);

    """
        Recover DIV from distribution (from Encrypted Diversifier)

        Arguments:
            idx  - Number: holding the index of the device in which the calculation takes place
            dhk  - Number: containing the Diversifier Hiding Key (128 bit)
            rand - Number: containing a 64 bit random number
            ediv - Number: containing the Encrypted Diversifier

        Calculations:
            k = DHK (Diversifier Hiding Key) is 128 bit
            r = Rand is 64 bit

            Y = dm(DHK, Rand)
            DIV = Y XOR EDIV
    """
    def __recoverDIV(self, idx, dhk, rand, ediv):
        success, y = self.__calcDIVMask(idx, dhk, rand);
        return success, (ediv ^ y);

    """
        Calculate keys to be distributed

        Arguments:
            idx - Number: holding the index of the device in which the calculation takes place

        Calculations:
            ir   : Identity Root   (unique to each device)
            er   : Encryption Root (unique to each device)
            dhk  = e(ir, 2)
            div  : random 128 bit number
            ltk  = d1(er, div, 0)
            rand : random 64 bit number
            ediv = dm(dhk, rand) XOR div
    """
    def __calculateKeys(self, idx):
        ir = er = 0x00112233445566778899AABBCCDDEEFF if idx == 0 else 0x112233445566778899AABBCCDDEEFF00;

        success, dhk = self.__encrypt(idx, ir, 0x02);
        success, div = self.__random128(idx);
        success, ltk = self.__calcLTK(idx, er, div);
        success, rand = self.__random(idx);
        success, ediv = self.__generateEDIV(idx, dhk, rand, div);
        ediv &= 0x00FFFF;

        return success, ediv, rand, ltk;

    def __publicKey(self):
        status = 0;

    """
        Prepare for pairing by exchanging requirements and capabilities...

                SMP_PAIRING_REQUEST -->
            <-- SMP_PAIRING_RESPONSE
    """
    def __capabilities(self, authRequest):
        smpData = SMPData();
        reply = { };

        distKeys = SMPDistribution.SMP_DST_ENCKEY | SMPDistribution.SMP_DST_IDKEY;

        txiData = smpData.encode( SMPOpcode.SMP_PAIRING_REQUEST, SMPCapability.SMP_CAP_NO_INPUT_NO_OUTPUT, SMPOOBFlag.SMP_OOB_NO_AUTH_DATA, authRequest, 16, distKeys, distKeys );
        success = self.__request( self.initiator.initiator, txiData );
        while success:
            if not self.initiator.peer is None:
                success, rxrData = self.__response( self.initiator.peer );
                if not success:
                    break;
                reply = smpData.decode( rxrData );
                success = reply["opcode"] == SMPOpcode.SMP_PAIRING_REQUEST;
                if not success:
                    break;
                txrData = smpData.encode( SMPOpcode.SMP_PAIRING_RESPONSE, SMPCapability.SMP_CAP_NO_INPUT_NO_OUTPUT, SMPOOBFlag.SMP_OOB_NO_AUTH_DATA, authRequest, 16, distKeys, distKeys );
                success = self.__request( self.initiator.peer, txrData );
                if not success:
                    break;

            success, rxiData = self.__response( self.initiator.initiator );
            if not success:
                break;
            reply = smpData.decode( rxiData );
            success = reply["opcode"] == SMPOpcode.SMP_PAIRING_RESPONSE;
            if not success:
                break;

            self.pRequest  = toNumber(txiData[4:]);
            self.pResponse = toNumber(rxiData[4:]);

            break;

        return success, reply;

    """
        Prepare for pairing by exchanging random numbers...

                SMP_PAIRING_CONFIRM -->
            <-- SMP_PAIRING_CONFIRM
                SMP_PAIRING_RANDOM  -->
            <-- SMP_PAIRING_RANDOM

        Finally calculate the STK to use for encrypting the connection.
    """
    def __legacyPairing(self, ia, ra):
        smpData = SMPData();
        success = True;
        stk = 0;

        while success:
            success, mRand = self.__random128( self.initiator.initiator );
            if not success:
                break;
            success, mConfirm = self.__calcConfirm( self.initiator.initiator, 0, mRand, self.pRequest, self.pResponse, ia, ra );
            if not success:
                break;
            txData = smpData.encode( SMPOpcode.SMP_PAIRING_CONFIRM, mConfirm );
            success = self.__request( self.initiator.initiator, txData );
            if not success:
                break;
            """
                If peer device doesn't have a Host layer to process the SMP_PAIRING_CONFIRM message, we need to do it...
            """
            if not self.initiator.peer is None:
                success, rxData = self.__response( self.initiator.peer );
                if not success:
                    break;
                reply = smpData.decode( rxData );
                success = reply["opcode"] == SMPOpcode.SMP_PAIRING_CONFIRM;
                if not success:
                    break;
                success, sRand = self.__random128( self.initiator.peer );
                if not success:
                    break;
                success, sConfirm = self.__calcConfirm( self.initiator.peer, 0, sRand, self.pRequest, self.pResponse, ia, ra );
                if not success:
                    break;
                txData = smpData.encode( SMPOpcode.SMP_PAIRING_CONFIRM, sConfirm );
                success = self.__request( self.initiator.peer, txData );

            success, rxData = self.__response( self.initiator.initiator );
            if not success:
                break;
            reply = smpData.decode( rxData );
            success = reply["opcode"] == SMPOpcode.SMP_PAIRING_CONFIRM;
            if not success:
                break;

            sConfirm = reply["value"];

            txData = smpData.encode( SMPOpcode.SMP_PAIRING_RANDOM, mRand );
            success = self.__request( self.initiator.initiator, txData );
            if not success:
                break;
            """
                If peer device doesn't have a Host layer to process the SMP_PAIRING_RANDOM message, we need to do it...
            """
            if not self.initiator.peer is None:
                success, rxData = self.__response( self.initiator.peer );
                if not success:
                    break;
                reply = smpData.decode( rxData );
                success = reply["opcode"] == SMPOpcode.SMP_PAIRING_RANDOM;
                if not success:
                    break;

                success, xConfirm = self.__calcConfirm( self.initiator.peer, 0, mRand, self.pRequest, self.pResponse, ia, ra );
                if not success:
                    break;
                success = xConfirm == mConfirm;
                if not success:
                    txData = smpData.encode( SMPOpcode.SMP_PAIRING_FAILED, SMPError.SMP_ERROR_CONFIRM );
                    success = self.__request( self.initiator.peer, txData );
                else:
                    txData = smpData.encode( SMPOpcode.SMP_PAIRING_RANDOM, sRand );
                    success = self.__request( self.initiator.peer, txData );
                if not success:
                    break;

            success, rxData = self.__response( self.initiator.initiator );
            if not success:
                break;
            reply = smpData.decode( rxData );
            success = reply["opcode"] == SMPOpcode.SMP_PAIRING_RANDOM;
            if not success:
                break;

            sRand = reply["value"];

            success, xConfirm = self.__calcConfirm( self.initiator.initiator, 0, sRand, self.pRequest, self.pResponse, ia, ra );
            if not success:
                break;
            success = xConfirm == sConfirm;
            if not success:
                txData = smpData.encode( SMPOpcode.SMP_PAIRING_FAILED, SMPError.SMP_ERROR_CONFIRM );
                self.__request( self.initiator.initiator, txData );
                break;

            success, stk = self.__calcSTK( self.initiator.initiator, 0, sRand, mRand );
            break;

        return success, stk;

    """
        Encrypt the link.

        
    """
    def __encryptLink(self, rand, ediv, ltk):
        status = le_start_encryption(self.transport, self.initiator.initiator, self.initiator.handles[0], rand, ediv, toArray(ltk, 16), 200);
        success = status == 0;
        event = get_event(self.transport, self.initiator.initiator, 100);
        self.trace.trace(7, str(event));
        success = success and event.isCommandStatus();
        while success:

            if not self.initiator.peer is None:
                success = has_event(self.transport, self.initiator.peer, 100)[0];
                while success:
                    event = get_event(self.transport, self.initiator.peer, 100);
                    self.trace.trace(7, str(event));
                    success = event.subEvent == MetaEvents.BT_HCI_EVT_LE_LTK_REQUEST;
                    if not success:
                        break;
                    handle = event.decode()[0];
                    status, handle = le_long_term_key_request_reply(self.transport, self.initiator.peer, handle, toArray(ltk, 16), 200);
                    success = status == 0;
                    if not success:
                        break;
                    event = get_event(self.transport, self.initiator.peer, 100);
                    self.trace.trace(7, str(event));
                    success = event.event == Events.BT_HCI_EVT_CMD_COMPLETE;
                    if not success:
                        break;
                    success = has_event(self.transport, self.initiator.peer, 1000)[0];
                    if not success:
                        break;
                    event = get_event(self.transport, self.initiator.peer, 100);
                    self.trace.trace(7, str(event));
                    success = (event.event == Events.BT_HCI_EVT_ENCRYPT_CHANGE_V1) or (event.event == Events.BT_HCI_EVT_ENCRYPT_KEY_REFRESH_COMPLETE);
                    if not success:
                        break;
                    if event.event == Events.BT_HCI_EVT_ENCRYPT_CHANGE_V1:
                        status, handle, enabled = event.decode();
                        success = (status == 0) and (enabled == 1);
                    else:
                        status, handle = event.decode();
                        success = status == 0;
                    break;

            if not success:
                break;
            success = has_event(self.transport, self.initiator.initiator, 1000)[0];
            if not success:
                break;
            event = get_event(self.transport, self.initiator.initiator, 100)[1:];
            self.trace.trace(7, str(event));
            success = (event.event == Events.BT_HCI_EVT_ENCRYPT_CHANGE_V1) or (event.event == Events.BT_HCI_EVT_ENCRYPT_KEY_REFRESH_COMPLETE);
            if not success:
                break;
            if event.event == Events.BT_HCI_EVT_ENCRYPT_CHANGE_V1:
                status, handle, enabled = event.decode();
                success = (status == 0) and (enabled == 1);
            else:
                status, handle = event.decode();
                success = status == 0;
            break;

        return success;

    """
        Distribute Initiators keys...
    
            LTK, EDIV, Rand, IRK, Address and Address Type are send to the peer.
    """
    def __sendInitiatorKeys(self, ltk, ediv, rand, irk):
        smpData = SMPData();

        txData = smpData.encode( SMPOpcode.SMP_ENCRYPTION_INFORMATION, ltk );
        success = self.__request( self.initiator.initiator, txData );
        while success:
            txData = smpData.encode( SMPOpcode.SMP_CENTRAL_IDENTIFICATION, ediv, rand );
            success = self.__request( self.initiator.initiator, txData );
            if not success:
                break;
            txData = smpData.encode( SMPOpcode.SMP_IDENTITY_INFORMATION, irk );
            success = self.__request( self.initiator.initiator, txData );
            if not success:
                break;
            txData = smpData.encode( SMPOpcode.SMP_IDENTITY_ADDRESS_INFORMATION, self.initiator.initiatorAddress.type, toNumber( self.initiator.initiatorAddress.address ) );
            success = self.__request( self.initiator.initiator, txData );
            break;
        return success;

    """
        Distribute Responder keys...

            LTK, EDIV, Rand, IRK, Address and Address Type are send to the initiator.
    """
    def __sendResponderKeys(self, ltk, ediv, rand, irk):
        smpData = SMPData();

        txData = smpData.encode( SMPOpcode.SMP_ENCRYPTION_INFORMATION, ltk );
        success = self.__request( self.initiator.peer, txData );
        while success:
            txData = smpData.encode( SMPOpcode.SMP_CENTRAL_IDENTIFICATION, ediv, rand );
            success = self.__request( self.initiator.peer, txData );
            if not success:
                break;
            txData = smpData.encode( SMPOpcode.SMP_IDENTITY_INFORMATION, irk );
            success = self.__request( self.initiator.peer, txData );
            if not success:
                break;
            txData = smpData.encode( SMPOpcode.SMP_IDENTITY_ADDRESS_INFORMATION, self.initiator.peerAddress.type, toNumber( self.initiator.peerAddress.address ) );
            success = self.__request( self.initiator.peer, txData );
            break;
        return success;

    """
        Receive keys send by the Responder...

            LTK, EDIV, Rand, IRK, Address and Address Type are received.
    """
    def __recvResponderKeys(self):
        smpData = SMPData();

        LTKs, EDIVs, RANDs, IRKs, address, addressType = 0, 0, 0, 0, 0, 0;

        mask  = (1<<SMPOpcode.SMP_ENCRYPTION_INFORMATION) | (1<<SMPOpcode.SMP_CENTRAL_IDENTIFICATION);
        mask |= (1<<SMPOpcode.SMP_IDENTITY_INFORMATION) | (1<<SMPOpcode.SMP_IDENTITY_ADDRESS_INFORMATION);
        recv = 0;
        success = True;

        while success and ((recv & mask) != mask):
            success, rxData = self.__response( self.initiator.initiator );
            if not success:
                break;
            reply = smpData.decode( rxData );

            recv |= 1<<reply["opcode"];

            if   reply["opcode"] == SMPOpcode.SMP_ENCRYPTION_INFORMATION:
               success = True;
               LTKs = reply["ltk"];
            elif reply["opcode"] == SMPOpcode.SMP_CENTRAL_IDENTIFICATION:
               success = True;
               EDIVs = reply["ediv"];
               RANDs = reply["rand"];
            elif reply["opcode"] == SMPOpcode.SMP_IDENTITY_INFORMATION:
               success = True;
               IRKs = reply["irk"];
            elif reply["opcode"] == SMPOpcode.SMP_IDENTITY_ADDRESS_INFORMATION:
               success = True;
               address = reply["address"];
               addressType = reply["type"];
            else:
               success = False;
    
            if not success:
                break;
        return success, LTKs, EDIVs, RANDs, IRKs, address, addressType;

    """
        Receive keys send by the Initiator...

            LTK, EDIV, Rand and IRK are received.
    """
    def __recvInitiatorKeys(self):
        smpData = SMPData();

        LTKm, EDIVm, RANDm, IRKm, address, addressType = 0, 0, 0, 0, 0, 0;

        mask  = (1<<SMPOpcode.SMP_ENCRYPTION_INFORMATION) | (1<<SMPOpcode.SMP_CENTRAL_IDENTIFICATION);
        mask |= (1<<SMPOpcode.SMP_IDENTITY_INFORMATION) | (1<<SMPOpcode.SMP_IDENTITY_ADDRESS_INFORMATION);
        recv = 0;
        success = True;

        while success and ((recv & mask) != mask):
            success, rxData = self.__response( self.initiator.peer );
            if not success:
                break;
            reply = smpData.decode( rxData );

            recv |= 1<<reply["opcode"];

            if   reply["opcode"] == SMPOpcode.SMP_ENCRYPTION_INFORMATION:
               success = True;
               LTKm = reply["ltk"];
            elif reply["opcode"] == SMPOpcode.SMP_CENTRAL_IDENTIFICATION:
               success = True;
               EDIVm = reply["ediv"];
               RANDm = reply["rand"];
            elif reply["opcode"] == SMPOpcode.SMP_IDENTITY_INFORMATION:
               success = True;
               IRKm = reply["irk"];
            elif reply["opcode"] == SMPOpcode.SMP_IDENTITY_ADDRESS_INFORMATION:
               success = True;
               address = reply["address"];
               addressType = reply["type"];
            else:
               success = False;
    
            if not success:
                break;
        return success, LTKm, EDIVm, RANDm, IRKm, address, addressType;

    """
        Establish an encrypted link between parties in a connection.

        First exchange capabilities and requirements to the encryption.
        Based on the outcome of this exchange of requirements and capabilities a decision is made whether to use LE Legacy Pairing or Secure Connections Pairing.
        Currently only LE Legacy Pairing is supported...

    """
    def pair(self):

        authRequest  = SMPBondingFlag.SMP_BOND_REQUESTED | SMPMITMFlag.SMP_MITM_NONE | SMPSecureConnections.SMP_SC_NOT_SUPPORTED;
        authRequest |= SMPKeyPressNotifications.SMP_KPN_NONE | SMPSupportH7.SMP_CT2_NO_SUPPORT;

        success, reply = self.__capabilities( authRequest );

        while success:

            SCFlagInitiator = (authRequest & SMPSecureConnections.SMP_SC_SUPPORTED) == SMPSecureConnections.SMP_SC_SUPPORTED;
            SCFlagResponder = (reply["auth"] & SMPSecureConnections.SMP_SC_SUPPORTED) == SMPSecureConnections.SMP_SC_SUPPORTED;

            CAPFlagINitiator = OOBFlagInitiator = MITMFlagInitiator = 0;

            CAPFlagResponder = reply["capability"];
            OOBFlagResponder = (reply["oob"] & SMPOOBFlag.SMP_OOB_AUTH_DATA_PRESENT) == SMPOOBFlag.SMP_OOB_AUTH_DATA_PRESENT;
            MITMFlagResponder = (reply["auth"] & SMPMITMFlag.SMP_MITM_REQUESTED) == SMPMITMFlag.SMP_MITM_REQUESTED;

            if SCFlagInitiator and SCFlagResponder:
                self.trace.trace(6,"Both Initiator and Responder supports Secure Connections...");

            success, self.stk = self.__legacyPairing( self.initiator.initiatorAddress, self.initiator.peerAddress );
            if not success:
                break;
            success = self.__encryptLink( 0, 0, self.stk );
            if not success:
                break;

            if not self.initiator.peer is None:
                success, ediv, rand, ltk = self.__calculateKeys( self.initiator.peer );
                if not success:
                    break;
                success = self.__sendResponderKeys( ltk, ediv, rand, self.IRKs );
                if not success:
                    break;

            success, self.LTKs, self.EDIVs, self.RANDs, self.IRKs, address, addressType = self.__recvResponderKeys( );
            if not success:
                break;

            self.trace.trace(6, "Responders  LTK = 0x%032X" % self.LTKs);
            self.trace.trace(6, "Responders EDIV = 0x%04X" % self.EDIVs);
            self.trace.trace(6, "Responders RAND = 0x%016X" % self.RANDs);
            self.trace.trace(6, "Responders  IRK = 0x%032X" % self.IRKs);
            self.trace.trace(6, "Responders ADDR = %s" % formatAddress(toArray(address, 6), addressType));

            success, self.ediv, self.rand, self.ltk = self.__calculateKeys( self.initiator.initiator );
            if not success:
                break;
            success = self.__sendInitiatorKeys( self.ltk, self.ediv, self.rand, self.IRKm );

            self.trace.trace(6, "Initiators  LTK = 0x%032X" % self.ltk);
            self.trace.trace(6, "Initiators EDIV = 0x%04X" % self.ediv);
            self.trace.trace(6, "Initiators RAND = 0x%016X" % self.rand);

            if not success:
                break;

            if not self.initiator.peer is None:
                success, LTKm, EDIVm, RANDm, IRKm, address, addressType = self.__recvInitiatorKeys( );
                if not success:
                    break;
            break;

        return success;

    """
        Pause encryption on the link...

                LL_PAUSE_ENC_REQ -->
            <-- LL_PAUSE_ENC_RSP
                LL_PAUSE_ENC_RSP -->
    """
    def pause(self):
        success = self.__encryptLink( 0, 0, self.stk );
        return success;

    """
        Resume encryption on the link...

                LL_ENC_REQ -->
            <-- LL_ENC_RSP
            <-- LL_START_ENC_REQ
                LL_START_ENC_RSP -->
            <-- LL_START_ENC_RSP
    """
    def resume(self):
        return True;
