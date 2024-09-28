import pytest
import pyparsing as pp
from crucible.parser.traces import trace_parser, event_parser, call_end_parser, trace_line, raw_event_parser

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


def test_raw_event_parser():
    event = """
    emit topic 0: 0xe7b046415cac9de47940c3087e06db13a0e058ccf53ac5f0edd49ebb4c2c3a6f
    │   │   │   │        topic 1: 0x89de88b8eb790de26f4649f543cb6893d93635c728ac857f0926e842fb0d298b
    │   │   │   │        topic 2: 0x0000000000000000000000005615deb798bb3e4dfa0139dfa1b3d433cc23b72f
    │   │   │   │        topic 3: 0x000000000000000000000000765de816845861e75a25fca122bb6898b8b1282a
    │   │   │   │           data: 0x00000000000000000000000022d9db95e6ae61c104a7b6f6c78d7993b94ec901000000000000000000000000456a3d042c0dbd3db53d5489e98dfb038553b0d0000000000000000000000000000000000000000000000000000007468d3cc41000000000000000000000000000000000000000000000000000039e90825b032c
    """.strip()
    raw_event = raw_event_parser.parse_string(event, parse_all=True)
    assert raw_event.topic0.bytes32 == "0xe7b046415cac9de47940c3087e06db13a0e058ccf53ac5f0edd49ebb4c2c3a6f"
    assert raw_event.topic1.bytes32 == "0x89de88b8eb790de26f4649f543cb6893d93635c728ac857f0926e842fb0d298b"
    assert raw_event.topic2.bytes32 == "0x0000000000000000000000005615deb798bb3e4dfa0139dfa1b3d433cc23b72f"
    assert raw_event.topic3.bytes32 == "0x000000000000000000000000765de816845861e75a25fca122bb6898b8b1282a"
    assert raw_event.data['bytes'] == "0x00000000000000000000000022d9db95e6ae61c104a7b6f6c78d7993b94ec901000000000000000000000000456a3d042c0dbd3db53d5489e98dfb038553b0d0000000000000000000000000000000000000000000000000000007468d3cc41000000000000000000000000000000000000000000000000000039e90825b032c"


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
        "emit Transfer(from: trader: [0x10E951fA67B511D044803c7757DA445Ddf646f6d], to: 0x9380fA34Fd9e4Fd14c06305fd7B6199089eD4eb9, value: 1000000000000000000 [1e18])"
    )
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
        "[8536] 0x000000000000000000000000000000000000ce10::getAddressForStringOrDie(\"Broker\") [staticcall]"
    )
    call1 = trace_parser.parse_string(
        "[8536] Contract::getAddressForStringOrDie(\"Broker\", 234) [staticcall]"
    )
    call2 = trace_parser.parse_string(
        "[0] VM::addr(<pk>) [staticcall]"
    )
    call3 = trace_parser.parse_string(
        "[0] VM::expectRevert(Governor: proposer votes below proposal threshold)"
    )


def test_call_end_parser():
    call_end = call_end_parser.parse_string(
        "← [Return] NewEmissionTarget: [0x2b65ee39398edDb5DAa958faB2FaAbCb957Cc09F]"
    )


def test_traces_sablier4(sablier4):
    assert_traces_from_fixture(sablier4)
