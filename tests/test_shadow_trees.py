import pytest
from crucible.parser.parser import output
from crucible.data.suite_tree import SuiteTree
from crucible.data.trace_tree import TraceTree


def test_suite_tree(full):
    out = output.parse_string(full, parse_all=True)
    tree = SuiteTree(out)


def test_trace_tree(test):
    out = output.parse_string(test, parse_all=True)
    tree = TraceTree(out)
    breakpoint()
