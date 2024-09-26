import pytest
import pyparsing as pp
from crucible.parser.suites import suites, suite_start, suite_end, test_result, test, suite, traces


def test_suite_start():
    fixture = "Ran 3 tests for test/unit/swap/BiPoolManager.t.sol:BiPoolManagerTest_ConstantSum"
    result = suite_start.parse_string(fixture)
    assert result.count == 3
    assert result.contract == "test/unit/swap/BiPoolManager.t.sol:BiPoolManagerTest_ConstantSum"


def test_test_result():
    fixture = "[PASS] test_quotesAndSwaps_whenMedianNotRecent_shouldRevert() (gas: 201220)"
    result = test_result.parse_string(fixture)
    assert result.gas == 201220
    assert result.test == "test_quotesAndSwaps_whenMedianNotRecent_shouldRevert"
    assert result.result == "PASS"


def test_test_failed0():
    fixture = "[FAIL: setup failed: vm.createSelectFork: Could not instantiate forked environment with fork url: YOUR_MAINNET_RPC_URL] setUp() (gas: 0)"
    result = test_result.parse_string(fixture)
    assert result.result == "FAIL"
    assert result.reason == "setup failed: vm.createSelectFork: Could not instantiate forked environment with fork url: YOUR_MAINNET_RPC_URL"
    assert result.test == "setUp"
    assert result.gas == 0


def test_test_failed():
    fixture = "[FAIL. Reason: assertion failed: 0x9bC6bc8F96DBa9Ec1c97D9AE3519586c48407Eb1 != 0x0000000000000000000000000000000000000000] test_emitsRelayerDeployedEvent() (gas: 94724)"
    result = test_result.parse_string(fixture)
    assert result.result == "FAIL"
    assert result.reason == "assertion failed: 0x9bC6bc8F96DBa9Ec1c97D9AE3519586c48407Eb1 != 0x0000000000000000000000000000000000000000"
    assert result.test == "test_emitsRelayerDeployedEvent"
    assert result.gas == 94724


def test_suite():
    fixture = """
Ran 3 tests for test/unit/swap/BiPoolManager.t.sol:BiPoolManagerTest_ConstantSum
[PASS] test_quotesAndSwaps_whenMedianNotRecent_shouldRevert() (gas: 201220)
[PASS] test_quotesAndSwaps_whenNotEnoughReports_shouldRevert() (gas: 258283)
[PASS] test_quotesAndSwaps_whenOldestReportExpired_shouldRevert() (gas: 275475)
Suite result: ok. 3 passed; 0 failed; 0 skipped; finished in 2.62ms (601.04µs CPU time)
    """.strip()
    result = suite.parse_string(fixture)
    assert result.count == 3
    assert len(result.tests) == 3
    assert result.tests[0].result == "PASS"
    assert result.tests[0].gas == 201220
    assert result.tests[0].test == "test_quotesAndSwaps_whenMedianNotRecent_shouldRevert"


def test_suites1(suites1):
    result = suites.parse_string(suites1)
    assert len(result.suites) == 2
    assert result.suites[0].count == 3
    assert result.suites[1].count == 11
    assert result.passed == 14
    assert result.failed == 0
    assert result.duration == "1.34s"


def test_suites2(suites2):
    result = suites.parse_string(suites2)
    assert len(result.suites) == 1
    assert result.passed == 8
    assert result.total == 8
    assert result.suites[0].count == 8


def test_suites_trace(suites_trace):
    result = suites.parse_string(suites_trace)
    assert len(result.suites) == 1
    assert result.passed == 1
    assert result.failed == 0
    assert result.suites[0].count == 1
    assert result.suites[0].tests[0].result == "PASS"
    assert result.suites[0].tests[0].gas == 329715
    assert len(result.suites[0].tests[0].trace_groups) == 1
    assert len(result.suites[0].tests[0].trace_groups[0].traces) == 113


def test_failing_traces(failing_traces):
    traces.parse_string(failing_traces, parse_all=True)


def test_failing_traces(failing_traces2):
    traces.parse_string(failing_traces2, parse_all=True)
