import pytest
import pyparsing as pp
from crucible.parser.traces import trace_parser, event_parser, call_end_parser, trace_line

ParseException = pp.exceptions.ParseException


def assert_traces_from_fixture(fixture):
    lines = fixture.split("Traces:\n")[1].split("Suite result")[0].split("\n")
    for line in lines:
        if line.strip():
            try:
                trace_line.parse_string(line, parse_all=True)
            except ParseException as e:
                print("Line: ")
                print(line)
                print("------------------")
                raise e


def test_each_suites_trace(suites_trace):
    assert_traces_from_fixture(suites_trace)


def test_each_test10(test10):
    assert_traces_from_fixture(test10)


def test_each_test12(test12):
    assert_traces_from_fixture(test12)


def test_each_test13(test13):
    assert_traces_from_fixture(test13)


def test_each_test14(test14):
    assert_traces_from_fixture(test14)


def test_event_parser():
    event = event_parser.parse_string(
        "│   │   │   │   ├─ emit Transfer(from: trader: [0x10E951fA67B511D044803c7757DA445Ddf646f6d], to: 0x9380fA34Fd9e4Fd14c06305fd7B6199089eD4eb9, value: 1000000000000000000 [1e18])"
    )
    assert event.prefix['depth'] == 4
    assert event.prefix['is_last_child'] == False
    assert event.name == "Transfer"
    assert len(event.args) == 3
    assert event.args[0].key == "from"
    assert event.args[0].value.address == "0x10E951fA67B511D044803c7757DA445Ddf646f6d"
    assert event.args[0].value.label == "trader"
    assert event.args[1].key == "to"
    assert event.args[1].value.address == "0x9380fA34Fd9e4Fd14c06305fd7B6199089eD4eb9"
    assert event.args[2].key == "value"
    assert event.args[2].value.number == 1000000000000000000


def test_call_parser():
    call0 = trace_parser.parse_string(
        "├─ [8536] 0x000000000000000000000000000000000000ce10::getAddressForStringOrDie(\"Broker\") [staticcall]"
    )
    call1 = trace_parser.parse_string(
        "├─ [8536] Contract::getAddressForStringOrDie(\"Broker\", 234) [staticcall]"
    )
    call2 = trace_parser.parse_string(
        "    ├─ [0] VM::addr(<pk>) [staticcall]"
    )
    call3 = trace_parser.parse_string(
        "    ├─ [0] VM::expectRevert(Governor: proposer votes below proposal threshold)"
    )


def test_call_end_parser():
    call_end = call_end_parser.parse_string(
        "│   └─ ← [Return] NewEmissionTarget: [0x2b65ee39398edDb5DAa958faB2FaAbCb957Cc09F]"
    )
