import pytest
from crucible.parser.parser import output
from crucible.runner.output import Output


def test1(forge_build_error):
    o = Output(output.parse_string(forge_build_error, parse_all=True))


def test2(forge_build_warnings):
    o = Output(output.parse_string(forge_build_warnings, parse_all=True))


def test3(forge_build_warnings2):
    output.parse_string(forge_build_warnings2, parse_all=True)


def test4(forge_compilation_skipped):
    output.parse_string(forge_compilation_skipped, parse_all=True)


def test5(traces_small):
    output.parse_string(traces_small, parse_all=True)


def test6(forge_full_suite):
    output.parse_string(forge_full_suite, parse_all=True)


def test7(test):
    output.parse_string(test, parse_all=True)


def test8(test2):
    output.parse_string(test2, parse_all=True)


def test9(test9):
    output.parse_string(test9, parse_all=True)


def test10(test10):
    output.parse_string(test10, parse_all=True)


def test11(test11):
    output.parse_string(test11, parse_all=True)


def test12(test12):
    output.parse_string(test12, parse_all=True)


def test13(test13):
    output.parse_string(test13, parse_all=True)


def test14(test14):
    output.parse_string(test14, parse_all=True)


def test15(suite_fail1):
    output.parse_string(suite_fail1, parse_all=True)


def test_sablier(sablier):
    output.parse_string(sablier, parse_all=True)


def test_sablier2(sablier2):
    output.parse_string(sablier2, parse_all=True)


def test_sablier3(sablier3):
    output.parse_string(sablier3, parse_all=True)


def test_sablier4(sablier4):
    o = Output(output.parse_string(sablier4, parse_all=True))
