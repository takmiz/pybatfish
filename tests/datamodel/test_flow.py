#   Copyright 2018 The Batfish Open Source Project
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from __future__ import absolute_import, print_function

import attr
import pytest

from pybatfish.datamodel.flow import (EnterInputIfaceStepDetail,
                                      ExitOutputIfaceStepDetail, Flow,
                                      FlowTraceHop, HeaderConstraints, Hop,
                                      RoutingStepDetail, Step)


def testFlowDeserialization():
    hopDict = {
        "dscp": 0,
        "dstIp": "2.1.1.1",
        "dstPort": 0,
        "ecn": 0,
        "fragmentOffset": 0,
        "icmpCode": 255,
        "icmpVar": 255,
        "ingressInterface": "intface",
        "ingressNode": "ingress",
        "ingressVrf": "vrfAbc",
        "ipProtocol": "IP",
        "packetLength": 0,
        "srcIp": "5.5.1.1",
        "srcPort": 0,
        "state": "NEW",
        "tag": "BASE",
        "tcpFlagsAck": 0,
        "tcpFlagsCwr": 0,
        "tcpFlagsEce": 0,
        "tcpFlagsFin": 0,
        "tcpFlagsPsh": 0,
        "tcpFlagsRst": 0,
        "tcpFlagsSyn": 0,
        "tcpFlagsUrg": 0
    }

    # check deserialization
    flow = Flow.from_dict(hopDict)
    assert flow.srcIp == "5.5.1.1"
    assert flow.ingressInterface == "intface"
    assert flow.ingressVrf == "vrfAbc"

    # check the string representation has the essential elements (without forcing a strict format)
    flowStr = str(flow)
    assert "5.5.1.1:0" in flowStr
    assert "intface" in flowStr
    assert "vrfAbc" in flowStr


# test if a flow is deserialized properly when the optional fields are missing
def testFlowDeserializationOptionalMissing():
    hopDict = {
        "dscp": 0,
        "dstIp": "2.1.1.1",
        "dstPort": 0,
        "ecn": 0,
        "fragmentOffset": 0,
        "icmpCode": 255,
        "icmpVar": 255,
        "ingressNode": "ingress",
        "ipProtocol": "IP",
        "packetLength": 0,
        "srcIp": "5.5.1.1",
        "srcPort": 0,
        "state": "NEW",
        "tag": "BASE",
        "tcpFlagsAck": 0,
        "tcpFlagsCwr": 0,
        "tcpFlagsEce": 0,
        "tcpFlagsFin": 0,
        "tcpFlagsPsh": 0,
        "tcpFlagsRst": 0,
        "tcpFlagsSyn": 0,
        "tcpFlagsUrg": 0
    }
    # check deserialization
    flow = Flow.from_dict(hopDict)
    assert flow.srcIp == "5.5.1.1"

    # should convert to string without problems
    str(flow)


def test_flow_trace_hop_no_transformed_flow():
    """Test we don't crash on missing or None values."""
    FlowTraceHop.from_dict(
        {'edge': {'node1': 'dummy', 'node1interface': 'eth0',
                  'node2': 'router1', 'node2interface': 'Ethernet1'},
         'filterIn': None, 'filterOut': None, 'routes': [
            'StaticRoute<0.0.0.0/0,nhip:10.192.48.1,nhint:eth0>_fnhip:10.192.48.1'],
         'transformedFlow': None})

    FlowTraceHop.from_dict(
        {'edge': {'node1': 'dummy', 'node1interface': 'eth0',
                  'node2': 'router1', 'node2interface': 'Ethernet1'},
         'filterIn': None, 'filterOut': None, 'routes': [
            'StaticRoute<0.0.0.0/0,nhip:10.192.48.1,nhint:eth0>_fnhip:10.192.48.1']})


def test_get_ip_protocol_str():
    flowDict = {
        "dscp": 0,
        "dstIp": "2.1.1.1",
        "dstPort": 0,
        "ecn": 0,
        "fragmentOffset": 0,
        "icmpCode": 255,
        "icmpVar": 255,
        "ingressNode": "ingress",
        "ipProtocol": "UNNAMED_243",
        "packetLength": 0,
        "srcIp": "5.5.1.1",
        "srcPort": 0,
        "state": "NEW",
        "tag": "BASE",
        "tcpFlagsAck": 0,
        "tcpFlagsCwr": 0,
        "tcpFlagsEce": 0,
        "tcpFlagsFin": 0,
        "tcpFlagsPsh": 0,
        "tcpFlagsRst": 0,
        "tcpFlagsSyn": 0,
        "tcpFlagsUrg": 0
    }
    assert Flow.from_dict(flowDict).get_ip_protocol_str() == "ipProtocol=243"

    flowDict["ipProtocol"] = "TCP"
    assert Flow.from_dict(flowDict).get_ip_protocol_str() == "TCP"


def test_header_constraints_serialization():
    hc = HeaderConstraints()
    hcd = hc.dict()
    for field in attr.fields(HeaderConstraints):
        assert hcd[field.name] is None

    hc = HeaderConstraints(srcIps="1.1.1.1")
    assert hc.dict()["srcIps"] == "1.1.1.1"

    hc = HeaderConstraints(dstPorts=["10-20", "33-33"])
    assert hc.dict()["dstPorts"] == "10-20,33-33"

    hc = HeaderConstraints(dstPorts="10-20,33")
    assert hc.dict()["dstPorts"] == "10-20,33"

    hc = HeaderConstraints(applications="dns,ssh")
    assert hc.dict()["applications"] == ['dns', 'ssh']

    hc = HeaderConstraints(applications=['dns', 'ssh'])
    assert hc.dict()["applications"] == ['dns', 'ssh']

    hc = HeaderConstraints(ipProtocols="  ,  dns,")
    assert hc.dict()["ipProtocols"] == ['dns']

    hc = HeaderConstraints(ipProtocols=['tcp', 'udp'])
    assert hc.dict()["ipProtocols"] == ['tcp', 'udp']

    with pytest.raises(ValueError):
        HeaderConstraints(applications="")


def test_hop_repr_str():
    hop = Hop("node1", [
        Step(
            EnterInputIfaceStepDetail("in_iface1", "in_vrf1", "in_filter1"),
            "SENT_IN"),
        Step(RoutingStepDetail(
            [{"network": "1.1.1.1/24", "protocol": "bgp",
              "nextHopIp": "1.2.3.4"},
             {"network": "1.1.1.2/24", "protocol": "static",
              "nextHopIp": "1.2.3.5"}]), "FORWARDED"),
        Step(ExitOutputIfaceStepDetail("out_iface1", "out_filter1", None),
             "SENT_OUT")
    ])
    assert str(
        hop) == "node: node1\n steps: SENT_IN(in_iface1: in_filter1) -> FORWARDED(Routes: bgp [Network: 1.1.1.1/24, Next Hop IP:1.2.3.4],static [Network: 1.1.1.2/24, Next Hop IP:1.2.3.5]) -> SENT_OUT(out_iface1: out_filter1)"


if __name__ == "__main__":
    pytest.main()
